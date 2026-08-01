# 项目知识 BASE — orch（Claude Code 插件）

> 全量探索产出（2026-08-01）。版本 v0.10.0。这是项目级 context 的集中式知识库，取代原分散的 tech-stack/architecture/conventions/code-patterns。
> 供所有后续需求继承（context-inheritance-protocol 步骤 1-2）。

## 一句话定位
**orch**（Orchestra）是面向 Claude Code 的企业级 SDD+TDD 工作流插件：22 Skills + 26 Agents + 14 Commands + 6 Hooks，覆盖从需求到归档的全生命周期，并支持 Cursor/Gemini/OpenCode/Codex/CodeBuddy 多平台适配。

## 核心工作流（13 步）

```
/start-dev → Skill("orch:workflow")
  → 0 初始化（模式检测/状态恢复/优化规则注入/基线生成）
  → 0.5 clarify（苏格拉底澄清，模糊度 > 0.2 触发）
  → 1 spec（code-explorer 探索 + BDD 规范生成）
  → 2 test-design ⟷ 3 design（并行，互不阻塞）
  → 3.5 contract（fullstack 强制）
  → 4 task（DAG 任务拆解）
  → 5 execute（TDD + git-worktree 隔离 + 两阶段审查，批次并行）
  → 5.5 exception（后端/全栈自动）
  → 6 test（集成/E2E/性能 + 闭环验证）
  → 7 archive（主规范合并 + context 同步）
  → 8 evaluation（context-budget 预估 + cost DB 实记 双路并行）
  → 9 continuous-learning（knowledge-curator 提取 + completion-reporter 完成报告）
```

## 模块划分总览

| 模块 | 数量 | 位置 |
|------|------|------|
| Skills | 22 | `skills/`（编排1 + 核心11 + 工具3 + 扩展7） |
| Agents | 26+1 | `agents/`（工作流核心13 + 扩展12 + tdd-guide + 辅助） |
| Commands | 14 | `commands/` |
| Hooks | 6 | `hooks/hooks.json` + `scripts/hooks/*.js` |
| 运行时库 | 8 | `scripts/lib/*.js` |
| Schemas | 3 | `schemas/`（workflow-state/eval/deliverables） |
| 配置 | 3 | `config/`（platforms/stacks/socratic-config） |

## 设计原则

| 原则 | 说明 |
|------|------|
| 规范优先 | 一切从 spec 开始，所有设计开发基于规范 |
| 设计驱动 | design 生成架构方案，审批后进入 Task |
| 任务清晰 | task 拆解为可执行任务，含依赖和验收标准 |
| 执行严谨 | execute 两阶段审查 + TDD（RED→GREEN→REFACTOR→REVIEW）+ 覆盖率 ≥85% |
| 测试完整 | test 集成/E2E/性能 + 闭环验证（TV→Test→Code→Result 对应） |
| 状态持久 | 每阶段完成后立即写 .workflow-state.json / .workflow-eval.json，不依赖会话内存 |
| 知识复利 | 每次工作流结束沉淀模式，持续增强下次需求 |

## 关键约束（HARD-GATE）

### 阶段纪律（最高优先级）
- 工作流阶段必须按序执行（0→9），禁止跳过。PreToolUse stage-gate hook + PostToolUse workflow-gate hook 双层校验。
- 步骤 8 evaluation 和步骤 9 continuous-learning **不可跳过**。archive 完成后必须自动执行。
- 步骤 9 完成后必须派遣 completion-reporter 生成四段完成报告，否则工作流不可标记 completed。

### 文档产出约束
- spec 首轮最多 5 个核心文件；15 分钟内产出第一段工作代码。
- 辅助文件（infrastructure/deployment/monitoring/security/diagrams）在用户确认后按需生成。

### 并行执行协议
- 批次内 2+ 无依赖 Task 必须 `run_in_background=true` 并行派遣，禁止串行。
- 同批次内测试 Task 优先（RED 先于 GREEN）；最大并发 ≤5。
- Task 失败 ≥2 次 → `debug`；Task >3 批次 → `ralph-loop`。

## 上下文双层次机制

| 层次 | 路径 | 生命周期 | 说明 |
|------|------|---------|------|
| 项目级 context | `orch-spec/context/` | 跨需求持久 | index.json 注册 + 关键词匹配继承 |
| 需求级 req-context | `orch-spec/{req_id}/req-context/` | 单次工作流 | project-map.json + key-files.md + decisions.md |

**继承协议**（context-inheritance-protocol.md）：
1. workflow 步骤0 从需求提取关键词 → 匹配 index.json tags → 生成 `.baseline-context.json`
2. code-explorer 接收 baseline_context → 增量探索（SHA 一致跳过，不一致只扫 git diff）
3. archive 步骤同步新发现回 context/ + 更新 requirements.yaml + .exploration-state.json

## 探索模式

| 模式 | 触发 | 策略 |
|------|------|------|
| 全量 | 首次运行 / context 缺失 | 全量扫描 + 生成 project-context + project-map.json |
| 增量 | baseline_context 提供 | 只扫 git diff 变更文件，追加到 project-map.json |

## 自主进化系统（continuous-learning v2）

- 偏差分析：任何可数值化偏差（token/耗时/HARD-GATE/retry/user_intervention）deviation > 20% 触发优化假设
- optimization.rules[] 生命周期：trial（confidence<30，禁止注入）→ active（≥30）→ archived（3 次无效）
- 注入点：workflow_step0 / spec_prompt / design_prompt / execute_prompt / review_prompt
- instinct 学习层：hook 级会话观察 + 原子 instincts + 置信度评分 + 项目级隔离

## 成本追踪管线

- Stop hook（cost-tracker.js）读取 session transcript JSONL → 汇总 token 用量
- 双写：`~/.claude/orch-costs/costs.jsonl` + `usage.db`（SQLite）
- 定价：内置 BUILTIN_RATES（haiku/opus/sonnet/deepseek）+ 外部 `pricing.json` 覆盖
- eval 桥接：state-store.updateStageTokens 同步到 .workflow-eval.json actual_tokens

## 插件自身测试

- `tests/test-suite.py` — Python 测试套件
- `tests/pressure-scenarios/` — 压力场景（时间压力/沉没成本/权威简化/穷尽验证）
- 无 Jest/前端测试（插件本体为 Markdown + Node 脚本）

## 版本与发布

- 当前版本 v0.10.0，CHANGELOG.md 记录演进
- 通过 Marketplace（marketplace.json）发布，`claude plugin validate` 校验
- 最近里程碑：完成报告流程优化（completion-reporter）、成本管线修复、step7-8-9 context 切分
