# orch — Agent 注册表（中文）

## 工作流核心 Agents

| Agent | 职责 | 使用时机 |
|-------|------|---------|
| workflow | 统一入口 + 流程编排 | 新需求入口 |
| spec | 需求分析和规范生成 | 需求分析阶段 |
| test-designer | 测试设计和规范生成 | 规范完成后 |
| code-architect | 代码设计规划 | 设计阶段 |
| tasker | 任务列表生成 | 设计确认后 |
| code-executor | TDD 代码实现 | 任务定义后 |
| code-reviewer | 代码规范+质量审查 | 代码实现后 |
| tester | 测试验证和闭环 | 代码审查后 |
| exception | 异常模式扫描+代码生成 | 后端/全栈编码时 |
| knowledge-curator | 知识复利执行 | 工作流完成后 |
| archiver | 规范归档合并 | 测试通过后 |

## 扩展能力 Agents

| Agent | 职责 | 来源 |
|-------|------|------|
| planner | 实现规划 | 引入 |
| tdd-guide | TDD 流程引导 | 引入 |
| code-simplifier | 代码简化重构 | 引入 |
| silent-failure-hunter | 静默失败检测 | 引入 |
| comment-analyzer | 代码注释分析 | 引入 |
| conversation-analyzer | 对话分析 | 引入 |
| pr-test-analyzer | PR 测试覆盖分析 | 引入 |
| refactor-cleaner | 死代码清理 | 引入 |
| loop-operator | 自主循环操作 | 引入 |
| harness-optimizer | 工作流调优 | 引入 |
| doc-updater | 文档更新 | 引入 |
| e2e-runner | 端到端测试执行 | 引入 |
| code-explorer | 代码库探索 | 整合 |
| contract-creator | 接口契约定义 | 已有 |
