# Git-Worktrees 快速参考

## 创建

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" create {task-id} {branch}    # 脚本（5 步重试）
# 或原生命令：
git worktree add .claude/worktrees/{task-id}-{name} HEAD
cd .claude/worktrees/{task-id}-{name}
```

## 常用命令

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" list          # 列出全部（含孤儿标记）
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" status        # 仓库+worktree 状态
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" cleanup       # 自动清理孤儿+残留分支
git worktree remove .claude/worktrees/T1   # 手动删除
cd .claude/worktrees/T1 && git log         # 查看历史
```

## 生命周期

创建 → 编码/TDD → 审查 → 修复 → cherry-pick合并 → 清理

## 安全约束

严禁跨分支提交 | 严禁worktree中切换分支 | 每次修复独立commit

## 合并

```bash
# 脚本（推荐）——自动 cherry-pick + 恢复原分支
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" merge {task-id} {target-branch}

# cherry-pick（手动）
git checkout main
git cherry-pick <commit-hash>

# squash merge
git checkout main
git merge --squash .claude/worktrees/T1
git commit -m "feat: task1 complete"
```

## 失败恢复

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" cleanup --force   # 强制清理
git worktree remove .claude/worktrees/T1   # 删除
git worktree add .claude/worktrees/T1 HEAD  # 重新开始
```
