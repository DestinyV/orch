# Agents + Commands + Hooks + Scripts 审计报告

> 元任务：plugin-capability-optimization（插件本体能力优化）
> 审计对象：`agents/` + `commands/` + `hooks/` + `scripts/`
> 模式：全量探索（无 baseline_context）
> 审计人：code-explorer（Agent C — Agents 体系 + 运行时脚本审计）
> 审计日期：2026-08-01

---

## 1. Agent 清单（26 个定义文件 + 1 个模板）

**注册表口径**：`AGENTS.md` 声明 25 个（13 工作流核心 + 12 扩展），但磁盘上有 26 个 agent 定义文件。`tdd-guide` 不在注册表中（见 F2）。

### 1.1 工作流核心 Agents（13 个，与 AGENTS.md 一致）

| # | 文件 | name | tools | model | color | Skill/流程引用 | 质量评估 |
|---|------|------|-------|-------|-------|---------------|---------|
| 1 | `agents/workflow.md` | workflow | 无 | 无 | 无 | `commands/start-dev.md`（Skill 调用） | 空泛：正文仅约 15 行，纯指向 `skills/workflow/SKILL.md`。Skill 型 Agent 可接受，但 frontmatter 无 tools/model/color（F7） |
| 2 | `agents/spec.md` | spec | 无 | 无 | 无 | `commands/start-dev.md`（Skill 调用） | 空泛：正文极薄，明确"非 Agent 派遣"。frontmatter 无 tools/model/color（F7） |
| 3 | `agents/code-explorer.md` | code-explorer | Glob/Grep/LS/Read/WebFetch/Bash | inherit | blue | `archive/SKILL.md:36`、`workflow/SKILL.md` 批次1 | 精确：双模式定义、Context 优先策略、输出契约完整 |
| 4 | `agents/test-designer.md` | test-designer | Write/Edit/Bash/Glob/Grep/LS/Read | inherit | blue | `test-design/SKILL.md:35` | 精确：能力矩阵、决策规则、覆盖率指标齐备 |
| 5 | `agents/code-architect.md` | code-architect | Glob/Grep/LS/Read | inherit | green | `design/SKILL.md:56` | 精确但两处瑕疵：引用 `project-map.md`（实为 `.json`，F1）；`### 0.` 编号重复（F8） |
| 6 | `agents/tasker.md` | tasker | Write/Edit/Bash/Glob/Grep/LS/Read | inherit | green | `task/SKILL.md:54` | 精确：DAG、covers 追溯、Token 预算。瑕疵：引用 `project-map.md`（F1） |
| 7 | `agents/executor.md` | executor | Write/Edit/Bash/Glob/Grep/LS/Read | inherit | red | `workflow/references/agent-dispatch-code.md`、`execute/SKILL.md` | 精确：注入上下文自检、命令输出摘要策略、resume_from 协议完善 |
| 8 | `agents/code-reviewer.md` | code-reviewer | Glob/Grep/LS/Read/WebFetch/WebSearch/Bash | inherit | yellow | `execute/SKILL.md:201`、`test/references/code-reviewer.md`、`commands/code-review.md` | 精确：分层置信度阈值、多视角轮换、三深度层级 |
| 9 | `agents/tester.md` | tester | Write/Edit/Bash/Glob/Grep/LS/Read | inherit | purple | `test/SKILL.md:44`、`workflow/SKILL.md` | 精确：环境检查、失败诊断、契约验证流程完整 |
| 10 | `agents/contract-creator.md` | contract-creator | Write/Edit/Bash/Glob/Grep/LS/Read | inherit | green | `contract/SKILL.md:46` | 精确：六维度审查表、PASS/FAIL 判定清晰 |
| 11 | `agents/exception.md` | exception | Write/Edit/Bash/Glob/Grep/LS/Read | inherit | red | `exception/SKILL.md:32`、execute 子过程 | 精确：零硬编码、四类型场景表、多语言适配 |
| 12 | `agents/archiver.md` | archiver | Write/Edit/Bash/Glob/Grep/LS/Read | inherit | green | `archive/SKILL.md:57` | 精确：冲突四类型、合并五策略、安全约束 |
| 13 | `agents/knowledge-curator.md` | knowledge-curator | Write/Edit/Bash/Glob/Grep/LS/Read | inherit | purple | `continuous-learning/SKILL.md:90,222` | 精确：6 阶段流程、A/B 实验、进化规则完整 |

### 1.2 扩展能力 Agents（12 个，与 AGENTS.md 一致）

