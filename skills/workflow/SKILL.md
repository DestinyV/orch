---
name: workflow
description: |
  统一入口 + 流程编排（Workflow-Control 阶段）
  输入：需求描述（文本或需求ID）
  输出：完整工作流执行 + .workflow-state.json（状态追踪）+ .workflow-eval.json（效果评估+Token用量）
  功能：SDD+TDD工作流的唯一入口，接收需求后自动编排所有下游Skill的执行顺序，
  支持模式自动检测、并行分支调度、HARD-GATE卡点管控、自动补偿、中断恢复、效果评估与Token追踪。
---

# workflow — 流程编排引擎


## When to Use

- 新需求入口，自动编排从需求到归档的完整流程
- 需要中断恢复、状态追踪、效果评估

## 职责

SDD+TDD 工作流的**入口编排器**。步骤控制 → `commands/start-dev.md`，内容管理 → 本文件。

> **Source of Truth**: 各阶段输入/输出契约、校验规则、失败纠正详见 [`references/flow-execution-reference.md`](references/flow-execution-reference.md)。

## 通用规则

| 规则       | 策略                                                                           |
| ---------- | ------------------------------------------------------------------------------ |
| 失败处理   | 自动重试 1 次；仍失败 → AskUserQuestion（重试/跳过/人工/降级）                 |
| 状态持久化 | 每阶段完成后立即写入 `.workflow-state.json`，不依赖会话内存                    |
| Token 记录 | 每阶段完成后调用 `context-budget` 记录上下文消耗，记录到 `.workflow-eval.json` |
| 上下文监控 | 阶段切换时检测上下文余量，不足时建议 compact 或精简后续步骤                    |

<HARD-GATE>禁止在正式流程前执行代码探索，由 spec 内部负责。</HARD-GATE>
<HARD-GATE>禁止跳过阶段。即使已有 spec 目录，也必须从步骤0开始，由状态检测决定中断恢复。</HARD-GATE>

---

## 步骤0: 初始化

1. 接收需求 → 检查 `orch-spec/` 下 `.workflow-state.json`（存在则中断恢复）
2. project-mode：直接 AskUserQuestion 让用户从 [frontend / backend / fullstack / mobile] 中选择，**禁止通过分析项目或需求特征推断**
3. AskUserQuestion 确认：数据库类型/快速或标准/设计图偏好
4. 加载知识增强 → `preferences.json` → `always_check[]` 注入 spec
5. 初始化 `.workflow-state.json` + `.workflow-eval.json`
6. 检测需求模糊度 → 模糊 > 0.2 时派遣 `clarify`；否则级联 `spec`
7. **CodeGraph 可选加速**：检测 `codegraph` 命令是否存在，不存在则自动安装（`npm i -g @colbymchenry/codegraph 2>/dev/null || npm i -g @colbymchenry/codegraph`）。已安装则：`cd $CLAUDE_PLUGIN_ROOT && codegraph init -i 2>/dev/null && echo '{"mcpServers":{"codegraph":{"command":"codegraph","args":["serve","--mcp"],"env":{}}}}' > .mcp.json && nohup codegraph serve --mcp > /dev/null 2>&1 &`。成功后各 Agent 可使用 `codegraph_search/explore/context/trace/callers/callees/impact/node` MCP 工具代替 grep/Read 进行代码检索。安装失败或不存在时自然回退到 grep/Read。

### 步骤0.5: 苏格拉底澄清

<HARD-GATE>模糊度 > 0.2 时不允许跳过澄清。</HARD-GATE>

```bash
Skill("orch:clarify", args="{requirement_desc}")
```

产出校验：`clarification.md` 存在且含 `final_ambiguity`。完成后自动级联 `spec`。

### 流持续化检查

<HARD-GATE>检测到未完成状态时提示用户，不允许静默退出。</HARD-GATE>

```bash
for f in orch-spec/*/.workflow-state.json; do
  [ -f "$f" ] || continue
  STATUS=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('status',''))" 2>/dev/null)
  [ "$STATUS" = "in_progress" ] && echo "[INFO] 工作流进行中: $(basename $(dirname $f))"
done
```

---

## 步骤1-9: 督导闭环

每阶段：**前置校验 → 派遣 → 产出校验 → Token记录 → 纠正**。

