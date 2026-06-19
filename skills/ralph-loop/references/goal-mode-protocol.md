# Goal 模式协议（迭代逼近目标型）

## 概述

适用于目标明确但路径不确定的任务。循环执行 `执行 → 评估 → 调整 → 再执行`，每次迭代都量化的目标达成度，直到收敛或达到上限。

## 触发条件

| 条件 | 说明 |
|------|------|
| spec 中包含 `@goal-adaptive` 标签 | 需求明确需要目标驱动迭代 |
| 用户步骤5 指定 goal 模式 | 手动启用 |
| Task 批次 > 3 且设计不确定性高 | 自动建议 |

## 核心循环

```
Step 1: Load Goal Baseline
  → 从 spec 提取 @critical 验收标准 → JSON 化目标矩阵
  → 初始化 goal-state.json

Step 2: Execute Batch
  → 按 tasks.md DAG 执行当前批次（executor ×N）
  → 标准 TDD 流程

Step 3: Evaluate Batch（goal-evaluator）
  → 独立运行验证命令（不信任 executor 报告）
  → 逐项评分目标达成度 0-100
  → 三维度进展指标：覆盖率 / 验收标准达成率 / 代码健康度
  → 交叉验证：随机抽取 2 个其他 executor 的测试运行在被评 Task 上

Step 4: Calculate Goal Achieved
  → goal_achieved = min(各项验收标准分数)
  → 单调递增检测：如果 goal_achieved 下降 → 标记为 regression
  
Step 5: Adapt Plan（if goal_achieved < 0.95 AND batches_used < max）
  → 识别未达标的验收标准
  → 拆分/合并/重排序 tasks.md 中的 Task
  → 为下一 batch 生成新的测试用例
  → 更新 goal-state.json

Step 6: Loop（回到 Step 2）OR Exit
  → goal_achieved >= 0.95 → 成功退出
  → batches_used >= max_iterations (默认 5) → AskUserQuestion
  → 连续 2 batch 无进展（goal_achieved 持平或下降） → 强制 adapt_plan
```

## 三维度进展指标

| 维度 | 指标 | 测量方法 |
|------|------|---------|
| **覆盖率**（quantitative） | 行/分支/函数覆盖率 | 覆盖率工具 raw output |
| **验收标准达成率**（semantic） | @critical 场景的逐项通过率 | goal-evaluator 独立运行测试 |
| **代码健康度**（trend） | 循环至当前回合的代码行数/复杂度变化趋势 | git diff --stat 和 cyclomatic complexity |

## 退出判断

```python
def should_exit(goal_state):
    # 成功退出
    if goal_state.goal_achieved >= 0.95:
        return "SUCCESS"
    # 失败退出
    if goal_state.batches_used >= goal_state.max_iterations:
        return "MAX_ITERATIONS"
    # 停滞退出
    if goal_state.consecutive_no_progress >= 2:
        return "STALLED"
    # 继续
    return "CONTINUE"
```

## 收敛保证

| 机制 | 实现 |
|------|------|
| 单调递增 | goal_achieved 允许平、不允许降。降意味着 regression，触发回退 |
| 停滞检测 | 连续 2 batch 无进展 → 强制拆分当前 Task |
| 最大迭代 | 默认 5 batch，超出 AskUserQuestion |
| 最小粒度 | Task 已经是单函数级别且仍无进展 → escalate 人工 |
| 收敛奖励 | evaluator 对"离目标更近"的进展给予正反馈 |

## HARD-GATE 模式

Goal 模式下 `@critical` 验收标准的 HARD-GATE 改为 **fail-closed**（阻断下一批次执行）：

```bash
# 在 workflow-gate.js 中，检测到 goal 模式时：
if (mode === 'goal' && event.type === 'hard_gate' && is_critical) {
    exit(1);  // fail-closed: 阻断执行
}
```

## goal-state.json 格式

```json
{
  "_meta": {
    "mode": "goal",
    "created_at": "2026-06-19T10:00:00Z",
    "max_iterations": 5
  },
  "goal_achieved": 0.0,
  "previous_goal_achieved": 0.0,
  "consecutive_no_progress": 0,
  "batches_used": 0,
  "acceptance_criteria": [
    {
      "id": "AC-001",
      "scene": "scenarios/order.md#INSUFFICIENT_STOCK",
      "score": 0.0,
      "threshold": 0.95,
      "last_batch_score": null
    }
  ],
  "current_plan": {
    "pending_tasks": ["Task-3", "Task-4"],
    "next_batch": ["Task-3"],
    "adapt_history": []
  },
  "batch_history": [
    {
      "batch": 1,
      "goal_achieved_before": 0.0,
      "goal_achieved_after": 0.4,
      "tasks_completed": ["Task-1", "Task-2"],
      "regressions": []
    }
  ]
}
```
