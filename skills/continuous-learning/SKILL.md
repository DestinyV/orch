---
name: continuous-learning
description: |
  知识复利引擎 v2 — 从工作流执行记录中提取关键决策和模式，沉淀到知识库，增强下次需求。
  新增 instinct 架构：hook 级会话观察 + 原子 instincts + 置信度评分 + 项目级隔离。
  输入：.workflow-eval.json + patterns/ + user-preferences/ + hook observations
  输出：更新的 instinct/{personal,inherited}/ + pattern-index.json + preferences.json + 知识提炼报告
---

# knowledge-continuum v2 — 知识复利引擎

## When to Use

- 工作流归档完成后自动触发（post-spec-archive）
- 需要从工作流中提取模式、沉淀知识
- 需要查看或管理 instincts（原子学习单元）

## How It Works

双架构并行：
- Layer 1（Workflow Knowledge）：工作流结束后，从 .workflow-eval.json 提取决策数据，匹配 patterns/，更新 preferences/
- Layer 2（Instinct Learning）：通过 hook 实时观察会话，自动创建原子 instincts 并置信度评分

## 双架构概览

```
                    ┌─────────────────────────────────────┐
                    │   Layer 1: Workflow Knowledge (v1)   │
                    │   工作流结束后触发 (post-spec-archive)  │
                    │   patterns/ + user-preferences/      │
                    └─────────────────────────────────────┘
                                        +
                    ┌─────────────────────────────────────┐
                    │   Layer 2: Instinct Learning (v2)    │
                    │   Hook 级实时观察 (PreToolUse/Post)   │
                    │   observations → instincts → evolve   │
                    └─────────────────────────────────────┘
```

**v1**（现有）: 工作流级知识复利，spec → patterns → distill → refresh
**v2**（新增）: 会话级 instinct 学习，hook 观察 → 原子 instincts → 置信度 → 进化

## 核心原则

知识复利是**辅助增强**，不是流程省略。每次新需求完整执行全部流程，知识库用于"补充遗漏维度"而非"跳过步骤"。

<HARD-GATE>禁止因历史经验而跳过任何确认步骤</HARD-GATE>
<HARD-GATE>每次新需求必须完整执行全部流程</HARD-GATE>

---

## Layer 1: Workflow Knowledge (v1 — 原有流程)

### 知识分类体系

每次知识沉淀按以下分类体系归档：

**分类**：
- `durable_fact` — 持久项目事实（架构决策、约定、约束）
- `temporary_note` — 临时笔记（当前需求上下文，下次过后可清理）
- `preference` — 用户偏好（选择倾向、工作习惯）
- `duplicate` — 重复内容（与已有模式冲突，需合并或丢弃）

**质量门**（`durable_fact` 和 `preference` 必须通过）：
- 非通用可搜索（不能是 Google 能找到的标准做法）
- 项目特有（必须是本次需求的独特决策或模式）
- 来之不易（必须是通过 HARD-GATE / 用户纠错 / 重复返工学到的）

**目标存储**：
| 分类 | 目标 |
|------|------|
| `durable_fact` | `patterns/*.md` 历史教训章节 |
| `temporary_note` | 不持久化，仅在当前需求上下文使用 |
| `preference` | `user-preferences/preferences.json` |
| `duplicate` | 合并到已有模式，或标记废弃 |

### 输入依赖校验

```bash
test -f spec-dev/{req}/.workflow-eval.json || echo "[WARN] .workflow-eval.json 缺失"
python3 -c "import json; d=json.load(open('spec-dev/{req}/.workflow-eval.json')); assert d.get('diagnosis')" || echo "[INFO] diagnosis 为空"

test -f "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/patterns/pattern-index.json" || echo "[WARN] pattern-index.json 缺失"
```
WARN → 降级为"仅索引初始化"，不阻塞流程。

### 知识复利 Agent 派遣

<HARD-GATE>必须通过 Agent 派遣 knowledge-curator，不允许主上下文直接执行</HARD-GATE>

