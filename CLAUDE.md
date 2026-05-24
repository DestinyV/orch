# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在 **orch** 代码库中工作时提供指导。

减少常见 LLM 编码错误的行为准则。根据项目具体指令合并使用。

**权衡：** 这些准则偏向谨慎而非速度。对于简单任务，自行判断。

## 1. 先思考再编码
**不要假设。不要隐藏疑问。暴露权衡。**
- 明确陈述你的假设。不确定时，直接问。
- 如果存在多种解读，全部列出——不要默默选一个。
- 如果有更简单的方案，说出来。必要时提出异议。
- 如果某事不清楚，停下来。说出困惑点。提问。

## 2. 简洁优先
**用最少的代码解决问题。不做任何推测性工作。**
- 不实现未要求的功能。不为单次使用场景做抽象。
- 不添加未要求的"灵活性"或"可配置性"。
- 不为不可能发生的场景写错误处理。
- 如果你写了 200 行而它可以缩到 50 行，重写它。
- 问自己："高级工程师会觉得这个过于复杂吗？"

## 3. 精确修改
**只动必须动的代码。只清理自己造成的混乱。**
- 不要"改进"相邻的代码、注释或格式。
- 不要重构没坏的东西。遵循现有风格。
- 移除你的修改导致的未使用导入/变量/函数。
- 除非被要求，不要删除已有的死代码。
- 检验标准：每一行修改都应直接追溯到用户的需求。

## 4. 目标驱动
**定义成功标准。循环验证直到通过。**
- "添加校验" → "先写无效输入的测试，再让它们通过"
- "修复 Bug" → "先写复现 Bug 的测试，再让它通过"
- "重构 X" → "确保测试前后均通过"
- 对于多步骤任务，给出简洁计划：`1. [步骤] → 验证：[检查项]`

---

**验证准则是否生效：** diff 中不必要的变更减少，因过度复杂化导致的重写减少，澄清性问题出现在实现之前而非之后。

---

## 项目概述

**orch**（/ɔːrk/，Orchestra 缩写，意为编排指挥）是一个企业级 Claude Code 插件，提供 AI 辅助开发的完整全栈工作流。18 Skills + 23 Agents + 12 Commands，覆盖从需求到归档的全生命周期。多平台适配：Cursor/Gemini/OpenCode/Codex/CodeBuddy。

**核心工作流**：
```
/start → spec → test-design ⟷ design → contract(fullstack)
→ task → execute → exception(后端/全栈) → test
→ archive → continuous-learning
```

**TDD 数据链路**：`spec (TEST-VERIFY) → test-designer (test-spec + fixtures) → execute (RED-GREEN-REFACTOR-REVIEW)`

**版本**：v0.5.0 (2026-05-24)

## 架构与文件结构

```
orch/
├── skills/          # 18个 Skills（workflow/spec/test-design/design/contract/
│                    #   task/execute/exception/test/archive/
│                    #   scripts/continuous-learning/using-orch/
│                    #   context-budget/depth/compact/
│                    #   cost/ralph-loop）
├── agents/          # 23个 Agents（11工作流核心 + 12扩展）
├── commands/        # 12个斜杠命令
├── rules/           # 语言规则（common/typescript/python/zh）
├── scripts/lib/     # 运行时脚本（resolve-root/project-detect/state-store/utils）
├── hooks/hooks.json # Hook 注册表
├── references/      # 多平台工具映射
├── config/          # 项目栈配置
├── schemas/         # JSON Schema
├── docs/            # 文档（zh/en 双语）
└── .claude-plugin/  # 插件元数据
```

