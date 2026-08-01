# 场景: S2 Agent 体系优化

**优先级**：高
**相关场景**：S3（Skills）、S4（TDD 闭环）
**场景间依赖**：
- depends-on: S1（编排层修正支撑 Agent 派遣）
- provides-to: S4（审查能力支撑 TDD 闭环）

---

## 场景描述

优化 Agent 体系的注册表口径、frontmatter 一致性、Prompt Defense 幂等性，消除孤立 agent 与文件引用错误，提升派遣准确率。

---

## 前置条件

- 探索审计已定位 F1/F2/F5/F7/F8/F12
- agents/ 目录 27 个文件（26 agent + _prompt-defense.md）

---

## Case 1: project-map 文件名引用统一

**目标**：修复 F1 —— 3 处引用 project-map.md（实为 .json）

**WHEN**
```
- 读取 agents/code-architect.md:19
- 读取 agents/tasker.md:13
- 读取 skills/design/SKILL.md:45
- 三处均引用 req-context/project-map.md
```

**THEN**
```
- 统一改为 req-context/project-map.json
- 消除下游 design/task 阶段上下文注入失败风险
```

**备注**：直接提升产出达标率。

---

## Case 2: tdd-guide 孤立 agent 处置

**目标**：修复 F2 —— tdd-guide 不在 AGENTS.md 注册表

**WHEN**
```
- AGENTS.md 声明 25 个 agent
- 磁盘实际 26 个（含 tdd-guide）
- tdd-guide 被 agent-dispatch-code.md / flow-execution-reference.md 引用
- 职责已被 code-reviewer 维度 3 吸收
```

**THEN**
```
- 处置方案：从 dispatch 引用移除 tdd-guide，标注 deprecated
- 或在 AGENTS.md 注册并明确与 code-reviewer 边界
- 同步 agent-dispatch-code.md / flow-execution-reference.md 引用
```

---

## Case 3: Prompt Defense 幂等同步

**目标**：修复 F5 —— 8 个 agent 的 "## Prompt Defense Baseline" 节重复

**WHEN**
```
- 运行 scripts/sync-prompt-defense.py
- 目标 agent 已含 "## Prompt Defense Baseline" 节
- 脚本未检测已有节 → 重复插入
```

**THEN**
```
- 修复 sync 脚本幂等性（检测已有节，替换而非追加）
- 清理已重复的 8 个 agent 文件
- 重新运行验证无重复
```

---

## Case 4: frontmatter 统一

**目标**：修复 F7 —— tools 语法风格不统一 + 稀疏 frontmatter

**WHEN**
```
- 检查 26 个 agent 的 frontmatter
- 7 个社区 agent 用数组语法 ["Read",...]
- 13 个本地 agent 用逗号语法 "Glob, Grep"
- workflow/spec 无 tools/model/color；5 个 agent 无 color
```

**THEN**
```
- 统一 tools 为逗号分隔语法
- 补齐缺失的 model/color
- 保持 model: inherit 约定
```

---

## Case 5: code-architect 编号修复

**目标**：修复 F8 —— 两处 "### 0." 编号重复

**WHEN**
```
- 读取 agents/code-architect.md
- 发现两处 "### 0."（共识式审查参与 / 读取项目上下文）
```

**THEN**
```
- 改为 0 与 1
- 保持文档编号连续
```

---

## Case 6: 异常情况 — 外部命令残留

**目标**：修复 F12 —— conversation-analyzer 引用 /hookify（orch 无此命令）

**WHEN**
```
- 读取 agents/conversation-analyzer.md
- description 或正文引用 /hookify 命令
```

**THEN**
```
- 替换为 orch 实际可用的分析入口或移除
- 消除外部残留
```

---

## 验证清单

- [ ] project-map.md → .json 全部修正
- [ ] tdd-guide 处置完成，口径一致
- [ ] Prompt Defense 无重复节
- [ ] frontmatter 风格统一
- [ ] code-architect 编号连续
- [ ] 无 /hookify 残留

---

## TEST-VERIFY（可测试的验收标准）

- [ ] 应 grep 确认无 project-map.md 引用残留
- [ ] 应校验 AGENTS.md 注册数与磁盘文件数一致
- [ ] 应运行 sync-prompt-defense.py 两次，确认无重复插入
- [ ] 应校验全部 agent frontmatter 语法统一
- [ ] 应校验 code-architect.md 编号连续
- [ ] 应 grep 确认无 /hookify 引用

### Mock Data

**有效输入**：
```json
{ "agent": "code-architect", "ref": "project-map.json" }
```

**边界值**：
```json
{ "agent": "tdd-guide", "status": "deprecated" }
```

**特殊值**：
```json
{ "file": "conversation-analyzer.md", "forbidden": "/hookify" }
```
