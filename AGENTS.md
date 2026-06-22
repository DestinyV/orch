# orch — Agent Registry

SDD+TDD 工作流专用 Agent 注册表。共 25 个 Agents（13 工作流核心 + 12 扩展能力）。

## 工作流核心 Agents

| Agent | 职责 | 使用时机 |
|-------|------|---------|
| [workflow](agents/workflow.md) | 统一入口 + 流程编排 | 新需求入口 |
| [spec](agents/spec.md) | 需求分析和规范生成 | 需求分析阶段 |
| [code-explorer](agents/code-explorer.md) | 代码库探索 + project-map 生成 | 规范阶段 |
| [test-designer](agents/test-designer.md) | 测试设计和规范生成 | 规范完成后 |
| [code-architect](agents/code-architect.md) | 代码设计规划 | 设计阶段 |
| [tasker](agents/tasker.md) | 任务列表生成 | 设计确认后 |
| [executor](agents/executor.md) | TDD 代码实现 | 任务定义后 |
| [code-reviewer](agents/code-reviewer.md) | 一次性综合性审查（规范+质量+TDD+覆盖率+追溯） | 代码实现后 |
| [tester](agents/tester.md) | 测试验证和闭环 | 代码审查后 |
| [exception](agents/exception.md) | 异常模式扫描+代码生成 | 后端/全栈编码时 |
| [knowledge-curator](agents/knowledge-curator.md) | 知识复利执行 | 工作流完成后 |
| [completion-reporter](agents/completion-reporter.md) | 工作流完成报告生成（四段：总结/效率/沉淀/建议） | knowledge-curator 完成后 |
| [archiver](agents/archiver.md) | 规范归档合并 + context 同步 | 测试通过后 |

## 扩展能力 Agents

| Agent | 职责 | 来源 |
|-------|------|------|
| [code-cleaner](agents/code-cleaner.md) | 代码清理（简化+死代码+静默失败） | 合并 |
| [comment-analyzer](agents/comment-analyzer.md) | 代码注释分析 | 引入 |
| [conversation-analyzer](agents/conversation-analyzer.md) | 对话分析 | 引入 |
| [contract-creator](agents/contract-creator.md) | 接口契约定义 | 已有 |
| [debug](agents/debug.md) | 证据驱动因果追踪 | 引入 |
| [doc-updater](agents/doc-updater.md) | 文档更新 | 引入 |
| [e2e-runner](agents/e2e-runner.md) | 端到端测试执行 | 引入 |
| [goal-evaluator](agents/goal-evaluator.md) | 目标达成度评估（Goal 模式独立验证） | 新增 |
| [loop-operator](agents/loop-operator.md) | 自主循环操作 | 引入 |
| [planner](agents/planner.md) | 实现规划 | 引入 |
| [test-verifier](agents/test-verifier.md) | 基于证据的完成验证 | 保留 |
| [clarifier](agents/clarifier.md) | 苏格拉底需求澄清 | 已有 |
