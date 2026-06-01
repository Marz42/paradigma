# Project Paradigima

*Vibe Coding时代的项目开发基座*

## 如何使用/How To Use





## 目录结构和用途


📁 memory-bank/
 ├── 📄 project-brief.md       # 【定海神针】项目愿景、核心受众、功能边界（明确规定“不做什么”，防止功能蔓延）
 ├── 📄 architecture.md        # 【系统蓝图】整体技术栈、顶层目录结构、前后端交互宏观流程
 ├── 📄 data-contracts.md      # 【最高法律】核心数据库表结构(ER图)、公共API的请求/响应JSON格式（写代码前必读）
 ├── 📄 conventions.md         # 【肌肉记忆】代码规范（如Vue3必须用组合式API，FastAPI依赖注入规则，错误处理规范）
 ├── 📄 roadmap.md             # 【宏观进度】已完成的大版本、当前版本目标、未来规划
 ├── 📄 active-task.md         # ★【当前焦点】当前正在做的单个具体任务。严格的 Check-list，做完一步打钩一步
 │
 ├── 📁 domains/               # 【领域拆分】（解决Token爆炸，用到哪个模块喂哪个文件）
 │    ├── 📄 auth-module.md    # 登录与权限模块的设计与特殊逻辑
 │    ├── 📄 ai-agent.md       # AI指令模块的提示词策略与上下文处理逻辑
 │    └── 📄 task-flow.md      # 事务协同模块的流转规则
 │
 └── 📁 manuals/               # 【操作手册】（冷数据，平时不喂给AI）
      ├── 📄 deploy.md         # 部署与运维指南
      └── 📄 testing-guide.md  # 测试用例编写规范与测试账号数据