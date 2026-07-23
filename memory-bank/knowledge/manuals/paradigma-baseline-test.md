---
type: paradigma-manual
title: Paradigma Baseline Validation
description: Baseline validation sequence for Paradigma knowledge quality, deterministic tooling, and release readiness.
tags: [manual, testing, quality, paradigma]
timestamp: 2026-07-23T21:35:00+08:00
paradigma:
  schema_version: "0.1"
  temperature: warm
  lifecycle: evolving
  update_policy: agent-editable
  epistemic_status: confirmed
  retrieval_hints:
    zh:
      - Paradigma 基线校验
      - 校验命令
      - 质量门禁
    en:
      - paradigma baseline
      - validation commands
      - quality gate
  relations:
    related_to:
      - /conventions.md
      - /contracts/repository-contract.md
---

# Purpose

This guide defines the local validation sequence for Paradigma changes. It is **not** a general-purpose testing guide for derived projects — it documents the baseline quality gates that the Paradigma repository itself must pass. Derived projects should write their own testing guide under `manuals/`.

# Preconditions

- Run commands from the repository root.
- Use Python 3.11+ and install `requirements.txt` with `python -m pip install -r requirements.txt`.
- Set `PYTHONDONTWRITEBYTECODE=1` when running validation if you want to avoid local `__pycache__` files.

# Steps

1. Run the standard-library unittest suite before and after tool refactors.
2. Run version consistency checks after release, config, OKF, or document schema changes.
3. Run strict OKF lint after concept or schema edits.
4. Run link checks after Markdown links, relations, or index entries change.
5. Run `pd-index.py rebuild` after concept metadata changes, then run `pd-index.py verify`.
6. Run hot-size checks before ending substantial sessions.
7. Compile Python tools when their implementation changes.
8. Run archive tests after changing task state, templates, mutation planning, atomic writes, or retry behavior.

# Verification

Recommended command sequence:

```powershell
python -m pip install -r requirements.txt
python .paradigma/tools/pd-index.py rebuild
python -m unittest discover -s tests -p "test_*.py" -v
python .paradigma/tools/pd-check-all.py
```

Individual tools can also be run separately:

# Rollback

Validation tools should not delete source content. If a local or machine index is wrong, fix canonical frontmatter/relations and rerun `pd-index.py rebuild`; deleting `.paradigma/cache/` is always safe.

# Troubleshooting

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| Version check fails | Distribution, installed, config, OKF, or document schema metadata drifted | Run `pd-version.py --verbose --check` and update only the field whose semantic version changed |
| `unknown type` | Schema registry missing the concept type | Add the type to `.paradigma/schemas/paradigma-types.schema.yaml` |
| Timestamp error | Non-ISO frontmatter timestamp | Use `YYYY-MM-DDTHH:mm:ss+08:00` |
| `YAML_SYNTAX_ERROR` / `YAML_DUPLICATE_KEY` | Invalid YAML or an ambiguous repeated key | Fix the reported source line; do not suppress the parser diagnostic |
| `ENCODING_ERROR` | File is not valid UTF-8 | Re-save as UTF-8 (UTF-8 BOM is accepted) |
| `PD_ARCHIVE_INVALID_STATUS` | `Current Status` is prose, punctuated, empty, or unknown | Use exactly one of `pending`, `active`, `blocked`, `completed`, `aborted` |
| `PD_ARCHIVE_SOURCE_CHANGED` | active-task changed after dry-run plan generation | Generate and review a fresh plan; do not force the stale plan |
| Archive exists but active-task was not reset | Process stopped between the two atomic writes | Re-run `pd-archive-task.py --write`; it reuses the same `archive_id` |
| Machine cache missing or stale | Cache was deleted/corrupted or source metadata changed | Run `pd-index.py rebuild`, then `pd-index.py verify` |
| Root index starts growing with every concept | Recursive generated block was reintroduced | Remove it with rebuild and keep only high-level human navigation |
| Link check reports a planned relation | The target is intentionally future work | Keep it under `paradigma.relations.planned` |

# Citations

- `.paradigma/tools/pd-version.py`
- `.paradigma/tools/pd-lint-okf.py`
- `.paradigma/tools/pd-check-links.py`
- `.paradigma/tools/pd-index.py`
- `.paradigma/tools/pd-sync-index.py` (compatibility wrapper)
