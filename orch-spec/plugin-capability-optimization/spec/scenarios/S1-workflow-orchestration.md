# 场景: S1 工作流编排引擎优化

**优先级**：高
**相关场景**：S4（TDD 闭环）、S5（Hooks 激活）
**场景间依赖**：
- depends-on: 无
- provides-to: S4（门控完整支撑 TDD 闭环）、S5（hook 激活支撑编排）

---

## 场景描述

优化工作流编排引擎的核心能力：阶段门控完整性、中断恢复的自动补偿、HARD-GATE 校验完备。确保编排层在不限制模型能力的前提下（北极星原则），提供更可靠的流程保障。

---

## 前置条件

- 插件 v0.10.0 已安装
- hooks/hooks.json 存在
- 探索审计已定位薄弱环节（F9/F10）

---

## Case 1: workflow-gate 产出校验覆盖全部阶段

**目标**：修复 F10 —— STAGE_OUTPUTS 仅覆盖 0/1/4/7 四阶段，补齐 3.5/5/6/9

**WHEN**
```
- workflow-gate.js 执行 PostToolUse 校验
- 当前阶段为 3.5(contract) / 5(execute) / 6(test) / 9(continuous-learning) 之一
- 该阶段缺少应有的产出文件
```

**THEN**
```
- 触发 HARD-GATE 告警（fail-open 不阻断，但记录 warning）
- 输出缺失的产出文件路径清单
- 与 stage-gate.js 的 SKILL_PREREQUISITES 对称
```

**数据**：
```json
{
  "stage": "5_execute",
  "expected_outputs": ["execution-report.md"],
  "missing": ["execution-report.md"],
  "gate": "fail-open"
}
```

**备注**：补齐 STAGE_OUTPUTS 覆盖 contract/execute/test/continuous-learning 阶段。

---

## Case 2: 中断恢复的自动补偿动作

**目标**：从"仅提示"升级为"自动补偿"——session-start 检测到未完成工作流时，不仅提示，还自动尝试恢复

**WHEN**
```
- 新会话启动
- session-start.js 检测到 .workflow-state.json 存在且 status=in_progress
- 最后完成阶段为 N，未完成阶段为 N+1
```

**THEN**
```
- 输出恢复建议：从阶段 N+1 续接
- 检查 N+1 前置产出是否齐全
- 产出缺失 → 提示具体缺失文件；产出齐全 → 建议直接 Skill 续接
- 不静默继续（北极星原则：模型自主决策，但提供完整信息）
```

**数据**：
```json
{
  "last_done_stage": 5,
  "next_stage": 6,
  "prereq_ok": true,
  "action": "resume-from-6"
}
```

---

## Case 3: 阶段门控的北极星原则审查

**目标**：确认所有 GATE 约束不限制模型能力，只约束流程正确性

**WHEN**
```
- 审查 stage-gate.js 的 SKILL_PREREQUISITES 与 workflow 的 GATE 定义
- 检查是否有"过度约束"（限制模型思考深度/探索自由/创造性）
```

**THEN**
```
- 识别并列出所有"能力限制型"约束
- 将仅约束流程顺序/产出存在的约束保留
- 将限制思考深度/探索的约束降级为建议
- 输出审查结论到 business-rules.md
```

**备注**：北极星原则落地审查，后续所有优化场景共用此检查。

---

## Case 4: 异常情况 — stage-gate 读 stdin 无超时

**目标**：修复 stage-gate.js 阻塞 readFileSync(fd) 无超时问题（与 stdin.js 的 2s 超时防护不一致）

**WHEN**
```
- PreToolUse hook 触发 stage-gate.js
- stdin 数据迟迟未到
- 无超时保护 → 阻塞挂起
```

**THEN**
```
- 引入超时防护（复用 scripts/lib/stdin.js 的 2s 超时模式）
- 超时后 fail-open 继续（不阻断 Skill 调用）
- 记录 timeout 事件
```

---

## Case 5: 异常情况 — 命令/Skill 命名空间混用

**目标**：修复 F9 —— EXEMPT_SKILLS 混入 7 个命令名

**WHEN**
```
- 审查 stage-gate.js 的 EXEMPT_SKILLS 数组
- 发现 checkpoint/code-review/plan/quality-gate/session-resume/session-save/start-dev 等命令名
```

**THEN**
```
- 分离 EXEMPT_SKILLS（Skill 名）与 EXEMPT_COMMANDS（命令名）
- 消除命名空间歧义
- 更新注释说明
```

---

## 验证清单

- [ ] STAGE_OUTPUTS 覆盖全部 8 个阶段
- [ ] 中断恢复有自动补偿动作
- [ ] GATE 审查无能力限制型约束
- [ ] stage-gate stdin 有超时防护
- [ ] 命令/Skill 命名空间分离

---

## TEST-VERIFY（可测试的验收标准）

- [ ] 应校验 workflow-gate.js 中 STAGE_OUTPUTS 包含 3.5/5/6/9 阶段产出定义
- [ ] 应模拟 in_progress 状态，验证 session-start.js 输出自动补偿建议
- [ ] 应审查全部 GATE 约束，无一条限制模型思考深度
- [ ] 应模拟 stdin 阻塞，验证 stage-gate.js 在 2s 后 fail-open
- [ ] 应校验 EXEMPT_SKILLS 仅含 Skill 名，命令名已分离

### Mock Data

**有效输入**：
```json
{ "stage": "6_test", "expected": ["testing-report.md"] }
```

**边界值**：
```json
{ "stage": "9_cl", "expected": ["learnings.md", "completion-report"] }
```

**特殊值**：
```json
{ "stage": "unknown", "expected": "fail-open" }
```
