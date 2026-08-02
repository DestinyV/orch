# Git-Worktrees 指南

在 execute 阶段为每个 Task 创建隔离工作环境，确保修复循环的安全性、可追踪性。

## 脚本化（推荐）

worktree 生命周期由 `scripts/worktree.js` 脚本管理（封装创建重试/合并/自动清理），模型也可自由使用原生 git 命令——脚本是护栏，不限制能力。

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" create {task-id} {branch}    # 创建（5 步重试）
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" merge {task-id} {target}     # cherry-pick 合并
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" cleanup                      # 清理孤儿+残留分支
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" list                        # 列出全部 worktree
node "${CLAUDE_PLUGIN_ROOT}/scripts/worktree.js" status                      # 仓库+worktree 状态
```

## 生命周期

创建 → 编码/TDD → 审查 → 修复 → cherry-pick/squash合并 → 删除/清理

## 安全协议

- 严禁跨分支提交 | 严禁 worktree 中切换分支
- 每次修复作为独立 commit
- 修复失败可直接删除 worktree 重新开始

## 合并策略

**推荐**（脚本 `merge`）：`git cherry-pick` 逐个复制 commit 到目标分支
**可选**：`git merge --squash` 合并所有 commit 为单个

## 常见操作（原生命令参考）

```bash
git worktree list                  # 列出所有 worktree
git worktree remove .claude/worktrees/T1-xxx  # 删除
cd .claude/worktrees/T1-xxx && git log       # 查看修复历史
git worktree prune                 # 清理孤儿注册
```

详见 `references/branch-safety-protocol.md` | `references/worktree-confirmation-protocol.md` | `references/subagent-protocol.md`
