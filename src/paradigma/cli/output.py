"""Text and JSON rendering for command outcomes."""

from __future__ import annotations

import json

from ..application.outcomes import CommandOutcome


def render_json(outcome: CommandOutcome) -> str:
    return json.dumps(outcome.to_dict(), ensure_ascii=False, indent=2)


def render_text(outcome: CommandOutcome) -> str:
    lines = list(outcome.messages)
    if outcome.command == "version":
        lines.extend(f"{key}: {value}" for key, value in outcome.data.items())
    elif outcome.command == "config validate":
        lines.extend(
            (
                f"config_schema_version: {outcome.data['config_schema_version']}",
                "knowledge_roots: " + ", ".join(outcome.data["knowledge_roots"]),
                f"machine_index_path: {outcome.data['machine_index_path']}",
            )
        )
    elif outcome.command == "index verify":
        for item in outcome.data["items"]:
            state = "OK" if item["current"] else "STALE"
            lines.append(f"{state}: {item['label']}: {item['path']}")
        lines.append(f"Verified derived indexes; stale={outcome.data['stale']}.")
    elif outcome.command == "index rebuild":
        action = "would_update" if outcome.dry_run else "updated"
        lines.append(
            f"concepts={outcome.data['concept_count']}; "
            f"{action}={outcome.data[action]}."
        )
        lines.extend(outcome.data["paths"])
    elif outcome.command == "check":
        for step in outcome.data["steps"]:
            lines.append(f"{'OK' if step['ok'] else 'FAILED'}: {step['name']}")
    elif outcome.command == "diagnose":
        lines.extend(
            (
                f"detected_version: {outcome.data['detected_version']}",
                f"upstream_version: {outcome.data['upstream_version']}",
                f"gaps: {outcome.data['summary']['total']}",
            )
        )
    elif outcome.command == "task archive" and not outcome.data.get(
        "already_archived"
    ):
        plan = outcome.data["plan"]
        lines.extend(
            (
                f"task_id: {plan['task_id']}",
                f"status: {plan['status']}",
                f"archive_id: {plan['archive_id']}",
                f"target: {plan['target']}",
            )
        )
    for diagnostic in outcome.diagnostics:
        lines.append(f"ERROR: {diagnostic.format()}")
    return "\n".join(lines)


def render(outcome: CommandOutcome, output_format: str) -> str:
    return render_json(outcome) if output_format == "json" else render_text(outcome)
