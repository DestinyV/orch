---
name: ralph-loop
description: |
  自主 Agent 循环模式选择指南 — 带有质量门控、评估和恢复控制的连续自治 Agent 循环。
  TRIGGER when: 需要循环执行的任务场景、批量处理、持续集成/PR 控制、RFC 分解、探索性并行生成。
origin: community
---

# Continuous Agent Loop

自主 Agent 循环模式选择。在需要循环执行任务时选择合适的循环模式。

## When to Use

- 需要循环执行的任务场景（批量处理、持续集成/PR 控制）
- 需要 RFC 分解的大功能
- 探索性并行生成（多种方案比较）

## How It Works

从 5 种循环模式中选择：sequential（顺序执行） / continuous-pr（CI门控） / rfc-dag（DAG拓扑排序） / infinite（探索性并行） / **goal（迭代逼近目标型，新增）**。
每循环有明确退出条件和质量门控。goal 模式详见 [`references/goal-mode-protocol.md`](references/goal-mode-protocol.md)。

## 循环选择流程

```text
Start
  |
  +-- Need strict CI/PR control? -- yes --> continuous-pr
  |
  +-- Need RFC decomposition? -- yes --> rfc-dag
  |
  +-- Need exploratory parallel? -- yes --> infinite
  |
  +-- Need goal-driven iteration? -- yes --> goal（迭代逼近）
  |   （spec 含 @goal-adaptive / 用户明确指定）
  |
  +-- default --> sequential
```

## 循环模式

### Sequential（默认）

单步顺序执行，每步完成后进入下一步。

```
Loop: task → verify → next-task → verify → ...
```

**适合**: 有依赖关系的任务链、需要顺序验证的场景。
**质量门控**: 每步验证通过才继续。

### Continuous-PR（CI/PR 控制）

每次循环产生独立分支 + PR，通过 CI 门控后才合并。

```
Loop: branch → implement → PR → CI check → merge → next
```

**适合**: 需要严格代码审查的场景、多人协作项目。
**质量门控**: CI pipeline 必须通过，HARD-GATE 阻断失败。

### RFC-DAG（有向无环图分解）

将大任务拆解为 RFC，按 DAG 拓扑排序执行。

```
RFC decomposition → DAG batch 1 → DAG batch 2 → ... → merge
```

**适合**: 大功能拆解、多模块并行开发。
**质量门控**: 每批完成 harnes-audit。

### Infinite（探索性并行）

并行 spawn 多个 Agent，各自探索不同方案后择优。

```
Agent A (方案1) ─┐
Agent B (方案2) ─┼── eval → select best → merge
Agent C (方案3) ─┘
```

**适合**: 探索性研究、多种方案比较、原型验证。
**质量门控**: eval-harness 评估选择最优。

### Goal（迭代逼近目标型，新增）

适用于目标明确但路径不确定的任务。循环执行 `执行 → 评估 → 调整 → 再执行`，每次迭代计算量化的目标达成度，直到收敛。

```
Goal Baseline → Execute Batch → Evaluate → Adapt Plan → Loop or Exit
```

**适合**: 复杂需求需要多轮逼近、实现路径不明确、需要渐进式完善的场景。
**质量门控**: goal-evaluator 独立评分，@critical 验收标准 HARD-GATE fail-closed。
**退出条件**: goal_achieved >= 0.95 / max_iterations / consecutive stall。

详见 [`references/goal-mode-protocol.md`](references/goal-mode-protocol.md)。

## 推荐生产栈

1. RFC decomposition → `ralphinho-rfc-pipeline`
2. Quality gates → `/quality-gate`
3. Eval loop → `eval-harness`
4. Session persistence → `nanoclaw-repl`

## 失败模式

- 循环空转无可测量进展
- 相同根因的重复重试
- Merge queue stall
- 无限制升级导致的成本漂移

## 恢复策略

1. Freeze loop — 立即暂停循环
2. Run `/harness-audit` — 评估当前状态
3. Reduce scope — 缩减到失败单元
4. Replay — 以明确验收标准重放

## 与 orch 工作流集成

```
/start "批量处理 10 个需求"
  → workflow 检测到循环需求
  → 选择 sequential loop (有依赖) 或 infinite (无依赖)
  → 每需求：spec → design → ... → archive
  → 每轮验证 + 下一轮自动触发
  → 全部完成 → 输出摘要
```

## 关键约束

- ✅ 每循环必须有明确退出条件
- ✅ 失败必须可检测且可阻断
- ✅ 循环必须有进展指标（不空转）
- ❌ 不允许无限制循环（必须有硬限制）
- ❌ 不允许静默失败（每轮必须验证）


## Output

选定循环模式后的执行结果。

## Constraints

- 每循环必须有明确退出条件
- 失败必须可检测且可阻断
- 循环必须有进展指标（不空转）
- 不允许无限制循环（必须有硬限制）
- 不允许静默失败（每轮必须验证）

<GATE>每循环必须有退出条件 | 不允许无限制循环 | 不允许静默失败</GATE>