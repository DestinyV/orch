# 架构

> 全量探索产出（2026-08-01）。记录插件自身架构分层、模块划分与文件树。当前版本 v0.10.0。

## 整体分层

```
orch/  （插件根目录）
├── skills/            # 22 个 Skill（工作流核心单元 + 工具 + 扩展）
├── agents/            # 26 个 Agent + 1 个辅助文件（_prompt-defense.md）
├── commands/          # 14 个斜杠命令
├── hooks/hooks.json   # Hook 注册表（SessionStart/PreToolUse/PostToolUse/PreCompact/Stop）
├── scripts/           # 运行时脚本（hooks/ + lib/ + 2 个 Python 工具）
├── config/            # 项目栈/平台/澄清参数配置
├── schemas/           # JSON Schema（workflow-state/eval/deliverables）
├── rules/             # 代码规则（common/typescript/python/zh）
├── references/        # 多平台工具映射（cursor/codebuddy）
├── templates/hooks/   # Hook 模板（post-tool-use/pre-tool-use/session-start）
├── docs/              # 双语文档（zh/en）
├── .claude-plugin/    # 插件元数据（plugin.json/marketplace.json）
├── .cursor/ .gemini/ .opencode/ .codex/ .codebuddy/  # 多平台适配目录
├── tests/             # 插件自身测试（Python + 压力场景）
└── orch-spec/         # 工作流输出目录（项目级 context + 各需求目录）
    ├── context/       # 项目级上下文注册中心（index.json + 各 section）
    ├── spec/          # 主规范库
    └── {req_id}/      # 各需求工作目录（.workflow-state.json + spec/ + req-context/ + ...）
```

## 分层职责

| 层 | 目录 | 职责 |
|----|------|------|
| 定义层 | skills/ agents/ commands/ | 全部可调用能力（Markdown 定义 + frontmatter） |
| 编排层 | skills/workflow/ commands/start-dev.md | 13 步工作流编排、状态机、Agent 派遣 |
| 运行时层 | scripts/hooks/ scripts/lib/ | Hook 实现 + 状态/成本/门控工具库 |
| 校验层 | hooks/hooks.json schemas/ rules/ | Hook 注册、Schema 校验、编码规则 |
| 配置层 | config/ .claude-plugin/ | 插件元数据、平台/栈/澄清参数 |
| 持久层 | orch-spec/context/ orch-spec/{req_id}/ | 跨需求知识 + 单需求工作产物 |

## Skills 模块（22 个）

| Skill | 目录 | 类型 | 职责 |
|-------|------|------|------|
| workflow | skills/workflow/ | 编排 | 统一入口 + 流程编排 + 状态机 |
| clarify | skills/clarify/ | 前置 | 苏格拉底需求澄清（模糊度 > 0.2 触发） |
| spec | skills/spec/ | 核心 | 需求分析 + BDD 规范生成 |
| test-design | skills/test-design/ | 核心 | 测试规范 + fixtures + test-*.template |
| design | skills/design/ | 核心 | 架构/技术设计（数据库先行 + 契约驱动） |
| contract | skills/contract/ | 核心 | 接口契约定义与审查（fullstack 强制） |
| task | skills/task/ | 核心 | 设计到任务拆解（DAG + provides/consumes） |
| execute | skills/execute/ | 核心 | TDD 代码实现 + git-worktree 隔离 + 两阶段审查 |
| exception | skills/exception/ | 核心 | 异常模式扫描 + 代码生成（后端/全栈自动） |
| test | skills/test/ | 核心 | 集成/E2E/性能测试 + 闭环验证 |
| archive | skills/archive/ | 核心 | 规范归档合并 + context 同步 |
| continuous-learning | skills/continuous-learning/ | 核心 | 知识复利 + 自主进化规则 |
| scripts | skills/scripts/ | 工具 | 工具优先策略（脚本化文件操作） |
| spec-migrate | skills/spec-migrate/ | 工具 | 规范迁移导入 |
| using-orch | skills/using-orch/ | 工具 | 使用指引（多平台工具映射） |
| context-budget | skills/context-budget/ | 扩展 | 上下文窗口审计 |
| depth | skills/depth/ | 扩展 | 响应深度控制 |
| compact | skills/compact/ | 扩展 | 逻辑边界 compact 建议 |
| cost | skills/cost/ | 扩展 | Token 成本追踪查询 |
| ralph-loop | skills/ralph-loop/ | 扩展 | 自主循环模式选择 |
| debug | skills/debug/ | 扩展 | 证据驱动因果追踪 |
| req-change | skills/req-change/ | 扩展 | 需求变更管理 |

**Skill 目录通用结构**：SKILL.md + references/ + templates/（部分含 prompts/ patterns/ assets/）。

## Agents 模块（26 个 + 辅助）

### 工作流核心（13）
workflow / spec / code-explorer / test-designer / code-architect / tasker / executor / code-reviewer / tester / exception / knowledge-curator / completion-reporter / archiver

### 扩展能力（12）
code-cleaner / comment-analyzer / conversation-analyzer / contract-creator / debug / doc-updater / e2e-runner / goal-evaluator / loop-operator / planner / test-verifier / clarifier

### 其他
tdd-guide（TDD 执行引导）、_prompt-defense.md（Prompt 防御辅助，非 Agent）

## Commands 模块（14 个）

