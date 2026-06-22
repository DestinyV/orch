---
description: 查看进化规则系统状态。展示 optimization.rules[] 的活跃规则、置信度分布、进化历史。
argument-hint: "[rule-id]"
---

# Instinct Status — 进化规则状态

查看 `orch-spec/user-preferences/preferences.json → optimization.rules[]` 的当前状态。

## 执行流程

1. 读取 preferences.json → optimization.rules[]
2. 按状态分组展示（active / trial / archived）
3. 统计各 injection_point 的规则分布
4. 可选：查看指定规则的进化历史

## 参数

- 无参数：总览模式（规则数量/状态分布/置信度分布/injection_point分布）
- `rule-id`：查看指定规则的完整 evolution 历史

## 输出格式

### 总览模式

```
🧬 进化规则引擎状态
━━━━━━━━━━━━━━━━━━━━
总规则数: {total}
  Active: {active_count} (置信度 ≥ 30，参与注入)
  Trial:  {trial_count} (置信度 < 30，观察中)
  Archived: {archived_count} (已淘汰)

📊 置信度分布
  强规则(≥70): {strong_count}
  有效(30-69): {effective_count}
  观察(<30):   {trial_count}
  已淘汰(<20): {archived_count}

🎯 注入点分布
  workflow_step0: {count} rules
  spec_prompt:     {count} rules
  design_prompt:   {count} rules
  execute_prompt:  {count} rules
  review_prompt:   {count} rules

📈 进化统计
  总应用次数: {total_applied}
  有效次数:   {total_effective}
  无效次数:   {total_ineffective}
  有效比:     {effectiveness_ratio}%
```

### 规则详情模式（指定 rule-id）

```
🧬 Rule: {rule_id}
  Status: {status}
  Confidence: {confidence} (initial: 30)
  创建: {created_at}
  更新: {last_updated}

  📋 Observation
    Source: {observation.source}
    Baseline: {observation.baseline} → Actual: {observation.actual}
    Deviation: {observation.deviation}%

  💡 Hypothesis
    Problem: {hypothesis.problem}
    Root Cause: {hypothesis.root_cause}

  ⚡ Action
    Type: {action.type}
    Target: {action.target}
    Injection: {action.injection_point}

  📈 Evolution
    Applied: {evolution.applied_count} times
    Effective: {evolution.effective_count} times
    Ineffective: {evolution.ineffective_count} times
    Effectiveness History: [{evolution.effectiveness_history}]
```

## 数据来源

`orch-spec/user-preferences/preferences.json → optimization.rules[]`

## 关键约束

- 仅读取，不修改规则
- preferences.json 不存在时提示"规则引擎未初始化，完成一次完整工作流后自动激活"