```bash
Agent(
  subagent_type="orch:knowledge-curator",
  prompt="执行知识复利流程：1. 收集 .workflow-eval.json 数据 2. 识别 patterns/pattern-index.json 模式 3. 沉淀更新 4. 提炼 5. 自适应更新 preferences.json",
  run_in_background=false
)
```

详见 `../../agents/knowledge-curator.md`。

### 产出校验

```bash
python3 -c "
import json, os
idx = json.load(open(os.path.join(os.environ['CLAUDE_PLUGIN_ROOT'], 'skills/continuous-learning/patterns/pattern-index.json')))
freq = sum(p.get('frequency', 0) for p in idx.get('patterns', []))
print(f'patterns: {len(idx[\"patterns\"])} | total_frequency: {freq}')
" || echo "[WARN] pattern-index.json 未更新"

test -f "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/user-preferences/preferences.json" || echo "[WARN] preferences.json 缺失"
```

### 反馈闭合

workflow-control 步骤0 加载 `preferences.json` → `always_check[]` 注入 spec-creation 追问清单。

### 输出清单

- `patterns/pattern-index.json` — 更新频次和最后使用时间
- `patterns/*.md` — 更新历史教训（10 个维度）
- `user-preferences/preferences.json` — 更新 always_check + preference_history

---

## Layer 2: Instinct Learning (v2 — 新增)

### 架构

```
Session Activity
      │
      │ hooks/observe.sh (PreToolUse/PostToolUse, 100% reliable)
      v
observations.jsonl (project-scoped)
      │
      │ Background Observer (Haiku, configurable)
      v
Pattern Detection:
  • HARD-GATE triggers → resolutions
  • User corrections → preferences
  • Repeated sequences → workflows
  • Consistency choices → defaults
      │
      v
instincts/personal/<id>.yaml  (atomic, confidence-scored)
      │
      │ /evolve → cluster → promote
      v
evolved/{skills,commands,agents}/
```

### 快速开始

#### 1. Enable Observation Hooks

**Plugin install**: hooks/observe.sh 通过 plugin hooks/hooks.json 自动加载。

**Manual install**: 在 `~/.claude/settings.json` 添加：

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/hooks/observe.sh" }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/hooks/observe.sh" }]
    }]
  }
}
```

#### 2. 初始化目录

```bash
mkdir -p "${KNC_HOMUNCULUS_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/knc-homunculus}"/{instincts/{personal,inherited},evolved/{agents,skills,commands},projects}
```

#### 3. 管理 Instincts

```bash
# 查看所有 instincts
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" status

# 集群进化
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" evolve

# 提升到全局
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" promote [id]

# 导出/导入
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" export -o my-instincts.json
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" import my-instincts.json

# 清理过期
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" prune --days 30

# 项目列表
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" projects
```

### Instinct 模型

原子学习单元：

```yaml
---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.7
domain: "code-style"
source: "session-observation"
scope: project
project_id: "a1b2c3d4e5f6"
project_name: "my-react-app"
---

# Prefer Functional Style

## Action
Use functional patterns over classes when appropriate.

## Evidence
- Observed 5 instances of functional pattern preference
- User corrected class-based approach to functional on 2026-05-23
- Last observed: 2026-05-23
```

**属性**:
- **Atomic** — 一个触发条件，一个动作
- **Confidence-weighted** — 0.3 (tentative) ~ 0.9 (near-certain)
- **Domain-tagged** — workflow, code-quality, testing, design, process
- **Evidence-backed** — 追踪创建来源
- **Scope-aware** — project (default) 或 global

### 置信度评分

| Score | Meaning | Behavior |
|-------|---------|----------|
| 0.3 | Tentative | Suggested but not enforced |
| 0.5 | Moderate | Applied when relevant |
| 0.7 | Strong | Auto-approved for application |
| 0.9 | Near-certain | Core behavior |

**Increase** when: pattern repeatedly observed, user doesn't correct
**Decrease** when: user explicitly corrects, pattern not observed for extended periods

### 范围决策

| Pattern Type | Scope | Examples |
|-------------|-------|---------|
| Workflow preferences | **project** | "HARD-GATE resolution strategy", "skill sequence" |
| Code style | **project** | "Use functional style" |
| Error handling | **project** | "Use Result type" |
| Security practices | **global** | "Validate user input" |
| General best practices | **global** | "Grep before Edit" |
| Git practices | **global** | "Conventional commits" |

### 升级 (Project → Global)

Same instinct in 2+ projects with confidence ≥ 0.8 → auto-promotion candidate.

```bash
# 预览
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" promote --dry-run

