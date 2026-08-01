# 命名规范与项目约定

> 全量探索产出（2026-08-01）。来源：RULES.md / CLAUDE.md / 各 SKILL.md/agent/command frontmatter / rules/。

## 文件命名规范

| 组件 | 路径规则 | 示例 |
|------|---------|------|
| Skill | `skills/{skill-name}/SKILL.md` | `skills/workflow/SKILL.md` |
| Skill 参考 | `skills/{skill}/references/*.md` | `references/flow-execution-reference.md` |
| Skill 模板 | `skills/{skill}/templates/*.md` | `templates/spec-requirement-template.md` |
| Skill 提示词 | `skills/{skill}/prompts/*.md` | `execute/prompts/tdd-implementer-prompt.md` |
| Agent | `agents/{agent-name}.md` | `agents/code-architect.md` |
| Command | `commands/{command-name}.md` | `commands/start-dev.md` |
| Hook 脚本 | `scripts/hooks/{hook-name}.js` | `scripts/hooks/workflow-gate.js` |
| 工具库 | `scripts/lib/{module}.js` | `scripts/lib/state-store.js` |
| 需求目录 | `orch-spec/{req_id}/` | `orch-spec/plugin-capability-optimization/` |

**Skill 目录命名**：单数/动词（spec, design, execute, debug, clarify）。
**req_id 命名**：小写 kebab-case（`plugin-capability-optimization`）。

## Frontmatter 格式

### Skill（SKILL.md）
```yaml
---
name: {skill-name}
description: |
  {职责 + 输入 + 输出 + 功能描述}
  {TRIGGER when: ...（社区类 skill 常见）}
  {origin: community（外部引入标记，可选）}
---
```

### Agent（agents/*.md）
```yaml
---
name: {agent-name}
description: {角色 + 职责 + 输入/输出}
tools: [Read, Write, Edit, Bash, Grep, Glob]   # 或逗号分隔 "Glob, Grep, LS, Read"
model: inherit                                   # 约定：全部 agent 继承会话模型
color: {颜色}                                    # 可选
---
```

### Command（commands/*.md）
```yaml
---
description: {命令用途}
argument-hint: {参数提示}
---
```
注意：command 多数**没有 name 字段**（由文件名决定）。

## 命名/编码约定

- Agent 全部使用 `model: inherit`（继承会话模型，避免 thinking 参数冲突）
- Agent tools 数组两种风格并存：字符串数组 `["Read", "Write"]` 或逗号分隔 `"Glob, Grep, LS, Read"`
- Skill description 用 `|` 多行块；社区引入的 skill 标注 `origin: community`
- HARD-GATE 标记：`<GATE>...</GATE>`（阶段纪律最强约束）
- 出口验证：`- [ ] 检查项`（checklist 格式）
- 失败处理：默认 fail-open（hook）或重试 1 次后 AskUserQuestion（工作流）

## 文档结构约定

| 文档 | 位置 | 结构 |
|------|------|------|
| 工作流规范输出 | `orch-spec/{req_id}/spec/` | requirement.md + scenarios/*.md + data-models.md + business-rules.md + glossary.md |
| 工作流设计输出 | `orch-spec/{req_id}/design/` | design.md（架构/组件/决策记录三章节） |
| 任务输出 | `orch-spec/{req_id}/tasks/` | tasks.md（provides/consumes/验收标准/DAG） |
| 测试输出 | `orch-spec/{req_id}/testing/` | testing-report.md（验证矩阵 + 测试结果） |
| 主规范库 | `orch-spec/spec/` | 按场景拆分合并的长期规范 |
| 项目上下文 | `orch-spec/context/` | index.json 注册中心 + 各 section 文件 |
| 用户偏好 | `orch-spec/user-preferences/preferences.json` | always_check/rejected_approaches/optimization.rules[] |

## 规则目录约定（rules/）

| 目录 | 语言 | 文件 |
|------|------|------|
| rules/common/ | 通用 | coding-style / development-workflow / git-workflow / security / testing |
| rules/typescript/ | TS/JS | coding-style / patterns / testing |
| rules/python/ | Python | coding-style / patterns / security / testing |
| rules/zh/ | 中文 | coding-style / development-workflow |

## 状态持久化约定

| 文件 | 写入时机 | 内容 |
|------|---------|------|
| .workflow-state.json | 每阶段完成后立即写入 | status/current_stage/stages[]/progress/checkpoint |
| .workflow-eval.json | 每阶段完成后追加 | stages[]/events[]/token_usage/diagnosis/learnings |
| .exploration-state.json | archive 后更新 | last_explored_sha/section_freshness |
| requirements.yaml | archive 后更新 | 历史需求相似度索引 |

**不依赖会话内存**，每阶段完成后立即落盘。

## Git 约定

- Conventional Commit：`<type>(<scope>): <description>`
  - 例：`feat: 完成报告流程优化` / `fix(cost): repair token collection pipeline`
- Git Trailers 记录决策上下文：`Constraint / Rejected / Directive / Spec / HARD-GATE`
- 工作流输出目录 `orch-spec/` 纳入版本管理

## 关键约束标记

- `<GATE>...</GATE>` — HARD-GATE，禁止违反（跳过阶段/降级/缺产出）
- `<HARD-GATE>...</HARD-GATE>` — 显式硬门禁格式（legacy 文档）
- `<!-- SOURCE OF TRUTH: ... -->` — 权威定义标记（flow-execution-reference.md）

## 跨平台约定

- 主平台 Claude Code 用 `Skill("orch:{name}")` + `Agent(subagent_type="orch:{name}")`
- 其他平台映射在 `config/platforms.json` + `references/*.md` + `.cursor/` `.opencode/` `.codex/` 等
