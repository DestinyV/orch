---
description: 生成 Claude Code 成本报告。从本地 cost SQLite 数据库查询用量、花费和趋势。
argument-hint: "[csv]"
---

# Cost Report Command (SDD+TDD 适配版)

查询本地 cost 数据库并呈现花费报告，按天、项目、工具和会话维度。与 orch 的 `cost` skill 深度集成。

## 先决条件

```bash
command -v sqlite3 >/dev/null && echo "sqlite3 available" || echo "sqlite3 missing"
test -f ~/.claude/orch-costs/usage.db && echo "Database found" || echo "Database not found"
```

数据库缺失告知用户成本追踪未配置，建议安装可信的 Claude Code 成本追踪 hook/plugin。

**唯一权威路径**：`~/.claude/orch-costs/usage.db`（由 `scripts/lib/cost-db.js` 写入）。

## 预期表结构

| 列 | 说明 |
| ----- | ------- |
| `timestamp` | ISO 时间戳 |
| `project` | 项目名 |
| `tool_name` | 工具或事件名 |
| `input_tokens` | 输入 token 数 |
| `output_tokens` | 输出 token 数 |
| `cost_usd` | USD 预计算成本 |
| `session_id` | 会话 ID |
| `model` | 模型 |

优先使用 `cost_usd` 避免手动计算（价格和缓存定价经常变化）。

## 查询

### 摘要

```bash
sqlite3 -header -column ~/.claude/orch-costs/usage.db "
  SELECT
    ROUND(COALESCE(SUM(CASE WHEN date(timestamp) = date('now') THEN cost_usd END), 0), 4) AS today_cost,
    ROUND(COALESCE(SUM(CASE WHEN date(timestamp) = date('now', '-1 day') THEN cost_usd END), 0), 4) AS yesterday_cost,
    ROUND(COALESCE(SUM(cost_usd), 0), 4) AS total_cost,
    COUNT(*) AS total_calls,
    COUNT(DISTINCT session_id) AS sessions
  FROM usage;
"
```

### 按项目

```bash
sqlite3 -header -column ~/.claude-cost-tracker/usage.db "
  SELECT project, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS calls
  FROM usage
  GROUP BY project
  ORDER BY cost DESC;
"
```

### 按工具

```bash
sqlite3 -header -column ~/.claude-cost-tracker/usage.db "
  SELECT tool_name, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS calls
  FROM usage
  GROUP BY tool_name
  ORDER BY cost DESC;
"
```

### 最近 7 天

```bash
sqlite3 -header -column ~/.claude-cost-tracker/usage.db "
  SELECT date(timestamp) AS date, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS calls
  FROM usage
  GROUP BY date(timestamp)
  ORDER BY date DESC
  LIMIT 7;
"
```

### CSV 导出

```bash
sqlite3 -csv -header ~/.claude-cost-tracker/usage.db "
  SELECT timestamp, project, tool_name, input_tokens, output_tokens, cost_usd, session_id, model
  FROM usage
  ORDER BY timestamp DESC
  LIMIT 100;
"
```

## SDD+TDD 工作流成本追踪

SDD+TDD 工作流通过 `cost` skill 在每个阶段完成后记录 Token 用量和花费到数据库：

| 阶段 | 预期 Token 范围 | 累计比例 |
|------|----------------|---------|
| spec | 10K-20K | ~10% |
| test-design + design | 10K-20K | ~20% |
| task | 5K-10K | ~25% |
| execute | 50K-100K | ~65% |
| test | 20K-40K | ~85% |
| archive + continuous-learning | 10K-20K | ~100% |

各项目/工具成本可在数据库中通过 `project = 'orch'` 过滤。

## 报告格式

1. **摘要**: today, yesterday, total, calls, sessions
2. **按项目**: 各项目按总成本排名
3. **按工具**: 各工具按总成本排名
4. **最近 7 天**: 日期、成本、调用次数

使用 4 位小数显示 <$1 金额。依赖预计算的 `cost_usd`，不从原始 token 估算价格。
