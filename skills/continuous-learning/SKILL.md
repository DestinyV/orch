---
name: continuous-learning
description: |
  知识复利引擎 — 从工作流执行记录中提取用户纠正、效率优化、质量模式、项目约定，沉淀到 orch-spec/ 供下次需求增强。

  输入：.workflow-eval.json
  输出：orch-spec/patterns/ + orch-spec/user-preferences/preferences.json
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
| design ADR 决策记录 | 架构决策 → 下次复用 | `patterns/architecture.md` |
| exception 阶段异常模式 | 项目异常规范 → 下次直接使用 | `preferences.json → exception_patterns` |
| project-context.md 技术栈 | 技术栈快照 → 跳过重复探索 | `preferences.json → tech_stack` |

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
    输出写入 orch-spec/patterns/ 和 orch-spec/user-preferences/preferences.json",
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

## 输出

- `orch-spec/patterns/` — 更新的模式文件（corrections/quality/testing/naming/architecture）
- `orch-spec/user-preferences/preferences.json` — 更新的 always_check[] + rejected_approaches[] + bottlenecks[] + task_sizing + concurrency
- `.workflow-eval.json`（更新）— learnings[] 字段已写入
- `.workflow-state.json`（更新）— status: completed

## 关键约束

<HARD-GATE>evaluation 未完成时禁止进入 continuous-learning</HARD-GATE>
<HARD-GATE>learnings[] 为空时不允许标记 status=completed</HARD-GATE>

✅ 必须：读取 eval.json diagnosis | 提取 learnings | 更新 preferences.json
❌ 禁止：跳过沉淀直接 completed | learnings[] 为空还标记完成
