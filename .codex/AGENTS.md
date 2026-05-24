# Codex Agent 注册表 — orch

与 Codex 兼容的 11 个工作流核心 Agents（通过 `spawn_agent` 调用）。

## 工作流核心 Agents

| Agent | 文件 | spawn_agent 名称 | 描述 |
|-------|------|-----------------|------|
| workflow | agents/workflow.md | orch-wfc | 入口 + 编排 |
| spec | agents/spec-creation.md | orch-spec | BDD 规范生成 |
| test-designer | agents/test-designer.md | orch-test-des | 测试用例设计 |
| code-architect | agents/code-architect.md | orch-arch | 架构设计 |
| tasker | agents/tasker.md | orch-tasker | 任务列表生成 |
| code-executor | agents/code-executor.md | orch-exec | TDD 实现 |
| code-reviewer | agents/code-reviewer.md | orch-review | 两阶段代码审查 |
| tester | agents/tester.md | orch-tester | 高层测试 |
| exception | agents/exception.md | orch-exc | 异常处理 |
| archiver | agents/archiver.md | orch-archiver | 规范归档合并 |
| knowledge-curator | agents/knowledge-curator.md | orch-kc | 知识复利 |

## Codex 适配说明

1. **Skill 发现**：Codex 有原生 skill 发现机制，通过 SKILL.md 文件自动加载，无需 `Skill` 工具
2. **工具映射**：详见 `skills/using-orch/references/codex-tools.md`
3. **`spawn_agent`**：使用上表的 spawn_agent 名称，参数格式参考 Codex 文档
4. **状态持久化**：工作流状态保存在 `.workflow-state.json`（与 Claude Code 格式一致）
