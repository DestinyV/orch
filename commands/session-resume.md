---
description: 从 session 文件和 .workflow-state.json 恢复工作流上下文。自动加载最近保存的会话。
argument-hint: "[date | file-path]"
---

# Session Resume Command (SDD+TDD 适配版)

加载最近保存的会话，恢复工作流上下文。与 `/session-save` 成对使用，深度集成 `.workflow-state.json` 实现工作流中断恢复。

## 何时使用

- 开始新会话继续之前的工作
- 因上下文限制开启新会话后
- 收到来自其他来源的 session 文件（提供文件路径）
- SDD+TDD 工作流中断后需要恢复

## 用法

```
/session-resume                                          # 加载 ~/.claude/session-data/ 中最新的文件
/session-resume 2026-05-24                                # 加载指定日期的最新 session
/session-resume ~/.claude/session-data/2026-05-24-abc-session.tmp  # 加载指定文件
```

## 流程

### Step 1: 查找 session 文件

如无参数：
1. 检查 `~/.claude/session-data/`
2. 选择最近修改的 `*-session.tmp` 文件
3. 如无文件：
   ```
   No session files found in ~/.claude/session-data/
   Run /session-save at the end of a session to create one.
   ```
   然后停止。

如有参数：
- `YYYY-MM-DD` 格式 → 搜索对应日期的 session 文件
- 文件路径 → 直接读取

### Step 2: 加载工作流状态

```bash
# 搜索 session 文件所在项目的 .workflow-state.json
test -f orch-spec/*/.workflow-state.json && echo "Workflow state found" || echo "No workflow state"
```

如找到工作流状态文件，读取当前 stage、已完成步骤、待办步骤和 HARD-GATE 状态。

### Step 3: 读取完整 session 文件

读取完整文件内容。不要先总结。

### Step 4: 结构化汇报

```
SESSION LOADED: {file path}
═══════════════════════════════════════
WORKFLOW STATE: {path to .workflow-state.json}

PROJECT: {project name}
CURRENT STAGE: {spec | test-design | design | ...}
PROGRESS: {X/Y stages completed}

WHAT WE'RE BUILDING:
{2-3 句总结}

CURRENT STATE:
PASS: Working: {N} items confirmed
In Progress: {files in progress}
Not Started: {planned but untouched}

WHAT NOT TO RETRY:
{每个失败的方法及其原因}

HARD-GATE STATUS:
GATE            STATUS
spec-done       [PASS/FAIL/PENDING]
design-done     [PASS/FAIL/PENDING]
test-pass       [PASS/FAIL/PENDING]
archive-ready   [PASS/FAIL/PENDING]

WORKFLOW NEXT:
{下一步要调用的 Skill}

OPEN QUESTIONS / BLOCKERS:
{blockers}

NEXT STEP:
{exact next step}
═══════════════════════════════════════
Ready to continue. What would you like to do?
```

### Step 5: 等待用户

不自动开始工作。不触碰任何文件。等待用户指示。

如果 session 文件中明确定义了下一步，用户说"继续"或"yes" → 执行该步骤。

如未定义 → 询问用户从哪里开始。

## 边界情况

**多个 session 文件同一天**: 加载最近修改的。

**引用的文件已不存在**: 汇报时警告：`WARNING: path/to/file 在 session 中有引用但磁盘上不存在。`

**session 文件超过 7 天**: `WARNING: 此 session 来自 {N} 天前，内容可能已过时。`

**工作流状态不同步**: `WARNING: .workflow-state.json 的状态与 session 文件不匹配（state: {X}, session: {Y}）。建议手动检查。`

**session 文件为空或格式错误**: `Session file found but appears empty or unreadable.`

## 与 workflow 中断恢复的关系

`workflow` 通过 `.workflow-state.json` 实现自动中断恢复：

```
workflow 启动
    → 检测 .workflow-state.json 是否存在
    → 如存在，读取 last_completed_stage
    → 自动从下一 stage 继续（无需用户干预）
```

`/session-resume` 提供**人工驱动**的恢复路径——用户在非编排场景下手动恢复到之前的工作状态。两者互补。
