#!/usr/bin/env python3
"""Safely archive a completed active task into progress logs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile

from _paradigma_yaml import (
    ParseFailure,
    flatten_mapping,
    parse_markdown_text,
    read_utf8_text,
)
from _task_state import (
    TaskStateFailure,
    TaskStatus,
    extract_section,
    parse_task_status,
    task_identifier,
)


ROOT = Path(__file__).resolve().parents[2]
ACTIVE_TASK = ROOT / "memory-bank" / "runtime" / "active-task.md"
ACTIVE_TASK_TEMPLATE = ROOT / "memory-bank-template" / "runtime" / "active-task.template.md"
PROGRESS_ROOT = ROOT / "memory-bank" / "logs" / "progress"
LAST_ARCHIVE_ID_PATTERN = re.compile(
    r"^Last archive ID:\s*`?([0-9a-f]{64})`?\s*$", re.MULTILINE
)


class ArchiveExit(IntEnum):
    OK = 0
    INVALID_TASK = 1
    IO_ERROR = 2
    CONFLICT = 3


class ArchiveFailure(RuntimeError):
    def __init__(self, code: str, message: str, exit_code: ArchiveExit):
        self.code = code
        self.exit_code = exit_code
        super().__init__(message)

    def format(self) -> str:
        return f"[{self.code}] {self}"


@dataclass(frozen=True)
class ArchivePlan:
    task_id: str
    status: TaskStatus
    source_hash: str
    archive_id: str
    target: Path
    archive_content: str
    reset_content: str
    create_archive: bool

    def format(self) -> str:
        archive_action = "CREATE" if self.create_archive else "KEEP (already created)"
        return "\n".join(
            [
                "Mutation plan:",
                f"  task_id: {self.task_id}",
                f"  status: {self.status.value}",
                f"  archive_id: {self.archive_id}",
                f"  {archive_action}: {display_path(self.target)}",
                f"  REPLACE: {display_path(ACTIVE_TASK)} -> status=pending",
            ]
        )


def now_local() -> datetime:
    return datetime.now().astimezone()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff-]+", "-", value)
    return value.strip("-") or "active-task"


def replace_section(text: str, heading: str, value: str) -> str:
    pattern = re.compile(
        rf"(^## {re.escape(heading)}\s*$)(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    if not pattern.search(text):
        raise ArchiveFailure(
            "PD_ARCHIVE_TEMPLATE_ERROR",
            f"active-task template is missing section `## {heading}`",
            ArchiveExit.INVALID_TASK,
        )
    return pattern.sub(
        lambda match: f"{match.group(1)}\n\n{value.strip()}\n\n",
        text,
        count=1,
    )


def parse_status(text: str) -> TaskStatus:
    try:
        return parse_task_status(text)
    except TaskStateFailure as error:
        raise ArchiveFailure(
            "PD_ARCHIVE_INVALID_STATUS",
            str(error),
            ArchiveExit.INVALID_TASK,
        ) from error


def is_completed(text: str) -> bool:
    """Return true only for the exact, validated `completed` state."""
    return parse_status(text) is TaskStatus.COMPLETED


def last_archive_id(text: str) -> str | None:
    match = LAST_ARCHIVE_ID_PATTERN.search(extract_section(text, "Notes"))
    return match.group(1) if match else None


def is_already_archived_reset(text: str, status: TaskStatus) -> bool:
    return (
        status is TaskStatus.PENDING
        and not task_identifier(text)
        and last_archive_id(text) is not None
    )


def archive_path(task_slug: str, current_time: datetime) -> Path:
    base = PROGRESS_ROOT / f"{current_time:%Y-%m-%d}-{task_slug}.md"
    if not base.exists():
        return base
    for index in range(2, 100):
        candidate = PROGRESS_ROOT / f"{current_time:%Y-%m-%d}-{task_slug}-{index}.md"
        if not candidate.exists():
            return candidate
    raise ArchiveFailure(
        "PD_ARCHIVE_TARGET_EXHAUSTED",
        "could not find an available archive filename",
        ArchiveExit.CONFLICT,
    )


def find_existing_archive(archive_id: str) -> Path | None:
    if not PROGRESS_ROOT.exists():
        return None
    marker = f'archive_id: "{archive_id}"'
    for path in sorted(PROGRESS_ROOT.glob("*.md")):
        text = read_utf8_text(path)
        if marker not in text:
            continue
        parsed = parse_markdown_text(text, source=str(path))
        metadata = flatten_mapping(parsed.metadata)
        if metadata.get("paradigma.archive_id") == archive_id:
            return path
    return None


def render_archive_content(
    active_text: str, task_id: str, archive_id: str, current_time: datetime
) -> str:
    title = json.dumps(f"Archived Active Task {task_id}", ensure_ascii=False)
    return f'''---
type: paradigma-progress-log
title: {title}
description: Archived active task generated by pd-archive-task.py.
tags: [progress, archive, active-task]
timestamp: {current_time.isoformat(timespec="seconds")}
paradigma:
  layer: logs
  lifecycle: append-only
  update_policy: append-only
  source: memory-bank/runtime/active-task.md
  archive_id: "{archive_id}"
---

# Archived Active Task

Archived at: {current_time:%Y-%m-%d %H:%M}

{active_text.strip()}
'''


def render_reset_content(
    template_text: str, target: Path, archive_id: str, current_time: datetime
) -> str:
    content = template_text.replace(
        "YYYY-MM-DDTHH:mm:ssZ", current_time.isoformat(timespec="seconds")
    )
    content = replace_section(content, "Current Status", TaskStatus.PENDING.value)
    notes = (
        f"Last archive: {display_path(target)}\n"
        f"Last archive ID: `{archive_id}`"
    )
    content = replace_section(content, "Notes", notes)
    return content.rstrip() + "\n"


def build_archive_plan(
    active_text: str, template_text: str, current_time: datetime, *, force: bool
) -> ArchivePlan:
    status = parse_status(active_text)
    if status is not TaskStatus.COMPLETED and not force:
        raise ArchiveFailure(
            "PD_ARCHIVE_TASK_NOT_ARCHIVABLE",
            f"task status is {status.value!r}; only completed tasks can be archived",
            ArchiveExit.INVALID_TASK,
        )
    identifier = task_identifier(active_text)
    if not identifier:
        raise ArchiveFailure(
            "PD_ARCHIVE_MISSING_TASK_ID",
            "Task ID must be non-empty before archiving",
            ArchiveExit.INVALID_TASK,
        )
    source_hash = hashlib.sha256(active_text.encode("utf-8")).hexdigest()
    archive_id = source_hash
    existing = find_existing_archive(archive_id)
    target = existing or archive_path(slugify(identifier), current_time)
    archive_text = (
        read_utf8_text(existing)
        if existing is not None
        else render_archive_content(active_text, identifier, archive_id, current_time)
    )
    return ArchivePlan(
        task_id=identifier,
        status=status,
        source_hash=source_hash,
        archive_id=archive_id,
        target=target,
        archive_content=archive_text,
        reset_content=render_reset_content(
            template_text, target, archive_id, current_time
        ),
        create_archive=existing is None,
    )


def _write_temp_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return temporary_path


def atomic_create(path: Path, content: str) -> None:
    temporary_path = _write_temp_file(path, content)
    try:
        os.link(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def atomic_replace(path: Path, content: str) -> None:
    temporary_path = _write_temp_file(path, content)
    try:
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def execute_archive_plan(plan: ArchivePlan) -> None:
    current_text = read_utf8_text(ACTIVE_TASK)
    current_hash = hashlib.sha256(current_text.encode("utf-8")).hexdigest()
    if current_hash != plan.source_hash:
        raise ArchiveFailure(
            "PD_ARCHIVE_SOURCE_CHANGED",
            "active task changed after the mutation plan was generated",
            ArchiveExit.CONFLICT,
        )
    try:
        if plan.create_archive:
            atomic_create(plan.target, plan.archive_content)
        atomic_replace(ACTIVE_TASK, plan.reset_content)
    except FileExistsError as error:
        raise ArchiveFailure(
            "PD_ARCHIVE_TARGET_CONFLICT",
            f"archive target appeared while applying the plan: {display_path(plan.target)}",
            ArchiveExit.CONFLICT,
        ) from error
    except OSError as error:
        raise ArchiveFailure(
            "PD_ARCHIVE_IO_ERROR",
            f"archive transaction failed: {error}",
            ArchiveExit.IO_ERROR,
        ) from error


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="apply the archive mutation plan")
    mode.add_argument("--dry-run", action="store_true", help="print the mutation plan without writing (default)")
    parser.add_argument(
        "--force",
        action="store_true",
        help="archive a task in another valid state; unknown states still fail",
    )
    args = parser.parse_args()

    try:
        if not ACTIVE_TASK.exists():
            raise ArchiveFailure(
                "PD_ARCHIVE_MISSING_ACTIVE_TASK",
                f"missing {display_path(ACTIVE_TASK)}",
                ArchiveExit.INVALID_TASK,
            )
        active_text = read_utf8_text(ACTIVE_TASK)
        status = parse_status(active_text)
        if is_already_archived_reset(active_text, status):
            print(
                "Already archived; active task is the pending reset state "
                f"for archive {last_archive_id(active_text)}."
            )
            return ArchiveExit.OK
        template_text = read_utf8_text(ACTIVE_TASK_TEMPLATE)
        plan = build_archive_plan(
            active_text, template_text, now_local(), force=args.force
        )
        print(plan.format())
        if not args.write:
            print("Dry run only. Pass --write to apply this mutation plan.")
            return ArchiveExit.OK
        execute_archive_plan(plan)
        print(
            f"Archived active task to {display_path(plan.target)} and reset "
            f"{display_path(ACTIVE_TASK)}."
        )
        return ArchiveExit.OK
    except ParseFailure as error:
        print(f"ERROR: {error.diagnostic.format()}", file=sys.stderr)
        return ArchiveExit.IO_ERROR
    except ArchiveFailure as error:
        print(f"ERROR: {error.format()}", file=sys.stderr)
        return error.exit_code


if __name__ == "__main__":
    sys.exit(main())
