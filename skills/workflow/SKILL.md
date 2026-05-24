---
name: workflow
description: |
  统一入口 + 流程编排（Workflow-Control 阶段）
  输入：需求描述（文本或需求ID）
  输出：完整工作流执行 + .workflow-state.json（状态追踪）+ .workflow-eval.json（效果评估+Token用量）
  功能：SDD+TDD工作流的唯一入口，接收需求后自动编排所有下游Skill的执行顺序，
  支持模式自动检测、并行分支调度、HARD-GATE卡点管控、自动补偿、中断恢复、效果评估与Token追踪。
---

# workflow-control — 流程编排引擎


## When to Use

- 新需求入口，自动编排从需求到归档的完整流程
- 需要中断恢复、状态追踪、效果评估

## 职责

SDD+TDD 工作流的**入口编排器**。步骤控制 → `commands/start-dev.md`，内容管理 → 本文件。

> **Source of Truth**: 各阶段输入/输出契约、校验规则、失败纠正详见 [`references/flow-execution-reference.md`](references/flow-execution-reference.md)。

## 通用规则

| 规则 | 策略 |
|------|------|
| 失败处理 | 自动重试 1 次；仍失败 → AskUserQuestion（重试/跳过/人工/降级） |
| 状态持久化 | 每阶段完成后立即写入 `.workflow-state.json`，不依赖会话内存 |
| Token 记录 | 每阶段完成后调用 `context-budget` 记录上下文消耗，记录到 `.workflow-eval.json` |
| 上下文监控 | 阶段切换时检测上下文余量，不足时建议 compact 或精简后续步骤 |

<HARD-GATE>禁止在正式流程前执行代码探索，由 spec-creation 内部负责。</HARD-GATE>
<HARD-GATE>禁止跳过阶段。即使已有 spec 目录，也必须从步骤0开始，由状态检测决定中断恢复。</HARD-GATE>

---

## 步骤0: 初始化

1. 接收需求 → 检查 `spec-dev/` 下 `.workflow-state.json`（存在则中断恢复）
2. 自动推断 project-mode：

| 需求特征 | 推断 |
|---------|------|
| UI/页面/组件/交互 | frontend / fullstack |
| API/数据库/服务/存储 | backend / fullstack |
| UI + 后端同时涉及 | fullstack |

3. AskUserQuestion 确认：模式/数据库/快速或标准/设计图偏好
4. 加载知识增强 → `preferences.json` → `always_check[]` 注入 spec-creation
5. 初始化 `.workflow-state.json` + `.workflow-eval.json`
6. 检测需求模糊度 → 模糊 > 0.2 时派遣 `clarify`；否则级联 `spec`

### 步骤0.5: 苏格拉底澄清

<HARD-GATE>模糊度 > 0.2 时不允许跳过澄清。</HARD-GATE>

```bash
Skill("orch:clarify", args="{requirement_desc}")
```

产出校验：`clarification.md` 存在且含 `final_ambiguity`。完成后自动级联 `spec`。

### 流持续化检查

<HARD-GATE>检测到未完成状态时提示用户，不允许静默退出。</HARD-GATE>

```bash
for f in spec-dev/*/.workflow-state.json; do
  [ -f "$f" ] || continue
  STATUS=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('status',''))" 2>/dev/null)
  [ "$STATUS" = "in_progress" ] && echo "[INFO] 工作流进行中: $(basename $(dirname $f))"
done
```

---

---

## 步骤1-9: 督导闭环

每阶段：**前置校验 → 派遣 → 产出校验 → Token记录 → 纠正**。

<HARD-GATE>每阶段完成后必须写入 `.workflow-eval.json` 追加 stage 数据（stage/status/tokens_input/tokens_output/duration/agent）。token_usage 和 stages[] 为空时不允许进入下一阶段。</HARD-GATE>

完成后写入 `.workflow-eval.json`（含 stage/tokens_input/tokens_output/duration），步骤8 汇总诊断。
校验脚本和纠正措施详见 `references/flow-execution-reference.md`。

