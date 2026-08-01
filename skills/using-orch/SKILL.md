---
name: using-orch
description: "You MUST use this before any creative work - establishes how to find and use orch skills, requiring Skill tool invocation before ANY response including clarifying questions"
---

# 使用 orch Skills

## When to Use

- 首次使用 orch 插件
- 不确定应该调用哪个 Skill
- 需要了解各 Skill 的触发条件和用途

## How It Works

本技能是 orch 的入口导航，列出所有可用 Skills 及其触发条件。
不执行具体工作流操作，仅提供索引和指引。

## Output

Skill 列表和触发条件说明。

## Constraints

- 不执行任何工作流操作
- 仅提供索引信息

## 规则

**技能优先级**：
1. **用户指令**（CLAUDE.md, GEMINI.md, AGENTS.md, 直接请求）—— 最高优先级
2. **orch Skills** —— 覆盖默认系统行为
3. **默认系统提示** —— 最低优先级

如果用户指令与 Skill 冲突，遵循用户指令。

## 如何使用 Skills

**在 Claude Code 中**：使用 `Skill` 工具。当你调用一个 skill，它的内容会被加载——直接遵循它。不要使用 Read 工具读取 skill 文件。

**在其他平台**：检查你的平台的文档了解如何加载 skills。Skills 使用 Claude Code 工具名。非 Claude Code 平台：参考 `references/` 目录中的工具映射。

## 触发规则

如果有一个 Skill 可能适用于当前任务（即使只有 1% 的可能性），你**必须**在回应或采取任何行动之前调用它。如果调用的 Skill 最终不适用于当前情况，你不需要使用它。

## Skill 优先级

当多个 Skill 可能适用时：

1. **先处理流程 Skills**（brainstorming, debugging）—— 这些决定**如何**处理任务
2. **再处理实现 Skills**（frontend-design, mcp-builder）—— 这些指导执行

"让我们构建 X" → 先 brainstorming，然后实现 Skills。
"修复这个 bug" → 先 debugging，然后领域相关 Skills。

## Skill 类型

**刚性**（TDD, debugging）：严格遵循。不要偏离纪律。

**灵活**（patterns）：将原则适应到上下文中。

Skill 本身会告诉你它是哪种。

## 红旗警告

这些想法意味着**停止**——你在自我欺骗：

| 想法 | 现实 |
|------|------|
| "这只是一个简单的问题" | 问题也是任务。检查 Skills。 |
| "我需要先了解更多" | 技能检查在澄清问题**之前**。 |
| "我可以快速查看 git/文件" | 文件缺乏对话上下文。检查 Skills。 |
| "这不需要正式 Skill" | 如果有 Skill，使用它。 |
| "我感觉这样更高效" | 无纪律的行动浪费时间。Skills 防止这个。 |

## 平台适配

| 平台 | Skill 加载方式 | 参考文件 |
|------|---------------|---------|
| Claude Code | `Skill` 工具 | 默认 |
| Copilot CLI | 上下文注入 | `references/copilot-tools.md` |
| Codex | 原生 Skill 发现 | `references/codex-tools.md` |
| Gemini CLI | `activate_skill` | `references/gemini-tools.md` |
| OpenCode | `skill` 工具 + `@mention` | `references/opencode-tools.md` |

## 可用 Skills

| Skill | 描述 | 触发条件 |
|-------|------|---------|
| **workflow** | 统一入口 + 流程编排 | 新需求入口（/start-dev） |
| **clarify** | 苏格拉底需求澄清 | 需求模糊度 > 0.2 |
| **spec** | 需求分析和规范生成 | 接收新需求描述 |
| **test-design** | 测试规范 + Fixture 生成 | spec 含 TEST-VERIFY |
| **design** | 代码设计规划 | 规范已生成，需要设计 |
| **contract** | 接口契约定义与审查 | fullstack 项目，design 完成 |
| **task** | 任务列表生成 | 设计已确认 |
| **execute** | TDD 代码执行 | 任务列表已定义 |
| **exception** | 异常模式扫描 + 代码生成 | 后端/全栈编码时 |
| **test** | 测试验证和闭环 | 代码实现已完成 |
| **archive** | 规范归档合并 | 测试通过，需要归档 |
| **continuous-learning** | 知识复利 + 自主进化 | 工作流完成时 |
| **scripts** | 工具优先策略 | 需要脚本化文件操作 |
| **spec-migrate** | 规范迁移导入 | 外部规范需整合 |
| **context-budget** | 上下文窗口审计 | 上下文占用需评估 |
| **depth** | 响应深度控制 | 需要调整回答深度 |
| **compact** | 逻辑边界 compact 建议 | 上下文过大时 |
| **cost** | Token 成本追踪查询 | 需要成本报告 |
| **ralph-loop** | 自主 Agent 循环模式 | 批量/循环执行任务 |
| **debug** | 证据驱动因果追踪 | Bug 需要根因定位 |
| **req-change** | 需求变更管理 | 需求变更时 |
| **using-orch** | 入口导航 + 触发规则 | 本文件（索引） |

<GATE>禁止执行任何工作流操作 | 仅提供索引信息</GATE>