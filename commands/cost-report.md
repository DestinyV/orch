---
description: 生成 Claude Code 成本报告。委托给 orch:cost skill 查询本地 cost SQLite 数据库。
argument-hint: "[csv]"
---

# Cost Report Command (轻量入口)

**委托执行**：本命令为轻量入口包装。实际查询逻辑由 `Skill("orch:cost")` 统一处理，避免 SQL 模板在 skill 和 command 间重复维护。

## 执行流程

1. 确认数据库：`test -f ~/.claude/orch-costs/usage.db || echo "DB_NOT_FOUND"`
2. DB 存在 → 调用 `Skill("orch:cost")`，传递用户意图（摘要/按项目/按模型/7天趋势/CSV导出）
3. DB 不存在 → 告知用户并建议运行任意 workflow 阶段触发 cost-tracker

## 参数

- 无参数：输出完整报告（摘要 + 按项目 + 按模型 + 最近7天 + SDD+TDD 工作流成本参考）
- `csv`：输出 CSV 格式最近100条记录

## 输出格式

1. **摘要**: today, yesterday, total, sessions
2. **按项目**: 各项目按总成本排名
3. **按模型**: 各模型按总成本排名
4. **最近 7 天**: 日期、成本、会话数
5. **SDD+TDD 工作流成本参考**（见 cost skill 中的参考表）

## SDD+TDD 工作流成本参考

| 阶段 | 预期 Token 范围 | 累计比例 |
|------|----------------|---------|
| spec | 10K-20K | ~10% |
| test-design + design | 10K-20K | ~20% |
| task | 5K-10K | ~25% |
| execute | 50K-100K | ~65% |
| test | 20K-40K | ~85% |
| archive + continuous-learning | 10K-20K | ~100% |

> 详细 SQL 查询模板、累计快照语义说明、DB 不存在时的回退策略见 `skills/cost/SKILL.md`。