# 执行
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" promote
```

### 配置

`config.json`:

```json
{
  "version": "2.0",
  "observer": {
    "enabled": false,
    "run_interval_minutes": 5,
    "min_observations_to_analyze": 20
  },
  "instinct": {
    "min_confidence_for_apply": 0.5,
    "promote_min_confidence": 0.8,
    "promote_min_projects": 2
  },
  "distill": {
    "core_frequency_threshold": 3,
    "similarity_merge_threshold": 70
  },
  "refresh": {
    "expire_days": 30
  }
}
```

### 文件结构

```
${KNC_HOMUNCULUS_DIR:-~/.local/share/knc-homunculus}/
├── config.json                  # 运行时配置
├── observations.jsonl           # 全局观察日志
├── instincts/
│   ├── personal/                # 全局 auto-learned instincts
│   └── inherited/               # 全局 imported instincts
├── evolved/
│   ├── agents/
│   ├── skills/
│   └── commands/
└── projects/
    └── <project-hash>/
        ├── observations.jsonl
        ├── observations.archive/
        ├── instincts/
        │   ├── personal/
        │   └── inherited/
        ├── evolved/
        └── .observer.pid
```

## 关键约束

- ✅ 记录每次工作流关键决策 | 每 3 个需求执行一次提炼 | 每 30 天执行一次刷新
- ✅ Instincts 仅作为建议层，不得跳过确认步骤
- ✅ 首次运行自动创建所有目录，不报错
- ❌ 禁止自动修改偏好不确认 | 禁止因历史经验跳过确认步骤

## 参考文档速查

| 文档 | 场景 |
|------|------|
| `references/continuous-learning.md` | 完整参考（能力矩阵、设计决策表） |
| `scripts/instinct-cli.py` | Instinct CLI 管理工具 |
| `agents/observer.md` | Background observer agent 详情 |
| `hooks/observe.sh` | Hook 级观察实现 |
| `config.json` | 运行时配置 |

## Layer 3: Solution Documentation（新增）

在工作流完成后，将具体问题和解决方案捕获为结构化文档，作为抽象 patterns 的实例补充。

### 架构

```
[workflow 完成] → [knowledge-curator Agent]
  │
  ├── Layer 1: patterns/（抽象模式更新）
  ├── Layer 2: instincts/（原子学习）
  └── Layer 3: solutions/（解决方案文档）
        │
        ├── 并行派遣 3 子代理：
        │   1. Context Analyzer — 确定 track/category
        │   2. Solution Extractor — 提取解决方案内容
        │   3. Related Docs Finder — 扫描重叠检测
        │
        ├── 重叠检测 → 写入或更新文档
        ├── frontmatter 安全验证
        └── Discoverability Check
```

### 输出路径

`spec-dev/{req_id}/knowledge/solutions/{category}/{slug}.md`

### 计划扩展

当前以 knowledge-curator Agent 提示词形式集成。未来可扩展为独立子代理流程。

## 与 workflow-control 的集成

workflow-control 步骤0 初始化时，从两个来源加载增强：
1. `preferences.json` → `always_check[]` → spec-creation 追问清单
2. `instincts/` → 高置信度工作流 instincts → 注入 HARD-GATE 策略建议
