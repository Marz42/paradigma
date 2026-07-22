---
type: paradigma-contract
title: Repository Contract
description: Current repository-level contract boundaries for APIs, databases, tools, and versioning.
tags: [contract, repository, tooling]
timestamp: 2026-07-23T00:04:40+08:00
paradigma:
  schema_version: "0.1"
  temperature: hot
  lifecycle: evolving
  update_policy: requires-human-confirmation
  epistemic_status: confirmed
  contract_kind: repository
  retrieval_hints:
    zh:
      - 仓库契约
      - 工具命令
      - 兼容策略
    en:
      - repository contract
      - tool commands
      - compatibility policy
  symbols:
    - pd-version.py
    - pd-lint-okf.py
    - pd-sync-index.py
    - VERSION
  relations:
    depends_on:
      - /architecture.md
---

# Scope

This contract defines the externally meaningful repository boundaries for Project Paradigma. The project is currently a documentation/template/tooling repository, not an application runtime.

# Contract

## Repository Layout

| Area | Contract |
|------|----------|
| `memory-bank/runtime/` | Ephemeral Agent state; not exported as OKF knowledge |
| `memory-bank/logs/` | Operational logs and changelog; append-first history |
| `memory-bank/knowledge/` | OKF-compatible long-lived knowledge bundle |
| `docs/rfc/` | OKF-compatible proposal/RFC documents |
| `memory-bank-template/` | Blank templates for derived projects |
| `.paradigma/tools/` | Deterministic local tooling |
| `.paradigma/tools/_paradigma_yaml.py` | Sole YAML/frontmatter parser for tool consumers |
| `tests/characterization/` | Executable baseline for current tool CLI and mutation behavior |

## Tool Commands

| Command | Status | Contract |
|---------|--------|----------|
| `python -m unittest discover -s tests -p "test_*.py" -v` | Stable | Runs the pre-refactor characterization suite using Python standard-library unittest |
| `python .paradigma/tools/pd-version.py --verbose` | Stable | Reports distribution, installed distribution, config schema, OKF, and document schema versions |
| `python .paradigma/tools/pd-version.py --check` | Stable | Fails when required version fields are missing, legacy fields remain, or the installed distribution drifts from root `VERSION` |
| `python .paradigma/tools/pd-check-all.py` | Stable | Aggregates version, lint, link, index, hot-size, and DESIGN.md validation into a single quality gate |
| `python .paradigma/tools/pd-lint-okf.py --strict` | Stable | Checks concept documents against schema, sections, timestamps, policies, and generated blocks |
| `python .paradigma/tools/pd-check-links.py` | Stable | Checks Markdown links, frontmatter relations, and generated index entries |
| `python .paradigma/tools/pd-sync-index.py --write` | Stable | Scans concepts and updates root and subdirectory generated index blocks |
| `python .paradigma/tools/pd-check-hot-size.py` | Stable | Reports active-task, HOT knowledge, and progress index size status |
| `python .paradigma/tools/pd-archive-task.py --write` | Stable | Archives completed active task into session logs and resets active task |
| `python .paradigma/tools/pd-compact-progress.py --write` | Stable | Writes a compact progress summary without deleting source logs |
| `python .paradigma/tools/pd-diagnose.py --upstream <path>` | Experimental | Compares project harness against upstream Paradigma; reports gaps across structure, tools, schema, config, and protocol |

# Request Schema

No HTTP, SDK, or CLI request schema is currently published. Tool command arguments are intentionally minimal and documented in each script help text.

# Response Schema

Tooling uses process exit codes:

| Exit code | Meaning |
|-----------|---------|
| `0` | Success |
| `1` | Validation failed |
| `2` | Diagnose input/path/parser failure where supported by `pd-diagnose.py` |

Parser failures include a stable code, source, message, and optional line/column. YAML syntax and encoding failures must not be reported as document Schema failures. Supported parser codes are `ENCODING_ERROR`, `FILE_READ_ERROR`, `FRONTMATTER_MISSING`, `FRONTMATTER_UNCLOSED`, `YAML_SYNTAX_ERROR`, `YAML_DUPLICATE_KEY`, and `YAML_ROOT_TYPE_ERROR`.

# State Transitions

```text
User request -> runtime active task -> knowledge routing -> edits -> lint -> logs/knowledge update
```

# Compatibility Notes

- Adding new optional frontmatter fields is backward compatible.
- Tooling requires Python 3.11+ and dependencies declared in root `requirements.txt`.
- Adding new Paradigma concept types is backward compatible if existing types remain valid.
- Moving core paths such as `memory-bank/knowledge/` or changing required tooling commands is a compatibility-impacting protocol change and requires version evaluation.

# Breaking Change Policy

Breaking repository protocol changes require explicit user confirmation and SemVer evaluation under `memory-bank/knowledge/conventions.md`.

# Citations

- [OKF v0.1 Draft](https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md)
