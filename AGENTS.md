# orch — Agent Registry

SDD+TDD 工作流专用 Agent 注册表。共 25 个 Agents（11 工作流核心 + 14 扩展能力）。

## 工作流核心 Agents

| Agent | 职责 | 使用时机 |
|-------|------|---------|
| [workflow-control](agents/workflow-control.md) | 统一入口 + 流程编排 | 新需求入口 |
| [spec-creation](agents/spec-creation.md) | 需求分析和规范生成 | 需求分析阶段 |
| [test-designer](agents/test-designer.md) | 测试设计和规范生成 | 规范完成后 |
| [code-architect](agents/code-architect.md) | 代码设计规划 | 设计阶段 |
| [code-tasker](agents/code-tasker.md) | 任务列表生成 | 设计确认后 |
| [code-executor](agents/code-executor.md) | TDD 代码实现 | 任务定义后 |
| [code-reviewer](agents/code-reviewer.md) | 代码规范+质量审查 | 代码实现后 |
| [code-tester](agents/code-tester.md) | 测试验证和闭环 | 代码审查后 |
| [exception-handler](agents/exception-handler.md) | 异常模式扫描+代码生成 | 后端/全栈编码时 |
| [knowledge-curator](agents/knowledge-curator.md) | 知识复利执行 | 工作流完成后 |
| [spec-archiver](agents/spec-archiver.md) | 规范归档合并 | 测试通过后 |

## 扩展能力 Agents

| Agent | 职责 | 来源 |
|-------|------|------|
| [planner](agents/planner.md) | 实现规划 | 引入 |
| [tdd-guide](agents/tdd-guide.md) | TDD 流程引导 | 引入 |
| [code-simplifier](agents/code-simplifier.md) | 代码简化重构 | 引入 |
| [silent-failure-hunter](agents/silent-failure-hunter.md) | 静默失败检测 | 引入 |
| [comment-analyzer](agents/comment-analyzer.md) | 代码注释分析 | 引入 |
| [conversation-analyzer](agents/conversation-analyzer.md) | 对话分析 | 引入 |
| [pr-test-analyzer](agents/pr-test-analyzer.md) | PR 测试覆盖分析 | 引入 |
| [refactor-cleaner](agents/refactor-cleaner.md) | 死代码清理 | 引入 |
| [loop-operator](agents/loop-operator.md) | 自主循环操作 | 引入 |
| [harness-optimizer](agents/harness-optimizer.md) | 工作流调优 | 引入 |
| [doc-updater](agents/doc-updater.md) | 文档更新 | 引入 |
| [e2e-runner](agents/e2e-runner.md) | 端到端测试执行 | 引入 |
| [code-explorer](agents/code-explorer.md) | 代码库探索 | 整合 |
| [api-contract-creator](agents/api-contract-creator.md) | 接口契约定义 | 已有 |
