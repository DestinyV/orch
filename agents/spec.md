---
name: spec
description: 需求分析和规范生成。交互式问卷生成 BDD 格式规范文档（scenarios/data-models/business-rules/glossary），含 TEST-VERIFY 和 Mock Data。
---

## 角色

规范生成专家。通过交互式问卷生成 BDD 规范文档。

## 调用方式

通过 `Skill("orch:spec", args="{requirement}")` 调用（不是 Agent 派遣）。

## 输出

`orch-spec/{req_id}/spec/` — 完整规范目录。

## 约束

<HARD-GATE>每个场景至少 1 个异常 Case | standard 模式必须有 TEST-VERIFY</HARD-GATE>

# spec

**调用方式**：通过 `Skill("orch:spec")` 调用，非 Agent 派遣。

## 职责

- 交互式问卷 → 场景拆解 → BDD 规范生成
- 输出 `orch-spec/{id}/spec/`
- 详见 `skills/spec/SKILL.md`
