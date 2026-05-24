---
name: cost-tracking
description: |
  从本地 SQLite 数据库查询 Claude Code Token 用量、花费和预算。
  TRIGGER when: 用户询问花费/用量/token/budget/昨日对比/按项目成本分析。
  预期用户在 `~/.claude-cost-tracker/usage.db` 已有成本追踪 hook 或插件写入行。
origin: community
---

# Cost Tracking

分析 Claude Code 成本和用量历史。

## When to Use

- 用户询问"花费了多少"、"这个会话花了多少钱"、"Token用量"
- 需要按项目/工具/日期查看成本分析

## How It Works

查询本地 SQLite 数据库 `~/.claude-cost-tracker/usage.db`，通过 sqlite3 执行聚合查询。
优先使用 `cost_usd` 列（source of truth），不手动计算价格。

## 先决条件

```bash
command -v sqlite3 >/dev/null && echo "sqlite3 available" || echo "sqlite3 missing"
test -f ~/.claude-cost-tracker/usage.db && echo "Database found" || echo "Database not found"
```

数据库缺失时不要编造数据。告知用户成本追踪未配置，建议安装可信的成本追踪 hook/plugin。

## 预期表结构

| Column | Meaning |
| ------ | ------- |
| `timestamp` | ISO 时间戳 |
| `project` | 项目名称 |
| `tool_name` | 工具或事件名 |
| `input_tokens` | 输入 token 数 |
| `output_tokens` | 输出 token 数 |
| `cost_usd` | USD 预计算成本 |
| `session_id` | 会话 ID |
| `model` | 模型 |

优先使用 `cost_usd`，而非手动计算价格（价格和缓存定价经常变化）。

## 查询示例

### 快捷摘要

```bash
sqlite3 ~/.claude-cost-tracker/usage.db "
  SELECT
    'Today: $' || ROUND(COALESCE(SUM(CASE WHEN date(timestamp) = date('now') THEN cost_usd END), 0), 4) ||
    ' | Total: $' || ROUND(COALESCE(SUM(cost_usd), 0), 4) ||
    ' | Calls: ' || COUNT(*) ||
    ' | Sessions: ' || COUNT(DISTINCT session_id)
  FROM usage;
"
```

### 按项目

```bash
sqlite3 -header -column ~/.claude-cost-tracker/usage.db "
  SELECT project, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS calls
  FROM usage GROUP BY project ORDER BY cost DESC;
"
```

### 按工具

```bash
sqlite3 -header -column ~/.claude-cost-tracker/usage.db "
  SELECT tool_name, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS calls
  FROM usage GROUP BY tool_name ORDER BY cost DESC;
"
```

### 最近 7 天

```bash
sqlite3 -header -column ~/.claude-cost-tracker/usage.db "
  SELECT date(timestamp) AS date, ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS calls
  FROM usage GROUP BY date(timestamp) ORDER BY date DESC LIMIT 7;
"
```

### 会话钻取

```bash
sqlite3 -header -column ~/.claude-cost-tracker/usage.db "
  SELECT session_id, MIN(timestamp) AS started, MAX(timestamp) AS ended,
    ROUND(SUM(cost_usd), 4) AS cost, COUNT(*) AS calls
  FROM usage GROUP BY session_id ORDER BY started DESC LIMIT 10;
"
```

## 报告指南

包含：
1. 今日花费 vs 昨日
2. 总计花费
3. 按项目排名的 Top 项目
4. 按工具排名的 Top 工具
5. 会话数和平均成本/会话

金额格式化：小金额 4 位小数，大金额 2 位。

## 反模式

- 有 `cost_usd` 时不要从原始 tokens 估算
- 不要假设数据库存在而不检查
- 不要在大数据库上运行无限制的 `SELECT *`
- 不要在面向用户的回答中硬编码当前模型定价
- 不要推荐安装未审查的 hook/plugin

## 集成

与 `token-budget-advisor` 配合：成本上下文 + 深度控制 → 更精确的预算管理。
与 `context-budget` 配合：审计出膨胀组件后，追踪其实际花费。

## 关键约束

- ✅ 优先使用 `cost_usd` 列（source of truth）
- ❌ 数据库不存在时不编造数据
- ❌ 不硬编码模型定价


## Output

成本查询结果（今日/总计/按项目/按工具/按日期的 SQL 查询输出）。

## Constraints

- 优先使用 `cost_usd` 列（source of truth）
- 数据库不存在时不编造数据
- 不硬编码模型定价

<HARD-GATE>数据库不存在时不编造数据 | 优先使用 cost_usd 列 | 不硬编码定价</HARD-GATE>