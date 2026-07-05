---
type: paradigma-glossary
title: Project Glossary
description: Glossary of project-specific terms and abbreviations.
tags: [glossary, terminology]
timestamp: 2026-07-05T11:45:00+08:00
paradigma:
  schema_version: "0.1"
  temperature: cold
  lifecycle: evolving
  update_policy: agent-editable
  epistemic_status: confirmed
  retrieval_hints:
    zh:
      - 术语
      - 缩写
      - OKF
    en:
      - glossary
      - abbreviations
      - OKF
  symbols:
    - OKF
    - Memory-Bank
  relations:
    related_to:
      - /project-brief.md
---

# Terms

| Term | Meaning | Notes |
|------|---------|-------|
| OKF | Open Knowledge Format | Markdown + YAML frontmatter knowledge bundle format. |
| Memory-Bank | External memory system used by Paradigma | Split into runtime, logs, and knowledge in the OKF iteration. |
| Runtime | Ephemeral Agent state (`memory-bank/runtime/`) | Holds active-task; not exported as OKF knowledge. |
| Logs | Operational logs (`memory-bank/logs/`) | Progress sessions, changelog, tool-generated summaries; append-first. |
| Knowledge | Long-lived OKF-compatible concepts (`memory-bank/knowledge/`) | architecture, contracts, decisions, domains, manuals, known issues, glossary. |
| HOT | Files read at every session start | active-task (runtime) + HOT knowledge (project-brief, architecture, conventions, repository-contract). |
| WARM | Files read on-demand by task routing | domains, contracts, manuals, RFC docs. |
| COLD | Files read for audits, archaeology, or disputes | decisions, known issues, glossary. |
| Concept Document | OKF-compatible Markdown file under `knowledge/` or `docs/rfc/` | Must have YAML frontmatter with non-empty `type`. |
| Paradigma Namespace | `paradigma:` block in frontmatter | Holds Paradigma-specific metadata (temperature, lifecycle, update_policy, epistemic_status, retrieval_hints, symbols, relations). |
| Retrieval Hints | `paradigma.retrieval_hints` in frontmatter | zh/en keyword arrays that `pd-sync-index.py` uses to build route tables. |
| Symbols | `paradigma.symbols` in frontmatter | Domain-specific identifiers (class names, endpoints, constants) for index routing. |
| Epistemic Status | `paradigma.epistemic_status` field | One of: confirmed, decision, proposal, assumption, deprecated, unknown. |
| Update Policy | `paradigma.update_policy` field | One of: agent-editable, requires-human-confirmation, append-only, generated, read-only. |
| Generated Block | Section between `<!-- BEGIN PARADIGMA AUTO-INDEX -->` and `<!-- END PARADIGMA AUTO-INDEX -->` | Maintained by `pd-sync-index.py`; agents must not edit by hand. |
| Session Log | Progress log under `logs/progress/` | Records one Agent session: goal, actions, files, decisions, follow-ups. |
| ADR | Architecture Decision Record | Stored under `knowledge/decisions/`; append-only, accepted decisions constrain future work. |
| Active Task | Current task state in `memory-bank/runtime/active-task.md` | Single focus; archived to session log on completion. |

# Abbreviations

| Abbreviation | Meaning |
|--------------|---------|
| RFC | Request for Comments |
| OKF | Open Knowledge Format |
| ADR | Architecture Decision Record |
| SemVer | Semantic Versioning |

# Domain-specific Meanings

| Term | Domain | Meaning |
|------|--------|---------|
| pd-* | Tooling | Paradigma deterministic tool prefix (e.g., `pd-lint-okf.py`). |
| HOT/WARM/COLD | Memory-Bank | Temperature tiers for retrieval frequency, not directory location. |
