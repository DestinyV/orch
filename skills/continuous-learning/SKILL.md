---
name: continuous-learning
description: |
  知识复利引擎 + 自主进化系统 — 从工作流执行记录中提取用户纠正、效率优化、质量模式、项目约定，沉淀到 orch-spec/ 供下次需求增强。
  通过偏差分析自动生成优化假设，经多轮验证形成自进化闭环。

  输入：.workflow-eval.json
  输出：orch-spec/context/learnings.md + orch-spec/user-preferences/preferences.json + optimization rules
---

# continuous-learning — 知识复利引擎

## 职责

工作流完成后，从执行记录中提取可复用的知识，沉淀到 `orch-spec/`，增强下次需求。

## 何时使用

- 步骤8 evaluation 完成后自动触发
- 工作流归档完成后
- 需要从工作流中提取模式、沉淀知识

## 知识沉淀来源

从以下四个维度提取知识：

### 1. 用户纠正反馈

| 来源 | 沉淀内容 | 写入位置 |
|------|---------|---------|
| clarify 追问轮数(x轮) | 需求模糊领域 → 追加检查项 | `preferences.json → always_check[]` |
| AskUserQuestion 否决 | 被否决策 → 记录原因 | `preferences.json → rejected_approaches[]` |
| 用户手动修改代码文件 | 修改模式 → 常见错误 | `patterns/corrections.md` |

### 2. 流程效率

| 来源 | 沉淀内容 | 写入位置 |
|------|---------|---------|
| 某阶段耗时占总时长>50% | 瓶颈阶段 → 下回预分配更多资源 | `preferences.json → bottlenecks[]` |
| 同类型Task重复执行≥3次 | 最佳粒度 → Task拆分建议 | `preferences.json → task_sizing` |
| 并行阶段实际串行执行 | 并行无效 → 强制并行 | `preferences.json → concurrency` |

### 3. 质量模式

| 来源 | 沉淀内容 | 写入位置 |
|------|---------|---------|
| code-reviewer 高频问题 | 规则缺失 → rules/补充建议 | `patterns/quality.md` |
| test 阶段常见失败类型 | 测试模板不足 → test-design优化 | `patterns/testing.md` |
| archive 阶段冲突类型 | 命名约定不统一 → 规范优化 | `patterns/naming.md` |

### 4. 项目约定

| 来源 | 沉淀内容 | 写入位置 |
|------|---------|---------|
| design ADR 决策记录 | 架构决策 → 下次复用 | `context/learnings.md → ## 架构决策` |
| exception 阶段异常模式 | 项目异常规范 → 下次直接使用 | `preferences.json → exception_patterns` |
| project-context.md 技术栈 | 技术栈快照 → 跳过重复探索 | `preferences.json → tech_stack` |

### 5. 自主进化规则（自动发现，无需预设分类）

**不预设优化方向**。任何可数值化的偏差都是优化候选。

| 发现方式 | 判断逻辑 | 沉淀位置 |
|---------|---------|---------|
| Token 消耗偏离基线 > 20% | tokens_total 偏离同类型均值 → 生成优化假设 | `preferences.json → optimization.rules[]` |
| 阶段耗时偏离基线 > 20% | duration_sec 偏离基线 → 生成优化假设 | 同上 |
| 用户干预事件（不限阶段） | user_intervention 频繁 → 生成纠正假设 | 同上 |
| Hard-gate 触发频次偏离 | hard_gate_triggers 偏离 → 生成质量假设 | 同上 |
| Agent retry 偏离 | retries 偏离 → 生成上下文假设 | 同上 |

**所有偏差统一按 `deviation > 20%` 阈值触发，不存在预设的"重要偏差"清单。** |

## 工作流程

### 步骤1: 读取 eval.json

```bash
# 读取 diagnosis 诊断数据
python3 -c "
import json
eval_data = json.load(open('orch-spec/{req_id}/.workflow-eval.json'))
diag = eval_data.get('diagnosis', {})
print(json.dumps(diag, indent=2))
"
```

