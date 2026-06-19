---
name: cost
description: |
  从本地 SQLite 数据库查询 Claude Code Token 用量、花费和预算。
  TRIGGER when: 用户询问花费/用量/token/budget/昨日对比/按项目成本分析。
  数据来自 Stop hook 自动采集（JSONL + SQLite 双写），零外部依赖。
---

# Cost Tracking

查询 Claude Code 成本和用量历史。数据由 Stop hook（`cost-tracker.js`）在每次响应后自动从 transcript 采集并写入本地数据库。

## 数据源

| 来源 | 路径 | 说明 |
|------|------|------|
| **orch 本地 DB** | `~/.claude/orch-costs/usage.db` | Stop hook 自动采集，**唯一权威数据源** |
| **orch 原始流水** | `~/.claude/orch-costs/costs.jsonl` | JSONL 格式，零依赖兜底，DB 不可用时回退 |

## ⚠️ 累计快照语义（避免高估）

orch 的 `cost-tracker.js` 每次响应后把**整个 transcript 重算成累计值**写入一行。因此同一 `session_id` 会有多行，每行是该 session 截至该时刻的累计消耗。

**禁止跨行直接 `SUM(cost_usd)`** —— 那会把同一会话的多个快照相加，严重高估。

**正确做法**：先用子查询取每个 session 的最新一行（最新累计快照），再跨 session 聚合：

```sql
WITH latest AS (
  SELECT * FROM usage WHERE rowid IN (SELECT MAX(rowid) FROM usage GROUP BY session_id)
)
SELECT ... FROM latest ...
```

下文所有查询示例均遵循此模式。

## 工作原理

```bash
# 确认 DB 存在
test -f ~/.claude/orch-costs/usage.db && echo "orch DB found"
```

## 查询示例

### 今日汇总

```bash
sqlite3 ~/.claude/orch-costs/usage.db "
  WITH latest AS (
    SELECT * FROM usage WHERE rowid IN (SELECT MAX(rowid) FROM usage GROUP BY session_id)
  )
  SELECT
    '今日: $' || ROUND(COALESCE(SUM(CASE WHEN date(timestamp) = date('now') THEN cost_usd END), 0), 4) ||
    ' | 总计: $' || ROUND(COALESCE(SUM(cost_usd), 0), 4) ||
    ' | 会话: ' || COUNT(*)
  FROM latest;
"
```

### 按项目成本

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  WITH latest AS (
    SELECT * FROM usage WHERE rowid IN (SELECT MAX(rowid) FROM usage GROUP BY session_id)
  )
  SELECT project, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS sessions,
         SUM(input_tokens) AS input_tok, SUM(output_tokens) AS output_tok
  FROM latest
  GROUP BY project
  ORDER BY cost DESC;
"
```

### 按工作流阶段

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  WITH latest AS (
    SELECT * FROM usage WHERE rowid IN (SELECT MAX(rowid) FROM usage GROUP BY session_id)
  )
  SELECT stage, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS sessions
  FROM latest
  WHERE stage != ''
  GROUP BY stage
  ORDER BY cost DESC;
"
```

### 按模型

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  WITH latest AS (
    SELECT * FROM usage WHERE rowid IN (SELECT MAX(rowid) FROM usage GROUP BY session_id)
  )
  SELECT model, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS sessions,
         SUM(input_tokens) AS input, SUM(output_tokens) AS output
  FROM latest
  GROUP BY model
  ORDER BY cost DESC;
"
```

### 最近 7 天趋势

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  WITH latest AS (
    SELECT * FROM usage WHERE rowid IN (SELECT MAX(rowid) FROM usage GROUP BY session_id)
  )
  SELECT date(timestamp) AS date, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS sessions
  FROM latest
  GROUP BY date(timestamp)
  ORDER BY date DESC
  LIMIT 7;
"
```

### 会话明细

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  WITH latest AS (
    SELECT * FROM usage WHERE rowid IN (SELECT MAX(rowid) FROM usage GROUP BY session_id)
  )
  SELECT session_id,
    MIN(timestamp) AS started,
    MAX(timestamp) AS ended,
    ROUND(MAX(cost_usd), 4) AS cost,
    MAX(input_tokens) AS input_tok,
    MAX(output_tokens) AS output_tok
  FROM latest
  GROUP BY session_id
  ORDER BY ended DESC
  LIMIT 10;
"
```

> 单 session 明细中 `cost_usd` 本身已是累计值，取 `MAX`（最新快照）即可，不再 SUM。`ended` 比 `started` 更适合排序（最新活动会话排前）。

## 无 DB 时的回退策略

DB 不存在时：

1. 告知用户 cost-tracker 未运行（Stop hook 未触发过）
2. 回退到 `~/.claude/orch-costs/costs.jsonl` 逐行解析（最后一行即是该 session 最新累计值）
3. 建议运行任意 workflow 阶段产生一条记录
4. 不编造数据，不硬编码定价

## 约束

- 优先使用 `cost_usd` 列（source of truth），不手动计算价格
- **跨行查询必须先取每 session 最新快照（`MAX(rowid) GROUP BY session_id`），禁止直接 SUM 全表**
- 数据库不存在时不编造数据
- 不硬编码模型定价（定价表仅在 hook 中用于估算，DB 中的 `cost_usd` 是已计算值）