<HARD-GATE>每阶段完成后必须写入 `.workflow-eval.json` 追加 stage 数据（stage/status/tokens_input/tokens_output/duration/agent）。token_usage 和 stages[] 为空时不允许进入下一阶段。</HARD-GATE>

完成后写入 `.workflow-eval.json`（含 stage/tokens_input/tokens_output/duration），步骤8 汇总诊断。
校验脚本和纠正措施详见 `references/flow-execution-reference.md`。

| 步骤                      | 前置                                  | 产出                                                                      | 记录                               | 纠正               |
| ------------------------- | ------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------- | ------------------ |
| 1 spec                    | state.json 已初始化                   | requirement/scenarios/data/business/glossary 非空 + 模式标签 + 异常场景   | stage/stats/agent 写入 eval.json   | 缺失回溯           |
| 2-3 parallel              | scenarios 含 TEST-VERIFY              | test-spec非空+fixtures可解析 / design.md含架构+组件+决策                  | stage/stats/agent×2 写入 eval.json | 缺失重新派遣       |
| 3.5 contract              | design done + fullstack               | contract.md + review-report无blocking                                     | stage/stats 写入 eval.json         | blocking修复后重审 |
| 4 task                    | design.md 存在                        | tasks.md 每Task有 provides/consumes/验收标准/DAG                          | stage/stats 写入 eval.json         | 补全后继续         |
| 5 execute                 | tasks.md存在 + TDD出口验证            | src/非空 + execution-report.md + TDD四阶段日志(RED/GREEN/REFACTOR/REVIEW) | stage/batch_stats 写入 eval.json   | 回溯/补测试/拆批次 |
| 5.5 exception             | 后端/全栈自动                         | 异常代码生成                                                              | —                                  | —                  |
| 6 test                    | src/存在 + report存在                 | testing-report.md存在 + E2E执行                                           | stage/stats/agent×2 写入 eval.json | 失败回execute      |
| 7 archive                 | 全部测试通过                          | 主规范已合并 + archive-log.md                                             | stage/stats 写入 eval.json         | 失败回溯           |
| 8 evaluation | archive done + eval.json 含全阶段数据 | diagnosis字段已写入 + context-budget + cost | 汇总诊断报告 | stages[]为空则回溯 |
| 9 continuous-learning | evaluation done | orch-spec/patterns/ + preferences.json 更新 | — | — |

<HARD-GATE>步骤8(evaluation)和步骤9(continuous-learning)不可跳过。archive完成后必须自动执行。</HARD-GATE>

---

## Agent 派遣总览

> 详细契约见 `references/flow-execution-reference.md`。以下为编排时直接使用的派遣代码。

### 派遣索引

| 批次      | 步骤    | Agent                                  | 调度策略                                                                       |
| --------- | ------- | -------------------------------------- | ------------------------------------------------------------------------------ |
| 批次1     | 1       | `code-explorer` ×3                     | **三路并行**：A 技术栈 / B 目录结构 / C 项目约定，全部完成后合并               |
| **批次2** | **2-3** | **`test-designer` + `code-architect`** | **两 Agent 同时 `run_in_background=true`，互不阻塞**                           |
| —         | 3.5     | `contract-creator`                     | 批次2 全部完成后串行，仅 fullstack                                             |
| —         | 4       | `tasker`                               | 批次2+3.5 完成后串行                                                           |
| 批次3     | 5       | `executor` ×N + `code-reviewer`        | 批次4 完成后，同批次内无依赖 Task 并行启动 (for 循环 `run_in_background=true`) |
| —         | 5.5     | `exception`                            | 步骤5 子过程自动                                                               |
| —         | 6       | `tester` ×3 + `test-verifier`          | **三路并行**：集成/E2E/性能同时跑，全部完成后 test-verifier 串行验证           |
| —         | 7       | `archiver`                             | 步骤6 完成后串行                                                               |
| —         | 8       | evaluation                             | **双路并行**：`context-budget` 估算 + `cost` DB 实记同时跑，后合并诊断对比     |
| —         | 9       | `knowledge-curator`                    | 步骤8 完成后串行                                                               |

