---
type: paradigma-manual
title: Deployment Manual
description: Deployment and operations notes for projects based on Paradigma.
tags: [manual, deploy, operations]
timestamp: 2026-07-04T22:50:00+08:00
paradigma:
  schema_version: "0.1"
  temperature: cold
  lifecycle: evolving
  update_policy: agent-editable
  epistemic_status: confirmed
  retrieval_hints:
    zh:
      - 部署
      - 运维
      - 回滚
    en:
      - deployment
      - operations
      - rollback
  relations:
    related_to:
      - /architecture.md
---

# Purpose

This manual records deployment and operations notes for projects that use Paradigma. Paradigma itself is currently a documentation/template/tooling repository and does not publish a hosted runtime.

# Preconditions

- The repository has an initialized `memory-bank/` structure.
- Tooling commands are run from the repository root.
- Production credentials or secrets are never stored in Memory-Bank files.

# Steps

For the Paradigma repository, deployment means preparing a releasable repository state:

1. Run OKF lint and link checks.
2. Sync indexes after knowledge changes.
3. Update `VERSION`, changelog, ADRs, and progress logs when required.
4. Review generated blocks and untracked files before release.

# Verification

- `python .paradigma/tools/pd-lint-okf.py --strict`
- `python .paradigma/tools/pd-check-links.py`
- `python .paradigma/tools/pd-sync-index.py --check`
- `python .paradigma/tools/pd-check-hot-size.py`

# Rollback

If a release preparation step produces incorrect generated content, restore the affected generated block by rerunning the relevant tool after fixing the source concept document. Do not rewrite historical changelog entries; add a corrective entry in the next release.

# Troubleshooting

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| Strict lint fails | Missing frontmatter field or section | Add the required field/section according to schema |
| Link check fails | Moved document or stale relation | Update the link or relation target |
| Index check fails | Concept changed after index generation | Run `pd-sync-index.py --write` |

# Citations

- `memory-bank/knowledge/contracts/repository-contract.md`
- `memory-bank/knowledge/conventions.md`
