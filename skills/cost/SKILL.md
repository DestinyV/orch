---
name: cost
description: |
  从本地 SQLite 数据库查询 Claude Code Token 用量、花费和预算。
  TRIGGER when: 用户询问花费/用量/token/budget/昨日对比/按项目成本分析。
  数据来自 Stop hook 自动采集（JSONL + SQLite 双写），零外部依赖。
---

# Cost Tracking

查询 Claude Code 成本和用量历史。数据由 Stop hook（`cost-tracker.js`）在每次响应后自动从 transcript 采集并写入本地数据库。

## 数据源（按优先级）

| 来源 | 路径 | 说明 |
|------|------|------|
| **orch 本地 DB** | `~/.claude/orch-costs/usage.db` | Stop hook 自动采集，写入即用 |
| **orch 原始流水** | `~/.claude/orch-costs/costs.jsonl` | JSONL 格式，零依赖兜底 |
| **社区 cost-tracker** | `~/.claude-cost-tracker/usage.db` | 兼容社区插件，若存在则自动回退 |

## 工作原理

```bash
# 步骤1: 确认 DB 存在
test -f ~/.claude/orch-costs/usage.db && echo "orch DB found"
test -f ~/.claude-cost-tracker/usage.db && echo "community DB found"

# 步骤2: orch DB 优先，社区 DB 回退
```

## 查询示例

### 今日汇总

```bash
# orch 本地 DB
sqlite3 ~/.claude/orch-costs/usage.db "
  SELECT
    '今日: $' || ROUND(COALESCE(SUM(CASE WHEN date(timestamp) = date('now') THEN cost_usd END), 0), 4) ||
    ' | 总计: $' || ROUND(COALESCE(SUM(cost_usd), 0), 4) ||
    ' | 调用: ' || COUNT(*) ||
    ' | 会话: ' || COUNT(DISTINCT session_id)
  FROM usage;
"
```

### 按项目成本

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  SELECT project, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS calls,
         SUM(input_tokens) AS input_tok, SUM(output_tokens) AS output_tok
  FROM usage
  GROUP BY project
  ORDER BY cost DESC;
"
```

### 按工作流阶段

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  SELECT stage, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS calls
  FROM usage
  WHERE stage != ''
  GROUP BY stage
  ORDER BY cost DESC;
"
```

### 按模型

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  SELECT model, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS calls,
         SUM(input_tokens) AS input, SUM(output_tokens) AS output
  FROM usage
  GROUP BY model
  ORDER BY cost DESC;
"
```

### 最近 7 天趋势

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  SELECT date(timestamp) AS date, ROUND(SUM(cost_usd), 4) AS cost,
         COUNT(*) AS calls, COUNT(DISTINCT session_id) AS sessions
  FROM usage
  GROUP BY date(timestamp)
  ORDER BY date DESC
  LIMIT 7;
"
```

### 会话明细

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  SELECT session_id,
    MIN(timestamp) AS started,
    MAX(timestamp) AS ended,
    ROUND(SUM(cost_usd), 4) AS cost,
    COUNT(*) AS calls,
    SUM(input_tokens) AS input_tok,
    SUM(output_tokens) AS output_tok
  FROM usage
  GROUP BY session_id
  ORDER BY started DESC
  LIMIT 10;
"
```

## 无 DB 时的回退策略

两种 DB 都不存在时：

1. 告知用户 cost-tracker 未运行（Stop hook 未触发过）
2. 建议运行任意 workflow 阶段产生一条记录
3. 不编造数据，不硬编码定价

## 约束

- 优先使用 `cost_usd` 列（source of truth），不手动计算价格
- 数据库不存在时不编造数据
- 不硬编码模型定价（定价表仅在 hook 中用于估算，DB 中的 `cost_usd` 是已计算值）
