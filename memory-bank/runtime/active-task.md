---
type: paradigma-runtime-state
title: Active Task
description: Current active task state for the Agent session.
tags: [runtime, active-task]
timestamp: 2026-07-22T23:49:54+08:00
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

2026-07-22-phase0-version-model

## User Request

执行 Paradigma v0.5.1 Phase 0 Batch 0.1：统一发行版本、配置 Schema、OKF 和文档 Schema 版本语义，修复诊断器版本混淆并加入 CI 门禁。

## Current Status

Completed.

## Checklist

- [x] 定义并记录四类版本字段及旧字段迁移语义
- [x] 实现共享版本读取和 `pd-version.py --verbose/--check`
- [x] 修复 `pd-diagnose.py` 上游版本解析与配置比较
- [x] 将版本一致性检查加入 `pd-check-all.py` / CI
- [x] 补充版本模型回归测试
- [x] 同步协议、契约、手册、ADR 和 changelog
- [x] 运行完整验证并提交 Batch 0.1

## Relevant Knowledge

- /docs/devplan/paradigma_dev_5+.md
- /memory-bank/knowledge/architecture.md
- /memory-bank/knowledge/conventions.md
- /memory-bank/knowledge/contracts/repository-contract.md
- /memory-bank/knowledge/domains/tooling.md
- /memory-bank/knowledge/domains/migration-flows.md

## Blockers

None.

## Notes

根 `VERSION` 是源码发行版本真相源。配置中的安装版本只表示当前 workspace 使用的 Paradigma distribution，必须使用无歧义名称并由版本门禁检查漂移；旧 `paradigma_harness_version` 只作为迁移兼容输入。验证结果：20/20 unittest、全部工具 py_compile、pd-check-all 6/6、pd-diagnose self-check 和 git diff check 全部通过。下一批为 Batch 0.2：统一 YAML/frontmatter parser。