| # | 文件 | name | tools | model | color | Skill/流程引用 | 质量评估 |
|---|------|------|-------|-------|-------|---------------|---------|
| 14 | `agents/clarifier.md` | clarifier | Read/Write/Grep/Glob | inherit（约束 Opus+temp0.1） | 无 | `clarify/SKILL.md:102` | 精确：评分维度权重表、JSON 输出格式 |
| 15 | `agents/debug.md` | debug | Grep/Glob/Read/Bash | inherit | 无 | `debug/SKILL.md:35`、workflow 辅助 | 精确：多假设竞争 + 证据强度排序 + 反驳回合 |
| 16 | `agents/test-verifier.md` | test-verifier | Bash/Grep/Read/Glob | inherit | 无 | `agent-dispatch-code.md:208` | 精确：证据层级、不接受历史输出 |
| 17 | `agents/goal-evaluator.md` | goal-evaluator | Bash/Grep/Read/Glob | inherit | 无 | `ralph-loop` references | 精确：逐项评分 + 交叉验证 + JSON 报告 |
| 18 | `agents/e2e-runner.md` | e2e-runner | Read/Write/Edit/Bash/Grep/Glob | inherit | 无 | `workflow/SKILL.md:146`（辅助） | 精确：POM、flaky 隔离、artifact 管理 |
| 19 | `agents/loop-operator.md` | loop-operator | Read/Grep/Glob/Bash/Edit | inherit | orange | `workflow/SKILL.md:147`、`ralph-loop` | 精确：停滞检测、升级条件、集成表 |
| 20 | `agents/planner.md` | planner | Read/Grep/Glob | inherit | 无 | `workflow/SKILL.md:148`（辅助） | 精确：分阶段计划模板。瑕疵：Prompt Defense 重复（F5） |
| 21 | `agents/doc-updater.md` | doc-updater | Read/Write/Edit/Bash/Grep/Glob | inherit | 无 | 无 skill 引用 | 精确。瑕疵：Prompt Defense 重复（F5） |
| 22 | `agents/comment-analyzer.md` | comment-analyzer | Read/Grep/Glob | inherit | 无 | 无 skill 引用 | 较薄。瑕疵：Prompt Defense 重复（F5） |
| 23 | `agents/conversation-analyzer.md` | conversation-analyzer | Read/Grep | inherit | 无 | `/hookify`（orch 无此命令） | 较薄。瑕疵：Prompt Defense 重复（F5）；引用外部命令 `/hookify`（F12） |
| 24 | `agents/code-cleaner.md` | code-cleaner | Read/Write/Edit/Bash/Grep/Glob | inherit | 无 | 无 skill 引用 | 精确：三模式 + GATE。瑕疵：Prompt Defense 重复（F5）、无 color |
| 25 | `agents/tdd-guide.md` | tdd-guide | Read/Write/Edit/Bash/Grep | inherit | 无 | `agent-dispatch-code.md:182`、`flow-execution-reference.md:35` | **孤立**：不在 AGENTS.md 注册表；职责已被 code-reviewer 维度3吸收（code-reviewer.md 标注"原 tdd-guide 职责"）。建议标注 deprecated 或移除引用（F2） |

> 注：`contract-creator` 同时出现在 AGENTS.md 核心表与扩展表（重复登记，仅口径问题）。

### 1.3 模板文件（非 Agent）

| 文件 | 用途 |
|------|------|
| `agents/_prompt-defense.md` | Prompt Defense Baseline 单一来源，`scripts/sync-prompt-defense.py` 同步到各 agent |

---

## 2. Commands 清单（14 个，与 CLAUDE.md 口径一致）

