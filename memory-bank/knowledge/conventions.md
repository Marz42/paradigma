---
type: paradigma-convention
title: Coding and Collaboration Conventions
description: Coding, naming, testing, documentation, versioning, and prohibited patterns for Project Paradigma.
tags: [conventions, semver, collaboration, tooling]
timestamp: 2026-07-04T22:50:00+08:00
paradigma:
  schema_version: "0.1"
  temperature: hot
  lifecycle: stable
  update_policy: requires-human-confirmation
  epistemic_status: confirmed
  retrieval_hints:
    zh:
      - 代码规范
      - 版本规则
      - 文档约定
      - 工具校验
    en:
      - coding conventions
      - versioning
      - documentation
      - tooling
  symbols:
    - SemVer
    - VERSION
    - Update Phase
  relations:
    constrains:
      - /contracts/repository-contract.md
      - /manuals/testing-guide.md
---

# Naming

| Target | Rule | Example |
|--------|------|---------|
| Files and directories | kebab-case, except established tool names | `pd-lint-okf.py`, `memory-bank` |
| Python functions/variables | snake_case | `parse_frontmatter` |
| Python classes | PascalCase | `LintIssue` |
| Constants | UPPER_SNAKE_CASE | `RESERVED_FILENAMES` |
| Markdown concept type | stable kebab-like string | `paradigma-contract` |

Avoid pinyin, ambiguous abbreviations, and generic names such as `data`, `info`, or `temp` unless scoped to a tiny local context.

# Code Style

- Prefer standard-library Python for Paradigma MVP tools.
- Keep tools single-purpose: lint, link check, index sync, hot-size check, archive, compact.
- Keep parsing conservative and deterministic. Do not rely on LLM interpretation for generated indexes or validation results.
- Avoid premature abstractions until duplicated logic proves stable across at least three tools.
- Use comments only when they explain why a rule exists or why a parser is intentionally limited.

# Error Handling

- Tool failures should use non-zero exit codes when they produce ERROR-level findings.
- WARNING-level findings should be visible but should not fail `warn` mode.
- CLI output should include repository-relative paths.
- Generated files should be updated only when the user passes an explicit write flag or archive/compact command.

# Testing Conventions

- Run `python .paradigma/tools/pd-lint-okf.py --strict` after knowledge/RFC edits.
- Run `python .paradigma/tools/pd-check-links.py` after link, relation, or index edits.
- Run `python .paradigma/tools/pd-sync-index.py --write` after adding/removing concept documents.
- Run `python .paradigma/tools/pd-check-hot-size.py` before ending substantial sessions.
- Compile Python tools with `python -m py_compile` when tool code changes, then remove or ignore `__pycache__` outputs.

# Documentation Conventions

- `AGENT_RULES.md` is the source of truth for Agent protocol.
- `.cursor/rules/memory-bank-protocol.mdc` is a synchronized Cursor adapter.
- `README.md` explains user-facing setup and maintenance workflows.
- `INIT_PROMPT.md` contains copyable conversation starters.
- `docs/rfc/*.md` stores proposal documents and must remain OKF-compatible.
- Long-lived knowledge belongs in `memory-bank/knowledge/`; runtime state belongs in `memory-bank/runtime/`; process logs belong in `memory-bank/logs/`.

## Versioning

Project Paradigma follows SemVer using the root `VERSION` file as the source of truth.

| Change type | Version action |
|-------------|----------------|
| Typo or wording only | May skip version bump |
| Template path, protocol, or tooling behavior change | PATCH or MINOR depending on scope |
| New workflow/tooling capability | MINOR |
| Breaking protocol/path change for derived projects | MAJOR proposal, requires user confirmation |

When bumping versions, update:

1. `VERSION`
2. `memory-bank/logs/changelog.md`
3. A progress session in `memory-bank/logs/progress/`
4. ADR when the change is architectural

# Prohibited Patterns

- Do not write long-lived facts into `memory-bank/runtime/active-task.md`.
- Do not manually edit generated index blocks.
- Do not add new concept documents without OKF frontmatter.
- Do not change contracts, architecture, or accepted ADRs without checking update policy.
- Do not keep legacy flat Memory-Bank paths in active protocol docs.
- Do not introduce external dependencies into tooling without explicit justification.
