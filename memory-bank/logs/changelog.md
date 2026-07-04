# 变更日志

> 🌡️ WARM 知识 — 记录 Project Paradigma 模板库自身的版本发布历史。
>
> 格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

---

## [0.4.0] - 2026-07-04

### Added
- 新增 strict OKF lint，校验 schema、type、section、timestamp、policy 和 generated block checksum。
- 新增 `pd-check-links.py`，校验 Markdown links、frontmatter relations 和 generated index entries。
- 新增 hot-size、active-task archive、progress compact 工具。
- 新增 ADR-003，记录从 OKF MVP 进入严格生产规则。

### Changed
- 升级 `pd-sync-index.py`，生成含 retrieval hints、symbols、relations 和 checksum 的根/子目录索引。
- 更新 README、INIT_PROMPT、AGENT_RULES 和 Cursor rule，采用 lint + link check + index check + hot-size check 的 Update Phase。
- 收敛核心 knowledge/templates section 结构，修正旧路径引用与 RFC 关系目标。

## [0.3.0] - 2026-07-04

### Added
- 新增 OKF-compatible runtime/logs/knowledge 三态 Memory-Bank 结构。
- 新增 `docs/rfc/`，并将 OKF runtime 草案迁入 RFC concept 文档。
- 新增 `.paradigma/config.yaml`、轻量 type registry 和最小 Python 工具链。
- 新增 `pd-lint-okf.py` 与 `pd-sync-index.py`。

### Changed
- 更新 `AGENT_RULES.md`、Cursor rule、`INIT_PROMPT.md` 和 README，切换到 OKF-compatible Agent runtime protocol。
- 将长期知识迁移到 `memory-bank/knowledge/` 并补充 OKF frontmatter。
- 将运行状态迁移到 `memory-bank/runtime/`，将日志迁移到 `memory-bank/logs/`。

## [0.2.2] - 2026-07-04

### Changed
- 将空白 `.template.md` 文件从 `memory-bank/` 迁移到 `memory-bank-template/`，与项目运行记忆分离。
- 更新 `AGENT_RULES.md`、Cursor rule、`INIT_PROMPT.md` 和 README 中的模板回退与项目初始化路径。
- 移除 `.gitignore` 中对 `memory-bank/*.md` 运行时文件的排除规则，使 Paradigma 自身开发记忆可直接被版本控制追踪。

### Added
- 新增 Paradigma 自身的 `architecture.md`、`data-contracts.md`、`decisions.md` 和 `changelog.md` 运行时记忆文件。

## [0.2.1] - 2026-06-17

### Changed
- HOT/WARM 层占位文件统一改为 `.template.md` 格式范例（architecture、active-task、data-contracts、roadmap、domains）。
- `progress.md` 纳入统一模板机制，补充跨平台时间戳获取说明。
- `AGENT_RULES.md` 与 `memory-bank-protocol.mdc` 同步，新增模板回退读取规则。
- 统一时间格式为 `YYYY-MM-DD HH:mm`（changelog 发布日期为 `YYYY-MM-DD`）。
- `conventions.md` 新增「Paradigma 模板库自身维护」SemVer 规则。

### Fixed
- 消除 HOT 层空占位文件导致 Agent 读取无有效信息的问题。

## [0.2.0] - 2026-06-17

### Changed
- 统一 `memory-bank` 目录命名（原 `memory_bank`）。
- 日志时间戳须通过工具获取，精确到分钟。
