# 使用指南

## 入口

```
/workflow "需求描述" → 自动执行完整 10 阶段流程
```

或手动逐步调用各 Skill。

## 工作流

```
/workflow → /spec → /test-design ⟷ /design → /contract → /task → /execute → /exception → /test → /archive
```

⟷ 表示可并行执行。

## 10 阶段说明

| 阶段 | Skill | 输入 | 输出 | Agent |
|------|-------|------|------|-------|
| 编排 | `/workflow` | 需求描述 | .workflow-state.json | 无（主控Skill） |
| 规范 | `/spec` | 需求描述 | `spec-dev/{id}/spec/` | code-explorer |
| 测试设计 | `/test-design` | spec | `tests/test-spec.md + fixtures.json + test-*.template` | test-designer |
| 设计 | `/design` | spec | `design/design.md` | code-architect |
| 接口契约 | `/contract` | design.md | `contract.md + review-report.md` | contract-creator |
| 任务 | `/task` | design.md + tests | `tasks/tasks.md` | tasker |
| 执行 | `/execute` | tasks + tests | `src/ + execution-report.md` | code-executor + code-reviewer |
| 异常处理 | `/exception` | src | `src/ (添加异常处理)` | exception |
| 测试 | `/test` | src + spec | `testing-report.md` | code-reviewer |
| 归档 | `/archive` | 测试通过的 spec | 合并到主规范库 | archiver |

## 并行执行

- `/test-design`(2) 和 `/design`(3) 可并行（均依赖 spec）
- workflow 自动处理并行调度

## 全栈项目

`project-mode: fullstack` 时自动触发：
- `/contract` 在 design 和 task 之间自动执行接口契约
- `/exception` 在 execute 之后自动执行异常处理

## 工作模式

| 标签 | standard（默认） | quick |
|------|-----------------|-------|
| TDD | 必须 | 可跳过 |
| 子代理 | 必须 | 可选 |
| 审查 | 两阶段 | 单阶段 |
| 覆盖率 | ≥85% | ≥60% |
| 跳过阶段 | 无 | test-design/contract/exception |

## 中断恢复

workflow 自动维护 `spec-dev/{id}/.workflow-state.json`，会话中断后重新执行 `/workflow` 即可从中断处继续。

## 关键约束

- 所有新需求必须从 `/workflow` 启动（唯一入口）
- 设计审批后才能进入 Task 阶段
- standard 模式每个 Task 必须使用独立子代理 + worktree
- 所有 Task 通过两阶段审查（规范+质量）
- 禁止跳过测试验证
- 9 个 Agent 必须通过 `Agent()` 显式派遣
