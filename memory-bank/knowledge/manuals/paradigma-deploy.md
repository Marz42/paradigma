---
type: paradigma-manual
title: Paradigma Release Preparation
description: Pre-release validation and deployment notes specific to the Paradigma repository itself.
tags: [manual, deploy, operations, paradigma]
timestamp: 2026-07-23T22:08:27+08:00
paradigma:
  schema_version: "0.1"
  temperature: cold
  lifecycle: evolving
  update_policy: agent-editable
  epistemic_status: confirmed
  retrieval_hints:
    zh:
      - Paradigma 发布
      - 部署前校验
      - 运维
      - 回滚
    en:
      - paradigma release
      - pre-release validation
      - operations
      - rollback
  relations:
    related_to:
      - /architecture.md
---

# Purpose

This manual records Paradigma-specific release preparation steps. It is **not** a general-purpose deploy guide for derived projects — it documents how the Paradigma repository itself reaches a releasable state. Derived projects should write their own deploy manual under `manuals/`.

# Preconditions

- The repository has an initialized `memory-bank/` structure.
- Tooling commands are run from the repository root.
- Production credentials or secrets are never stored in Memory-Bank files.

# Steps

1. Confirm the release scope is complete and the previous batch commits are present.
2. Update root `VERSION`, config `installed_distribution_version`, README current version, repository test expectations, and the changelog release heading in one change.
3. Keep config, OKF, and document schema versions unchanged unless their formats changed independently.
4. Document and test the previous-release upgrade path, including dependency and private helper copies.
5. Rebuild derived indexes after knowledge changes, then run characterization tests, compilation, aggregate checks, self-diagnosis, and `git diff --check`.
6. Commit the release preparation with a clean worktree. Do not create a tag or push until the release candidate has been reviewed.

For v0.5.1, the release dimensions are:

| Dimension | Value |
|-----------|-------|
| Distribution | `0.5.1` |
| Installed distribution | `0.5.1` |
| Config schema | `0.3` |
| OKF compatibility | `0.1` |
| Document schema | `0.2` |

# Verification

```powershell
python .paradigma/tools/pd-index.py rebuild
python -m unittest discover -s tests -p "test_*.py" -v
python .paradigma/tools/pd-version.py --verbose --check
python .paradigma/tools/pd-check-all.py --keep-going
python .paradigma/tools/pd-diagnose.py --project . --upstream . --json
git diff --check
git status --short --branch
```

After human approval, the release action is an annotated `v0.5.1` tag followed by pushing the commit and tag. Those external actions are not part of release preparation.

# Rollback

If a release preparation step produces incorrect generated content, restore the affected generated block by rerunning the relevant tool after fixing the source concept document. Do not rewrite historical changelog entries; add a corrective entry in the next release.

# Troubleshooting

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| Strict lint fails | Missing frontmatter field or section | Add the required field/section according to schema |
| Link check fails | Moved document or stale relation | Update the link or relation target |
| Index check fails | Concept changed after index generation | Run `pd-index.py rebuild`, then `pd-index.py verify` |
| Derived 0.5.0 project cannot import version/diagnose tools | PyYAML or `_paradigma_yaml.py` was not copied | Install `requirements.txt` and copy the full `.paradigma/tools/` set |

# Citations

- `memory-bank/knowledge/contracts/repository-contract.md`
- `memory-bank/knowledge/conventions.md`
