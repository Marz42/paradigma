# INIT_PROMPT.md — 会话启动模板

> **使用方式**：根据你的场景复制对应模板，将 `{{PLACEHOLDER}}` 替换为实际内容后粘贴到 IDE 对话框中。
>
> **前置条件**：确保已按照 README.md 完成步骤 1（获取基座、断开上游 git remote）。

---

## 模式 F：Project Setup & Bootstrap（一次性机械设置）

> **适用场景**：刚 clone 了 Paradigma，还没有做任何初始化设置。让 Agent 帮你完成机械操作。

```
你好，我刚从这个项目模板创建了我的新项目。

【我的项目名】：{{项目名，例如 TodoTracker}}

请先阅读 README.md 的"如何使用"部分，理解完整设置流程。然后帮我按以下步骤操作：

1. 激活 OKF-compatible Memory-Bank 模板：
   - 从 memory-bank-template/runtime/ 复制到 memory-bank/runtime/
   - 从 memory-bank-template/logs/ 复制到 memory-bank/logs/
   - 从 memory-bank-template/knowledge/ 复制到 memory-bank/knowledge/

2. 确认 runtime/logs/knowledge 三态结构存在：
   - memory-bank/runtime/active-task.md
   - memory-bank/logs/progress/
   - memory-bank/knowledge/index.md
   - memory-bank/knowledge/project-brief.md
   - memory-bank/knowledge/architecture.md
   - memory-bank/knowledge/conventions.md
   - memory-bank/knowledge/contracts/

3. 修改项目标识：
   - 将 README.md 的标题从 "Project Paradigma" 改为 "{{项目名}}"
   - 将 README.md 的副标题改为适合我项目的简介
   - 更新 memory-bank/knowledge/project-brief.md 中的项目身份信息

4. 处理 git remote：
   - 执行 `git remote -v` 检查当前 remote
   - 如果 remote 仍指向 Marz42/paradigma，执行 `git remote remove origin`
   - 然后告诉我你的 GitHub 仓库 URL，我帮你关联 `git remote add origin <你的仓库URL>`

5. 运行 `python .paradigma/tools/pd-check-all.py` 和 `python .paradigma/tools/pd-sync-index.py --write` 验证 Memory-Bank 状态。

6. 将所有更改做首次 commit：
   - 提交信息：chore: init from paradigma template
   - 如果 remote 已配置且与你的仓库关联，同时 push

7. 完成后告诉我一切就绪，我们可以进入模式 A 填充项目知识，或者直接开始写代码。
```

---

## 模式 A：全新项目初始化（Agent 填充所有文档）

```
你好，我们将开始一个新项目。

【项目目标】
{{用1-2句话描述项目要解决什么问题，面向什么用户}}

【技术栈偏好】
{{例如：Vue3 + FastAPI + PostgreSQL，或其他}}

【核心卖点 / 差异化特性】
{{例如：支持自然语言输入记账}}

请按以下步骤操作：

1. 读取 memory-bank/runtime/active-task.md、memory-bank/knowledge/index.md 和 HOT knowledge。
2. 基于 memory-bank/knowledge/project-brief.md 填充项目愿景、受众、边界和成功指标。
3. 基于 memory-bank/knowledge/architecture.md 填充整体技术栈、顶层目录结构和关键约束。
4. 基于 memory-bank/knowledge/contracts/repository-contract.md 设计第一版契约边界；如涉及 API/数据库，新增 contracts 文档。
5. 基于 memory-bank/runtime/active-task.md 创建第一个 MVP 任务。
6. 对暂时无法确定的字段标记为 `TODO`，不要编造。
7. 运行 `python .paradigma/tools/pd-check-all.py` 和 `python .paradigma/tools/pd-sync-index.py --write`。
8. 完成文档初始化后告诉我，我们再开始写第一行代码。
```

---

## 模式 B：已有项目续接（Agent 读取已有文档并审查）

```
你好，这是一个已有项目。请按以下步骤操作：

1. 读取 memory-bank/runtime/active-task.md。
2. 读取 memory-bank/knowledge/index.md 和 HOT knowledge。
3. 根据 index 审查相关 WARM/COLD 文档，告诉我：
   - 哪些文档信息不足或过时
   - architecture 与实际代码结构是否一致
   - contracts 的约束是否仍然有效
4. 阅读 memory-bank/logs/progress/ 下最近的 session log，了解项目历史。
5. 给出审查意见，然后我们继续推进 {{具体的下一步任务}}。
```

---

## 模式 C：单任务突击（跳过审查，直接执行）

```
你好，请按以下步骤操作：

1. 读取 memory-bank/runtime/active-task.md、memory-bank/knowledge/index.md 和 HOT knowledge。
2. 根据任务从 index 选择必要的 WARM/COLD 文档。
3. 理解当前项目状态后，直接开始执行任务：
   {{具体任务描述}}
4. 执行完成后，按照 AGENT_RULES.md 的 Update Phase 更新 runtime/logs/knowledge，并运行 `python .paradigma/tools/pd-check-all.py`。
```

---

## 模式 D：架构决策讨论（聚焦决策层面）

```
你好，我们需要做一个架构决策。

【背景】
{{简要描述当前遇到的架构问题或需要决策的事项}}

请按以下步骤操作：

1. 读取 active-task、knowledge/index、architecture、repository contract 和相关 decisions。
2. 给出 2-3 个可行方案，并分析各自优缺点。
3. 给出你的推荐方案及理由。
4. 待我确认后，将最终决策追加到 memory-bank/knowledge/decisions/。
```

---

## 自定义提示

核心原则：

- 始终让 Agent 先读 runtime active task、knowledge index 和 HOT knowledge。
- 明确告诉 Agent 你期望的输出，是填充知识、写代码还是做决策。
- 约定好会话结束时的交付物，并要求执行 Update Phase：`python .paradigma/tools/pd-check-all.py`，必要时 archive/compact。