### 步骤2: 派遣 knowledge-curator

```bash
Agent(subagent_type="orch:knowledge-curator",
  prompt="知识复利提取：
    从 .workflow-eval.json 提取 learnings[]：
    1. events[] 中 type=user_intervention → 用户纠正
    2. stages[] 中耗时占比>50% → 瓶颈
    3. diagnosis 中覆盖率<85%/审查<80 → 质量问题
    4. design ADR + exception patterns → 项目约定
    输出写入 orch-spec/context/learnings.md 和 orch-spec/user-preferences/preferences.json",
  run_in_background=false)
```

```json
// 写入 eval.json → learnings[]
"learnings": [
  {
    "source": "用户纠正",
    "phase": "design",
    "trigger": "用户指出数据库主键应UNSIGNED",
    "action": "preferences.always_check追加: 主键BIGINT UNSIGNED",
    "ts": "2026-05-24T21:00Z"
  }
]
```

### 步骤3: 更新 preferences.json

```bash
python3 -c "
import json, os
prefs_path = 'orch-spec/user-preferences/preferences.json'
prefs = json.load(open(prefs_path)) if os.path.exists(prefs_path) else {}
prefs.setdefault('always_check', [])
prefs.setdefault('rejected_approaches', [])
# 从 learnings 合并
json.dump(prefs, open(prefs_path, 'w'), indent=2, ensure_ascii=False)
"
```

### 步骤4: 更新工作流状态

```bash
# 写入 .workflow-state.json
python3 -c "
import json
state = json.load(open('orch-spec/{req_id}/.workflow-state.json'))
state['current_stage'] = 'knowledge'
state['stages'].append({'stage': 'knowledge', 'status': 'done'})
state['status'] = 'completed'
json.dump(state, open('orch-spec/{req_id}/.workflow-state.json', 'w'), indent=2)
"
```

### 步骤5: 自主进化规则提取

> 详见 [`references/optimization-rules.md`](references/optimization-rules.md)

#### 步骤5a: 对比基线计算 deviation

```bash
# 将本轮执行数据 vs .workflow-baseline.json 对比
python3 -c "
import json, os
req = '{requirement_desc_abstract}'
eval_path = f'orch-spec/{req}/.workflow-eval.json'
baseline_path = 'orch-spec/context/.workflow-baseline.json'
if os.path.exists(eval_path) and os.path.exists(baseline_path):
    eval_data = json.load(open(eval_path))
    baseline = json.load(open(baseline_path))
    deviations = []
    for stage_record in eval_data.get('stages', []):
        sn = stage_record.get('stage', '')
        bl = baseline.get('stages', {}).get(sn, {})
        actual_tokens = stage_record.get('tokens_input', 0) + stage_record.get('tokens_output', 0)
        actual_duration = stage_record.get('completed_at', 0)
        if bl.get('avg_tokens', 0) > 0:
            t_dev = round((actual_tokens - bl['avg_tokens']) / bl['avg_tokens'] * 100, 1)
            d_dev = round((actual_duration - bl.get('avg_duration', 0)) / max(bl.get('avg_duration', 1), 1) * 100, 1)
            if abs(t_dev) > 20:
                deviations.append({'source': f'stage_token_{sn}', 'metric': 'tokens', 'deviation': t_dev, 'baseline': bl['avg_tokens'], 'actual': actual_tokens})
            if abs(d_dev) > 20:
                deviations.append({'source': f'stage_duration_{sn}', 'metric': 'duration', 'deviation': d_dev, 'baseline': bl.get('avg_duration', 0), 'actual': actual_duration})
    eval_data['diagnosis']['deviation'] = {'items': deviations, 'baseline_updated': baseline.get('project_level', {}).get('total_workflows', 0)}
    json.dump(eval_data, open(eval_path, 'w'), indent=2)
    print(f'[evaluate] Found {len(deviations)} deviations > 20%')
"
```

#### 步骤5b: 效果回测（E3）

对比注入的优化规则效果：本轮 deviation vs 上一轮同 source deviation：

