---
type: paradigma-decision
title: ADR-001 Split Template Source and Runtime Memory
description: Decision to separate blank templates from Project Paradigma runtime memory.
tags: [adr, memory-bank, templates]
timestamp: 2026-07-04T22:33:00+08:00
paradigma:
  schema_version: "0.1"
  temperature: cold
  lifecycle: append-only
  update_policy: append-only
  epistemic_status: decision
  status: accepted
  retrieval_hints:
    zh:
      - 模板拆分
      - 运行记忆
      - 初始化流程
    en:
      - template split
      - runtime memory
      - bootstrap flow
  relations:
    superseded_by:
      - /decisions/adr-002-okf-compatible-memory-runtime.md
---

# Context

Project Paradigma originally mixed blank `.template.md` files with the repository's own active memory files. This made new-project bootstrap less direct and made it harder to track Paradigma's own development history as repository state.

# Decision

Move blank templates into `memory-bank-template/` while reserving `memory-bank/` for actual project memory. Runtime files are copied from templates during bootstrap instead of being mixed with template sources.

# Consequences

- Derived projects can copy templates into active memory locations with fewer `.gitignore` exceptions.
- Paradigma itself can version its active memory as part of repository history.
- Later OKF migration can split `memory-bank/` into runtime/logs/knowledge without colliding with blank templates.

# Alternatives Considered

- Keep templates and runtime memory together: lowest migration cost, but bootstrap remains noisy.
- Move templates into a generic `templates/memory-bank/` path: clearer spelling, but it did not match the user-requested `memory-bank-template` directory.

# Status

Accepted.

# Related Documents

- `memory-bank/knowledge/decisions/adr-002-okf-compatible-memory-runtime.md`
- `memory-bank/knowledge/architecture.md`
- `INIT_PROMPT.md`