| # | 文件 | 命令名 | 用途 | 调用 skill/agent |
|---|------|--------|------|-----------------|
| 1 | `commands/start-dev.md` | /start-dev | SDD+TDD 统一入口，13 步流程编排 | `Skill("orch:workflow")` |
| 2 | `commands/checkpoint.md` | /checkpoint | 命名检查点 create/verify/list，集成 `.workflow-state.json` | 无（shell 流程） |
| 3 | `commands/context-budget.md` | /context-budget | 上下文窗口 Token 审计 | 无（手动估算，非 `Skill("orch:context-budget")`） |
| 4 | `commands/code-review.md` | /code-review | 本地/PR 两阶段审查 | `Agent(subagent_type="orch:code-reviewer")` |
| 5 | `commands/plan.md` | /plan | 从 spec/design/tasks 生成实施计划 | 无（planner agent 可选） |
| 6 | `commands/quality-gate.md` | /quality-gate | HARD-GATE 质量管道（规范+覆盖+质量） | 无（shell 命令，手动触发） |
| 7 | `commands/req-change.md` | /req-change | 需求变更影响分析 + 增量调整 | `Skill("orch:req-change")` |
| 8 | `commands/session-resume.md` | /session-resume | 人工驱动工作流恢复 | 无（读取 session 文件 + state） |
| 9 | `commands/session-save.md` | /session-save | 保存会话 + 工作流状态 | 无 |
| 10 | `commands/spec-migrate.md` | /spec-migrate | 规范迁移导入主库 | `Skill("orch:spec-migrate")` |
| 11 | `commands/cost-report.md` | /cost-report | 成本报告（轻量包装） | 委托 `Skill("orch:cost")` |
| 12 | `commands/instinct-export.md` | /instinct-export | 导出 optimization.rules[] | 无（读 preferences.json） |
| 13 | `commands/instinct-import.md` | /instinct-import | 导入优化规则（去重/校验） | 无（写 preferences.json） |
| 14 | `commands/instinct-status.md` | /instinct-status | 查看进化规则状态 | 无（读 preferences.json） |

**评估**：
- 入口命令 `start-dev` 有明确 GATE（禁止调用 workflow 前探索），调度表完整。
- 7 个命令是纯 shell 流程（checkpoint/context-budget/plan/quality-gate/session-*），未委托 skill/agent。
- `plan`、`quality-gate`、`session-resume`、`start-dev` 等命令名同时出现在 `stage-gate.js` 的 EXEMPT_SKILLS 中（F9：命令/skill 命名空间混用，无害但易误导维护者）。
- `conversation-analyzer` 描述引用的 `/hookify` 命令在 orch commands/ 中不存在（外部来源残留，F12）。

---

## 3. Hooks 注册审计（hooks/hooks.json）

### 3.1 已注册（6 个注册项，5 个事件）

| 事件 | matcher | id | 脚本路径 | 用途 | 超时 | 状态 |
|------|---------|----|---------|------|------|------|
| SessionStart | * | `session:init` | `scripts/hooks/session-start.js` | 检测未完成工作流 + 状态恢复提示 | 10s | 脚本存在 ✓ 已注册 ✓ |
| PreToolUse | Skill | `pretool:stage-gate` | `scripts/hooks/stage-gate.js` | 阶段门控：前置未完成则 deny | 5s | 脚本存在 ✓ 已注册 ✓ |
| PostToolUse | Skill\|Agent | `posttool:hard-gate` | `scripts/hooks/workflow-gate.js` | HARD-GATE 校验（fail-open）+ 串行降级检测 | 5s | 脚本存在 ✓ 已注册 ✓ |
| PreCompact | * | `precompact:state` | `scripts/hooks/pre-compact.js` | compact 前保存状态检查点 | 5s | 脚本存在 ✓ 已注册 ✓ |
| Stop | * | `stop:evaluate` | `scripts/hooks/session-evaluate.js` | 会话评估 + 工作流持续化检测 | 10s | 脚本存在 ✓ 已注册 ✓ |
| Stop | * | `stop:cost-tracker` | `scripts/hooks/cost-tracker.js` | Token/成本追踪（JSONL+SQLite） | 10s | 脚本存在 ✓ 已注册 ✓ |

### 3.2 异常项

| 项 | CLAUDE.md 声明 | hooks.json 实际 | 文件是否存在 | 结论 |
|----|--------------|----------------|------------|------|
| instinct 观察 | PreToolUse + PostToolUse → `observe.sh` | **未注册** | **observe.sh 不存在**（全库 glob 无结果） | **配置死引用**：CLAUDE.md 与 `hook-flags.js` 的 PROFILES 均含 `pre:observe`/`post:observe`，但 hooks.json 从未注册，observe.sh 也不存在。instinct 观察层实际未生效（F4） |
| compact 建议 | PreToolUse (Edit/Write) → `suggest-compact.js` | **未注册** | `scripts/hooks/suggest-compact.js` 存在 | **有脚本未注册**：suggest-compact.js 已实现（阈值 40 次 Edit/Write 提示 /compact），但 hooks.json 无对应注册项，功能未激活（F3） |
| strict profile | — | — | `hook-flags.js` PROFILES.strict 含 `stop:workflow-check` | 该 id 无对应注册 hook，strict 配置中为死 id |

### 3.3 Hook 脚本自身评估