| 辅助 Agent           | 触发条件                                           | 集成点         |
| -------------------- | -------------------------------------------------- | -------------- |
| `socratic-clarifier` | 模糊度 > 0.2                                       | clarify        |
| `tracer`             | Task 失败 ≥ 2 次                                   | execute        |
| `e2e-runner`         | 前端/全栈 E2E                                      | test           |
| `loop-operator`      | Task > 3 批次                                      | execute        |
| `planner`            | 用户要求                                           | design         |
| `tdd-guide` | standard 模式, 每批次审查TDD四阶段日志, 不满足驳回 | execute 每批次 |

### 派遣代码块

```bash
# ═══ 步骤1: spec — 项目探索补偿（三路并行） ═══
<HARD-GATE>code-explorer 必须三路并行启动，不允许串行。全部完成后合并为完整 project-context.md。</HARD-GATE>

# Agent A: 文档探索
Agent(subagent_type="orch:code-explorer", run_in_background=true,
      prompt="扫描 CLAUDE.md/README.md/docs/ 提取架构约定和项目文档摘要。工具优先：使用 Skill('orch:scripts') 进行文件定位和关键词提取。输出到 orch-spec/{req_id}/project-context.md 的 ## 文档摘要 章节")

# Agent B: 历史需求探索（标准模式）
Agent(subagent_type="orch:code-explorer", run_in_background=true,
      prompt="扫描 orch-spec/ 下最近 3-5 个已完成需求的 requirement.md，提取：1)常用数据模型 2)典型业务规则 3)命名惯例。输出到 orch-spec/{req_id}/project-context.md 的 ## 历史模式 章节")

# Agent C: 代码模式探索
Agent(subagent_type="orch:code-explorer", run_in_background=true,
      prompt="扫描 src/ 提取架构约定和代码模式。工具优先：使用 Skill('orch:scripts') 进行批量检索。CodeGraph MCP 已安装时依次使用: codegraph_explore \"src/ 模块划分和分层\" → codegraph_context \"核心模块接口\" → codegraph_callers \"主要入口点\"。输出到 orch-spec/{req_id}/project-context.md 的 ## 代码模式 章节")

# 全部完成后，合并 A+B+C 三部分为完整 orch-spec/{req_id}/project-context.md
# 小型项目(<200文件)可保持串行

# ═══ 步骤2-3: test-design + design（并行） ═══
Agent(subagent_type="orch:test-designer", run_in_background=true,
      prompt="读取 orch-spec/{req}/spec/scenarios/ 中 TEST-VERIFY，生成到 orch-spec/{req}/tests/：1)test-spec.md(AAA模式) 2)fixtures.json(有效/边界/特殊值+Mock) 3)test-*.template(Jest/Vitest/pytest)。Mock策略：只Mock外部依赖，不Mock业务逻辑")

Agent(subagent_type="orch:code-architect", run_in_background=true,
      prompt="基于 orch-spec/{req}/spec/ 架构设计：1)技术栈/模块边界 2)架构模式(Layered/Clean/Hexagonal) 3)组件(文件路径/职责/接口/依赖) 4)数据流/构建序列。后端额外：数据库/服务依赖/可观测性。前端额外：构建/CDN/性能监控。输出到 orch-spec/{req}/design/design.md")

# ═══ 步骤3.5: contract（fullstack） ═══
Agent(subagent_type="orch:contract-creator",
      prompt="读取 orch-spec/{req}/design/design.md 接口定义，生成到 orch-spec/{req}/contract/：contract.md + review-report.md。审查：命名一致性/类型匹配/错误完整/约定遵循/字段一致。接口命名/路由/格式与现有风格一致")

# ═══ 步骤4: task ═══
Agent(subagent_type="orch:tasker",
      prompt="读取 orch-spec/{req}/design/design.md 拆解 Task 清单。每Task标注：id/名称/描述/provides/consumes/depends_on/验收标准/预估文件。依赖DAG无环。输出到 orch-spec/{req}/tasks/tasks.md")

# ═══ 步骤5: execute（每Task独立子代理并行） ═══
for task in $(python3 -c "import json;tasks=json.load(open('orch-spec/{req}/tasks/tasks.json'));[print(t['id']) for t in tasks if not t.get('depends_on')]"); do
  Agent(subagent_type="orch:executor", run_in_background=true,
        prompt="<HARD-GATE>禁止编造测试结果。每阶段必须执行命令并将stdout粘贴为证据。RED: 运行测试确认FAIL粘贴失败输出; GREEN: 运行测试确认PASS粘贴通过输出; REFACTOR: 再次运行确认全部PASS; REVIEW: 运行lint+typecheck+coverage粘贴结果。出口验证: TDD四阶段日志缺任一个命令输出则驳回。Git+Trailers(Constraint/Rejected/Spec)")
done

# TDD监督派遣
Agent(subagent_type="orch:tdd-guide",
      prompt="审查每Task TDD四阶段日志: RED有失败证据/GREEN有通过证据/REFACTOR测试未回归/REVIEW全达标。任一不满足驳回")
      prompt="对已完成批次两阶段审查。规范审查(对照design.md检查架构/命名/结构)。质量审查(对照rules/检查type/lint/DRY/SOLID)。仅报告confidence≥80。输出: CRITICAL|WARNING|INFO + file:line")

# ═══ 步骤5.5: exception（后端/全栈） ═══
Agent(subagent_type="orch:exception",
      prompt="扫描 src/ 异常场景。1)项目约定扫描(异常类名/错误码/RPC模式) 2)识别场景(数据库/RPC/JSON/参数) 3)按约定生成异常代码。RPC→远程异常|业务→业务异常|参数→参数异常|系统→系统异常。禁止硬编码")

# ═══ 步骤6: test（三路并行） ═══
<HARD-GATE>集成/E2E/性能三路必须并行启动，不允许串行。全部完成后由 test-verifier 统一验证。</HARD-GATE>

# Agent A: 集成测试
Agent(subagent_type="orch:tester", run_in_background=true,
      prompt="<HARD-GATE>禁止分析代码后编造测试结果。必须先执行测试命令，将命令原文和stdout粘贴到报告中。</HARD-GATE>
运行集成测试: 1)确认测试命令(go test ./... -v -count=1 或 npx vitest run --reporter=json) 2)执行命令，将完整stdout作为 ```bash 代码块粘贴 3)从命令输出中提取PASS/FAIL/覆盖率统计 4)基于命令输出写报告，禁止基于代码阅读写报告。
出口验证: 报告含命令原文+stdout代码块; 无'经分析''推测''应该'等推断措辞。写入 orch-spec/{req}/testing/testing-report.md ## 集成测试")

