#!/usr/bin/env python3
"""Check local Markdown links, frontmatter relations, and index entries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote
import argparse
import re
import sys

from _paradigma_yaml import (
    FlatValue,
    ParseFailure,
    flatten_mapping,
    load_flat_yaml_file,
    parse_markdown_text,
    read_utf8_text,
)


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / ".paradigma" / "config.yaml"
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
BEGIN_MARKER = "<!-- BEGIN PARADIGMA AUTO-INDEX -->"
END_MARKER = "<!-- END PARADIGMA AUTO-INDEX -->"


@dataclass
class LinkIssue:
    level: str
    path: Path
    target: str
    message: str

    def format(self) -> str:
        return f"{self.level}: {self.path.relative_to(ROOT)} -> {self.target}: {self.message}"


def get_list(data: dict[str, FlatValue], key: str) -> list[str]:
    value = data.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)] if value else []


def knowledge_roots() -> list[Path]:
    config = load_flat_yaml_file(CONFIG_PATH, missing_ok=True)
    roots = get_list(config, "knowledge_roots") or ["memory-bank/knowledge", "docs/rfc"]
    return [(ROOT / root).resolve() for root in roots]


def markdown_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(sorted(root.rglob("*.md")))
    return files


def is_external(target: str) -> bool:
    lower = target.lower()
    return lower.startswith(("http://", "https://", "mailto:", "tel:"))


def strip_fragment(target: str) -> str:
    return target.split("#", 1)[0].strip()


def root_for(path: Path, roots: list[Path]) -> Path | None:
    resolved = path.resolve()
    for root in roots:
        try:
            resolved.relative_to(root)
            return root
        except ValueError:
            continue
    return None


def resolve_target(source: Path, target: str, roots: list[Path]) -> Path | None:
    clean = unquote(strip_fragment(target).strip())
    if not clean or is_external(clean):
        return None
    if clean.startswith("/"):
        bundle_root = root_for(source, roots)
        if bundle_root is None:
            return (ROOT / clean.lstrip("/")).resolve()
        return (bundle_root / clean.lstrip("/")).resolve()
    return (source.parent / clean).resolve()


def target_exists(path: Path) -> bool:
    if path.exists():
        return True
    if path.suffix == "" and (path / "index.md").exists():
        return True
    return False


def relation_targets(metadata: dict[str, FlatValue]) -> list[tuple[str, str]]:
    targets: list[tuple[str, str]] = []
    for key, value in metadata.items():
        if not key.startswith("paradigma.relations."):
            continue
        relation_kind = key.rsplit(".", 1)[-1]
        values = value if isinstance(value, list) else [value]
        for item in values:
            if str(item).strip():
                targets.append((relation_kind, str(item).strip()))
    return targets


def strip_code_content(text: str) -> str:
    """Strip fenced code blocks, inline code spans, and indented code blocks.

    Returns text with code regions blanked so that Markdown link patterns
    inside code are not flagged as false-positive links.
    """
    # 1. Fenced code blocks: ``` ... ```
    text = re.sub(r"```[\s\S]*?```", "", text)
    # 2. Inline code spans: `...`
    text = re.sub(r"`[^`\n]+`", "", text)
    # 3. Indented code blocks: lines starting with 4+ spaces or a tab
    #    are blanked to avoid matching links in indented verbatim blocks.
    lines = text.splitlines()
    cleaned: list[str] = []
    for line in lines:
        if line.startswith("    ") or line.startswith("\t"):
            cleaned.append("")
        else:
            cleaned.append(line)
    return "\n".join(cleaned)


def markdown_targets(body: str) -> list[str]:
    targets: list[str] = []
    for match in MARKDOWN_LINK_PATTERN.finditer(body):
        target = match.group(1).strip()
        if " " in target and not target.startswith("<"):
            target = target.split()[0]
        targets.append(target.strip("<>"))
    return targets


def check_file(path: Path, roots: list[Path]) -> list[LinkIssue]:
    try:
        text = read_utf8_text(path)
        if text.splitlines()[:1] == ["---"]:
            parsed = parse_markdown_text(text, source=str(path))
            metadata, body = flatten_mapping(parsed.metadata), parsed.body
        else:
            metadata, body = {}, text
    except ParseFailure as error:
        return [LinkIssue("ERROR", path, "frontmatter", error.diagnostic.format())]
    issues: list[LinkIssue] = []

    targets = [("markdown", target) for target in markdown_targets(strip_code_content(body))]
    targets.extend(relation_targets(metadata))

    for kind, target in targets:
        if is_external(target) or strip_fragment(target) == "":
            continue
        resolved = resolve_target(path, target, roots)
        if resolved is None:
            continue
        if not target_exists(resolved):
            level = "WARN" if kind == "planned" else "ERROR"
            issues.append(LinkIssue(level, path, target, f"missing {kind} target"))

    if path.name == "index.md" and (BEGIN_MARKER in text or END_MARKER in text):
        if text.count(BEGIN_MARKER) != text.count(END_MARKER):
            issues.append(LinkIssue("ERROR", path, "generated block", "unbalanced generated index markers"))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-warnings", action="store_true", help="exit 0 when only warnings are present")
    args = parser.parse_args()

    try:
        roots = knowledge_roots()
    except ParseFailure as error:
        print(f"ERROR: {error.diagnostic.format()}")
        return 1
    files = markdown_files(roots)
    issues: list[LinkIssue] = []
    for path in files:
        issues.extend(check_file(path, roots))

    for issue in issues:
        print(issue.format())

    errors = sum(1 for issue in issues if issue.level == "ERROR")
    warnings = sum(1 for issue in issues if issue.level == "WARN")
    print(f"Checked {len(files)} markdown file(s); errors={errors}, warnings={warnings}.")
    return 1 if errors or (warnings and not args.allow_warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
