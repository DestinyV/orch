---
description: 保存当前会话状态 + 工作流状态到 session 文件和 .workflow-state.json。支持中断后恢复。
---

# Session Save Command (SDD+TDD 适配版)

保存当前会话的完整上下文，包含工作流进度、代码变更和决策记录。与 `.workflow-state.json` 深度集成，确保工作流中断后可精确恢复。

## 何时使用

- 结束工作会话前
- 接近上下文限制时（先 `/session-save`，再开启新会话）
- 解决复杂问题后
- 需要将上下文移交给未来会话的任何时候
- SDD+TDD 工作流手动暂停时

## 流程

### Step 1: 收集上下文
- 读取所有本会话中修改的文件（git diff 或会话记忆）
- 收集工作流状态：`.workflow-state.json`
- 检查当前 spec-dev/ 进度
- 记录错误/失败及其根因

### Step 2: 保存工作流状态

确保 `.workflow-state.json` 已更新为最新状态：

```bash
# 检查当前状态文件
test -f spec-dev/*/.workflow-state.json && echo "State file found" || echo "No workflow state (non-workflow session)"
```

如有状态文件，记录当前 stage 和进度百分比。

### Step 3: 创建 session 数据文件夹

```bash
mkdir -p ~/.claude/session-data
```

### Step 4: 写入 session 文件

创建 `~/.claude/session-data/YYYY-MM-DD-<short-id>-session.tmp`：

```markdown
# Session: YYYY-MM-DD

**Started:** {approximate time}
**Last Updated:** {current time}
**Project:** {project path}
**Workflow State File:** {path to .workflow-state.json}
**Stage:** {current stage from state file}

---

## What We Are Building
{1-3 段落描述目标}

---

## What WORKED (with evidence)
- {working item} — confirmed by: {evidence}

---

## What Did NOT Work (and why)
- {failed approach} — failed because: {exact reason}

---

## What Has NOT Been Tried Yet
- {untried approach}

---

## Current State of Files
| File | Status | Notes |
|------|--------|-------|
| `path/to/file` | PASS: Complete | {what it does} |
| `path/to/file` | In Progress | {what's left} |

---

## Workflow Stage
**Current**: {spec / test-design / design / ...}
**Next**: {next skill to invoke}
**Blockers**: {any HARD-GATE blocks}

## Decisions Made
- {decision} — reason: {why}

---

## Blockers & Open Questions
- {blocker}

---

## Exact Next Step
{最优先要做的下一步}
```

### Step 5: 展示给用户

显示文件路径和摘要，等待确认：

```
Session saved to ~/.claude/session-data/2026-05-24-abc123de-session.tmp

Does this look accurate? Anything to correct or add before we close?
```

## 与 SDD+TDD 工作流集成

```bash
# 在 workflow 中自动触发
# 每阶段完成时：
# 1. 更新 .workflow-state.json（强制）
# 2. 更新 .workflow-eval.json（Token/效果）
# 3. session file 记录的补充信息

# 手动触发：
/session-save  # 保存完整会话上下文
/session-save --light  # 仅保存状态和文件清单
```

## 输出文件

| 文件 | 用途 | 位置 |
|------|------|------|
| Session 文件 | 会话上下文 | `~/.claude/session-data/YYYY-MM-DD-<id>-session.tmp` |
| 工作流状态 | 阶段状态 | `spec-dev/{req}/.workflow-state.json` |
| 工作流评估 | Token/效果 | `spec-dev/{req}/.workflow-eval.json` |
