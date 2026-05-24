# Git-Worktrees 快速参考

## 创建

```bash
git worktree add .claude/worktrees/{task-id}-{name} HEAD
cd .claude/worktrees/{task-id}-{name}
```

## 常用命令

```bash
git worktree list                          # 列出所有
git worktree remove .claude/worktrees/T1   # 删除
cd .claude/worktrees/T1 && git log         # 查看历史
```

## 生命周期

创建 → 编码/TDD → 审查 → 修复 → cherry-pick合并 → 删除

## 安全约束

严禁跨分支提交 | 严禁worktree中切换分支 | 每次修复独立commit

## 合并

```bash
# cherry-pick（推荐）
git checkout main
git cherry-pick <commit-hash>

# squash merge
git checkout main
git merge --squash .claude/worktrees/T1
git commit -m "feat: task1 complete"
```

## 失败恢复

```bash
git worktree remove .claude/worktrees/T1   # 删除
git worktree add .claude/worktrees/T1 HEAD  # 重新开始
```