| 脚本 | 功能 | 缺陷/风险 |
|------|------|----------|
| `stage-gate.js` | Skill 前置阶段阻断，fail-open | `SKILL_PREREQUISITES` 硬编码；`EXEMPT_SKILLS` 混入命令名（F9）；读 stdin 用阻塞 `readFileSync(fd)` 循环，无超时（与 `stdin.js` 的 timeout 防护不一致） |
| `workflow-gate.js` | 阶段顺序 + 产出文件 + 串行降级检测 | `STAGE_OUTPUTS` 仅覆盖 0/1/4/7 四阶段（缺 3.5/5/6/9），校验不完整（F10） |
| `session-start.js` / `pre-compact.js` / `session-evaluate.js` | 均用 `isHookEnabled` 门控 | 一致；fail-open |
| `cost-tracker.js` | 读 transcript 累计 token → JSONL+SQLite + 桥接 eval.json | 依赖外部 `sqlite3` CLI（无则降级 JSONL）；Stop 输入按协议透传 |
| `suggest-compact.js` | Edit/Write 计数 → 建议 /compact | 未注册（F3）；计数器文件写 `cwd/.claude/.compact-counter`，多工作流共享 |

---

## 4. Scripts 运行时脚本清单

### 4.1 scripts/lib（8 个，均为纯 Node，无缺失依赖）

| 文件 | 功能 | 依赖 |
|------|------|------|
| `resolve-root.js` | 解析插件根目录（env→标准安装→plugin→cache→fallback） | 无 |
| `project-detect.js` | 技术栈/测试框架/包管理器检测 | 无 |
| `state-store.js` | 读写 `.workflow-state.json` / `.workflow-eval.json`，stage token 更新 | 无 |
| `utils.js` | ensureDir / glob / timestamp | 无 |
| `hook-runner.js` | 安全 hook 执行器（超时 30s、fail-open、路径穿越防护、Windows 兼容） | 无 |
| `stdin.js` | 安全 stdin 读取（2s 超时防护） | 无 |
| `hook-flags.js` | hook 开关 profile 门控（minimal/standard/strict + SDD_DISABLED_HOOKS） | 无 |
| `cost-db.js` | 成本库：JSONL+SQLite 双写、外部 pricing.json、execFileSync 免 shell | 外部 `sqlite3` CLI、`git` |

### 4.2 scripts/hooks（7 个，见 §3.3）

### 4.3 根级脚本

| 文件 | 功能 | 引用方 |
|------|------|--------|
| `generate-completion-data.py` | 从 `.workflow-eval.json` 提取完成报告预填数据 | `agents/completion-reporter.md` |
| `sync-prompt-defense.py` | 同步 `_prompt-defense.md` 到各 agent | `agents/_prompt-defense.md` |
| `scripts/__pycache__/generate-completion-data.cpython-312.pyc` | Python 编译缓存 | **已提交到 git 的构建产物**（F11） |

**依赖检查结论**：全部 `require()` 均指向内部 `scripts/lib` / `scripts/hooks` 且文件存在，无缺失依赖。外部依赖仅 `sqlite3` CLI 与 `git`（预期内）。

---

## 5. 关键发现与薄弱环节（能力优化候选）

> 编号 F1-F12 供 design/task 阶段直接引用。

### F1 — project-map 文件名不一致（3 处 .md 错误引用）
`code-explorer` 实际产出 `req-context/project-map.json`，但 `agents/code-architect.md:19`、`agents/tasker.md:13`、`skills/design/SKILL.md:45` 均引用 `req-context/project-map.md`。下游 design/task 阶段会读不到文件。
**影响**：架构设计与任务拆解阶段上下文注入失败风险，直接拉低产出达标率。
**修复**：统一为 `.json`。

### F2 — tdd-guide 孤立 agent
`agents/tdd-guide.md` 存在且被 `agent-dispatch-code.md`、`flow-execution-reference.md` 引用，但不在 `AGENTS.md` 注册表（25 个），职责已被 `code-reviewer` 维度 3 吸收。注册表口径（CLAUDE.md=25 / AGENTS.md=25）与磁盘实际 26 个不符。
**影响**：Agent 清单口径混乱，可能被重复派遣或遗漏。
**修复**：从 dispatch 引用中移除 tdd-guide，或恢复注册并明确与 code-reviewer 的边界。

### F3 — suggest-compact.js 有脚本未注册
实现已存在但 hooks.json 无 PreToolUse(Edit/Write) 注册项，compact 建议功能未激活。
**影响**：逻辑边界 compact 建议失效（CLAUDE.md 宣称存在）。
**修复**：hooks.json 补注册项，或从 CLAUDE.md 移除声明。