### 文档层级
- **README.md** → 项目概述、核心特性、快速开始
- **docs/USAGE.md** → 详细使用场景和 TDD 流程说明
- **docs/INSTALLATION.md** → 安装和故障排查
- **docs/BEST_PRACTICES.md** → 最佳实践和检查清单
- **skills/*/SKILL.md** → 每个 Skill 的完整工作流文档

### Skills 简介

| Skill | 职责 | 阶段 |
|-------|------|------|
| scripts | 工具优先策略 | Utility |
| spec-import | 规范迁移导入 | Utility |
| workflow | 统一入口+流程编排 | 入口 |
| spec | 需求分析和规范生成 | Spec |
| test-design | 测试规范 + Fixture 生成 | Test-Design |
| design | 代码设计规划 | Design |
| contract | 接口契约定义与审查 (fullstack) | Api-Contract |
| task | 任务分解 | Task |
| execute | TDD 实现 + git-worktree + 两阶段审查 | Execute |
| exception | 异常模式扫描+代码生成 | Exception |
| test | 集成/E2E/性能测试 + 闭环验证 | Test |
| archive | 规范归档合并 | Archive |
| continuous-learning | 知识复利 + instinct 学习 | Knowledge |
| context-budget | 上下文窗口审计 | Utility |
| depth | 响应深度控制 | Utility |
| compact | 逻辑边界 compact 建议 | Utility |
| cost | Token 成本追踪 | Utility |
| ralph-loop | 自主循环模式选择 | Utility |

### 多平台支持

| 平台 | Skill 加载 | 子代理 |
|------|-----------|--------|
| **Claude Code** | `Skill` 工具 | ✅ Agent 派遣 |
| **Cursor** | `.cursor/rules/` | ❌ rules 驱动 |
| **Gemini CLI** | `activate_skill` | ❌ 串行执行 |
| **OpenCode** | `skill` 工具 / `@mention` | ✅ 子上下文 |
| **Codex** | AGENTS.md 注册 | ✅ spawn_agent |
| **CodeBuddy** | instruction 文件 | ✅ Agent 系统 |

详见 `references/` 目录下的平台映射文件。

### Agent 注册表（工作流核心）

| Agent | 职责 |
|-------|------|
| workflow | 统一入口 + 流程编排 |
| spec | 需求分析和规范生成 |
| test-designer | 测试设计 |
| code-architect | 代码设计规划 |
| tasker | 任务列表生成 |
| code-executor | TDD 代码实现 |
| code-reviewer | 规范 + 质量两阶段审查 |
| tester | 高层测试运行 |
| exception | 异常模式扫描 |
| knowledge-curator | 知识复利执行 |
| archiver | 规范归档合并 |

另含 12 个扩展 Agents（planner/tdd-guide/code-simplifier/silent-failure-hunter/comment-analyzer/conversation-analyzer/pr-test-analyzer/refactor-cleaner/loop-operator/harness-optimizer/doc-updater/e2e-runner），详情见 `AGENTS.md`。

### 支持技术栈

| 领域 | 框架/语言 | 测试 |
|------|-----------|------|
| **前端** | React/Vue/Angular/Svelte + TypeScript + Tailwind | Vitest/Jest/Playwright |
| **后端** | Node.js/Python/Go/Java + Express/Django/Spring Boot/Gin | Jest/Pytest/JUnit/Go test |
| **数据库** | PostgreSQL/MySQL/SQLite/MongoDB/Redis + Prisma/TypeORM | 迁移脚本 |
| **移动端** | React Native/Flutter | Jest/Flutter test |
| **全栈** | Next.js/Nuxt/Remix + 前后端+数据库 | Vitest/Playwright |

## 设计原则

| 原则 | 说明 |
|------|------|
| **规范优先** | 一切从 spec 开始，所有设计开发基于规范 |
| **设计驱动** | design 生成架构方案，审批后进入 Task 阶段 |
| **任务清晰** | task 将设计拆解为可执行任务清单，含依赖和验收标准 |
| **执行严谨** | execute 两阶段审查（规范+质量）+ TDD（RED→GREEN→REFACTOR→REVIEW）+ 覆盖率≥85% |
| **测试完整** | test 执行集成/E2E/性能测试 + 闭环验证（TV→Test→Code→Result 对应）|

## Skills 关系

```
用户需求
  ↓
[spec]  生成 orch-spec/{req_id}/spec/（含 TEST-VERIFY + Mock Data）
  ↓
  ├── [test-design]  ← 并行 →  [design]
  │   生成 test-spec + fixtures      生成 design.md
  ↓                              ↓
  ├── [contract]（fullstack 强制）→ contract.md + review-report.md
  ↓
[task]  →  tasks.md
  ↓
[execute]  →  test-*.template + fixtures → RED→GREEN→REFACTOR→REVIEW
  ↓              →  exception（后端/全栈自动）
[test]   →  集成 / E2E / 性能测试 + 闭环验证
  ↓
[archive]  →  合并到主规范库
  ↓
[continuous-learning]  →  patterns/ + instincts/ + preferences/
  ↓
✅ 完成
```

- test-design 与 design 可并行执行，互不阻塞
- exception 仅后端/全栈自动触发（execute 子过程）
- continuous-learning v2 含 instinct 学习层（hook 级会话观察 + 原子 instincts + 置信度评分 + 项目级隔离）

## 架构参考

### 提交协议
- Conventional Commit 格式：`<type>(<scope>): <description>`
- Git Trailers 记录决策上下文：Constraint / Rejected / Directive / Spec / HARD-GATE
- 详见 `rules/common/git-workflow.md`

### 执行协议
- Explore first, then plan — 不探索代码库就不设计
- 2+ 独立任务并行执行 — 批次级并行，批次间串行
- Authoring 和 review 分离 — 从不自我审批，两阶段审查严格排序
- 拒绝"应该/可能" — 每条验收标准必须有新鲜证据

### 钩子系统
| 事件 | 钩子 | 用途 |
|------|------|------|
| SessionStart | session-start.js | 未完成工作流检测 + 状态恢复 |
| PreToolUse | observe.sh | Instinct 学习观察 |
| PreToolUse (Edit/Write) | suggest-compact.js | 逻辑边界 compact 建议 |
| PostToolUse | observe.sh | 观察完成 |
| PreCompact | pre-compact.js | Compact 前保存工作流状态 |
| Stop | session-evaluate.js | 会话评估 + 工作流持续化检测 |

### 状态持久化
- `.workflow-state.json` — 各阶段状态追踪
- `.workflow-eval.json` — 效果评估 + Token 用量
- 不依赖会话内存，每阶段完成后立即写入

## 核心约束

| ✅ 必须 | ❌ 禁止 |
|---------|--------|
| 首次使用前运行 spec 生成规范 | 跳过设计阶段直接编码 |
| 设计审批通过后才能进入 task | execute 中跳过规范或质量审查 |
| 遵循 Task 清单严格执行 | 发现问题不修复就继续下一个 Task |
| test 闭环验证（≥80% 覆盖率） | 为了让测试通过修改源代码逻辑 |

## 关键要点

1. **规范驱动** — 一切从 `/spec` 开始
2. **测试先行** — `/test-design` 从 TEST-VERIFY 生成测试规范和 Fixture
3. **设计优先** — `/design` 数据库先行 + 接口契约驱动
4. **多阶段审查** — git-worktree 隔离 + 规范+质量两道关卡
5. **闭环验证** — Task-代码-测试完全对应
6. **知识复利** — 每次工作流结束沉淀模式，持续增强下次需求

**整个工作流是规范驱动且任务清晰的。** 规范和设计确定后，所有 Skill 严格按照清单执行。