| 步骤 | 前置 | 产出 | 记录 | 纠正 |
|------|------|------|------|------|
| 1 spec | state.json 已初始化 | requirement/scenarios/data/business/glossary 非空 + 模式标签 + 异常场景 | stage/stats/agent 写入 eval.json | 缺失回溯 |
| 2-3 parallel | scenarios 含 TEST-VERIFY | test-spec非空+fixtures可解析 / design.md含架构+组件+决策 | stage/stats/agent×2 写入 eval.json | 缺失重新派遣 |
| 3.5 contract | design done + fullstack | contract.md + review-report无blocking | stage/stats 写入 eval.json | blocking修复后重审 |
| 4 task | design.md 存在 | tasks.md 每Task有 provides/consumes/验收标准/DAG | stage/stats 写入 eval.json | 补全后继续 |
| 5 execute | tasks.md存在 + TDD出口验证 | src/非空 + execution-report.md + TDD四阶段日志(RED/GREEN/REFACTOR/REVIEW) | stage/batch_stats 写入 eval.json | 回溯/补测试/拆批次 |
| 5.5 exception | 后端/全栈自动 | 异常代码生成 | — | — |
| 6 test | src/存在 + report存在 | testing-report.md存在 + E2E执行 | stage/stats/agent×2 写入 eval.json | 失败回execute |
| 7 archive | 全部测试通过 | 主规范已合并 + archive-log.md | stage/stats 写入 eval.json | 失败回溯 |
| 8 evaluation | archive done + eval.json 含全阶段数据 | diagnosis字段已写入 + context-budget + cost | 汇总诊断报告 | stages[]为空则回溯 |
| 9 knowledge | evaluation done | pattern-index.json 更新 | — | — |

---

## Agent 派遣总览

> 详细契约见 `references/flow-execution-reference.md`。以下为编排时直接使用的派遣代码。

### 派遣索引

| 步骤 | Agent | 调度 |
|------|-------|------|
| 1 | `code-explorer` | `run_in_background=true` |
| 2 | `test-designer` | `run_in_background=true` |
| 3 | `code-architect` | `run_in_background=true` |
| 3.5 | `contract-creator` | `run_in_background=false` |
| 4 | `tasker` | `run_in_background=false` |
| 5 | `code-executor` ×N + `code-reviewer` | `run_in_background=true` ×N |
| 5.5 | `exception` | 子过程自动 |
| 6 | `tester` + `test-verifier` | `run_in_background=false` |
| 7 | `archiver` | `run_in_background=false` |
| 9 | `knowledge-curator` | `run_in_background=false` |

| 辅助 Agent | 触发条件 | 集成点 |
|-----------|---------|--------|
| `socratic-clarifier` | 模糊度 > 0.2 | clarify |
| `tracer` | Task 失败 ≥ 2 次 | execute |
| `e2e-runner` | 前端/全栈 E2E | test |
| `loop-operator` | Task > 3 批次 | execute |
| `planner` | 用户要求 | design |
| `tdd-guide` | standard 模式, 每批次审查TDD四阶段日志, 不满足驳回 | execute 每批次 | | execute 启动 |

### 派遣代码块

