# 自主优化知识复利 — 设计方案

## 目标

在工作流每一轮执行后，从 token 消耗数据和用户纠正行为中提取优化规则，沉淀到知识库，在下轮工作流中自动应用。

## 核心概念

**优化规则** = 从执行历史中提炼的可重复优化策略，包含触发条件 + 建议动作 + 置信度。

三条优化赛道：

| 赛道 | 数据来源 | 规则示例 |
|------|---------|---------|
| Token 效率 | stage token 消耗 + agent 派遣次数 | "简单 Task（<30行）跳过 REFACTOR" |
| 用户纠正 | events[type=user_intervention] 频次 | "数据库设计时自动检查主键 UNSIGNED" |
| 工作流调优 | 耗时占比 + hard_gate 触发频次 | "Task >3 批次自动启用 ralph-loop" |

---

## 改动清单

| 文件 | 动作 | 说明 |
|------|------|------|
| `skills/continuous-learning/SKILL.md` | 修改 | 增加自主优化维度（步骤5） |
| `skills/continuous-learning/references/optimization-rules.md` | **新建** | 优化规则格式定义 + 三条赛道详解 |
| `agents/knowledge-curator.md` | 修改 | 增加优化规则提取职责 |
| `skills/workflow/SKILL.md` | 修改 | 步骤0 加载优化规则注入上下文 |
| `skills/workflow/references/agent-dispatch-code.md` | 修改 | 步骤9 知识沉淀增加优化规则输出 |
| `skills/evaluation/SKILL.md` | 修改 | 步骤8 产出 token 效率分析 |
