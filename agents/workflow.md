---
name: workflow
description: 统一入口 + 流程编排。接收需求后自动编排所有下游 Skill 的执行顺序，支持模式自动检测、HARD-GATE 卡点管控、中断恢复。
---

# workflow-control

**调用方式**：通过 `Skill("orch:workflow")` 调用，非 Agent 派遣。

## 调用方式

通过 `Skill("orch:workflow", args="{requirement_desc}")` 调用（不是 Agent 派遣）。

## 输出

- `.workflow-state.json` — 状态追踪
- `.workflow-eval.json` — 效果评估 + Token 用量

## 约束

<HARD-GATE>禁止跳过阶段 | 禁止在正式流程前执行代码探索</HARD-GATE>

## 职责

- 接收需求 → 模式检测 → 串联所有 Skill → 状态追踪 → 卡点管控 → 偏差补偿 → 归档
- 详见 `skills/workflow/SKILL.md`
