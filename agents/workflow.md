---
name: workflow
description: 统一入口 + 流程编排。接收需求后自动编排所有下游 Skill 的执行顺序，支持模式自动检测、HARD-GATE 卡点管控、中断恢复。
---

# workflow

## 调用方式

通过 `Skill("orch:workflow", args="{requirement_desc}")` 调用。

<GATE>零预探索契约：被调用时禁止在此之前已执行任何文件读取、目录扫描或项目分析。需求来自 args 参数，项目探索由 spec 阶段(code-explorer)负责。</GATE>

## 输出

- `.workflow-state.json` — 状态追踪
- `.workflow-eval.json` — 效果评估 + Token 用量

## 约束

<GATE>禁止跳过阶段 | 禁止在正式流程前执行代码探索 | 禁止在调用前已读取过任何项目文件</GATE>

## 职责

- 接收需求 → 模式检测 → 串联所有 Skill → 状态追踪 → 卡点管控 → 偏差补偿 → 归档
- 详见 `skills/workflow/SKILL.md`
