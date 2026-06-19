# 工作流内微进化（Intra-Workflow Adaptation）

## 设计目标

在**单次工作流执行过程中**，基于已执行 batch 的 token/耗时/质量数据，动态调整剩余 batch 的执行策略。不等工作流末尾的 continuous-learning 来反馈——实时自适应。

## 触发检查点

步骤5 (execute) 的每个 batch 完成后插入微进化检查点：

```
Batch 1 完成
    │
    ├─ 检查点: 分析 Batch 1 执行数据
    │     ├─ token 消耗 vs 预估 → 超 150%？→ 启用输出摘要读取
    │     ├─ hard_gate 触发 ≥ 2？→ 暂缓下一 batch，调整 executor prompt
    │     ├─ code-reviewer 驳回率 > 30%？→ 追加约束到下一 batch executor
    │     ├─ 用户干预次数 ≥ 3？→ 暂停 AskUserQuestion 确认方向
    │     └─ 一切正常 → 继续下一 batch
    │
    ├─ 调整生效（只作用于剩余 batch，不影响已完成 batch）
    │
    └─ Batch 2 以调整后的策略执行 → Batch 2 完成 → 重复检查点
```

## 调整维度

| 调整 | 触发条件 | 动作 | 作用范围 |
|------|---------|------|---------|
| 输出摘要模式 | token 超标 > 150% | executor prompt 注入 `| tail -3` 强制 | 剩余所有 batch |
| 约束收紧 | hard_gate ≥ 2 | code-reviewer prompt 追加已知问题检查项 | 下一个 batch |
| 审查加速 | code-reviewer 驳回 > 30% | 启用批次级审查（单次批 diff 代替逐 Task 审查） | 下一个 batch |
| 方向纠正 | 用户干预 ≥ 3 | AskUserQuestion "方向是否正确？是否需要调整设计？" | 暂停，人工确认 |
| Task 拆分 | 某 Task 连续 2 次失败 | 自动将该 Task 拆分为 2 个子 Task | 下一个 batch |

## 注入方式

调整指令通过 `executor prompt` 追加实现，不在 agent 定义中写死：

```
# 原始 executor prompt
实现 Task-N，遵循 TDD 流程

# token 超标后追加
[微进化调整] 验证命令输出只用 `tail -3`，禁止全量读取
```
