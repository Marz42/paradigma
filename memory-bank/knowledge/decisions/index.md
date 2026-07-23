# Decisions Index

* [ADR-001 Split Template Source and Runtime Memory](adr-001-template-runtime-split.md) - Separates blank templates from runtime memory.
* [ADR-002 Adopt OKF-Compatible Memory Runtime Structure](adr-002-okf-compatible-memory-runtime.md) - Adopts runtime/logs/knowledge and OKF-compatible knowledge.

<!-- BEGIN PARADIGMA AUTO-INDEX -->
<!-- checksum: 97f7c0976dbee3de -->
<!-- generated_by: pd-index.py -->

| Path | Type | Title | Hints | Symbols | Relations |
|------|------|-------|-------|---------|-----------|
| [adr-001-template-runtime-split.md](adr-001-template-runtime-split.md) | `paradigma-decision` | ADR-001 Split Template Source and Runtime Memory | 模板拆分<br>运行记忆<br>初始化流程 ... | - | superseded_by:/decisions/adr-002-okf-compatible-memory-runtime.md |
| [adr-002-okf-compatible-memory-runtime.md](adr-002-okf-compatible-memory-runtime.md) | `paradigma-decision` | ADR-002 Adopt OKF-Compatible Memory Runtime Structure | OKF 迁移<br>runtime logs knowledge<br>三态结构 ... | - | constrains:/architecture.md<br>constrains:/contracts/repository-contract.md |
| [adr-003-strict-okf-production-rules.md](adr-003-strict-okf-production-rules.md) | `paradigma-decision` | ADR-003 Adopt Strict OKF Production Rules | strict lint<br>link check<br>index checksum ... | - | constrains:/architecture.md<br>constrains:/contracts/repository-contract.md<br>follows:/decisions/adr-002-okf-compatible-memory-runtime.md |
| [adr-004-separate-version-dimensions.md](adr-004-separate-version-dimensions.md) | `paradigma-decision` | ADR-004 Separate Distribution and Schema Version Dimensions | 版本模型<br>配置版本<br>发行版本 ... | VERSION<br>installed_distribution_version<br>config_schema_version ... | constrains:/architecture.md<br>constrains:/contracts/repository-contract.md<br>constrains:/domains/tooling.md<br>follows:/decisions/adr-003-strict-okf-production-rules.md |
| [adr-005-unified-safe-yaml-parser.md](adr-005-unified-safe-yaml-parser.md) | `paradigma-decision` | ADR-005 Adopt a Unified Safe YAML Parser | 统一 YAML Parser<br>frontmatter 诊断<br>重复键 ... | _paradigma_yaml.py<br>ParseDiagnostic<br>ParseFailure ... | constrains:/architecture.md<br>constrains:/contracts/repository-contract.md<br>constrains:/domains/tooling.md<br>follows:/decisions/adr-004-separate-version-dimensions.md |
| [adr-006-transactional-task-archive.md](adr-006-transactional-task-archive.md) | `paradigma-decision` | ADR-006 Make Task Status Strict and Archive Recovery Idempotent | 严格任务状态<br>安全归档<br>原子写入 ... | TaskStatus<br>_task_state.py<br>ArchivePlan ... | constrains:/architecture.md<br>constrains:/conventions.md<br>constrains:/contracts/repository-contract.md<br>constrains:/domains/tooling.md ... |
| [adr-007-separate-index-boundaries.md](adr-007-separate-index-boundaries.md) | `paradigma-decision` | ADR-007 Separate Human Navigation from Derived Machine Indexes | 索引边界<br>根导航<br>机器索引缓存 ... | pd-index.py<br>_index.py<br>knowledge-index.json ... | constrains:/architecture.md<br>constrains:/conventions.md<br>constrains:/contracts/repository-contract.md<br>constrains:/domains/tooling.md ... |

<!-- END PARADIGMA AUTO-INDEX -->
