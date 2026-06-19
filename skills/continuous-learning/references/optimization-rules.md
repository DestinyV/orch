# 自主进化规则引擎

## 设计哲学

**不预设优化方向**。引擎只负责：观察偏差 → 生成假设 → 验证效果 → 自然选择。

工作流执行的每一轮都会产生"偏差数据"（token 消耗异常、耗时异常、用户干预、hard-gate 触发、agent 重试等）。引擎从偏差中自动生成优化假设，下一轮验证，有效则强化，无效则淘汰。这是一个达尔文式的进化过程——优化的具体方向完全由执行数据驱动，而非人工预设。

```
每一轮工作流
    │
    ├─ 步骤8: evaluation → 偏差数据 {deviations}
    │
    ├─ 步骤9: 知识沉淀
    │     ├─ 读取前 N 轮偏差数据
    │     ├─ 匹配现有规则
    │     │    ├─ 匹配 → 更新频次
    │     │    └─ 不匹配 → 生成优化假设 (confidence=30)
    │     └─ 更新规则库
    │
    └─ 下一轮步骤0
          ├─ 加载规则 (confidence ≥ 30)
          ├─ 注入到工作流上下文
          ├─ 执行完成
          └─ 评估效果 → 更新 confidence
```

---

## 规则数据模型

每条规则只有一个目的：**定义一个偏差模式和一个纠正动作**。

```json
{
  "rules": [
    {
      "id": "opt-{seq}-{auto|manual}",
      "status": "active|archived|trial",
      "created_at": "ISO",
      "last_updated": "ISO",

      "observation": {
        "source": "stage_token_ratio|stage_duration|user_intervention|hard_gate|agent_retry",
        "metric": "偏差涉及的指标名",
        "baseline": 0.0,
        "actual": 0.0,
        "deviation": 0.0
      },

      "hypothesis": {
        "problem": "自然语言描述观察到的偏差模式",
        "root_cause": "推测的根因"
      },

      "action": {
        "type": "prompt_injection|parameter_tuning|stage_skip|stage_merge|context_limit",
        "target": "作用目标（哪个阶段/哪个agent/哪个参数）",
        "payload": "具体的调整内容",
        "injection_point": "workflow_step0|spec_prompt|design_prompt|execute_prompt|review_prompt"
      },

      "evolution": {
        "confidence": 30,
        "applied_count": 0,
        "effective_count": 0,
        "ineffective_count": 0,
        "effectiveness_history": [],
        "last_effectiveness": 0.0
      }
    }
  ]
}
```

### 关键设计决策

**`observation` 是开放字段**。不限制 source 的类型，任何可以数值化的偏差都可以成为观测源。未来新增"git commit message 长度异常"也是合法的 observation。

**`action.type` 也是开放的**。当前支持 prompt_injection / parameter_tuning / stage_skip / stage_merge / context_limit，但可以随需求扩展。

---

## 进化回路

### 基础回路（每轮工作流执行一次）

```
Step 8:
  - 对比 baseline 和 actual 计算 deviation
  - deviation > threshold → 触发优化假设生成

Step 9:
  - 遍历所有 deviation
  - 检查是否已有匹配规则（同 source + 同 action type）
  - 有 → 更新频次 + 计算效果
  - 无 → 创建新规则 (confidence=30, status=trial)

下一轮 Step 0:
  - 加载 active 规则 (confidence ≥ 30)
  - 按 injection_point 分组 → 注入对应阶段
  - trial 规则 (confidence < 30) 不生效，仅跟踪

下一轮 Step 8:
  - 重新计算同 source 的 deviation
  - deviation 缩小 → application effective → confidence += 10
  - deviation 不变或扩大 → application ineffective → confidence -= 15
  - 连续 3 轮 ineffective → status = archived, 停止使用
```

### 置信度机制

| 事件 | confidence 变化 |
|------|----------------|
| 新规则创建 | 初始 30（trial） |
| 生效后偏差缩小 ≥ 20% | +15 |
| 生效后偏差缩小 < 20% | +5 |
| 生效后偏差不变 | -10 |
| 生效后偏差扩大 | -20 |
| 连续 3 轮 inactive（未触发） | -5/轮 |
| 超过 90 天未更新 | status = archived |
| status = trial + 连续 3 轮 deviation 仍然存在 | 转为 active（证明偏差模式稳定） |

### 自然选择

