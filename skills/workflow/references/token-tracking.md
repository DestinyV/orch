# Token 用量追踪

## 强制采集规则

1. **优先精确**：从 `usage` 字段提取，`accuracy` = `exact`
2. **兜底估算**：`字符数 × 0.25`，`accuracy` = `estimate`
3. **子 Agent**：通过 `TaskOutput` 返回结果提取

## 采集方法

| 数据源 | 获取方式 | 精确度 |
|--------|---------|--------|
| 主 Skill 调用 | API 响应 `usage` 字段；不可获取则字符估算 | exact/estimate |
| 子 Agent 调用 | Agent 返回结果中提取 Token（每个 Agent 调用后检查 `usage` 回传） | exact |
| 文件操作工具 | 主对话 usage 总量 - Agent 用量推算 | estimate |
| 兜底估算 | `字符数 × 0.25`（输入）、`字符数 × 0.25`（输出） | estimate±15% |

**采集时机**：每阶段完成后立即记录，写入 `.workflow-eval.json` 对应 stage 的 `tokens` 字段。无法获取精确值时填 `null` 并标注 `_note: "estimate"`。

## 诊断阈值

| 指标 | 警告 | 异常 |
|------|------|------|
| 单阶段 total > 100K | Token消耗偏高，考虑拆分 | 检查 Agent prompt 是否过长 |
| 子Agent output > 主模型 output | 子Agent返回内容过多 | 子Agent指令需收紧 |
| 全流程 total > 1M | 全流程Token预算超标 | 考虑 quick 模式 |
