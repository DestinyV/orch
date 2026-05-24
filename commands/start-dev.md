---
description: SDD+TDD 规范驱动开发工作流 — 统一入口：从需求到归档的完整流程
argument-hint: 可选：需求描述
---

# SDD+TDD 规范驱动开发工作流

统一入口命令，编排 10 阶段 SDD+TDD 流程。

> **流程执行参考（Source of Truth）**: 各阶段的输入/输出契约、校验规则、失败纠正、Agent 派遣详见 [`skills/workflow/references/flow-execution-reference.md`](skills/workflow/references/flow-execution-reference.md)。

## 入口

```
/start-dev "需求描述"   →   自动执行完整流程
```

逐步调用：
```
/spec → /test-design ⟷ /design → /contract → /task → /execute → /test → /archive
```

## 强制规则

1. **禁止在 workflow-control 之前执行代码探索**。探索由 spec-creation 内部负责。
2. **禁止跳过阶段**。必须从阶段0 开始，由状态检测决定中断恢复。

## 流程步骤

| 步骤 | Skill | Agent 派遣 | 前置 | 调度 |
|------|-------|-----------|------|------|
| 0 | workflow | — | 无 | 入口编排 |
| 0.5 | clarify | socratic-clarifier | 模糊度 > 0.2 | 条件触发 |
| 1 | spec | code-explorer | clarification done | 自动级联 |
| 2 | test-design | test-designer | spec done | 与步骤3 并行 |
| 3 | design | code-architect | spec done | 与步骤2 并行 |
| 3.5 | contract | contract-creator | design done + fullstack | 条件触发 |
| 4 | task | tasker | design [+ contract] | 串行 |
| 5 | execute | code-executor, code-reviewer | task done | 串行 |
| 5.5 | exception | exception | execute 内部 | 子过程自动 |
| 6 | test | tester, test-verifier | execute done | 串行 |
| 7 | archive | archiver | test done + 全通过 | 串行 |
| 8 | evaluation | — | archive done | 串行 |
| 9 | continuous-learning | knowledge-curator | evaluation done | 串行 |

## 工作模式

| 标签 | standard | quick |
|------|----------|-------|
| 流程 | 全 14 阶段 | spec → execute(精简) → test(精简) |
| TDD | 必须，test-*.template 存在才允许编码 | 可跳过 |
| 子代理 | 必须，N 个无依赖 Task 启动 N 个子代理并行 | 可选 |
| 审查 | 两阶段（规范 + 质量） | 单阶段 |
| 覆盖率 | ≥85% | ≥60% |

快速模式仅在用户明确要求时启用。

## 各阶段入口

| 步骤 | 调用 | 说明 |
|------|------|------|
| 0 | `Skill("orch:workflow")` | 模式检测 + 编排 |
| 0.5 | `Skill("orch:clarify")` | 苏格拉底澄清 |
| 1 | `Skill("orch:spec")` | BDD 规范生成 |
| 2 | `Agent(subagent_type=orch:test-designer, run_in_background=true)` | 测试规范 + fixtures |
| 3 | `Agent(subagent_type=orch:code-architect, run_in_background=true)` | 架构设计 |
| 3.5 | `Skill("orch:contract")` | 接口契约 + 审查 |
| 4 | `Skill("orch:task")` | 任务拆解 |
| 5 | `Skill("orch:execute")` | TDD 编码 |
| 6 | `Skill("orch:test")` | 集成/E2E/性能测试 |
| 7 | `Skill("orch:archive")` | 规范归档合并 |
| 8 | evaluation | 效果评估 + 辅助诊断 |
| 9 | `Skill("orch:continuous-learning")` | 知识沉淀 |
