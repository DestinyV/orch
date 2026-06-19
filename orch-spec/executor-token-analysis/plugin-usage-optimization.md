# orch 插件使用问题诊断与优化方案

**分析数据**: 19 会话 / 554 消息 / 58 Git 提交 / 2026-05-23 ~ 06-19

---

## 一、三个摩擦点根因分析

### 摩擦 1: Claude 频繁跳过流程阶段（最主要，5+ 次）

**症状**: 跳过项目探索 / 跳过 RED 阶段 / 跳过步骤 8-9 / 跳过 eval.json 填充 / 并行降级为串行

**根因**: 当前 GATE 系统存在三层缺陷：

| 层 | 现状 | 缺陷 |
|----|------|------|
| **文本层** | SKILL.md/agent 定义中的 `<GATE>` 文本指令 | LLM 可读但可自主决定忽略——无程序级阻断 |
| **钩子层** | PostToolUse `workflow-gate.js` | fail-open 设计——仅在事后输出 stderr 警告，不阻断执行 |
| **合约层** | 无 | 缺失 PreToolUse 阻断钩子——这是关键缺口 |

**核心矛盾**: orch 的 GATE 规则依赖 LLM 自觉遵守，但当上下文长度增加或 LLM 注意力分散时，GATE 文本指令的约束力衰减。

### 摩擦 2: 文档冗余（2 次会话废弃，30+ 分钟零代码）

**症状**: spec 阶段生成 18-22+ markdown 文件，30+ 分钟无工作代码

**根因**: spec SKILL.md 中的输出契约要求 `requirement.md / scenarios/*.md / data-models.md / business-rules.md / glossary.md / infrastructure.md / deployment.md / backend-monitoring.md / security.md / sql-ddl.md / diagrams/` —— 11+ 文件。全部生成后才进入下一阶段。

**核心矛盾**: 文件数量 × 每文件详细程度 = 巨大时间消耗，用户等待中失去耐心。

### 摩擦 3: 技术失败（API 冲突 / Socket / 类型错误）

**症状**: 子代理 API 参数冲突、Socket 断连、TypeScript 类型错误

**根因**: 
- 子代理派遣前无参数校验
- Socket 断连无重试机制（由 Claude Code 平台处理，orch 无法直接控制）
- TypeScript 类型错误——已由 TDD REFACTOR 阶段覆盖，但可能出现在 executor 未运行时

---

## 二、优化方案

### A: PreToolUse 阻断钩子（解决摩擦 1，影响最大）

**新增文件**: `scripts/hooks/stage-gate.js`
**注册**: `hooks.json` → PreToolUse → matcher: "Skill"

**工作原理**:
```
Claude 即将调用 Skill("orch:execute")
  → PreToolUse hook 触发
  → 检查 .workflow-state.json:
      design stage = done?
      task stage = done?
      是 → 放行
      否 → 返回阻断消息："Task stage 未完成，禁止进入 execute"
  → Claude 收到阻断消息 → 必须先完成前置阶段
```

**与现有 workflow-gate.js 的区别**:
| | workflow-gate.js (PostToolUse) | stage-gate.js (PreToolUse, 新增) |
|---|---|---|
| 触发时机 | Skill/Agent 调用**后** | Skill/Agent 调用**前** |
| 行为 | 事后警告（stderr） | **事前阻断**（返回拒绝消息） |
| 对 Claude 的影响 | Claude 已跳过，仅记录 | Claude 收到阻断，必须回头 |

### B: CLAUDE.md 反跳过强化（解决摩擦 1 + 2）

在 CLAUDE.md 核心约束段新增明确的阶段纪律规则。

### C: Spec 文档预算限制（解决摩擦 2）

在 spec SKILL.md 的输出契约中新增"首轮最多 5 文件"限制，其余文件在用户确认核心 spec 后按需生成。

### D: 并行降级检测 + agent 参数校验（解决摩擦 1 子项 + 摩擦 3）

在 workflow-gate.js 中新增串行降级检测：连续 2 次 agent 派遣之间无 `run_in_background=true` → 触发警告。

---

## 三、实施计划

### 文件变更清单

| # | 文件 | 动作 | 解决 |
|---|------|------|------|
| 1 | `scripts/hooks/stage-gate.js` | **新建** | 摩擦 1: PreToolUse 阻断 |
| 2 | `hooks/hooks.json` | 修改 | 注册 PreToolUse stage-gate |
| 3 | `CLAUDE.md` | 修改 | 摩擦 1+2: 反跳过 + 文档预算 |
| 4 | `skills/spec/SKILL.md` | 修改 | 摩擦 2: 首轮文件限制 |
| 5 | `scripts/hooks/workflow-gate.js` | 修改 | 摩擦 1+3: 串行降级检测 |

### 实施顺序

```
Step 1: 新建 stage-gate.js           ← 核心阻断逻辑
Step 2: 注册 hooks.json              ← 启用阻断
Step 3: 强化 CLAUDE.md               ← 文本层加强
Step 4: spec SKILL.md 文档预算       ← 减少等待时间
Step 5: workflow-gate.js 串行检测    ← 补充检测
Step 6: 全量回归                     ← 验证
```