```
confidence ≥ 70 → 强规则，注入优先级最高
confidence 30-69 → 有效规则，正常注入
confidence 20-29 → trial 观察期，不生效但跟踪
confidence < 20 → archived，不再使用
archived 满 180 天 → 自动清理
```

---

## 优化假设自动生成

### 生成时机

步骤 9 知识沉淀时，knowledge-curator 读取所有 deviation，对每一条 deviation 执行：是否匹配现有规则？

### 生成策略（非硬编码）

knowledge-curator 的 prompt 包含以下指令：

```
你正在从工作流执行数据中发现优化机会。

分析目标：.workflow-eval.json

分析维度：
1. 任何偏离 baseline 的指标（token/耗时/hard-gate/用户干预/retry）
2. 偏差 > 20% 的指标 → 生成优化假设
3. 假设必须包含：观察到的现象 → 推测的根因 → 建议动作

你不需要事先知道"什么偏差是重要的"。所有偏差都是候选。
但是对于用户干预事件（events[].type=user_intervention），即使偏差 < 20% 也应分析。

输出格式：workflow 优化规则 JSON
```

---

## 优化规则注入系统

### 规则按 injection_point 分组

| injection_point | 注入时机 | 生效方式 |
|----------------|---------|---------|
| `workflow_step0` | 工作流步骤0 初始化后 | 调整批次/并行度/阶段选择 |
| `spec_prompt` | 步骤1 spec agent prompt | 追加检查项 / 调整 prompt 长度 |
| `design_prompt` | 步骤3 code-architect prompt | 追加检查项 |
| `execute_prompt` | 步骤5 executor prompt | 追加效率指令 / 调整读取策略 |
| `review_prompt` | code-reviewer prompt | 调整审查深度 |

### 注入原则

1. **静默注入**：规则注入到 prompt 中作为背景上下文，不主动弹窗
2. **可观测注入**：每轮注入的规则列表写入 `.workflow-eval.json` → `applied_optimizations[]`
3. **效果可追溯**：下一轮通过同 source 的 deviation 变化判断规则效果

---

## 工作流数据流

```
.workflow-eval.json
  ├── stages[].tokens         → token 偏差
  ├── stages[].duration_sec   → 耗时偏差  
  ├── stages[].hard_gate_triggers → 质量偏差
  ├── events[]                → 用户干预/纠正
  └── diagnosis.deviation     → 综合偏差
        ↓
knowledge-curator 分析
        ↓
orch-spec/user-preferences/preferences.json
  └── optimization.rules[]    ← 优化规则库
        ↓
下一轮 workflow 步骤0 加载
  └── applied_optimizations[] ← 本轮注入的规则
        ↓
执行完成 → steps[] 更新 → 重新计算 deviation → 闭环
```

---

## 进化示例（全自动，无硬编码）

### 示例 1: Token 优化被发现

```
Round 1: execute 阶段 tokens 消耗 120K，同类型项目 baseline 70K，deviation=71%
  → knowledge-curator 生成假设:
    "execute 阶段 token 消耗高于基线 71%，推测是每 Task 独立派遣 code-reviewer 导致"
  → 规则创建: confidence=30, action={type="stage_merge", target="code-reviewer", ...}

Round 2: 规则生效，code-reviewer 改为批次级派遣
  deviation 缩小到 20% → 有效! confidence += 15 → 45

Round 3: 继续生效，deviation 缩小到 5% → 有效! confidence += 15 → 60
```

### 示例 2: 用户纠正模式被发现

```
Round 1: design 阶段 user_intervention 3 次，其他阶段 0
  → knowledge-curator 生成假设:
    "design 阶段频发用户干预，推测是数据库设计规范未对齐"
  → 规则创建: confidence=30, action={type="prompt_injection", target="design_prompt", ...}

Round 2: design prompt 追加了数据库设计检查项，用户干预降到 1 次
  → deviation 缩小 66% → 有效! confidence += 15 → 45

Round 3: 用户干预 0 次 → 有效! confidence += 15 → 60
```

### 示例 3: 错误的假设被淘汰

```
Round 1: spec 阶段耗时异常高，生成假设 "spec prompt 过长"
  → 规则创建: confidence=30, action={type="context_limit", target="spec_prompt", ...}

Round 2: spec prompt 被截断，但导致 spec 产出质量下降（archive 冲突增多）
  → 负面效果! confidence -= 20 → 10 → archived
  → 该假设被自然淘汰
```
