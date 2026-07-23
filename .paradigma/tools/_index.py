"""Derived index core for Paradigma human navigation and machine routing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import os
import tempfile

from _paradigma_yaml import (
    FlatValue,
    load_flat_yaml_file,
    parse_flat_frontmatter,
    read_utf8_text,
)


ROOT = Path(__file__).resolve().parents[2]
RESERVED_FILENAMES = {"index.md", "log.md"}
BEGIN_MARKER = "<!-- BEGIN PARADIGMA AUTO-INDEX -->"
END_MARKER = "<!-- END PARADIGMA AUTO-INDEX -->"
GENERATED_BY = "<!-- generated_by: pd-index.py -->"


class IndexFailure(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)

    def format(self) -> str:
        return f"[{self.code}] {self}"


@dataclass(frozen=True)
class IndexSettings:
    repository_root: Path
    knowledge_roots: tuple[Path, ...]
    cache_path: Path
    reserved_filenames: frozenset[str]


@dataclass(frozen=True)
class Concept:
    path: Path
    document_type: str
    title: str
    description: str
    hints: tuple[str, ...]
    symbols: tuple[str, ...]
    relations: tuple[str, ...]


@dataclass(frozen=True)
class RebuildResult:
    concept_count: int
    root_navigation_count: int
    local_index_count: int
    updated_markdown_count: int
    cache_path: Path


@dataclass(frozen=True)
class VerificationItem:
    label: str
    path: Path
    current: bool


def get_list(data: dict[str, FlatValue], key: str) -> list[str]:
    value = data.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)] if value else []


def load_settings(repository_root: Path = ROOT) -> IndexSettings:
    root = repository_root.resolve()
    config = load_flat_yaml_file(root / ".paradigma" / "config.yaml", missing_ok=True)
    root_names = get_list(config, "knowledge_roots") or ["memory-bank/knowledge"]
    reserved = set(get_list(config, "reserved_filenames")) or RESERVED_FILENAMES
    cache_value = config.get(
        "machine_index_path", ".paradigma/cache/knowledge-index.json"
    )
    if not isinstance(cache_value, str) or not cache_value.strip():
        raise IndexFailure(
            "PD_INDEX_CONFIG_INVALID",
            "machine_index_path must be a non-empty scalar path",
        )
    cache_path = (root / cache_value).resolve()
    cache_root = (root / ".paradigma" / "cache").resolve()
    try:
        cache_path.relative_to(cache_root)
    except ValueError as error:
        raise IndexFailure(
            "PD_INDEX_CACHE_PATH_INVALID",
            "machine_index_path must stay inside .paradigma/cache/",
        ) from error
    return IndexSettings(
        repository_root=root,
        knowledge_roots=tuple((root / name).resolve() for name in root_names),
        cache_path=cache_path,
        reserved_filenames=frozenset(reserved),
    )


def get_scalar(metadata: dict[str, FlatValue], key: str, default: str = "") -> str:
    value = metadata.get(key, default)
    return "" if isinstance(value, list) else str(value).strip()


def relation_summary(metadata: dict[str, FlatValue]) -> tuple[str, ...]:
    summary: list[str] = []
    for key, value in metadata.items():
        if not key.startswith("paradigma.relations."):
            continue
        relation = key.rsplit(".", 1)[-1]
        values = value if isinstance(value, list) else [value]
        summary.extend(
            f"{relation}:{str(item).strip()}"
            for item in values
            if str(item).strip()
        )
    return tuple(summary)


def collect_concepts(
    scope: Path, reserved_filenames: frozenset[str], *, recursive: bool
) -> list[Concept]:
    if not scope.exists():
        return []
    candidates = scope.rglob("*.md") if recursive else scope.glob("*.md")
    concepts: list[Concept] = []
    for path in sorted(candidates):
        if path.name in reserved_filenames:
            continue
        metadata, _body = parse_flat_frontmatter(path)
        document_type = get_scalar(metadata, "type")
        if not document_type:
            continue
        hints = get_list(metadata, "paradigma.retrieval_hints.zh") + get_list(
            metadata, "paradigma.retrieval_hints.en"
        )
        concepts.append(
            Concept(
                path=path,
                document_type=document_type,
                title=get_scalar(metadata, "title", path.stem) or path.stem,
                description=get_scalar(metadata, "description"),
                hints=tuple(hints),
                symbols=tuple(get_list(metadata, "paradigma.symbols")),
                relations=relation_summary(metadata),
            )
        )
    return concepts


def all_concepts(settings: IndexSettings) -> list[tuple[Path, Concept]]:
    collected: list[tuple[Path, Concept]] = []
    for knowledge_root in settings.knowledge_roots:
        for concept in collect_concepts(
            knowledge_root, settings.reserved_filenames, recursive=True
        ):
            collected.append((knowledge_root, concept))
    return sorted(collected, key=lambda item: repository_path(settings, item[1].path))


def repository_path(settings: IndexSettings, path: Path) -> str:
    try:
        return path.relative_to(settings.repository_root).as_posix()
    except ValueError as error:
        raise IndexFailure(
            "PD_INDEX_PATH_OUTSIDE_REPOSITORY",
            f"index source is outside repository root: {path}",
        ) from error


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def summarize(values: tuple[str, ...], limit: int = 3) -> str:
    if not values:
        return "-"
    clipped = values[:limit]
    suffix = " ..." if len(values) > limit else ""
    return "<br>".join(escape_cell(value) for value in clipped) + suffix


def render_local_inner(concepts: list[Concept], index_path: Path) -> list[str]:
    lines = [
        GENERATED_BY,
        "",
        "| Path | Type | Title | Hints | Symbols | Relations |",
        "|------|------|-------|-------|---------|-----------|",
    ]
    for concept in concepts:
        path_text = concept.path.relative_to(index_path.parent).as_posix()
        lines.append(
            "| "
            f"[{path_text}]({path_text}) | "
            f"`{escape_cell(concept.document_type)}` | "
            f"{escape_cell(concept.title)} | "
            f"{summarize(concept.hints)} | "
            f"{summarize(concept.symbols)} | "
            f"{summarize(concept.relations, limit=4)} |"
        )
    return lines


def checksum(lines: list[str]) -> str:
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]


def render_generated_block(concepts: list[Concept], index_path: Path) -> str:
    inner = render_local_inner(concepts, index_path)
    return "\n".join(
        [BEGIN_MARKER, f"<!-- checksum: {checksum(inner)} -->", *inner, "", END_MARKER]
    )


def _marker_state(text: str, path: Path) -> tuple[bool, bool]:
    has_begin = BEGIN_MARKER in text
    has_end = END_MARKER in text
    if has_begin != has_end or text.count(BEGIN_MARKER) > 1 or text.count(END_MARKER) > 1:
        raise IndexFailure(
            "PD_INDEX_MARKERS_INVALID",
            f"generated block markers are unbalanced or repeated: {path}",
        )
    return has_begin, has_end


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_generated_block(text: str, path: Path) -> str:
    text = normalize_newlines(text)
    has_begin, _has_end = _marker_state(text, path)
    if not has_begin:
        return text
    before = text.split(BEGIN_MARKER, 1)[0].rstrip()
    after = text.split(END_MARKER, 1)[1].lstrip()
    parts = [part for part in (before, after.rstrip()) if part]
    return "\n\n".join(parts).rstrip() + "\n"


def replace_generated_block(text: str, block: str, path: Path) -> str:
    text = normalize_newlines(text)
    has_begin, _has_end = _marker_state(text, path)
    if has_begin:
        before = text.split(BEGIN_MARKER, 1)[0].rstrip()
        after = text.split(END_MARKER, 1)[1].lstrip()
        return f"{before}\n\n{block}\n\n{after}".rstrip() + "\n"
    return text.rstrip() + "\n\n" + block + "\n"


def root_navigation_targets(settings: IndexSettings) -> list[Path]:
    return [root / "index.md" for root in settings.knowledge_roots if root.exists()]


def local_index_targets(settings: IndexSettings) -> list[tuple[Path, Path]]:
    targets: list[tuple[Path, Path]] = []
    for knowledge_root in settings.knowledge_roots:
        if not knowledge_root.exists():
            continue
        for scope in sorted(path for path in knowledge_root.rglob("*") if path.is_dir()):
            index_path = scope / "index.md"
            direct_concepts = collect_concepts(
                scope, settings.reserved_filenames, recursive=False
            )
            existing_generated = (
                index_path.exists() and BEGIN_MARKER in read_utf8_text(index_path)
            )
            if direct_concepts or existing_generated:
                targets.append((scope, index_path))
    return targets


def desired_root_navigation(index_path: Path) -> str:
    if not index_path.exists():
        raise IndexFailure(
            "PD_INDEX_ROOT_NAVIGATION_MISSING",
            f"root navigation must be maintained by humans: {index_path}",
        )
    return strip_generated_block(read_utf8_text(index_path), index_path)


def desired_local_index(
    settings: IndexSettings, scope: Path, index_path: Path
) -> str:
    existing = (
        read_utf8_text(index_path)
        if index_path.exists()
        else f"# {scope.name.title()} Index\n"
    )
    concepts = collect_concepts(scope, settings.reserved_filenames, recursive=False)
    return replace_generated_block(
        existing, render_generated_block(concepts, index_path), index_path
    )


def render_machine_index(settings: IndexSettings) -> str:
    entries = []
    for knowledge_root, concept in all_concepts(settings):
        entries.append(
            {
                "path": repository_path(settings, concept.path),
                "knowledge_root": repository_path(settings, knowledge_root),
                "type": concept.document_type,
                "title": concept.title,
                "description": concept.description,
                "hints": list(concept.hints),
                "symbols": list(concept.symbols),
                "relations": list(concept.relations),
            }
        )
    canonical_entries = json.dumps(
        entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    payload = {
        "schema_version": "1",
        "generated_by": "pd-index.py",
        "source_digest": hashlib.sha256(
            canonical_entries.encode("utf-8")
        ).hexdigest(),
        "entry_count": len(entries),
        "entries": entries,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def atomic_write_text(path: Path, content: str) -> None:
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
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def rebuild_indexes(settings: IndexSettings) -> RebuildResult:
    updated_markdown = 0
    roots = root_navigation_targets(settings)
    for index_path in roots:
        desired = desired_root_navigation(index_path)
        if read_utf8_text(index_path) != desired:
            atomic_write_text(index_path, desired)
            updated_markdown += 1

    locals_ = local_index_targets(settings)
    for scope, index_path in locals_:
        desired = desired_local_index(settings, scope, index_path)
        current = read_utf8_text(index_path) if index_path.exists() else ""
        if current != desired:
            atomic_write_text(index_path, desired)
            updated_markdown += 1

    machine = render_machine_index(settings)
    atomic_write_text(settings.cache_path, machine)
    return RebuildResult(
        concept_count=len(all_concepts(settings)),
        root_navigation_count=len(roots),
        local_index_count=len(locals_),
        updated_markdown_count=updated_markdown,
        cache_path=settings.cache_path,
    )


def verify_indexes(settings: IndexSettings) -> list[VerificationItem]:
    items: list[VerificationItem] = []
    for index_path in root_navigation_targets(settings):
        desired = desired_root_navigation(index_path)
        items.append(
            VerificationItem(
                "root navigation", index_path, read_utf8_text(index_path) == desired
            )
        )
    for scope, index_path in local_index_targets(settings):
        desired = desired_local_index(settings, scope, index_path)
        current = read_utf8_text(index_path) if index_path.exists() else ""
        items.append(VerificationItem("local index", index_path, current == desired))
    desired_cache = render_machine_index(settings)
    current_cache = (
        read_utf8_text(settings.cache_path) if settings.cache_path.exists() else ""
    )
    items.append(
        VerificationItem(
            "machine cache", settings.cache_path, current_cache == desired_cache
        )
    )
    return items


def inventory_lines(settings: IndexSettings) -> list[str]:
    lines: list[str] = []
    for knowledge_root, concept in all_concepts(settings):
        relative = concept.path.relative_to(knowledge_root).as_posix()
        lines.append(
            f"{knowledge_root.name}/{relative}\t{concept.document_type}\t"
            f"{concept.title}\t{summarize(concept.hints)}"
        )
    return lines
