# Paradigma Knowledge Index

Agent 路由指南：先读取 runtime active task，再读取本 index，根据任务选择最相关的 1-3 个文档继续阅读。One-shot retrieval 是第一跳，不是终点。

## HOT Knowledge

* [Project Brief](project-brief.md) - Project vision, target users, and scope.
* [System Architecture](architecture.md) - Repository structure and protocol boundaries.
* [Conventions](conventions.md) - Coding, versioning, and collaboration conventions.
* [Repository Contract](contracts/repository-contract.md) - Repository-level contract boundaries.

## WARM Knowledge

* [Contracts](contracts/) - API, repository, and tooling contracts.
* [Domains](domains/) - Module-level design documents.
* [Manuals](manuals/) - Operational guides.

## COLD Knowledge

* [Decisions](decisions/) - Architecture decision records.
* [Known Issues](known-issues/) - Debugging notes and recurring issues.

<!-- BEGIN PARADIGMA AUTO-INDEX -->
<!-- checksum: dd733e190f99daf4 -->
<!-- generated_by: pd-sync-index.py -->

| Path | Type | Title | Hints | Symbols | Relations |
|------|------|-------|-------|---------|-----------|
| [architecture.md](architecture.md) | `paradigma-architecture` | System Architecture | 总体架构<br>三态记忆结构<br>工具链边界 ... | AGENT_RULES.md<br>memory-bank/runtime<br>memory-bank/knowledge | related_to:/contracts/repository-contract.md<br>related_to:/decisions/adr-002-okf-compatible-memory-runtime.md |
| [contracts/repository-contract.md](contracts/repository-contract.md) | `paradigma-contract` | Repository Contract | 仓库契约<br>工具命令<br>兼容策略 ... | pd-lint-okf.py<br>pd-sync-index.py<br>VERSION | depends_on:/architecture.md |
| [conventions.md](conventions.md) | `paradigma-convention` | Coding and Collaboration Conventions | 代码规范<br>版本规则<br>文档约定 ... | SemVer<br>VERSION<br>Update Phase | constrains:/contracts/repository-contract.md<br>constrains:/manuals/testing-guide.md |
| [decisions/adr-001-template-runtime-split.md](decisions/adr-001-template-runtime-split.md) | `paradigma-decision` | ADR-001 Split Template Source and Runtime Memory | 模板拆分<br>运行记忆<br>初始化流程 ... | - | superseded_by:/decisions/adr-002-okf-compatible-memory-runtime.md |
| [decisions/adr-002-okf-compatible-memory-runtime.md](decisions/adr-002-okf-compatible-memory-runtime.md) | `paradigma-decision` | ADR-002 Adopt OKF-Compatible Memory Runtime Structure | OKF 迁移<br>runtime logs knowledge<br>三态结构 ... | - | constrains:/architecture.md<br>constrains:/contracts/repository-contract.md |
| [decisions/adr-003-strict-okf-production-rules.md](decisions/adr-003-strict-okf-production-rules.md) | `paradigma-decision` | ADR-003 Adopt Strict OKF Production Rules | strict lint<br>link check<br>index checksum ... | - | constrains:/architecture.md<br>constrains:/contracts/repository-contract.md<br>follows:/decisions/adr-002-okf-compatible-memory-runtime.md |
| [glossary.md](glossary.md) | `paradigma-glossary` | Project Glossary | 术语<br>缩写<br>OKF ... | OKF<br>Memory-Bank | related_to:/project-brief.md |
| [manuals/deploy.md](manuals/deploy.md) | `paradigma-manual` | Deployment Manual | 部署<br>运维<br>回滚 ... | - | related_to:/architecture.md |
| [manuals/testing-guide.md](manuals/testing-guide.md) | `paradigma-manual` | Testing Guide | 测试<br>校验命令<br>质量门禁 ... | - | related_to:/conventions.md<br>related_to:/contracts/repository-contract.md |
| [project-brief.md](project-brief.md) | `paradigma-project-brief` | Project Brief | 项目愿景<br>适用范围<br>Agent 外部记忆 ... | Project Paradigma<br>Memory-Bank<br>OKF | informs:/architecture.md<br>informs:/contracts/repository-contract.md |

<!-- END PARADIGMA AUTO-INDEX -->
