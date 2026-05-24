---
description: 创建工作流检查点，与 .workflow-state.json 集成。支持创建/验证/列出 HARD-GATE 状态点。
argument-hint: "[create|verify|list] [name]"
---

# Checkpoint Command (SDD+TDD 适配版)

创建或验证 SDD+TDD 工作流中的检查点。与 `.workflow-state.json` 深度集成，提供状态持久化和 HARD-GATE 验证。

## 用法

```
/checkpoint [create|verify|list] [name]
```

## 与 .workflow-state.json 的集成

SDD+TDD 工作流在每个阶段完成后写入 `.workflow-state.json`。`/checkpoint` 在此之上提供显式命名检查点：

```
.workflow-state.json（系统自动记录阶段状态）
    └── /checkpoint（用户手动创建命名检查点）
         ├── git commit SHA
         ├── 测试覆盖率快照
         ├── 当前 stage 状态
         └── 环境信息
```

## 操作

### create — 创建检查点

1. 读取当前 `.workflow-state.json`，获取当前 stage
2. 运行快速验证：
   ```bash
   git diff --stat HEAD
   command -v npm && npm test 2>/dev/null
   ```
3. 创建 git stash 或 commit
4. 记录检查点到 `.claude/checkpoints.log`：
   ```bash
   echo "$(date +%Y-%m-%d-%H:%M) | $NAME | $(git rev-parse --short HEAD) | stage: $(jq -r '.stages[-1].name // "unknown"' .workflow-state.json 2>/dev/null)" >> .claude/checkpoints.log
   ```
5. 记录额外状态：
   - Git commit hash
   - 当前 stage（来自 `.workflow-state.json`）
   - 测试状态（通过/失败计数）
   - 覆盖率快照（如有）

### verify — 验证检查点

对照命名检查点验证当前状态：

1. 从 `.claude/checkpoints.log` 读取检查点
2. 对比当前状态：
   - 文件变更计数
   - 测试通过率变化
   - HARD-GATE 合规状态
   - Stage 进度（`.workflow-state.json` stages 数量变化）

3. 输出 HARD-GATE 验证报告：
   ```
   CHECKPOINT COMPARISON: $NAME
   ============================
   Files changed: +X / -Y
   Tests: +Y passed / -Z failed
   Stage: {from} → {to}
   HARD-GATE: [PASS/FAIL]
   Spec coverage: {current}%
   ```

### list — 列出检查点

```
Available checkpoints:
  NAME           TIMESTAMP            SHA       STAGE
  feature-start  2026-05-24-10:00    a1b2c3d   spec-creation
  core-done      2026-05-24-14:30    e5f6g7h   code-execute
```

## 工作流集成

```
[workflow-control] → /checkpoint create "workflow-start"
    ↓
[spec-creation] → /checkpoint create "spec-done"
    ↓
[code-design] → /checkpoint verify "spec-done"
    ↓
[code-test] → /checkpoint create "test-done"
    ↓
[spec-archive] → /checkpoint verify "workflow-start" --full
```

## 参数

`$ARGUMENTS`:
- `create <name>` — 创建命名检查点
- `verify <name>` — 验证命名检查点
- `list` — 列出所有检查点
- `clear` — 清理旧检查点（保留最近 5 个）
