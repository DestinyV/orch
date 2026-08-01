# 数据模型定义（主规范库）

> 本文件汇总各需求归档的数据模型/实体。新增实体以 `##` 追加。
>
> 首个归档来源：plugin-capability-optimization（插件自身元任务，needs-database: false，无用户业务持久化，以下为插件内部状态/配置结构）。

---

## 1. 优化规则实体（optimization.rules[]）

**来源**：`skills/continuous-learning/user-preferences/preferences.json`

**描述**：自主进化系统的优化规则，本次优化可能新增规则。

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| id | string | Y | 唯一 | 规则标识，如 opt-001 |
| rule_id | string | Y | 引用 | 关联规则 ID |
| description | string | Y | - | 规则描述 |
| injection_point | string | Y | enum | workflow_step0/spec_prompt/design_prompt/execute_prompt/review_prompt |
| confidence | number | Y | 0-100 | 置信度（<30 = trial 禁止注入） |
| status | string | Y | enum | trial/active/archived |
| created_at | string | N | ISO | 创建时间 |

---

## 2. Hook 注册表实体

**来源**：`hooks/hooks.json`

**描述**：本次优化会增改注册项（suggest-compact/observe）。

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| matcher | string | Y | enum | SessionStart/PreToolUse/PostToolUse/PreCompact/Stop |
| hooks[].id | string | Y | 唯一 | 如 suggest-compact |
| hooks[].hooks[].type | string | Y | enum | PreToolUse 等 |
| hooks[].hooks[].command | string | Y | 路径 | scripts/hooks/*.js |
| hooks[].hooks[].timeout | number | N | 秒 | 执行超时 |

---

## 3. Agent 注册表实体

**来源**：`agents/*.md` frontmatter + `AGENTS.md`

**描述**：本次优化统一 frontmatter 语法、修复注册表口径。

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| name | string | Y | 唯一 | 与文件名一致 |
| description | string | Y | - | 角色+职责 |
| tools | string | Y | 逗号分隔 | 统一语法 "Glob, Grep, LS, Read" |
| model | string | Y | inherit | 全部继承会话模型 |
| color | string | N | - | 分类颜色 |

---

## 4. 阶段产出校验表（STAGE_OUTPUTS）

**来源**：`scripts/hooks/workflow-gate.js`

**描述**：本次优化补齐 3.5/5/6/9 阶段。

| 阶段 | 产出文件 | 现状 | 目标 |
|------|---------|------|------|
| 0 | .workflow-state.json | ✅ 已覆盖 | 保持 |
| 1 | spec/ 5 核心文件 | ✅ 已覆盖 | 保持 |
| 3.5 | contract.md + review-report.md | ❌ 缺失 | 补 |
| 4 | tasks.md | ✅ 已覆盖 | 保持 |
| 5 | execution-report.md | ❌ 缺失 | 补 |
| 6 | testing-report.md | ❌ 缺失 | 补 |
| 7 | archive-log.md | ✅ 已覆盖 | 保持 |
| 9 | learnings.md + completion-report | ❌ 缺失 | 补 |

---

## 5. 自检报告实体

**来源**：S4/S6 新建自检命令输出

**描述**：插件自身验证闭环的输出结构。

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| blocks | object | Y | - | 5 大块验证结果 |
| blocks.orchestration | string | Y | PASS/FAIL | 编排引擎 |
| blocks.agents | string | Y | PASS/FAIL | Agent 体系 |
| blocks.skills | string | Y | PASS/FAIL | Skills 指令 |
| blocks.tdd_loop | string | Y | PASS/FAIL | TDD 闭环 |
| blocks.commands_hooks | string | Y | PASS/FAIL | Commands+Hooks |
| issues[] | array | N | - | 失败项定位 |
| issues[].file | string | Y | 路径 | 具体文件 |
| issues[].suggestion | string | Y | - | 修复建议 |

---

## 6. 北极星原则审查记录

**描述**：对每条约束执行"护栏 vs 牢笼"审查的结果。

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| constraint_id | string | Y | 唯一 | 约束标识 |
| constraint_text | string | Y | - | 约束原文 |
| verdict | string | Y | enum | guardrail(护栏)/cage(牢笼) |
| rationale | string | Y | - | 判定依据 |
| action | string | Y | enum | keep/downgrade/remove |
