# 工作流数据结构

## .workflow-state.json

流程状态追踪，路径 `orch-spec/{requirement_desc_abstract}/.workflow-state.json`：

```json
{
  "workflow": "orch",
  "requirement_id": "{requirement_desc_abstract}",
  "project_mode": "fullstack|frontend|backend",
  "mode": "standard|quick",
  "needs_database": true|false,
  "started_at": "ISO时间",
  "stages": {
    "spec": { "status": "done|failed|skipped", "completed_at": "...", "tokens": { "input": 0, "output": 0, "total": 0 } },
    "test-design": { "status": "done|failed|skipped", "completed_at": "...", "tokens": { "input": 0, "output": 0, "total": 0 } },
    "design": { "status": "done|failed|skipped", "completed_at": "...", "tokens": { "input": 0, "output": 0, "total": 0 } },
    "contract": { "status": "done|failed|skipped|not_applicable", "completed_at": "...", "tokens": { "input": 0, "output": 0, "total": 0 } },
    "task": { "status": "done|failed|skipped", "completed_at": "...", "tokens": { "input": 0, "output": 0, "total": 0 } },
    "execute": { "status": "done|failed|skipped", "completed_at": "...", "tokens": { "input": 0, "output": 0, "total": 0, "agent_tokens": {} } },
    "test": { "status": "done|failed|skipped", "completed_at": "...", "tokens": { "input": 0, "output": 0, "total": 0 } },
    "archive": { "status": "done|failed|skipped", "completed_at": "...", "tokens": { "input": 0, "output": 0, "total": 0 } }
  },
  "token_summary": {
    "total_input": 0,
    "total_output": 0,
    "grand_total": 0,
    "estimated_cost_usd": 0.00
  }
}
```

### 心跳扩展（execute 进行中）

```json
{
  "execute": {
    "status": "in_progress",
    "progress": { "completed": 3, "total": 8, "current_task": "..." },
    "last_heartbeat": "2026-05-16T10:30:00Z",
    "tokens": { "input": 0, "output": 0, "total": 0 }
  }
}
```

### 注入优化规则（步骤0.3 初始化后）

```json
{
  "injected_optimizations": [
    {
      "id": "opt-001",
      "rule_id": "tok-001",
      "injection_point": "execute_prompt",
      "injected_at": "ISO时间"
    }
  ]
}
```

## .workflow-eval.json

效果评估数据，路径同上。模板见 `../workflow/templates/eval-template.json`。

### 每阶段记录

```json
{
  "stage": "{stage}",
  "skill": "{skill-name}",
  "status": "done|failed|skipped",
  "started_at": "ISO时间",
  "completed_at": "ISO时间",
  "duration_sec": 0,
  "hard_gate_triggers": 0,
  "user_interactions": 0,
  "tokens": {
    "input": 0, "output": 0, "total": 0,
    "model": "模型名",
    "accuracy": "exact|estimate"
  },
  "agent": { "name": "...", "dispatched": true|false, "status": "done|failed|retry", "retries": 0, "duration_sec": 0 },
  "events": [],
  "issues": [],
  "user_actions": [],
  "retry_log": []
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `started_at` / `completed_at` | ✅ | ISO 时间戳 |
| `tokens.accuracy` | ✅ | `exact`（usage 提取）或 `estimate`（字符估算） |
| `events[]` | 可选 | Agent 派遣/完成/HARD-GATE/补偿事件 |
| `issues[]` | 可选 | 问题及处理结果 |
| `user_actions[]` | 可选 | AskUserQuestion 调用详情 |
| `retry_log[]` | 可选 | 重试历史 |
