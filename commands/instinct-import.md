---
description: 从 JSON 文件导入进化规则。合并到 optimization.rules[]，按 rule_id 去重。
argument-hint: "<path>"
---

# Instinct Import — 规则导入

从外部 JSON 文件导入进化规则到 `orch-spec/user-preferences/preferences.json → optimization.rules[]`。

## 执行流程

1. 验证导入文件格式（必须含 `rules[]` 数组或直接为规则数组）
2. 按 `rule_id` 去重（已存在的规则跳过，除非 `--force`）
3. 合并到 preferences.json → optimization.rules[]
4. 标记所有导入规则的来源（`source: "imported"`）
5. 输出导入摘要

## 参数

- `path`（必填）：导入文件路径
- `--force`：覆盖已存在的同 ID 规则
- `--dry-run`：仅验证格式，不写入

## 导入格式

```json
{
  "rules": [
    {
      "id": "opt-001-auto",
      "status": "trial",
      "observation": { "source": "...", "metric": "...", "baseline": 0, "actual": 0, "deviation": 0 },
      "hypothesis": { "problem": "...", "root_cause": "..." },
      "action": { "type": "prompt_injection", "target": "...", "payload": "...", "injection_point": "..." },
      "evolution": { "confidence": 30, "applied_count": 0, "effective_count": 0, "ineffective_count": 0, "effectiveness_history": [], "last_effectiveness": 0 }
    }
  ]
}
```

## 输出

```
🧬 规则导入完成
  导入: {imported_count} 条
  跳过(重复): {skipped_count} 条
  覆盖: {overwritten_count} 条
  当前总数: {total_count} 条
```

## 安全约束

- <GATE>导入文件必须通过 JSON Schema 校验</GATE>
- <GATE>trial 状态规则（confidence < 30）导入后不参与注入，仅观察</GATE>
- 导入前自动备份 preferences.json → preferences.json.bak
- 不导入 status=archived 的规则（除非 `--include-archived`）
