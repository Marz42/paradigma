#!/usr/bin/env python3
"""Create a compact progress summary without deleting raw session logs."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import re
import sys

from _paradigma_yaml import ParseFailure, flatten_mapping, parse_markdown_text, read_utf8_text


ROOT = Path(__file__).resolve().parents[2]
PROGRESS_ROOT = ROOT / "memory-bank" / "logs" / "progress"
SUMMARY_PATH = PROGRESS_ROOT / "summary.md"
EXCLUDED = {"index.md", "summary.md"}


def title_for(path: Path, text: str) -> str:
    if text.splitlines()[:1] == ["---"]:
        metadata = flatten_mapping(parse_markdown_text(text, source=str(path)).metadata)
        title = metadata.get("title")
        if isinstance(title, str) and title.strip():
            return title.strip()
    heading_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()
    return path.stem


def first_nonempty_bullet(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            return stripped[2:].strip()
    return "No bullet summary recorded."


def collect_logs() -> list[tuple[Path, str, str]]:
    logs: list[tuple[Path, str, str]] = []
    if not PROGRESS_ROOT.exists():
        return logs
    for path in sorted(PROGRESS_ROOT.glob("*.md")):
        if path.name in EXCLUDED:
            continue
        text = read_utf8_text(path)
        logs.append((path, title_for(path, text), first_nonempty_bullet(text)))
    return logs


def render_summary(logs: list[tuple[Path, str, str]]) -> str:
    current_time = datetime.now().astimezone()
    lines = [
        "# Progress Summary",
        "",
        f"Generated at: {current_time:%Y-%m-%d %H:%M}",
        "",
        "This file summarizes progress logs without deleting or rewriting the source session logs.",
        "",
        "| Log | Title | First Signal |",
        "|-----|-------|--------------|",
    ]
    for path, title, signal in logs:
        rel = path.relative_to(PROGRESS_ROOT).as_posix()
        escaped_signal = signal.replace("|", "\\|")
        lines.append(f"| [{rel}]({rel}) | {title} | {escaped_signal} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write memory-bank/logs/progress/summary.md")
    args = parser.parse_args()

    try:
        logs = collect_logs()
    except ParseFailure as error:
        print(f"ERROR: {error.diagnostic.format()}")
        return 1
    summary = render_summary(logs)
    if args.write:
        PROGRESS_ROOT.mkdir(parents=True, exist_ok=True)
        SUMMARY_PATH.write_text(summary, encoding="utf-8", newline="\n")
        print(f"Wrote {SUMMARY_PATH.relative_to(ROOT)} with {len(logs)} source log(s).")
    else:
        print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
