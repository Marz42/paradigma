# 变更日志

> 🌡️ WARM 知识 — 记录 Project Paradigma 模板库自身的版本发布历史。
>
> 格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

---

## [0.4.2] - 2026-07-05

### Added
- 新增 `pd-check-all.py`，聚合 lint、link check、index check、hot-size 为单一质量门禁。
- 新增 `.github/workflows/check.yml`，在 push main 和 PR 上自动运行 `pd-check-all.py`。

### Fixed
- `pd-check-links.py` 现在排除 fenced/inline/indented code blocks 中的链接模式，避免 `[{rel}]({rel})` 等代码示例产生假阳性 ERROR。

### Changed
- 更新 `AGENT_RULES.md`、Cursor rule、`conventions.md`、`paradigma-baseline-test.md` 和 `repository-contract.md`，Update Phase 统一使用 `pd-check-all.py`。

## [0.4.1] - 2026-07-05

### Changed
- `deploy.md` 和 `testing-guide.md` 重命名为 `paradigma-deploy.md` (cold) 和 `paradigma-baseline-test.md` (warm)，避免与衍生项目自身 deploy/test 文档歧义。
- `pd-sync-index.py` 从 `.paradigma/config.yaml` 读取 `knowledge_roots` 配置，对每个 root 及其子目录自动生成索引（包括 `docs/rfc/`）。
- `pd-archive-task.py` 和 `pd-compact-progress.py` 状态从 Experimental 升级为 Stable。

### Added
- 新增 `domains/tooling.md` 和 `domains/protocol.md` 域文档。
- 新增 `known-issues/fstring-escape-in-compact.md` 和 `known-issues/stale-section-structure-in-adr001.md`。
- 扩充 `glossary.md` 至 20+ 核心术语。
- `docs/rfc/index.md` 补全 OKF frontmatter 并加入自动索引。

### Fixed
- 更新 `architecture.md` Open Questions 以反映 0.4.0 已实现工具。

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

---

> 📜 **Pre-history（从 pre-OKF 时代的 `memory_bank/changelog.md` 归档恢复）**
> 
> 以下条目记载了 Paradigma 项目最早期的发布历史。版本号在早期尚未严格遵循 SemVer，可能与本 changelog 中同版本号条目不完全一致。此处保留原始措辞以供历史参考。

## [0.2.0-pre] - 2026-06-03

### Added
- 版本管理体系：`VERSION` 文件作为版本号唯一真实来源，`changelog.md` 记录发布历史
- `conventions.md` 新增"主动版本管理"规则块，含修改类型 vs 版本动作决策表
- `AGENT_RULES.md` Update Phase 新增步骤 7：版本号评估
- `project-brief.md` 身份卡片新增"当前版本"字段

### Fixed
- README 步骤 1 缺少手动路径的"断开上游 git remote"说明
- README 步骤 4 模式列表缺少模式 F，导致新用户跳过 setup
- INIT_PROMPT 模式 F 步骤 4 不够主动（原为被动检查，改为主动执行 `git remote remove`）
- `.cursor/rules/memory-bank-protocol.mdc` 与 `AGENT_RULES.md` 不同步（缺少 version step、changelog、glossary）

## [0.1.0-pre] - 2026-06-02

### Added
- 设计 memory-bank 目录结构和知识温度体系（HOT / WARM / COLD）
- 创建 `AGENT_RULES.md` — IDE 无关的四阶段工作流协议
- 创建 `INIT_PROMPT.md` — 六种会话启动模式（F / A / B / C / D / 自定义）
- 创建 `conventions.md` — 编码规范（通用原则、命名约定、文件组织、前后端规范、类型安全、Git 提交、SemVer 摘要、测试规范、审查清单）
- 创建 `project-brief.md` — 九板块可填写模板
- 创建 `.cursor/rules/memory-bank-protocol.mdc` — Cursor 自动加载规则
- 创建 `.gitignore` — 模板与运行时分离机制
- 创建 `manuals/` 目录 — 部署运维和测试指南模板
- 创建 `changelog.md` — Keep a Changelog 格式发布日志
- 创建 `VERSION` — 版本号唯一真实源头
- 创建 `LICENSE` — MPL-2.0 文件级 copyleft 许可证
- 补充 conventions.md 中的 SemVer 操作摘要和 Agent 行为约定
- 补充 INIT_PROMPT.md 中的模式 F（Project Setup & Bootstrap）