# Agent B: E2E 测试（前端/全栈）
Agent(subagent_type="orch:tester", run_in_background=true,
      prompt="<HARD-GATE>禁止分析代码后编造测试结果。必须先执行测试命令，将命令原文和stdout粘贴到报告中。</HARD-GATE>
运行 E2E 测试: 1)确认命令(npx playwright test --grep @e2e --reporter=json) 2)执行命令，完整stdout粘贴 3)提取通过率/失败截图路径 4)基于命令输出写报告，禁止基于代码阅读写报告。
出口验证: 报告含命令原文+stdout代码块; 无推断措辞。写入 orch-spec/{req}/testing/testing-report.md ## E2E 测试")

# Agent C: 性能测试
Agent(subagent_type="orch:tester", run_in_background=true,
      prompt="<HARD-GATE>禁止分析代码后编造测试结果。必须先执行测试命令，将命令原文和stdout粘贴到报告中。</HARD-GATE>
运行性能测试: 1)确认测试命令 2)执行命令，完整stdout粘贴 3)提取P50/P95/P99延迟标记>500ms为失败 4)基于命令输出写报告，禁止基于代码阅读写报告。
出口验证: 报告含命令原文+stdout代码块; 无推断措辞。写入 orch-spec/{req}/testing/testing-report.md ## 性能测试")

# 全部完成后，统一验证
Agent(subagent_type="orch:test-verifier",
      prompt="读取 orch-spec/{req}/testing/testing-report.md 全部章节，对每条验收标准独立运行验证命令(不接受历史输出)。标记 VERIFIED/PARTIAL/MISSING。拒绝'应该能工作'类声明")

# ═══ 步骤7: archive ═══
Agent(subagent_type="orch:archiver",
      prompt="归档到 orch-spec/spec/: 1)场景合并(ID冲突追加不覆盖) 2)数据模型合并 3)业务规则合并(冲突标注DECISION_NEEDED) 4)术语合并(重复跳过) 5)标记archived:true 6)生成archive-log.md")

