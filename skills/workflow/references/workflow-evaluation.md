# 工作流效果评估

## 评估维度

### 1. Skill 执行评估

| 指标 | 记录内容 | 诊断阈值 |
|------|---------|---------|
| 耗时 | 开始→结束时间 | >10min 标记慢 |
| 状态 | done/failed/skipped | failed → 检查前置依赖 |
| HARD-GATE触发 | 触发次数+类型 | >3次 → 前置条件设计问题 |
| 用户交互次数 | AskUserQuestion调用数 | >5次 → 需求不够清晰 |

### 2. Agent 派遣评估

| 指标 | 记录内容 | 诊断阈值 |
|------|---------|---------|
| 派遣次数 | Agent()调用数 | 0 → 主上下文替代Agent(反模式) |
| 成功率 | done/failed/retry | <80% → Agent定义问题 |
| 重试次数 | retry计数 | >2 → prompt或上下文不足 |
| 执行时长 | 派遣→返回时间 | >5min → 任务粒度过大 |

### 3. 流程效率评估

| 指标 | 计算方式 | 诊断阈值 |
|------|---------|---------|
| 总耗时 | 所有阶段耗时之和 | >60min → 优化流程 |
| 并行效率 | 并行阶段(both)/串行耗时 | <30% → 未充分利用并行 |
| 阻塞率 | 卡点等待/总耗时 | >20% → HARD-GATE过严 |
| 阶段跳过率 | skipped/total | >30% → 快速模式更合适 |

### 4. 质量指标

| 指标 | 来源 | 诊断阈值 |
|------|------|---------|
| 测试覆盖率 | execute/test | <85% → TDD执行不严格 |
| Agent派遣率 | 所有阶段 | <100% → 主上下文替代 |
| 审查通过率 | code-reviewer返回 | <70% → 代码质量基线问题 |
| 冲突率 | archiver返回 | >10% → 规范粒度或命名问题 |

## 诊断规则

### 卡点诊断
```
HARD-GATE触发≥3次 同一阶段 → 前置条件检查过严或requirement不完整
用户交互≥5次 全流程 → 需求描述不够清晰，建议补充细节重新执行
阶段耗时比例失衡(某阶段>总耗时50%) → 该阶段需重点优化
```

### Agent诊断
```
Agent重试≥2次 → 检查prompt完整性 + 上下文是否充足
Agent未派遣(派遣=0) → 反模式:主上下文替代Agent
Agent失败率≥50% → Agent定义文件需优化
```

### 流程诊断
```
并行阶段串行执行 → 未启用workflow自动并行
全阶段全量执行但project_mode=frontend → 跳过后端阶段更高效
standard模式下耗时<5min → 项目可能更适合quick模式
```

## 输出格式

评估报告写入 `orch-spec/{requirement_id}/.workflow-eval.json`:

```json
{
  "requirement_id": "{id}",
  "project_mode": "fullstack",
  "mode": "standard",
  "started_at": "ISO",
  "completed_at": "ISO",
  "total_duration_sec": 0,
  "stages": [
    {
      "stage": "spec",
      "skill": "spec",
      "status": "done",
      "duration_sec": 0,
      "hard_gate_triggers": 0,
      "user_interactions": 0,
      "agent": {
        "name": "code-explorer",
        "dispatched": true,
        "status": "done",
        "retries": 0,
        "duration_sec": 0
      }
    }
  ],
  "summary": {
    "stages_total": 0,
    "stages_done": 0,
    "stages_failed": 0,
    "stages_skipped": 0,
    "agents_dispatched": 0,
    "agents_success": 0,
    "agents_failed": 0,
    "hard_gates_total": 0,
    "user_interactions_total": 0
  },
  "diagnosis": {
    "bottlenecks": [],
    "warnings": [],
    "suggestions": []
  }
}
```
