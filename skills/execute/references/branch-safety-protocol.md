# Git 分支安全协议

**核心原则**：创建 worktree 前确认基础分支 | 提交前确认目标分支 | 合并前再次确认 | 严禁同一 Task 跨分支提交

## 核心约束：同一 Task 改动必须提交到同一分支

创建 worktree 时选定的基础分支决定了该 Task 所有改动的最终目标分支。

**禁止**：分割提交到不同分支 | worktree 中切换分支后提交 | 同一 Task 合并到多分支

**正确**：选定目标分支后一致执行 | 明确指定基础分支 | 不同 Task 可有不同分支

## 确认协议

1. **创建 worktree 前**：AskUserQuestion 确认基础分支（当前/master/develop/其他）
2. **代码提交前**：确认提交到 worktree 对应分支
3. **合并前**：确认源分支和目标分支

## 合并策略

- **推荐**：`git cherry-pick` 将 worktree 的 commit 逐个复制到目标分支
- **可选**：`git merge --squash` 将 worktree 所有 commit 合并为单个
- **禁止**：直接在 worktree 中切换到其他分支后提交