### F4 — instinct 观察 hooks 死配置（observe.sh 缺失）
CLAUDE.md 宣称 PreToolUse/PostToolUse observe.sh，`hook-flags.js` PROFILES 含 `pre:observe`/`post:observe`，但 observe.sh 文件不存在且 hooks.json 未注册。continuous-learning v2 的 instinct 学习观察层实际未运行。
**影响**：instinct 学习数据源缺失，知识复利仅依赖 Stop 钩子，观察事件丢失。
**修复**：实现 observe.sh 并注册，或清理 hook-flags/CLAUDE.md 死引用。

### F5 — 8 个 agent 的 "## Prompt Defense Baseline" 重复
code-cleaner / comment-analyzer / conversation-analyzer / doc-updater / e2e-runner / loop-operator / planner / tdd-guide 均出现 2 次该节。`_prompt-defense.md` 是单一来源，说明 `sync-prompt-defense.py` 同步逻辑未检测已有节导致重复插入。
**影响**：agent 上下文冗余，每次派遣加载重复指令。
**修复**：修复 sync 脚本幂等性 + 清理已重复文件。

### F6 — CLAUDE.md 钩子表与 hooks.json 脱节
CLAUDE.md 钩子表仍写 observe.sh / suggest-compact.js，与实际注册不符（F3/F4 的根因之一）。文档与实现漂移。

### F7 — 部分 agent frontmatter 稀疏
workflow / spec 无 tools/model/color；completion-reporter / debug / test-verifier / goal-evaluator / clarifier 无 color。社区来源 7 个 agent 的 tools 用数组语法（`["Read",...]`），本地 13 个用逗号语法（`Glob, Grep`）——两种风格并存，需统一。

### F8 — code-architect.md 重复 `### 0.` 编号
两处 `### 0.`（"共识式审查参与" 与 "读取项目上下文"），应为 0 与 1。

### F9 — stage-gate EXEMPT_SKILLS 混入命令名
checkpoint / code-review / plan / quality-gate / session-resume / session-save / start-dev 是命令名而非 Skill 名，混入 Skill 豁免表。当前无害（Skill 调用不会以这些名字出现），但易误导维护者。

### F10 — workflow-gate STAGE_OUTPUTS 校验不完整
仅校验 0/1/4/7 四个阶段的产出，缺 3.5/5/6/9。与 `stage-gate.js` 的完整 SKILL_PREREQUISITES 不对称。

### F11 — __pycache__/.pyc 已提交
`scripts/__pycache__/generate-completion-data.cpython-312.pyc` 在仓库中，应加 .gitignore。

### F12 — 命令/Agent 命名空间混用
`conversation-analyzer` 引用 `/hookify`（orch 无此命令）；`cost-report` 是薄包装委托 `Skill("orch:cost")` 的模式值得推广（避免 SQL 模板重复维护）。

---

## 6. 与元任务验收标准的关联（现状基线）

| 元任务验收标准 | 现状基线（本审计证据） |
|---------------|----------------------|
| 自动流转率 ≥80% | stage-gate/workflow-gate 已实现阶段门控，但 workflow-gate 产出校验不完整（F10）、instinct 观察缺失（F4）、中断恢复仅靠 session-start/stop 提示，无自动补偿动作 |
| 产出达标率 ≥90% | 审查能力已集中到 code-reviewer（单次综合），但 project-map 文件名错误（F1）会导致 design/task 上下文注入失败，直接拉低达标率 |
| 容错自动恢复率 ≥80% | 脚本全部 fail-open ✓；但 suggest-compact 未激活（F3）、stage-gate 读 stdin 无超时（§3.3） |
| 每块有验证闭环 | **无插件自检命令**：agents/commands/hooks/scripts 均无测试或自检脚本（test_targets 为空）。这是最大缺口 |
| 智能判定生效 | 规则自决机制散落在 cost-db/state-store 中，无统一 gate 判定框架 |

---

## 附：文件路径索引

- Agent 定义：`E:\YYWorkSpace\projects\orch\agents\*.md`（26+1）
- 命令定义：`E:\YYWorkSpace\projects\orch\commands\*.md`（14）
- Hook 注册表：`E:\YYWorkSpace\projects\orch\hooks\hooks.json`
- Hook 脚本：`E:\YYWorkSpace\projects\orch\scripts\hooks\*.js`（7）
- 运行时库：`E:\YYWorkSpace\projects\orch\scripts\lib\*.js`（8）
- 根级脚本：`E:\YYWorkSpace\projects\orch\scripts\generate-completion-data.py`、`sync-prompt-defense.py`
- Agent 注册表：`E:\YYWorkSpace\projects\orch\AGENTS.md`