```bash
python3 -c "
import json, os
req = '{requirement_desc_abstract}'
eval_path = f'orch-spec/{req}/.workflow-eval.json'
prefs_path = 'orch-spec/user-preferences/preferences.json'
if os.path.exists(eval_path) and os.path.exists(prefs_path):
    eval_data = json.load(open(eval_path))
    prefs = json.load(open(prefs_path))
    rules = prefs.get('optimization', {}).get('rules', [])
    applied = eval_data.get('applied_optimizations', [])
    current_deviations = {d['source']: d['deviation'] for d in eval_data.get('diagnosis', {}).get('deviation', {}).get('items', [])}
    for rule in rules:
        if rule.get('id') in applied:
            source = rule.get('observation', {}).get('source', '')
            current_dev = current_deviations.get(source, 0)
            prev_dev = rule.get('evolution', {}).get('last_effectiveness', 0)
            if prev_dev != 0 and current_dev != 0:
                diff = abs(current_dev) - abs(prev_dev)
                if diff < -20:  # improvement
                    rule['evolution']['confidence'] = rule['evolution'].get('confidence', 30) + 15
                    rule['evolution']['effective_count'] = rule['evolution'].get('effective_count', 0) + 1
                elif diff < 5:   # stable
                    rule['evolution']['confidence'] = rule['evolution'].get('confidence', 30) - 10
                else:            # worse
                    rule['evolution']['confidence'] = rule['evolution'].get('confidence', 30) - 20
                    rule['evolution']['ineffective_count'] = rule['evolution'].get('ineffective_count', 0) + 1
                rule['evolution']['last_effectiveness'] = current_dev
            # Archive if 3 consecutive ineffective
            if rule['evolution'].get('ineffective_count', 0) >= 3:
                rule['status'] = 'archived'
    json.dump(prefs, open(prefs_path, 'w'), indent=2)
    print(f'[evaluate] Updated confidence for {len(applied)} applied rules')
"
```

#### 步骤5c: 规则提取

从 `.workflow-eval.json` 的 deviations 中自动发现优化机会：

```bash
Agent(subagent_type="orch:knowledge-curator",
  prompt="自主进化规则提取：
    从 orch-spec/{req_id}/.workflow-eval.json 的 diagnosis.deviation 中：
    1. 遍历所有 deviation > 20% 的指标
    2. 对每个偏差，检查是否已有匹配的优化规则（同 observation.source）
    3. 有匹配 → 更新 evolution 字段（applied_count/effective_count）
    4. 无匹配 → 创建新优化假设（initial confidence=30, status=trial）
    5. 读取 events[] 中 type=user_intervention → 提取纠正模式
    6. events[].type=user_intervention 不受 deviation 阈值限制，全部分析
    7. 对连续 3 轮 ineffective 的规则标记 status=archived
    
    输出写入 orch-spec/user-preferences/preferences.json → optimization.rules[]
    规则格式详见 skills/continuous-learning/references/optimization-rules.md",
  run_in_background=false)
```

## 输出

- `orch-spec/context/learnings.md` — 更新的知识沉淀（用户纠正/效率/质量/项目约定）
- `orch-spec/user-preferences/preferences.json` — 更新的 always_check[] + rejected_approaches[] + bottlenecks[] + task_sizing + concurrency + **optimization.rules[]**
- `.workflow-eval.json`（更新）— learnings[] 字段已写入, applied_optimizations[] 已写入
- `.workflow-state.json`（更新）— status: completed

## 关键约束

<GATE>evaluation 未完成时禁止进入 continuous-learning</GATE>
<GATE>learnings[] 为空时不允许标记 status=completed</GATE>
<GATE>optimization.rules[] 中 trial 状态的规则（confidence<30）禁止注入工作流，仅在下一轮生效</GATE>

✅ 必须：读取 eval.json diagnosis | 提取 learnings | 更新 preferences.json | 提取优化规则
❌ 禁止：跳过沉淀直接 completed | learnings[] 为空还标记完成 | trial 规则注入工作流
