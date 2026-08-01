# 场景: S3 Skills 指令优化

**优先级**：高
**相关场景**：S1（编排）、S5（Hooks）
**场景间依赖**：
- depends-on: 无
- provides-to: S4（Skills 完整支撑 TDD 闭环）

---

## 场景描述

优化 22 个 Skills 的指令质量：修复悬空引用（P0）、补齐 GATE 与索引覆盖（P1）、确认 observer 状态（P2）。确保每个 SKILL.md 可执行、引用有效、触发准确。

---

## 前置条件

- 探索审计已定位 P0×2 / P1×2 / P2×2
- skills/ 22 个 SKILL.md 全部存在

---

## Case 1: execute 悬空引用修复

**目标**：修复 P0 —— skills/execute/SKILL.md:56 引用不存在的 context-injection-protocol.md

**WHEN**
```
- 读取 skills/execute/SKILL.md:56
- 引用 ../workflow/references/context-injection-protocol.md
- 实际文件已重命名为 context-inheritance-protocol.md
```

**THEN**
```
- 更新引用为 context-inheritance-protocol.md
- 上下文注入模式恢复文档支撑
```

---

## Case 2: spec 悬空引用修复

**目标**：修复 P0 —— skills/spec/SKILL.md 引用不存在的本目录 diagram-trigger-rules.md

**WHEN**
```
- 读取 skills/spec/SKILL.md 「可视化确认」章节
- 引用 references/diagram-trigger-rules.md
- 真实文件在 skills/design/references/
```

**THEN**
```
- 改为 ../design/references/diagram-trigger-rules.md（与其他 skill 一致）
- 消除断链
```

---

## Case 3: cost 补 GATE 硬约束

**目标**：修复 P1 —— cost 是唯一无 <GATE> 的 skill

**WHEN**
```
- 读取 skills/cost/SKILL.md
- 高风险约束（禁止直接 SUM(cost_usd)/禁止硬编码定价）写在普通 ## 约束
```

**THEN**
```
- 将"禁止直接 SUM(cost_usd)"与"禁止硬编码模型定价"提升为 <GATE> 标记
- 与其余 21 个 skill 强度对齐
```

---

## Case 4: using-orch 索引补全

**目标**：修复 P1 —— using-orch 的可用 Skills 表仅列 6/22

**WHEN**
```
- 读取 skills/using-orch/SKILL.md 「可用 Skills」表格
- 仅列出 6 个核心工作流 skill
- 16 个 skill 未列出
```

**THEN**
```
- 补全 22 个 skill 的触发条件表
- 或改为动态引用 plugin 元数据
```

---

## Case 5: continuous-learning observer 状态确认

**目标**：处理 P2 —— skills/continuous-learning/config.json 中 observer.enabled = false

**WHEN**
```
- 读取 skills/continuous-learning/config.json
- observer.enabled = false
- CLAUDE.md 宣称 instinct 学习层存在
```

**THEN**
```
- 确认是否有意关闭
- 若能力优化目标含"自主进化"→ 启用 observer
- 或移除未启用配置 + 同步文档
```

---

## Case 6: 触发描述格式统一（跨平台）

**目标**：P2 —— 16 个核心工作流 skill 缺 TRIGGER when 关键词（跨平台弱化）

**WHEN**
```
- 检查 22 个 skill 的 description
- 6 个社区 skill 有英文 TRIGGER when
- 16 个核心 skill 用中文功能式描述
```

**THEN**
```
- 为核心 skill 补充 TRIGGER when 关键词（不破坏现有 workflow 门控）
- 增强 Cursor/Gemini/Codex 等平台自动触发能力
```

---

## 验证清单

- [ ] 全部引用有效（grep 交叉校验）
- [ ] 22 个 skill 均有 <GATE>（或明确标注无硬约束原因）
- [ ] using-orch 覆盖 22 个 skill
- [ ] observer 状态与文档一致
- [ ] 触发描述含 TRIGGER 关键词

---

## TEST-VERIFY（可测试的验收标准）

- [ ] 应 grep 交叉校验全部 skill 引用，无悬空引用
- [ ] 应校验 cost/SKILL.md 含 <GATE> 标记
- [ ] 应校验 using-orch 表格覆盖全部 22 个 skill
- [ ] 应校验 observer 配置与文档一致
- [ ] 应校验核心 skill description 含 TRIGGER 关键词

### Mock Data

**有效输入**：
```json
{ "skill": "execute", "ref": "context-inheritance-protocol.md" }
```

**边界值**：
```json
{ "skill": "cost", "gate": "GATE" }
```

**特殊值**：
```json
{ "skill": "using-orch", "indexed": 22 }
```
