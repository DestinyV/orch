---
description: 生成 Claude Code 成本报告。从本地 cost SQLite 数据库查询用量、花费和趋势。
argument-hint: "[csv]"
---

# Cost Report Command (SDD+TDD 适配版)

查询本地 cost 数据库并呈现花费报告，按天、项目、模型和会话维度。与 orch 的 `cost` skill 深度集成。

## 数据库

orch 的 Stop hook (`cost-tracker.js`) 每次响应后把整个 transcript 重算成**累计值**写入一行（同一 session 会有多行累计快照）。因此跨行**不可直接 SUM**——否则会把同一会话的多个快照相加导致严重高估。正确做法是每个 session 取最新一行快照（`latest` 视图），再跨 session 聚合。

**唯一权威路径**：`~/.claude/orch-costs/usage.db`（由 `scripts/lib/cost-db.js` 写入，JSONL 兜底在 `~/.claude/orch-costs/costs.jsonl`）。

## 先决条件

```bash
command -v sqlite3 >/dev/null && echo "sqlite3 available" || echo "sqlite3 missing"
test -f ~/.claude/orch-costs/usage.db && echo "Database found" || echo "Database not found"
```

## 预期表结构

| 列 | 说明 |
| ----- | ------- |
| `timestamp` | ISO 时间戳 |
| `session_id` | 会话 ID（每 session 多行累计快照） |
| `project` | 项目名 |
| `stage` | 工作流阶段 |
| `model` | 模型 |
| `input_tokens` | 累计输入 token（截至该快照） |
| `output_tokens` | 累计输出 token（截至该快照） |
| `cache_write` | 累计缓存写 token |
| `cache_read` | 累计缓存读 token |
| `cost_usd` | USD 预计算成本（累计值，截至该快照） |

优先使用 `cost_usd` 避免手动计算（价格和缓存定价经常变化）。

## 查询

> 所有查询先取 `latest` 视图（每个 session 最新快照），再跨 session 聚合。这是修复 SUM 累加高估的关键。

### 摘要

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  WITH latest AS (
    SELECT * FROM usage WHERE rowid IN (
      SELECT MAX(rowid) FROM usage GROUP BY session_id
    )
  )
  SELECT
    ROUND(COALESCE(SUM(CASE WHEN date(timestamp) = date('now') THEN cost_usd END), 0), 4) AS today_cost,
    ROUND(COALESCE(SUM(CASE WHEN date(timestamp) = date('now', '-1 day') THEN cost_usd END), 0), 4) AS yesterday_cost,
    ROUND(COALESCE(SUM(cost_usd), 0), 4) AS total_cost,
    COUNT(*) AS sessions
  FROM latest;
"
```

### 按项目

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  WITH latest AS (
    SELECT * FROM usage WHERE rowid IN (SELECT MAX(rowid) FROM usage GROUP BY session_id)
  )
  SELECT project, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS sessions
  FROM latest
  GROUP BY project
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
         SUM(input_tokens) AS input_tok, SUM(output_tokens) AS output_tok
  FROM latest
  GROUP BY model
  ORDER BY cost DESC;
"
```

### 最近 7 天

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

### CSV 导出

```bash
sqlite3 -csv -header ~/.claude/orch-costs/usage.db "
  WITH latest AS (
    SELECT * FROM usage WHERE rowid IN (SELECT MAX(rowid) FROM usage GROUP BY session_id)
  )
  SELECT timestamp, project, stage, model, input_tokens, output_tokens,
         cache_write, cache_read, cost_usd, session_id
  FROM latest
  ORDER BY timestamp DESC
  LIMIT 100;
"
```

## SDD+TDD 工作流成本参考

| 阶段 | 预期 Token 范围 | 累计比例 |
|------|----------------|---------|
| spec | 10K-20K | ~10% |
| test-design + design | 10K-20K | ~20% |
| task | 5K-10K | ~25% |
| execute | 50K-100K | ~65% |
| test | 20K-40K | ~85% |
| archive + continuous-learning | 10K-20K | ~100% |

## 报告格式

1. **摘要**: today, yesterday, total, sessions
2. **按项目**: 各项目按总成本排名
3. **按模型**: 各模型按总成本排名
4. **最近 7 天**: 日期、成本、会话数

使用 4 位小数显示 <$1 金额。依赖预计算的 `cost_usd`，不从原始 token 估算价格。
