"""Human navigation and derived machine index service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json

from ..atomic import atomic_replace_text
from ..config import ParadigmaConfig, require_valid_config
from ..diagnostics import Diagnostic
from ..errors import ParadigmaError
from ..parser import FlatValue, parse_flat_frontmatter, read_utf8_text
from .outcomes import CommandOutcome


BEGIN_MARKER = "<!-- BEGIN PARADIGMA AUTO-INDEX -->"
END_MARKER = "<!-- END PARADIGMA AUTO-INDEX -->"
GENERATED_BY = "<!-- generated_by: pd-index.py -->"


class IndexFailure(ParadigmaError, ValueError):
    pass


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
class IndexChange:
    label: str
    path: Path
    current: bool


def _get_list(data: dict[str, FlatValue], key: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return (str(value),) if value else ()


def _get_scalar(
    data: dict[str, FlatValue], key: str, default: str = ""
) -> str:
    value = data.get(key, default)
    return "" if isinstance(value, list) else str(value).strip()


def _relation_summary(metadata: dict[str, FlatValue]) -> tuple[str, ...]:
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
    scope: Path, reserved_filenames: tuple[str, ...], *, recursive: bool
) -> list[Concept]:
    if not scope.exists():
        return []
    candidates = scope.rglob("*.md") if recursive else scope.glob("*.md")
    concepts: list[Concept] = []
    for path in sorted(candidates):
        if path.name in reserved_filenames:
            continue
        metadata, _body = parse_flat_frontmatter(path)
        document_type = _get_scalar(metadata, "type")
        if not document_type:
            continue
        concepts.append(
            Concept(
                path=path,
                document_type=document_type,
                title=_get_scalar(metadata, "title", path.stem) or path.stem,
                description=_get_scalar(metadata, "description"),
                hints=_get_list(metadata, "paradigma.retrieval_hints.zh")
                + _get_list(metadata, "paradigma.retrieval_hints.en"),
                symbols=_get_list(metadata, "paradigma.symbols"),
                relations=_relation_summary(metadata),
            )
        )
    return concepts


def _repository_path(config: ParadigmaConfig, path: Path) -> str:
    try:
        return path.relative_to(config.repository_root).as_posix()
    except ValueError as error:
        raise IndexFailure(
            f"index source is outside repository root: {path}",
            code="PD_INDEX_PATH_OUTSIDE_REPOSITORY",
        ) from error


def all_concepts(config: ParadigmaConfig) -> list[tuple[Path, Concept]]:
    collected: list[tuple[Path, Concept]] = []
    for knowledge_root in config.knowledge_roots:
        for concept in collect_concepts(
            knowledge_root, config.reserved_filenames, recursive=True
        ):
            collected.append((knowledge_root, concept))
    return sorted(
        collected, key=lambda item: _repository_path(config, item[1].path)
    )


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _summarize(values: tuple[str, ...], limit: int = 3) -> str:
    if not values:
        return "-"
    suffix = " ..." if len(values) > limit else ""
    return "<br>".join(_escape_cell(value) for value in values[:limit]) + suffix


def _checksum(lines: list[str]) -> str:
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]


def _render_generated_block(concepts: list[Concept], index_path: Path) -> str:
    inner = [
        GENERATED_BY,
        "",
        "| Path | Type | Title | Hints | Symbols | Relations |",
        "|------|------|-------|-------|---------|-----------|",
    ]
    for concept in concepts:
        relative = concept.path.relative_to(index_path.parent).as_posix()
        inner.append(
            "| "
            f"[{relative}]({relative}) | "
            f"`{_escape_cell(concept.document_type)}` | "
            f"{_escape_cell(concept.title)} | "
            f"{_summarize(concept.hints)} | "
            f"{_summarize(concept.symbols)} | "
            f"{_summarize(concept.relations, limit=4)} |"
        )
    return "\n".join(
        [BEGIN_MARKER, f"<!-- checksum: {_checksum(inner)} -->", *inner, "", END_MARKER]
    )


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _marker_state(text: str, path: Path) -> bool:
    has_begin = BEGIN_MARKER in text
    has_end = END_MARKER in text
    if has_begin != has_end or text.count(BEGIN_MARKER) > 1 or text.count(END_MARKER) > 1:
        raise IndexFailure(
            f"generated block markers are unbalanced or repeated: {path}",
            code="PD_INDEX_MARKERS_INVALID",
        )
    return has_begin


def _strip_generated_block(text: str, path: Path) -> str:
    text = _normalize_newlines(text)
    if not _marker_state(text, path):
        return text
    before = text.split(BEGIN_MARKER, 1)[0].rstrip()
    after = text.split(END_MARKER, 1)[1].lstrip()
    parts = [part for part in (before, after.rstrip()) if part]
    return "\n\n".join(parts).rstrip() + "\n"


def _replace_generated_block(text: str, block: str, path: Path) -> str:
    text = _normalize_newlines(text)
    if _marker_state(text, path):
        before = text.split(BEGIN_MARKER, 1)[0].rstrip()
        after = text.split(END_MARKER, 1)[1].lstrip()
        return f"{before}\n\n{block}\n\n{after}".rstrip() + "\n"
    return text.rstrip() + "\n\n" + block + "\n"


def _local_targets(config: ParadigmaConfig) -> list[tuple[Path, Path]]:
    targets: list[tuple[Path, Path]] = []
    for knowledge_root in config.knowledge_roots:
        if not knowledge_root.exists():
            continue
        for scope in sorted(path for path in knowledge_root.rglob("*") if path.is_dir()):
            index_path = scope / "index.md"
            concepts = collect_concepts(
                scope, config.reserved_filenames, recursive=False
            )
            generated = (
                index_path.exists() and BEGIN_MARKER in read_utf8_text(index_path)
            )
            if concepts or generated:
                targets.append((scope, index_path))
    return targets


def _desired_root(index_path: Path) -> str:
    if not index_path.exists():
        raise IndexFailure(
            f"root navigation must be maintained by humans: {index_path}",
            code="PD_INDEX_ROOT_NAVIGATION_MISSING",
        )
    return _strip_generated_block(read_utf8_text(index_path), index_path)


def _desired_local(
    config: ParadigmaConfig, scope: Path, index_path: Path
) -> str:
    existing = (
        read_utf8_text(index_path)
        if index_path.exists()
        else f"# {scope.name.title()} Index\n"
    )
    concepts = collect_concepts(
        scope, config.reserved_filenames, recursive=False
    )
    return _replace_generated_block(
        existing, _render_generated_block(concepts, index_path), index_path
    )


def render_machine_index(config: ParadigmaConfig) -> str:
    entries = []
    for knowledge_root, concept in all_concepts(config):
        entries.append(
            {
                "path": _repository_path(config, concept.path),
                "knowledge_root": _repository_path(config, knowledge_root),
                "type": concept.document_type,
                "title": concept.title,
                "description": concept.description,
                "hints": list(concept.hints),
                "symbols": list(concept.symbols),
                "relations": list(concept.relations),
            }
        )
    canonical = json.dumps(
        entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    payload = {
        "schema_version": "1",
        "generated_by": "pd-index.py",
        "source_digest": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "entry_count": len(entries),
        "entries": entries,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def inspect_indexes(config: ParadigmaConfig) -> tuple[IndexChange, ...]:
    changes: list[IndexChange] = []
    for knowledge_root in config.knowledge_roots:
        if not knowledge_root.exists():
            continue
        index_path = knowledge_root / "index.md"
        desired = _desired_root(index_path)
        changes.append(
            IndexChange(
                "root navigation",
                index_path,
                read_utf8_text(index_path) == desired,
            )
        )
    for scope, index_path in _local_targets(config):
        current = read_utf8_text(index_path) if index_path.exists() else ""
        changes.append(
            IndexChange(
                "local index",
                index_path,
                current == _desired_local(config, scope, index_path),
            )
        )
    current_cache = (
        read_utf8_text(config.machine_index_path)
        if config.machine_index_path.exists()
        else ""
    )
    changes.append(
        IndexChange(
            "machine cache",
            config.machine_index_path,
            current_cache == render_machine_index(config),
        )
    )
    return tuple(changes)


def index_verify_outcome(
    repository_root: Path, *, dry_run: bool = False
) -> CommandOutcome:
    config = require_valid_config(repository_root)
    items = inspect_indexes(config)
    diagnostics = tuple(
        Diagnostic(
            "PD_INDEX_STALE",
            f"{item.label} is stale",
            _repository_path(config, item.path),
        )
        for item in items
        if not item.current
    )
    return CommandOutcome(
        command="index verify",
        data={
            "stale": len(diagnostics),
            "items": [
                {
                    "label": item.label,
                    "path": _repository_path(config, item.path),
                    "current": item.current,
                }
                for item in items
            ],
        },
        diagnostics=diagnostics,
        dry_run=dry_run,
    )


def index_rebuild_outcome(
    repository_root: Path, *, dry_run: bool = False
) -> CommandOutcome:
    config = require_valid_config(repository_root)
    before = inspect_indexes(config)
    updates = [item for item in before if not item.current]
    if not dry_run:
        for knowledge_root in config.knowledge_roots:
            if knowledge_root.exists():
                path = knowledge_root / "index.md"
                desired = _desired_root(path)
                if read_utf8_text(path) != desired:
                    atomic_replace_text(path, desired)
        for scope, index_path in _local_targets(config):
            desired = _desired_local(config, scope, index_path)
            current = read_utf8_text(index_path) if index_path.exists() else ""
            if current != desired:
                atomic_replace_text(index_path, desired)
        atomic_replace_text(config.machine_index_path, render_machine_index(config))
    concepts = all_concepts(config)
    return CommandOutcome(
        command="index rebuild",
        data={
            "concept_count": len(concepts),
            "would_update": len(updates),
            "updated": 0 if dry_run else len(updates),
            "paths": [_repository_path(config, item.path) for item in updates],
        },
        messages=(
            "Index rebuild plan generated."
            if dry_run
            else "Derived indexes rebuilt."
        ,),
        changed=bool(updates) and not dry_run,
        dry_run=dry_run,
    )

