# Git Workflow (SDD+TDD)

## Commit Message Format

```
<type>(<scope>): <description>
```

Types: feat, fix, refactor, docs, test, chore, perf, ci
Scope: the Task name or requirement shorthand (e.g., `auth`, `knowledge-continuum`)

## Every Task in Its Own Worktree

- Each Task from the task list (`tasks.md`) MUST be implemented in a **dedicated git worktree**
- Worktree name format: `task-<task-number>-<short-description>`
- This ensures complete isolation between parallel Tasks and enables safe partial rollback
- See `code-execute` skill for worktree creation automation

## Branch Naming

- Format: `sdd/<requirement-abbrev>/<task-number>-<short-desc>`
- Example: `sdd/eval-metrics/03-backend-service`

## Small Focused Commits

- One logical change per commit
- Each commit message references the spec scenario it fulfills
- Squash work-in-progress commits before PR

## Git Trailers — 决策追溯

每次提交自动附加决策上下文，便于追溯设计决策原因。

可用 trailer：

| Trailer | 用途 | 示例 |
|---------|------|------|
| `Constraint` | 影响决策的约束条件 | `Constraint: refresh_token 7天过期，单次使用后作废` |
| `Rejected` | 被拒绝方案 + 理由 | `Rejected: session-cookie | 无状态方案更适合微服务` |
| `Directive` | 对后续修改者的提示 | `Directive: 新增字段需同步更新 DTO 转换器` |
| `Spec` | 关联的 spec 场景 ID | `Spec: login-001` |
| `HARD-GATE` | 触发的 HARD-GATE 名称 | `HARD-GATE: coverage-below-85` |

示例：

```
feat(auth): 实现用户登录接口

Constraint: refresh_token 7天过期，单次使用后作废
Rejected: session-cookie | 无状态方案更适合微服务
Spec: login-001
```