| Command | 文件 | 类型 |
|---------|------|------|
| /start-dev | commands/start-dev.md | 工作流入口 |
| /plan | commands/plan.md | 实现计划 |
| /code-review | commands/code-review.md | 代码审查 |
| /checkpoint | commands/checkpoint.md | 工作流检查点 |
| /quality-gate | commands/quality-gate.md | HARD-GATE 质量门控 |
| /req-change | commands/req-change.md | 需求变更管理 |
| /session-save | commands/session-save.md | 会话保存 |
| /session-resume | commands/session-resume.md | 会话恢复 |
| /spec-migrate | commands/spec-migrate.md | 规范迁移导入 |
| /instinct-status | commands/instinct-status.md | 进化规则状态 |
| /instinct-export | commands/instinct-export.md | 进化规则导出 |
| /instinct-import | commands/instinct-import.md | 进化规则导入 |
| /context-budget | commands/context-budget.md | 上下文预算审计 |
| /cost-report | commands/cost-report.md | 成本报告 |

## Hooks 模块（5 事件 6 钩子）

| Hook ID | 事件 | Matcher | 脚本 | 职责 |
|---------|------|---------|------|------|
| session:init | SessionStart | * | scripts/hooks/session-start.js | 未完成工作流检测 + 状态恢复提示 |
| pretool:stage-gate | PreToolUse | Skill | scripts/hooks/stage-gate.js | 阶段门控（前置阶段未完成阻断 Skill） |
| posttool:hard-gate | PostToolUse | Skill或Agent | scripts/hooks/workflow-gate.js | HARD-GATE 校验（阶段顺序/产出文件/状态一致性），fail-open |
| precompact:state | PreCompact | * | scripts/hooks/pre-compact.js | Compact 前保存工作流状态 |
| stop:evaluate | Stop | * | scripts/hooks/session-evaluate.js | 会话评估 + 未完成检测 |
| stop:cost-tracker | Stop | * | scripts/hooks/cost-tracker.js | Token 成本采集（JSONL + SQLite 双写）+ eval 桥接 |

**Hook 辅助**：scripts/lib/hook-runner.js（超时/失败安全包装）、scripts/lib/hook-flags.js（档位控制：minimal/standard/strict）。

## 运行时工具库（scripts/lib/）

| 模块 | 职责 |
|------|------|
| state-store.js | 读写 .workflow-state.json / .workflow-eval.json，追加 stage，同步 token |
| cost-db.js | 成本 JSONL+SQLite 双写、定价外部化、transcript 解析 |
| hook-runner.js | 安全执行 hook（30s 超时、fail-open、路径穿越保护） |
| hook-flags.js | Hook 档位/profile 门控 |
| stdin.js | Hook stdin 读取 |
| utils.js | 通用工具（ensureDir 等） |
| resolve-root.js | 插件根目录解析 |
| project-detect.js | 项目类型检测 |

## 工作流编排（13 步）

```
/start-dev → Skill("orch:workflow")
  → 0   初始化（模式检测/状态恢复/优化规则注入/基线生成）
  → 0.5 clarify（模糊度 > 0.2）
  → 1   spec（code-explorer 探索 + BDD 规范）
  → 2   test-design ⟷ 3 design（并行）
  → 3.5 contract（fullstack）
  → 4   task（DAG 拆解）
  → 5   execute（TDD + git-worktree，批次并行）
  → 5.5 exception（后端/全栈）
  → 6   test（集成/E2E/性能 + 闭环验证）
  → 7   archive（主规范合并 + context 同步）
  → 8   evaluation（context-budget 预估 + cost DB 实记 双路并行）
  → 9   continuous-learning（knowledge-curator → completion-reporter）
```

## 上下文双层次

| 层次 | 路径 | 生命周期 | 生成 | 消费 |
|------|------|---------|------|------|
| 项目级 context | orch-spec/context/ | 跨需求持久 | archive 步骤同步 | 步骤1 Layer 1 关键词匹配 |
| 需求级 req-context | orch-spec/{req_id}/req-context/ | 单次工作流 | 步骤1 末尾（code-explorer） | design → execute → test |

## 状态持久化文件

| 文件 | 位置 | 内容 |
|------|------|------|
| .workflow-state.json | orch-spec/{req_id}/ | 阶段状态、进度、checkpoint、token_summary |
| .workflow-eval.json | orch-spec/{req_id}/ | stages[]/events[]/token_usage/diagnosis/learnings |
| .workflow-baseline.json | orch-spec/context/ | 跨需求执行基线 |
| preferences.json | orch-spec/user-preferences/ | always_check/rejected_approaches/optimization.rules[] |
| .exploration-state.json | orch-spec/context/ | 探索状态（SHA 追踪） |
| requirements.yaml | orch-spec/context/ | 历史需求相似度索引 |

## 关键参考文档（Source of Truth）

| 文档 | 角色 |
|------|------|
| skills/workflow/references/flow-execution-reference.md | 阶段契约唯一权威定义 |
| skills/workflow/references/agent-dispatch-code.md | Agent 派遣意图与验证 |
| skills/workflow/references/context-inheritance-protocol.md | 跨需求上下文复用协议 |
| skills/workflow/references/workflow-data-schema.md | 工作流 JSON 数据格式 |
| skills/workflow/references/token-tracking.md | Token 追踪协议 |
| skills/workflow/references/intra-workflow-adaptation.md | 批内微进化检查点 |
| skills/workflow/references/requirement-trace.md | 需求追溯 |
