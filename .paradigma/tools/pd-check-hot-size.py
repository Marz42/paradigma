#!/usr/bin/env python3
"""Report HOT memory and runtime file sizes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import sys

from _paradigma_yaml import ParseFailure, parse_flat_frontmatter, read_utf8_text


ROOT = Path(__file__).resolve().parents[2]
ACTIVE_TASK = ROOT / "memory-bank" / "runtime" / "active-task.md"
KNOWLEDGE_ROOT = ROOT / "memory-bank" / "knowledge"
PROGRESS_INDEX = ROOT / "memory-bank" / "logs" / "progress" / "index.md"


@dataclass
class SizeCheck:
    path: Path
    lines: int
    warn_at: int
    error_at: int
    category: str

    @property
    def level(self) -> str:
        if self.lines > self.error_at:
            return "ERROR"
        if self.lines > self.warn_at:
            return "WARN"
        return "OK"

    def format(self) -> str:
        return f"{self.level}: {self.path.relative_to(ROOT)}: {self.lines} lines ({self.category}; warn>{self.warn_at}, error>{self.error_at})"


def line_count(path: Path) -> int:
    return len(read_utf8_text(path).splitlines()) if path.exists() else 0


def hot_documents() -> list[Path]:
    documents: list[Path] = []
    if not KNOWLEDGE_ROOT.exists():
        return documents
    for path in sorted(KNOWLEDGE_ROOT.rglob("*.md")):
        if path.name in {"index.md", "log.md"}:
            continue
        metadata, _body = parse_flat_frontmatter(path)
        if metadata.get("paradigma.temperature") == "hot":
            documents.append(path)
    return documents


def collect_checks() -> list[SizeCheck]:
    checks: list[SizeCheck] = []
    if ACTIVE_TASK.exists():
        checks.append(SizeCheck(ACTIVE_TASK, line_count(ACTIVE_TASK), 160, 260, "runtime active task"))
    if PROGRESS_INDEX.exists():
        checks.append(SizeCheck(PROGRESS_INDEX, line_count(PROGRESS_INDEX), 160, 260, "progress index"))
    for path in hot_documents():
        checks.append(SizeCheck(path, line_count(path), 260, 420, "HOT knowledge"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fail-on-warn", action="store_true", help="return non-zero when any warning is present")
    args = parser.parse_args()

    try:
        checks = collect_checks()
    except ParseFailure as error:
        print(f"ERROR: {error.diagnostic.format()}")
        return 1
    for check in checks:
        print(check.format())
    errors = sum(1 for check in checks if check.level == "ERROR")
    warnings = sum(1 for check in checks if check.level == "WARN")
    print(f"Checked {len(checks)} HOT/runtime file(s); errors={errors}, warnings={warnings}.")
    return 1 if errors or (warnings and args.fail_on_warn) else 0


if __name__ == "__main__":
    sys.exit(main())