# ═══ 步骤8: evaluation（双路并行，三维度九指标） ═══
<HARD-GATE>archive 完成后不允许跳过 evaluation。</HARD-GATE>
# 成功度: 阶段完成率/Agent派遣/用户干预/HARD-GATE触发/回退 — 数据源 eval.json
# 效率:   并行利用/批次并发/阶段耗时比/Token效率 — 数据源 eval.json + cost DB
# 质量:   覆盖率(≥85%)/审查通过(≥80)/规范一致性/归档冲突(≤3) — 数据源 execute+reviewer+archive

# Agent A: context-budget 估算
Agent(run_in_background=true,
      prompt='Skill("orch:context-budget", args="write-to-eval") 写入 orch-spec/{req}/.workflow-eval.json 的 estimated_tokens')

# Agent B: cost DB 实记
Agent(run_in_background=true,
      prompt="查询 ~/.claude/orch-costs/usage.db 写入 orch-spec/{req}/.workflow-eval.json 的 actual_tokens 和 token_usage")

# A+B完成后: 逐阶段对比 estimated vs actual → 写入 diagnosis.偏差
# 按三维度评分(✅/⚠️/❌) → 写入 diagnosis.成功度/效率/质量 + 建议[] + score(0-100)
# 更新 .workflow-state.json: current_stage=evaluation, status=done

# ═══ 步骤9: continuous-learning（四维知识沉淀） ═══
<HARD-GATE>evaluation 完成后不允许跳过。learnings[] 为空时不允许标记 status=completed。</HARD-GATE>
# 用户纠正: clarify追问轮数→always_check[] / 否决决策→rejected_approaches[] / 手动改代码→corrections → preferences.json+patterns/
# 流程效率: 瓶颈阶段→bottlenecks[] / 重复Task→task_sizing / 并行失效→concurrency → preferences.json
# 质量模式: code-reviewer高频→quality / test失败类型→testing / archive冲突→naming → patterns/
# 项目约定: design ADR→architecture / exception模式→exception_patterns / tech_stack → patterns/+preferences.json

Agent(subagent_type="orch:knowledge-curator",
      prompt="从 .workflow-eval.json 提取知识四维度: 1)events[type=user_intervention]→用户纠正 2)stages[耗时>50%]→瓶颈 3)diagnosis[覆盖率<85%/审查<80]→质量 4)design ADR+exception→项目约定。写入 orch-spec/patterns/ 和 orch-spec/user-preferences/preferences.json。eval.json 追加 learnings[]")

# 全部完成后: .workflow-state.json → status: completed

## 中断恢复

检测 `orch-spec/{req}/.workflow-state.json`：

1. 无文件 → 新需求，步骤0开始
2. JSON 校验失败 → 默认从上一 done 阶段续接
3. 最后 done → 验证产出文件存在，缺失标记 failed + AskUserQuestion
4. 最后 failed → AskUserQuestion（重试/跳过/查看错误）
5. 步骤5 中断：检测 `execute.status=in_progress` → 列出已完成 Task，从未完成恢复
6. 上下文过大时，中断恢复前先调用 `Skill("orch:context-budget")` 审计 → `Skill("orch:compact")` 建议 compaction 后再继续

## 快速模式

跳过 test-design | 跳过 contract | execute 单审查/覆盖≥60% | test 精简（集成+E2E）。

## 关键约束

| ✅ 必须                    | ❌ 禁止                     |
| ------------------------- | -------------------------- |
| 状态实时持久化（含Token） | HARD-GATE 失败静默跳过     |
| 卡点暂停用户确认          | 模式锁定后更改             |
| project_mode 步骤0 锁定   | 跨越入口直接调用下游 Skill |

## 参考文档

| 文档                                     | 场景                                      |
| ---------------------------------------- | ----------------------------------------- |
| `references/flow-execution-reference.md` | 全部阶段输入/输出契约、校验脚本、纠正措施 |
| `references/workflow-data-schema.md`     | JSON 数据格式                             |
| `../../commands/start-dev.md`            | 流程步骤表                                |
