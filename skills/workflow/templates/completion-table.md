# 工作流完成报告

步骤9（continuous-learning）完成后，LLM 按此模板生成最终报告。**所有数据从 .workflow-eval.json 读取，不编造。**

---

## 📋 流程执行总结

| # | 步骤 | Skill | Agent | 状态 | Token | 耗时(min) | 产出概要 |
|----|------|-------|-------|------|-------|----------|---------|
| 0 | 初始化 | workflow | — | `{status}` | `{tokens}` | — | project_mode=`{mode}` |
| 0.5 | 苏格拉底澄清 | clarify | clarifier | `{status}` / `跳过` | `{tokens}` | — | `{rounds}`轮, 模糊度降至 `{score}%` |
| 1 | Spec | spec | code-explorer | `{status}` | `{tokens}` | — | `{file_count}` 规范文档 |
| 2 | Test Design | test-design | test-designer | `{status}` | `{tokens}` | — | `{file_count}` 文件（spec+fixtures+templates） |
| 3 | Design | design | code-architect | `{status}` | `{tokens}` | — | 架构蓝图 |
| 3.5 | Contract | contract | contract-creator | `{status}` / `跳过(fullstack-only)` | `{tokens}` | — | `{api_count}` 接口, `{blocking}` blocking |
| 4 | Task | task | tasker | `{status}` | `{tokens}` | — | `{task_count}` 任务, `{batch}` 批次, DAG无环 |
| 5 | Execute | execute | executor | `{status}` | `{tokens}` | — | `{file_count}` 文件, 覆盖率达标 |
| 5.5 | Exception | exception | exception | `自动` / `—` | — | — | 异常处理代码生成 |
| 6 | Test | test | tester | `{status}` | `{tokens}` | — | `{test_count}` 测试通过, `{fail}` 失败 |
| 7 | Archive | archive | archiver | `{status}` | `{tokens}` | — | 已合并到主规范库 |
| 8 | Evaluation | evaluation | context-budget + cost | `{status}` | `{tokens}` | — | 诊断完成, deviation对比基线 |
| 9 | Continuous-Learning | continuous-learning | knowledge-curator | `{status}` | `{tokens}` | — | `{learnings_count}` learnings, `{rules}` 规则变化 |

| **总计** | `{completed}/{total}` 步 | — | `{agent_count}` Agents | — | **`{total_tokens}`** | **`{total_duration}`** | — |

<GATE>13 步全部列出。跳过步骤标 `—`。步骤8/9 不可省略。Token/耗时从 `.workflow-eval.json → stages[]` 读取。</GATE>

---

## 📊 效率评估

### Token 消耗分布
| 阶段 | Token | 占总量 | 基线Token | 偏差 | 诊断 |
|------|-------|--------|----------|------|------|
| spec | `{tokens}` | `{pct}%` | `{baseline}` | `{deviation}%` | `{diagnosis}` |
| design | `{tokens}` | `{pct}%` | `{baseline}` | `{deviation}%` | `{diagnosis}` |
| execute | `{tokens}` | `{pct}%` | `{baseline}` | `{deviation}%` | `{diagnosis}` |
| test | `{tokens}` | `{pct}%` | `{baseline}` | `{deviation}%` | `{diagnosis}` |
| archive | `{tokens}` | `{pct}%` | `{baseline}` | `{deviation}%` | `{diagnosis}` |

> 偏差 = (本轮 - 基线) / 基线 × 100%。正数=超标，负数=低于基线。数据来源：`.workflow-eval.json` vs `.workflow-baseline.json`。

### 关键指标
| 指标 | 本轮 | 基线 | 偏差 | 评级 |
|------|------|------|------|------|
| 总 Token | `{total}` | `{baseline_total}` | `{dev}%` | `{grade}` |
| 总耗时(min) | `{total_duration}` | `{baseline_duration}` | `{dev}%` | `{grade}` |
| HARD-GATE 触发 | `{count}` | `{baseline}` | `{dev}%` | `{grade}` |
| 用户干预 | `{count}` | `{baseline}` | `{dev}%` | `{grade}` |
| 综合评分 | — | — | — | `{score}/100` |

### 瓶颈分析
- `{bottleneck_1}` — 来源: `diagnosis.bottlenecks[]`
- `{bottleneck_2}` — 来源: `diagnosis.bottlenecks[]`

---

## 🧠 知识沉淀

### 本次学习 (`{count}` 条)
- [用户纠正] `{learning}` — 写入 `preferences.json → always_check[]`
- [项目约定] `{learning}` — 写入 `context/learnings.md`
- [效率发现] `{learning}` — 写入 `preferences.json → optimization.rules[]`

> 数据来源：`.workflow-eval.json → learnings[]`

### 优化规则变化
| 规则ID | 变化 | 置信度 | 说明 |
|--------|------|--------|------|
| `{rule_id}` | `{action}` | `{old}→{new}` | `{reason}` |

> 数据来源：`preferences.json → optimization.rules[]`

---

## 🔧 下次优化建议

基于本轮 deviation 数据（`diagnosis.recommendations[]`）：

| 优先级 | 建议 | 数据依据 |
|--------|------|---------|
| ⚠️ 高 | `{recommendation}` | `{阶段} token偏差 {deviation}%, 基线 {baseline}` |
| 💡 中 | `{recommendation}` | `{阶段} HARD-GATE触发 {count}次, 基线 {baseline}` |
| ℹ️ 低 | `{recommendation}` | `{指标} {deviation}%, 接近正常范围` |

---

<GATE>此报告由 completion-table.md 模板生成。数据来源: .workflow-eval.json + .workflow-baseline.json + preferences.json。禁止手工编造数据或省略步骤8/9。</GATE>
