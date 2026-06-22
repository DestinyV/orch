# orch — Agent 注册表（中文）

SDD+TDD 工作流专用 Agent 注册表。共 25 个 Agents（13 工作流核心 + 12 扩展能力）。

## 工作流核心 Agents

| Agent | 职责 | 使用时机 |
|-------|------|---------|
| workflow | 统一入口 + 流程编排 | 新需求入口 |
| spec | 需求分析和规范生成 | 需求分析阶段 |
| code-explorer | 代码库探索 + project-map 生成 | 规范阶段 |
| test-designer | 测试设计和规范生成 | 规范完成后 |
| code-architect | 代码设计规划 | 设计阶段 |
| tasker | 任务列表生成 | 设计确认后 |
| executor | TDD 代码实现 | 任务定义后 |
| code-reviewer | 一次性综合性审查（规范+质量+TDD+覆盖率） | 代码实现后 |
| tester | 测试验证和闭环 | 代码审查后 |
| exception | 异常模式扫描+代码生成 | 后端/全栈编码时 |
| knowledge-curator | 知识复利执行 | 工作流完成后 |
| completion-reporter | 工作流完成报告生成（四段：总结/效率/沉淀/建议） | knowledge-curator 完成后 |
| archiver | 规范归档合并 + context 同步 | 测试通过后 |

## 扩展能力 Agents

| Agent | 职责 | 来源 |
|-------|------|------|
| clarifier | 苏格拉底需求澄清 | 已有 |
| code-cleaner | 代码清理（简化+死代码+静默失败） | 合并 |
| comment-analyzer | 代码注释分析 | 引入 |
| contract-creator | 接口契约定义 | 已有 |
| conversation-analyzer | 对话分析 | 引入 |
| debug | 证据驱动因果追踪 | 引入 |
| doc-updater | 文档更新 | 引入 |
| e2e-runner | 端到端测试执行 | 引入 |
| goal-evaluator | 目标达成度评估（Goal 模式） | 新增 |
| loop-operator | 自主循环操作 | 引入 |
| planner | 实现规划 | 引入 |
| test-verifier | 基于证据的完成验证 | 保留 |
