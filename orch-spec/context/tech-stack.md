# 技术栈

> 全量探索产出（2026-08-01），来源：`README.md` / `.claude-plugin/plugin.json` / `hooks/hooks.json` / `scripts/**` / `config/**` / `schemas/**`

## 项目类型
Claude Code 插件（企业级 SDD+TDD 工作流编排引擎）。非独立应用，是运行于 Claude Code 的 SDK 插件。

## 语言分布

| 语言 | 用途 | 位置 |
|------|------|------|
| **Markdown** | 全部 Skill / Agent / Command 定义 + 文档 | `skills/` `agents/` `commands/` `docs/` `rules/` |
| **JavaScript (Node.js)** | 钩子实现 + 运行时工具库 | `scripts/hooks/*.js` `scripts/lib/*.js` |
| **Python 3** | 辅助数据提取脚本 + 压力测试套件 | `scripts/generate-completion-data.py` `scripts/sync-prompt-defense.py` `tests/test-suite.py` |
| **JSON** | 插件元数据 / 配置 / Schema / 状态持久化 | `.claude-plugin/` `config/` `schemas/` `*.json` |
| **YAML** | 上下文逻辑链 / 需求索引 / 文件映射 | `orch-spec/context/*.yaml` |

## 插件机制（Claude Code Plugin）

- **Manifest**：`.claude-plugin/plugin.json` — 只声明 `skills` + `commands` 目录 + 空 `mcpServers`
- **Agents 自动发现**：`agents/*.md` 按约定自动注册，**禁止**在 plugin.json 声明 `agents` 字段（会报 Invalid input）
- **Hooks 自动加载**：`hooks/hooks.json` 按约定自动加载，**禁止**在 plugin.json 重复声明（会报 Duplicate hooks file）
- **Skill 命名空间**：`Skill("orch:{name}")` / `Agent(subagent_type="orch:{name}")`
- **CLAUDE_PLUGIN_ROOT 环境变量**：钩子/脚本通过它定位插件根目录

## 运行时依赖

| 依赖 | 版本/要求 | 用途 |
|------|----------|------|
| Node.js | >= 18（脚本用 `fs/spawnSync` 等） | hooks + scripts |
| sqlite3 CLI | 外部二进制 | cost skill 查询 `usage.db` |
| Python 3 | 3.12 | completion 数据提取、压力测试 |
| Git | worktree / diff | execute 隔离工作区、增量探索 |

**零外部 npm 依赖**（成本追踪 JSONL+SQLite 双写，均用 Node 内置模块）。

## 存储与数据

| 存储 | 路径 | 用途 |
|------|------|------|
| SQLite | `~/.claude/orch-costs/usage.db` | 成本追踪（Stop hook 写入） |
| JSONL | `~/.claude/orch-costs/costs.jsonl` | 成本追踪主存储（零依赖） |
| JSON | `~/.claude/orch-costs/pricing.json` | 外部化定价覆盖（可选） |
| JSON Schema | `schemas/workflow-state.json` `workflow-eval.json` `deliverables.json` | 状态/评估/交付物校验 |
| 工作流状态 | `orch-spec/{req_id}/.workflow-state.json` | 阶段状态追踪 |
| 工作流评估 | `orch-spec/{req_id}/.workflow-eval.json` | 效果评估 + Token 用量 |
| 上下文注册中心 | `orch-spec/context/index.json` | 项目级 context section 索引 |

## 配置体系

| 配置 | 路径 | 内容 |
|------|------|------|
| 插件元数据 | `.claude-plugin/plugin.json` `marketplace.json` | 版本、描述、市场挂载 |
| 平台映射 | `config/platforms.json` | 6 平台 skill/agent/hook 能力映射 |
| 技术栈 | `config/stacks.json` | 前端/后端/数据库/移动/全栈框架清单 |
| 澄清参数 | `config/socratic-config.json` | 苏格拉底澄清阈值/轮次/权重 |
| Hook 档位 | `scripts/lib/hook-flags.js` | `SDD_HOOK_PROFILE` + `SDD_DISABLED_HOOKS` |

## 多平台适配

| 平台 | Skill 加载 | 子代理 | Hook |
|------|-----------|--------|------|
| Claude Code | `Skill("orch:{}")` | ✅ Agent | ✅ hooks.json |
| Cursor | `.cursor/rules/` | ❌ | ❌ |
| Gemini CLI | `activate_skill` | ❌ 串行 | ❌ |
| OpenCode | `.opencode/` skill/@mention | ✅ 子上下文 | ❌ |
| Codex | `.codex/AGENTS.md` + `rules/` | ✅ spawn_agent | `.codex/hooks.json` |
| CodeBuddy | `.codebuddy/` instruction | ✅ | ❌ |

## 测试体系（插件自身）
- `tests/test-suite.py` — Python 测试套件
- `tests/pressure-scenarios/` — 压力场景（时间压力/沉没成本/权威简化/穷尽验证）
- 无 Jest/前端测试（插件本体为 Markdown + Node 脚本）

## 构建/发布
- 无构建工具，纯 Markdown + 原生 Node 脚本
- 通过 Marketplace（`marketplace.json`）发布，`claude plugin validate .claude-plugin/plugin.json` 校验
