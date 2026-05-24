# Git-Worktrees 指南

在 code-execute 阶段为每个 Task 创建隔离工作环境，确保修复循环的安全性、可追踪性。

## 创建 Worktree

```bash
# 必须 AskUserQuestion 确认基础分支
git worktree add .claude/worktrees/{task-id}-{name} {branch}
```

## 生命周期

创建 → 编码/TDD → 审查 → 修复 → cherry-pick/squash合并 → 删除

## 安全协议

- 严禁跨分支提交 | 严禁 worktree 中切换分支
- 每次修复作为独立 commit
- 修复失败可直接删除 worktree 重新开始

## 合并策略

**推荐**：`git cherry-pick` 逐个复制 commit 到目标分支
**可选**：`git merge --squash` 合并所有 commit 为单个

## 常见操作

```bash
git worktree list                  # 列出所有 worktree
git worktree remove .claude/worktrees/T1-xxx  # 删除
cd .claude/worktrees/T1-xxx && git log       # 查看修复历史
```

详见 `references/branch-safety-protocol.md` | `references/worktree-confirmation-protocol.md` | `references/subagent-protocol.md`
