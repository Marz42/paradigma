---
type: paradigma-runtime-state
title: Active Task
description: Current active task state for the Agent session.
tags: [runtime, active-task]
timestamp: 2026-07-05T12:19:00+08:00
paradigma:
  layer: runtime
  temperature: hot
  lifecycle: ephemeral
  okf_export: false
  update_policy: agent-editable
  archive_to: /memory-bank/logs/progress/
---

# Active Task

## Task ID

2026-07-05-tooling-fix-and-ci

## User Request

1. P2-1: 修复 pd-check-links.py 排除 fenced/inline/indented code blocks 中的假阳性链接。
2. P2-2: 创建 pd-check-all.py 聚合校验脚本 + GitHub Actions workflow。
3. P3: glossary 按需增补（本次跳过）。

## Current Status

Completed.

## Checklist

- [x] pd-check-links.py: 新增 strip_code_content() — 排除 fenced (```)、inline (`)、indented (4+ spaces/tab) code
- [x] 恢复 known-issues/fstring-escape-in-compact.md 的 Workaround 代码块为真实 Python 代码
- [x] 验证 code-stripping：`[{rel}]({rel})` 在 fence block 内不再触发假阳性
- [x] 创建 pd-check-all.py 聚合工具（顺序运行 4 个校验，支持 --keep-going）
- [x] 创建 .github/workflows/check.yml（push main + PR 触发）
- [x] 更新 AGENT_RULES.md、Cursor rule、conventions.md、paradigma-baseline-test.md、repository-contract.md、domains/tooling.md
- [x] 运行 pd-check-all.py 全部 4 checks passed
- [x] 版本 0.4.1 → 0.4.2 (PATCH: bugfix + new aggregation tool)

## Relevant Knowledge

- /memory-bank/knowledge/architecture.md
- /memory-bank/knowledge/contracts/repository-contract.md
- /memory-bank/knowledge/domains/tooling.md
- /memory-bank/knowledge/manuals/paradigma-baseline-test.md

## Blockers

None.

## Notes

版本升至 0.4.2：link check code-block 假阳性修复属 bugfix (PATCH)，pd-check-all.py 是新增工具 (可按 PATCH 对待，无破坏性变更)。
GitHub Actions workflow 使用 ubuntu-latest + Python 3.11，与项目要求一致。
代码块剥离策略：fence block 整块移除、inline code 正则替换、indented code 行级清空 — 对列表嵌套缩进有极小误伤风险但 Paradigma knowledge 不会遇到此场景。
