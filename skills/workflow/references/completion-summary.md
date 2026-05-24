# 完成摘要模板

步骤10 输出格式：

```
✅ SDD+TDD 工作流完成！
- 规范文档: spec-dev/{requirement_id}/spec/          [按状态]
- 设计方案: spec-dev/{requirement_id}/design/        [design done]
- 测试规范: spec-dev/{requirement_id}/tests/         [test-design done]
- 接口契约: spec-dev/{requirement_id}/contract/  [contract done]
- 任务清单: spec-dev/{requirement_id}/tasks/         [task done]
- 源代码:   src/                                     [execute done]
- 测试代码: tests/                                   [test done]
- 归档规范: spec-dev/spec/                           [archive done]
- 知识沉淀: skills/continuous-learning/patterns/     [continuous-learning done]

📊 耗时统计:
| 阶段 | 状态 | 耗时 | Token消耗 | Agent |
|------|------|------|-----------|-------|
| spec | ✅ | 2m | 12.5K in / 8.2K out | code-explorer ✅ |
| test-design | ✅ | 1m | 5.1K in / 3.8K out | test-designer ✅ |
| design | ✅ | 3m | 15.2K in / 10.1K out | code-architect ✅ |
...

💰 Token 汇总:
| 指标 | 总量 | 估算成本 |
|------|------|---------|
| 全流程输入 | XXXX | $X.XX |
| 全流程输出 | XXXX | $X.XX |
| **总计** | **XXXX** | **$X.XX** |

🔍 评估诊断:
⚠️ 瓶颈: execute阶段占总耗时45%（Token消耗占总量的60%），建议检查Task粒度
💡 建议: frontend项目可跳过exception（已跳过）
✅ Agent派遣率: 100% | 成功率: 100%
```