```bash
# ═══ 步骤1: spec-creation — 项目探索补偿 ═══
Agent(subagent_type="orch:code-explorer", run_in_background=true,
      prompt="扫描项目 CLAUDE.md/README.md/docs/ 提取：1)技术栈/框架版本 2)目录结构/分层 3)命名规范 4)API模式。输出 project-context.md")

# ═══ 步骤2-3: test-design + code-design（并行） ═══
Agent(subagent_type="orch:test-designer", run_in_background=true,
      prompt="读取 spec-dev/{req}/spec/scenarios/ 中 TEST-VERIFY，生成：1)test-spec-creation.md(AAA模式) 2)fixtures.json(有效/边界/特殊值+Mock) 3)test-*.template(Jest/Vitest/pytest)。Mock策略：只Mock外部依赖，不Mock业务逻辑")

Agent(subagent_type="orch:code-architect", run_in_background=true,
      prompt="基于 spec-dev/{req}/spec/ 架构设计：1)技术栈/模块边界 2)架构模式(Layered/Clean/Hexagonal) 3)组件(文件路径/职责/接口/依赖) 4)数据流/构建序列。后端额外：数据库/服务依赖/可观测性。前端额外：构建/CDN/性能监控。输出 design.md")

# ═══ 步骤3.5: api-contract（fullstack） ═══
Agent(subagent_type="orch:contract-creator",
      prompt="读取 design.md 接口定义，生成 api-contract.md + review-report.md。审查：命名一致性/类型匹配/错误完整/约定遵循/字段一致。接口命名/路由/格式与现有风格一致")

# ═══ 步骤4: code-task ═══
Agent(subagent_type="orch:tasker",
      prompt="读取 design.md 拆解 Task 清单。每Task标注：id/名称/描述/provides/consumes/depends_on/验收标准/预估文件。依赖DAG无环。输出 tasks.md")

# ═══ 步骤5: code-execute（每Task独立子代理并行） ═══
for task in $(python3 -c "import json;tasks=json.load(open('spec-dev/{req}/tasks/tasks.json'));[print(t['id']) for t in tasks if not t.get('depends_on')]"); do
  Agent(subagent_type="orch:executor", run_in_background=true,
        prompt="TDD: RED(写测试确认FAIL)->GREEN(最少代码PASS)->REFACTOR(优化保PASS)->REVIEW(lint/type/覆盖>=85%/无伪代码)。出口验证: 任一不满足阻塞。Git+Trailers(Constraint/Rejected/Spec)")
done

# TDD监督派遣
Agent(subagent_type="orch:tdd-guide",
      prompt="审查每Task TDD四阶段日志: RED有失败证据/GREEN有通过证据/REFACTOR测试未回归/REVIEW全达标。任一不满足驳回")
      prompt="对已完成批次两阶段审查。规范审查(对照design.md检查架构/命名/结构)。质量审查(对照rules/检查type/lint/DRY/SOLID)。仅报告confidence≥80。输出: CRITICAL|WARNING|INFO + file:line")

# ═══ 步骤5.5: exception-handler（后端/全栈） ═══
Agent(subagent_type="orch:exception",
      prompt="扫描 src/ 异常场景。1)项目约定扫描(异常类名/错误码/RPC模式) 2)识别场景(数据库/RPC/JSON/参数) 3)按约定生成异常代码。RPC→远程异常|业务→业务异常|参数→参数异常|系统→系统异常。禁止硬编码")

# ═══ 步骤6: code-test ═══
Agent(subagent_type="orch:tester",
      prompt="对 src/ 高层测试: 1)环境检查 2)集成测试(Repository/Service/API协作) 3)E2E(npx playwright test --grep @e2e) 4)契约(fullstack验证字段/类型) 5)性能(P95<500ms) 6)闭环(TV→Test→Code→Result)。返回 testing-report.md")

Agent(subagent_type="orch:test-verifier",
      prompt="对 testing-report.md 每条验收标准：独立运行验证命令(不接受历史输出)。标记 VERIFIED/PARTIAL/MISSING。拒绝'应该能工作'类声明")

# ═══ 步骤7: spec-archive ═══
Agent(subagent_type="orch:archiver",
      prompt="归档到 spec-dev/spec/: 1)场景合并(ID冲突追加不覆盖) 2)数据模型合并 3)业务规则合并(冲突标注DECISION_NEEDED) 4)术语合并(重复跳过) 5)标记archived:true 6)生成archive-log.md")

# ═══ 步骤9: knowledge-continuum ═══
Agent(subagent_type="orch:knowledge-curator",
      prompt="知识复利：收集→识别→沉淀(运行distill.sh去重)→提炼(运行refresh.sh扫描过期)→自适应(更新preferences.json)。Layer 3: 3子代理并行捕获解决方案")
```

## 中断恢复

检测 `spec-dev/{req}/.workflow-state.json`：

1. 无文件 → 新需求，步骤0开始
2. JSON 校验失败 → 默认从上一 done 阶段续接
3. 最后 done → 验证产出文件存在，缺失标记 failed + AskUserQuestion
4. 最后 failed → AskUserQuestion（重试/跳过/查看错误）
5. 步骤5 中断：检测 `code-execute.status=in_progress` → 列出已完成 Task，从未完成恢复
6. 上下文过大时，中断恢复前先调用 `Skill("orch:context-budget")` 审计 → `Skill("orch:compact")` 建议 compaction 后再继续

## 快速模式

跳过 test-design | 跳过 contract | execute 单审查/覆盖≥60% | test 精简（集成+E2E）。

## 关键约束

| ✅ 必须 | ❌ 禁止 |
|---------|--------|
| 状态实时持久化（含Token） | HARD-GATE 失败静默跳过 |
| 卡点暂停用户确认 | 模式锁定后更改 |
| project_mode 步骤0 锁定 | 跨越入口直接调用下游 Skill |

## 参考文档

| 文档 | 场景 |
|------|------|
| `references/flow-execution-reference.md` | 全部阶段输入/输出契约、校验脚本、纠正措施 |
| `references/workflow-data-schema.md` | JSON 数据格式 |
| `../../commands/start-dev.md` | 流程步骤表 |
