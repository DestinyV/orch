<!-- 模式: standard | project-mode: backend（无 DB/前端/contract，插件自身 Node/Markdown 工具链）| 覆盖率≥85% | TDD 必须 | 子代理必须 -->
<!-- req: plugin-capability-optimization | 需求类型: 元任务（优化 orch 插件自身）| 北极星原则：约束=护栏非牢笼，任何修改禁止限制模型能力 -->

# Task 清单 — plugin-capability-optimization（orch 插件本体全方位能力优化）

**版本**：1.0 ｜ **日期**：2026-08-01 ｜ **模式**：standard ｜ **project-mode**：backend
**数据链**：spec (29 TV) → test-spec (47 TC) → tasks（本文件）→ execute（TDD RED→GREEN）
**北极星原则（贯穿全部 Task）**：每一项修改都必须通过"护栏/牢笼"判定。护栏（guardrail，保留：纯流程顺序/产出存在/派遣完整性/可靠性）可直接落地；牢笼（cage，限制思考深度/探索自由/创造性）必须降级为建议。本清单中每个实现 Task 均已标注北极星判定。

---

## 0. 设计冲突裁决清单（先读，阻塞项）

| 编号 | 冲突 | 裁决建议 | 影响任务 |
|------|------|---------|---------|
| **R-1** | design §4.2/§5.4 新建 `commands/self-check.md`（命令 #15），但 fixtures `S5.docs_counts` + TC-S5-04 + design §4.2 自检自身断言均为 **22/26/14**。命令数口径矛盾 | **推荐**：self-check 定义为「内部自检命令」，不计入业务命令数 14；README/.claude-plugin/README/AGENTS.md 保持 22 Skills/26 Agents/14 Commands，并追加一句「另含内部自检命令 `/self-check`」。零 fixtures/TC 改动即全绿。若 orchestrator 裁决改为 15，则需 req-change 更新 `fixtures.json` S5.docs_counts（14→15）及 TC-S5-04 | T5.1, T6.1, T7.1 |
| **R-2** | design §7 Batch2 标称「5 并行」，但文件交集实际冲突：T2.1/T2.2 同改 `agent-dispatch-code.md`；T2.2/T2.3 同改 `tdd-guide.md`/`code-reviewer.md`；T2.4/T2.5 同改 `code-architect.md`/`conversation-analyzer.md` | 按文件交集 GATE **串行化** Batch2 为 T2.1→T2.2→T2.3→T2.4→T2.5（§4.2 已落地） | Batch2 全部 |
| **R-3** | design §7 Batch1 标称 T1.1/T1.2/T1.3「不同文件可并行」，但 T1.1 与 T1.2 均改 `workflow-gate.js`（STAGE_OUTPUTS vs :112 stdin） | 将 workflow-gate.js 的 stdin 修复**收编进 T1.1**；T1.2 仅改 `stage-gate.js`。且 T1.2/T1.3 `require('../lib/stage-contracts')` 依赖 T1.1 产出模块 → T1.1 先行，T1.2/T1.3 并行（§4.1） | T1.1, T1.2 |
| **R-4** | TC-S3-07 要求 observer「配置与文档一致」，但 CLAUDE.md 同步在 T5.1（Batch5），config.json 在 T3.4（Batch3） | TT-3.4 仅断言 `config.json observer.enabled===true`；「CLAUDE.md 一致 + observe 非死引用」交由 TT-4.2 + T6.1 self-check 承接 | T3.4, TT-3.4 |

---

## 1. 依赖图（批次 DAG）

```
Batch1 ── S1 编排（子批次见 §4.1）
  T1.1 stage-contracts 集中化 + workflow-gate(STAGE_OUTPUTS 8key + validateOutputs(state) + stdin)
  T1.2 stage-gate stdin 超时 fail-open + EXEMPT 命令分离     [dep: T1.1]
  T1.3 session-start 自动补偿                                [dep: T1.1]
  T1.4 北极星审查 → business-rules（start-dev/tasker GATE 降级）
        │
Batch2 ── S2 Agent（串行链，R-2）
  T2.1 → T2.2 → T2.3 → T2.4 → T2.5
  (project-map×4 → tdd-guide 注册 → prompt-defense 幂等 → frontmatter 统一 → 编号+hookify)
        │
Batch3 ── S3 Skills
  T3.1 悬空引用 / T3.2 cost GATE / T3.3 using-orch 22 / T3.4 observer.enabled=true   （4 并行）
  T3.5 16 skill TRIGGER                                                              [dep: T3.1]
        │
Batch4 ── S5 Hooks（3 并行）
  T4.1 hooks.json 注册(suggest-compact+observe) / T4.2 observe.js+observe.sh / T4.3 hook-flags 门控
        │
Batch5 ── S5 文档同步（dep: Batch2+4，内部 3 并行）
  T5.1 CLAUDE.md+AGENTS.md+README 同步  [dep: T2.2, T4.1, T4.2]
  T5.2 file-map.yaml+index.json          [dep: Batch2+4]
  T5.3 __pycache__ 清理 + .gitignore      [独立]
        │
Batch6 ── S4 自检与冒烟（dep: Batch1-5，内部 3 并行）
  T6.1 self-check.js+commands/self-check.md+verdict.js
  T6.2 hooks-smoke.test.js + 落地 test-*.template 全套
  T6.3 test-suite.py 扩展
        │
Batch7 ── S6 验证闭环（串行）
  T7.1 自检 5 块 PASS → T7.2 量化度量 → T7.3 testing-report.md
```

**拓扑序（无环验证）**：见 §6。每批次完成即触发批次验证钩子（§5），Batch6 产物反哺 T7.1 全量自检。

---

## 2. 全局执行纪律（所有 Task 生效）

1. **TDD 配对**：每个实现 Task T-x 在同批次配测试 Task TT-x；`TT-x.depends_on = [T-x]`（GATE 原文）。执行顺序为 RED（TT-x 先跑，断言当前状态失败）→ GREEN（T-x 实现）→ REFACTOR → REVIEW，二者在同一批次槽位内先后完成。
2. **RED 证据新鲜性**：每条验收标准必须附实际运行输出/文件快照，禁止"应该/可能"声明。
3. **fixtures 数据源**：所有测试断言值取自 `orch-spec/plugin-capability-optimization/tests/fixtures.json`（§3 各 TC 标注的 fixtures 键）。
4. **并行强制**：批次内无依赖 Task 必须 `run_in_background=true` 并行派遣；每批最大并发 ≤5。
5. **git-worktree 隔离**：每个 Task 在独立 worktree 实现，合并前无跨 Task 文件冲突（本清单的 DAG 已保证同批次无同文件写入）。
6. **北极星红线**：不得引入"禁止探索 Y""必须采用 X 方式思考""禁止跨行读取文件"等 cage 类约束。所有 GATE 仅约束流程顺序/产出存在/派遣完整性。
7. **hooks.json 有效**：任何修改后 `python -c "import json; json.load(open('hooks/hooks.json'))"` 必须通过。
8. **数量口径**：除 R-1 裁决外，全插件 Skills=22 / Agents=26（磁盘 agent 数，去 `_prompt-defense.md`）/ Commands=14 为唯一事实源。

---

## 3. TEST-VERIFY → Test Case → Task 映射表（47 TC / 29 TV，覆盖率 100%）

| TC-ID | TV-ID | 类型 | 断言摘要 | Task（TT） | 落地测试文件 |
|-------|-------|------|---------|-----------|-------------|
| TC-S1-01 | TV-S1-01 | Static | STAGE_OUTPUTS 覆盖 8 阶段 key | TT-1.1 | `tests/meta-b1-workflow-gate.py` |
| TC-S1-02 | TV-S1-01 | Static | 3.5/5/6/9 各含预期产出字符串 | TT-1.1 | 同上 |
| TC-S1-03 | TV-S1-01 | Behavior | 未知 stage fail-open（exit 0 无 stack） | TT-1.1 | 同上 |
| TC-S1-04 | TV-S1-02 | Behavior | in_progress → resume-from-6 建议 | TT-1.3 | `tests/meta-b1-session-start.py` |
| TC-S1-05 | TV-S1-02 | Behavior | 前置缺失 → 具体缺失文件清单 | TT-1.3 | 同上 |
| TC-S1-06 | TV-S1-02 | Behavior | 无 in_progress → no-op | TT-1.3 | 同上 |
| TC-S1-07 | TV-S1-03 | Static | workflow GATE 无能力限制型约束 | TT-1.4 | `tests/meta-b1-northstar.py` |
| TC-S1-08 | TV-S1-04 | Behavior | 空 stdin 阻塞 2s 内 fail-open allow | TT-1.2 | `tests/meta-b1-stage-gate.py` |
| TC-S1-09 | TV-S1-04 | Behavior | 合法 stdin → allow/deny 正确 | TT-1.2 | 同上 |
| TC-S1-10 | TV-S1-05 | Static | EXEMPT 命令名从 EXEMPT_SKILLS 移除 | TT-1.2 | 同上 |
| TC-S1-11 | TV-S1-05 | Static | EXEMPT_SKILLS ∩ 命令列表 = 空 | TT-1.2 | 同上 |
| TC-S2-01 | TV-S2-01 | Static | agents/+skills/ 内 project-map.md = 0 | TT-2.1 | `tests/meta-b2-project-map.py` |
| TC-S2-02 | TV-S2-01 | Static | 3 指定文件引用 project-map.json | TT-2.1 | 同上 |
| TC-S2-03 | TV-S2-02 | Static | 磁盘 agent 数 = 注册表 = 26 | TT-2.2 | `tests/meta-b2-registry.py` |
| TC-S2-04 | TV-S2-02 | Static | 注册表链接有效 + 磁盘全覆盖 | TT-2.2 | 同上 |
| TC-S2-05 | TV-S2-03 | Behavior | sync-prompt-defense 连跑两次幂等 | TT-2.3 | `tests/meta-b2-prompt-defense.py` |
| TC-S2-06 | TV-S2-03 | Static | 每 agent Prompt Defense 节 ≤1 | TT-2.3 | 同上 |
| TC-S2-07 | TV-S2-04 | Static | frontmatter 含 name/desc/tools/model；tools 逗号；model: inherit | TT-2.4 | `tests/meta-b2-frontmatter.py` |
| TC-S2-08 | TV-S2-05 | Static | code-architect `### 0.` 仅一次；编号升序连续 | TT-2.5 | `tests/meta-b2-numbering.py` |
| TC-S2-09 | TV-S2-06 | Static | agents/ 内 /hookify = 0 | TT-2.5 | 同上 |
| TC-S3-01 | TV-S3-01 | Static | execute 引用 context-inheritance-protocol.md 且存在 | TT-3.1 | `tests/meta-b3-refs.py` |
| TC-S3-02 | TV-S3-01 | Static | spec 引用 ../design/references/diagram-trigger-rules.md | TT-3.1 | 同上 |
| TC-S3-03 | TV-S3-01 | Static | skills/ 全部 .md 链接交叉校验通过 | TT-3.1 | 同上 |
| TC-S3-04 | TV-S3-02 | Static | cost SKILL.md 含 ≥1 `<GATE>` | TT-3.2 | `tests/meta-b3-cost.py` |
| TC-S3-05 | TV-S3-03 | Static | using-orch 表格覆盖 22 skill | TT-3.3 | `tests/meta-b3-using-orch.py` |
| TC-S3-06 | TV-S3-03 | Static | 无 skill 目录遗漏（差集空） | TT-3.3 | 同上 |
| TC-S3-07 | TV-S3-04 | Static | config observer.enabled 与文档一致（本 TT 断言 enabled=true） | TT-3.4 | `tests/meta-b3-observer.py` |
| TC-S3-08 | TV-S3-05 | Static | 核心 skill description 含 TRIGGER when | TT-3.5 | `tests/meta-b3-trigger.py` |
| TC-S3-09 | TV-S3-05 | Static | 22 skill description 非空 | TT-3.5 | 同上 |
| TC-S4-01 | TV-S4-01 | Behavior | self-check exit=0 且含 PASS | TT-6.1 | `tests/meta-b6-selfcheck.py` |
| TC-S4-02 | TV-S4-02 | Static | TDD 日志含 RED/GREEN/REFACTOR/REVIEW | TT-6.1 | 同上 |
| TC-S4-03 | TV-S4-03 | Behavior | claimed 85/actual 87 → VERIFIED | TT-6.1 | 同上 |
| TC-S4-04 | TV-S4-03 | Behavior | claimed 90/actual 72 → PARTIAL | TT-6.1 | 同上 |
| TC-S4-05 | TV-S4-03 | Behavior | 覆盖率独立重算（非自我报告） | TT-6.1 | 同上 |
| TC-S4-06 | TV-S4-04 | Behavior | tests/test-suite.py exit=0 errors=0 | TT-6.3 | 执行 test-suite.py |
| TC-S5-01 | TV-S5-01 | Static | hooks.json PreToolUse 注册 suggest-compact | TT-4.1 | `tests/meta-b4-hooks-json.py` |
| TC-S5-02 | TV-S5-02 | Static | observe.sh 存在且已注册（非死引用） | TT-4.2 | `tests/meta-b4-observe.py` |
| TC-S5-03 | TV-S5-03 | Static | CLAUDE.md 钩子表 ↔ hooks.json 双向一致 | TT-5.1 | `tests/meta-b5-docs.py` |
| TC-S5-04 | TV-S5-04 | Static | 文档数量口径 22/26/14 一致、无 /orch:sdd-dev | TT-5.1 | 同上 |
| TC-S5-05 | TV-S5-05 | Static | git ls-files 无 *.pyc；.gitignore 含 __pycache__/*.pyc | TT-5.3 | `tests/meta-b5-pyc.py` |
| TC-S6-01 | TV-S6-01 | Behavior | 自检 5 block 全 PASS | TT-6.1 / T7.1 | `tests/meta-b6-selfcheck.py` |
| TC-S6-02 | TV-S6-02 | Behavior | flow_rate 83 ≥ 80 → pass | TT-6.1 | 同上 |
| TC-S6-03 | TV-S6-02 | Behavior | flow_rate 75 < 80 → fail+optimize | TT-6.1 | 同上 |
| TC-S6-04 | TV-S6-03 | Behavior | pass_rate 90 ≥ 90 → pass | TT-6.1 | 同上 |
| TC-S6-05 | TV-S6-03 | Behavior | pass_rate 85 < 90 → fail | TT-6.1 | 同上 |
| TC-S6-06 | TV-S6-04 | Behavior | 编译/测试失败/缺文件 → auto-resolve | TT-6.1 | 同上 |
| TC-S6-07 | TV-S6-04 | Behavior | 需求冲突/验收不确定/HARD-GATE/跨仓库 → pause-for-human | TT-6.1 | 同上 |

> 说明：`tests/meta-b{批次}-*.py` 为 Task 级聚焦测试（TT 落地，RED→GREEN）；T6.2 将 test-designer 的 6 个 `.template` 落地为正式套件并合并吸收 meta 测试。TC-S3-07 的「文档一致/非死引用」后半段由 TT-4.2 + T6.1 承接（R-4）。

---

## 4. 并行批次计划（run_in_background 指引）

### 4.1 Batch1 — S1 工作流编排引擎（子批次 1a/1b）

| 槽位 | 并行 Task | run_in_background |
|------|-----------|-------------------|
| 1a | T1.1, TT-1.1, T1.4, TT-1.4 | 4 个均 true |
| 1b | T1.2, TT-1.2, T1.3, TT-1.3 | 4 个均 true（dep: T1.1） |

**批次验证钩子**：`node scripts/hooks/stage-gate.js`（空 stdin，2s 内输出 `{"decision":"allow"}` 并自行退出）；`node scripts/hooks/workflow-gate.js`（unknown stage，exit 0 无 stack）。

### 4.2 Batch2 — S2 Agent 体系（串行链，R-2）

| 槽位 | Task 对（impl+test） | run_in_background |
|------|---------------------|-------------------|
| 2a | T2.1 + TT-2.1 | true |
| 2b | T2.2 + TT-2.2（dep 2a） | true |
| 2c | T2.3 + TT-2.3（dep 2b） | true |
| 2d | T2.4 + TT-2.4（dep 2c） | true |
| 2e | T2.5 + TT-2.5（dep 2d） | true |

> 串行理由（R-2）：同文件交集。若 executor 希望加速，可将 T2.4+T2.5 合并为单 Task（仍 ≤4h），合并时验收标准并集不丢失。

### 4.3 Batch3 — S3 Skills 指令

| 槽位 | 并行 Task | run_in_background |
|------|-----------|-------------------|
| 3a | T3.1+TT-3.1, T3.2+TT-3.2, T3.3+TT-3.3, T3.4+TT-3.4 | 8 个均 true |
| 3b | T3.5 + TT-3.5（dep: T3.1） | true |

### 4.4 Batch4 — S5 Hooks 激活（3 并行）

| 槽位 | 并行 Task | run_in_background |
|------|-----------|-------------------|
| 4a | T4.1+TT-4.1, T4.2+TT-4.2, T4.3+TT-4.3 | 6 个均 true |

### 4.5 Batch5 — S5 文档同步（dep: Batch2+4，3 并行）

| 槽位 | 并行 Task | run_in_background |
|------|-----------|-------------------|
| 5a | T5.1+TT-5.1, T5.2+TT-5.2, T5.3+TT-5.3 | 6 个均 true |

### 4.6 Batch6 — S4 自检与冒烟（dep: Batch1-5，3 并行）

| 槽位 | 并行 Task | run_in_background |
|------|-----------|-------------------|
| 6a | T6.1+TT-6.1, T6.2+TT-6.2, T6.3+TT-6.3 | 6 个均 true |

**批次验证钩子**：`node scripts/self-check.js` 全 PASS（TT-6.1 内）。

### 4.7 Batch7 — S6 验证闭环（串行）

| 槽位 | Task | run_in_background |
|------|------|-------------------|
| 7a | T7.1（自检 5 块 PASS + 修复迭代） | true |
| 7b | T7.2（量化度量） | true |
| 7c | T7.3（testing-report.md） | true |

---

## 5. Task 清单

### Batch1 — S1 工作流编排引擎

#### T1.1 stage-contracts 集中化 + workflow-gate 产出校验补齐
- **类型**：实现 ｜ **估时**：3h
- **目标**：消除 stage 映射漂移（F10 根因），STAGE_OUTPUTS 覆盖全部 8 阶段；stdin 读入加超时防护。
- **交付物**：
  - 新建 `scripts/lib/stage-contracts.js`（导出 `STAGE_ORDER` / `STAGE_OUTPUTS` / `SKILL_PREREQUISITES` / `EXEMPT_SKILLS` / `EXEMPT_COMMANDS`）
  - 修改 `scripts/hooks/workflow-gate.js`：删除本地 STAGE_OUTPUTS/SKILL 副本，改 `require('../lib/stage-contracts')`；STAGE_OUTPUTS 含 3.5/5/6/9（`'../context/learnings.md'` + `'completion-report'`）；`validateOutputs(stageName, reqId)` → `validateOutputs(stageName, reqId, state)`，`out === 'completion-report'` 时改查 `state.completion_report_generated`；:112 阻塞式 `fs.readFileSync(process.stdin.fd)` 改 `readStdin(2000)` fail-open（R-3）
- **依赖**：无（stdin.js 已存在于磁盘）
- **provides**：`scripts/lib/stage-contracts.js`（阶段映射单一事实源）、`scripts/hooks/workflow-gate.js`（升级版）
- **consumes**：`scripts/lib/stdin.js`（readStdin）、`scripts/lib/state-store.js`（state 读取）
- **验收标准**：
  1. `stage-contracts.STAGE_OUTPUTS` 含 `0_workflow_control/1_spec_creation/3.5_api_contract/4_code_task/5_code_execute/6_code_test/7_spec_archive/9_knowledge_continuum` 共 8 key（TC-S1-01）
  2. 3.5→`contract.md,review-report.md`；5→`execution-report.md`；6→`testing-report.md`；9→`learnings.md,completion-report`（TC-S1-02）
  3. `workflow-gate.js` 对 `current_stage="unknown"` 的 hook JSON 输入 exit 0、stderr 无 stack（TC-S1-03）
  4. workflow-gate 空 stdin 2s 内自行退出（TC-S1-08 的 workflow-gate 半边，附运行时间戳证据）
- **covers**：`scenarios/S1-workflow-orchestration.md#S1-Case1`、`#S1-Case4`
- **TC 映射**：TC-S1-01/02/03（由 TT-1.1 落地断言）
- **北极星**：guardrail —— 只校验"产出存在"，不约束怎么产出；集中化反降误伤风险

#### TT-1.1 S1-a 测试（workflow-gate 产出校验 + stage-contracts）
- **类型**：测试 ｜ **估时**：1h ｜ **depends_on**：T1.1
- **交付物**：新建 `tests/meta-b1-workflow-gate.py`（落地并运行；RED 时断言当前缺 3.5/5/6/9）
- **provides**：`tests/meta-b1-workflow-gate.py`（TC-S1-01/02/03 断言）
- **consumes**：`fixtures.S1.stages_expected.*`、`scripts/lib/stage-contracts.js`、`scripts/hooks/workflow-gate.js`
- **验收标准**：运行测试 exit=0；RED 证据（T1.1 前 STAGE_OUTPUTS 缺 3.5/5/6/9 的 grep 输出）与 GREEN 证据（全通过）留档
- **covers**：`scenarios/S1-workflow-orchestration.md#S1-Case1`

#### T1.2 stage-gate stdin 超时 + EXEMPT 命令名分离
- **类型**：实现 ｜ **估时**：1.5h
- **目标**：stdin 阻塞 2s 后 fail-open（F9 + 可靠性护栏）；EXEMPT_SKILLS 仅含真 Skill 名。
- **交付物**：修改 `scripts/hooks/stage-gate.js`：删 :99-104 本地 EXEMPT 数组副本，改从 `stage-contracts` 消费 `EXEMPT_SKILLS`（10 真 Skill 名）/ `EXEMPT_COMMANDS`（9 命令名含 self-check）；:163-177 阻塞式 while 循环改 `async main() + await readStdin(2000)`，超时 stderr 记 `[STAGE-GATE] stdin timeout — fail-open` 并输出 `{decision:"allow"}`，`main().catch()` 兜底
- **依赖**：T1.1（需 `stage-contracts.js` 存在）
- **provides**：`scripts/hooks/stage-gate.js`（升级版）
- **consumes**：`scripts/lib/stage-contracts.js`（EXEMPT 常量）、`scripts/lib/stdin.js`
- **验收标准**：
  1. 空 stdin 阻塞进程 ≤2s 自行退出，stdout `{"decision":"allow"}`（TC-S1-08）
  2. 合法 Skill hook JSON stdin → 输出含 `decision` 字段的合法 JSON（TC-S1-09）
  3. `checkpoint/code-review/plan/quality-gate/session-resume/session-save/start-dev` 均不在 `EXEMPT_SKILLS`（TC-S1-10）
  4. `EXEMPT_SKILLS` ∩ `fixtures.S1.exempt.command_names` = 空集；存在独立 `EXEMPT_COMMANDS`（TC-S1-11）
- **covers**：`scenarios/S1-workflow-orchestration.md#S1-Case4`、`#S1-Case5`
- **北极星**：guardrail —— 纯命名清理 + 可靠性护栏，不改变任何门控行为

#### TT-1.2 S1-b 测试（stage-gate stdin + EXEMPT）
- **类型**：测试 ｜ **估时**：1h ｜ **depends_on**：T1.2
- **交付物**：新建 `tests/meta-b1-stage-gate.py`（spawn stage-gate.js，空 stdin 限时轮询；写合法 JSON）
- **provides**：`tests/meta-b1-stage-gate.py`
- **consumes**：`fixtures.S1.stdin_timeout_ms`、`fixtures.S1.exempt.*`、`fixtures.S1.gate_fail_open_decision`
- **验收标准**：TC-S1-08/09/10/11 全通过；RED 证据（修复前 6s 超时被杀）留档
- **covers**：`scenarios/S1-workflow-orchestration.md#S1-Case4`、`#S1-Case5`

#### T1.3 session-start 中断恢复自动补偿
- **类型**：实现 ｜ **估时**：2h
- **目标**：中断工作流自动给出恢复建议（不静默续接，模型自主决策）。
- **交付物**：修改 `scripts/hooks/session-start.js`（:12-29 `checkWorkflowState` 升级）：
  1. 对每个 in_progress 工作流，由 `STAGE_ORDER` 取最大 order 的 done/completed 阶段为 last_done；
  2. 推 next_stage（order 最小且 > last_done 且未 done）；
  3. 用 `STAGE_OUTPUTS[next_stage]` 检查前置产出：全部存在 → `resume-from-<N>` + 续接 Skill 建议；缺失 → 逐条列缺失文件路径；
  4. 无 in_progress → no-op
- **依赖**：T1.1（`STAGE_ORDER` + `STAGE_OUTPUTS`）
- **provides**：`scripts/hooks/session-start.js`（升级版）
- **consumes**：`scripts/lib/stage-contracts.js`、`scripts/lib/state-store.js`
- **验收标准**：
  1. mock state（`fixtures.S1.session_start.valid.mock_state`）→ stdout 含 `resume-from-6` 恢复建议（TC-S1-04）
  2. `prereq_missing.mock_state` → stdout 含具体缺失文件 `testing-report.md`（TC-S1-05）
  3. `no_workflow` 状态 → 无恢复建议输出（TC-S1-06）
- **covers**：`scenarios/S1-workflow-orchestration.md#S1-Case2`
- **北极星**：guardrail —— 提供信息、不剥夺决策权（明确不静默自动续接）

#### TT-1.3 S1-c 测试（session-start 自动补偿）
- **类型**：测试 ｜ **估时**：1h ｜ **depends_on**：T1.3
- **交付物**：新建 `tests/meta-b1-session-start.py`（临时目录造 mock state，`CLAUDE_PLUGIN_ROOT` 指向临时目录，spawn session-start.js）
- **provides**：`tests/meta-b1-session-start.py`
- **consumes**：`fixtures.S1.session_start.*`
- **验收标准**：TC-S1-04/05/06 全通过；三种 mock state 输出快照留档
- **covers**：`scenarios/S1-workflow-orchestration.md#S1-Case2`

#### T1.4 北极星原则审查（GATE 降级 + 结论落盘）
- **类型**：实现 ｜ **估时**：1.5h
- **目标**：消除 cage 类约束，审查结论进入业务规则（S1-Case3 全场景共用）。
- **交付物**：
  - 修改 `commands/start-dev.md:12`：GATE「收到指令后立即调用 Skill(workflow)，禁止调用前任何代码探索/文件读取/目录扫描」→ 降级为建议（北极星 cage 判定）
  - 修改 `agents/tasker.md:24`：「仅当注入信息不足以确定 Task 边界时才补充 Read 原文」→ 降级为建议（token 时代残留）
  - 追加 `orch-spec/plugin-capability-optimization/spec/business-rules.md`「北极星原则审查结论」章节：design §1.6 表格原样落盘（7 项判定：4 保留 + 3 降级）
- **依赖**：无
- **provides**：`commands/start-dev.md`、`agents/tasker.md`、`spec/business-rules.md`（追加）
- **consumes**：design §1.6 审查表（已注入）
- **验收标准**：
  1. `skills/workflow/SKILL.md` + `stage-gate.js` 的每条 GATE 仅约束「流程顺序/产出存在/派遣完整性」，无能力限制型措辞（TC-S1-07）
  2. start-dev.md:12 与 tasker.md:24 不再以 `<GATE>` 形式禁止探索/读取
  3. business-rules.md 含「北极星原则审查结论」章节，7 项判定齐全
- **covers**：`scenarios/S1-workflow-orchestration.md#S1-Case3`
- **北极星**：本任务即北极星审查动作本身

#### TT-1.4 S1-d 测试（北极星 GATE 审查）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T1.4
- **交付物**：新建 `tests/meta-b1-northstar.py`（逐条扫描 workflow SKILL.md GATE 文本 + stage-gate.js SKILL_PREREQUISITES，标记能力限制型条目）
- **provides**：`tests/meta-b1-northstar.py`
- **consumes**：`skills/workflow/SKILL.md`、`scripts/hooks/stage-gate.js`、`fixtures`（无专用键，直接文本扫描）
- **验收标准**：TC-S1-07 通过（无能力限制型 GATE）；审查表已落盘 business-rules.md
- **covers**：`scenarios/S1-workflow-orchestration.md#S1-Case3`

---

### Batch2 — S2 Agent 体系（串行链，R-2）

#### T2.1 project-map 引用统一 ×4（F1）
- **类型**：实现 ｜ **估时**：0.5h
- **交付物**（4 处 `project-map.md` → `project-map.json`）：
  - `agents/code-architect.md:19`、`agents/tasker.md:13`、`skills/design/SKILL.md:45`、`skills/workflow/references/agent-dispatch-code.md:125`
- **依赖**：无（Batch1 完成后）
- **provides**：上述 4 文件修正
- **consumes**：无
- **验收标准**：
  1. agents/+skills/ 递归 grep `project-map.md` = 0 匹配（TC-S2-01）
  2. code-architect.md / tasker.md / design/SKILL.md 均含 `project-map.json`（TC-S2-02）
- **covers**：`scenarios/S2-agent-system.md#S2-Case1`
- **北极星**：guardrail —— 纯文件名引用修正，无行为约束

#### TT-2.1 S2-a 测试（project-map）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T2.1
- **交付物**：新建 `tests/meta-b2-project-map.py`
- **provides**：`tests/meta-b2-project-map.py`
- **consumes**：`fixtures.S2.project_map.*`
- **验收标准**：TC-S2-01/02 通过（RED：修复前 4 处匹配）
- **covers**：`scenarios/S2-agent-system.md#S2-Case1`

#### T2.2 tdd-guide 注册 + deprecated（F2 / ADR-001）
- **类型**：实现 ｜ **估时**：1h
- **目标**：消除孤立 agent，注册表口径对齐（25→26）。
- **交付物**：
  - `agents/tdd-guide.md`：frontmatter 后加 deprecated 横幅
  - `AGENTS.md`：扩展能力表追加 `[tdd-guide](agents/tdd-guide.md)（deprecated）`，总数 25→26
  - `agents/code-reviewer.md:30`：补边界注记（tdd-guide=执行期四阶段门控；code-reviewer=批次后综合审查）
  - `skills/workflow/references/agent-dispatch-code.md:182` + `skills/workflow/references/flow-execution-reference.md:35`：保留四阶段 GATE 规则，行内注 deprecated
- **依赖**：T2.1（同改 agent-dispatch-code.md）
- **provides**：上述 5 文件
- **consumes**：`fixtures.S2.tdd_guide.*`、`fixtures.S2.agent_count.*`
- **验收标准**：
  1. 磁盘 agent 数（去 `_prompt-defense.md`）= AGENTS.md 注册表链接数 = 26（TC-S2-03）
  2. AGENTS.md 每个链接文件存在；磁盘 agent 全部在注册表（tdd-guide 显式 deprecated 标注）（TC-S2-04）
- **covers**：`scenarios/S2-agent-system.md#S2-Case2`
- **北极星**：guardrail —— 注册与标注，不新增约束

#### TT-2.2 S2-b 测试（tdd-guide 注册表）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T2.2
- **交付物**：新建 `tests/meta-b2-registry.py`
- **provides**：`tests/meta-b2-registry.py`
- **consumes**：`fixtures.S2.agent_count.*`、`fixtures.S2.tdd_guide.*`
- **验收标准**：TC-S2-03/04 通过
- **covers**：`scenarios/S2-agent-system.md#S2-Case2`

#### T2.3 Prompt Defense 幂等（F5）
- **类型**：实现 ｜ **估时**：1h
- **目标**：同步脚本幂等，消除 ×9 重复。
- **交付物**：修改 `scripts/sync-prompt-defense.py:23-30` →「先全量清除、再单次插入」：
  ```python
  cleaned = re.sub(r'^##\s*Prompt Defense Baseline\n.*?(?=\n## |\Z)', '', orig, count=0, flags=re.DOTALL)
  cleaned = re.sub(r'^#{1,3}\s*Prompt Defense Baseline\s*$', '', cleaned, flags=re.MULTILINE)
  ```
- **依赖**：T2.2（测试会运行脚本重写全部 agents/*.md，须在 T2.2 的 tdd-guide/code-reviewer 改动之后）
- **provides**：`scripts/sync-prompt-defense.py`（幂等版）
- **consumes**：`agents/_prompt-defense.md`（canonical 源）
- **验收标准**：
  1. 脚本连跑两次，任何 agent 的 `## Prompt Defense Baseline` 出现次数不增加（TC-S2-05）
  2. 全部 agents/*.md 该节 ≤1 次（TC-S2-06）
- **covers**：`scenarios/S2-agent-system.md#S2-Case3`
- **北极星**：guardrail —— 内容去重，不增加约束

#### TT-2.3 S2-c 测试（prompt-defense 幂等）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T2.3
- **交付物**：新建 `tests/meta-b2-prompt-defense.py`（spawn 脚本两次，计数对比）
- **provides**：`tests/meta-b2-prompt-defense.py`
- **consumes**：`fixtures.S2.prompt_defense.*`
- **验收标准**：TC-S2-05/06 通过；两次运行 diff 输出留档
- **covers**：`scenarios/S2-agent-system.md#S2-Case3`

#### T2.4 frontmatter 统一（F7）
- **类型**：实现 ｜ **估时**：2h
- **目标**：agent frontmatter 语法单一样式（tools 逗号分隔 + model: inherit + color 补全）。
- **交付物**：
  - 9 个数组语法 agent：`tools: ["Read", ...]` → `tools: Read, Write, Edit, Bash, Grep, Glob`（逗号分隔）
  - `agents/workflow.md` / `agents/spec.md`：补 `model: inherit` + `color:`；tools 补 `Read`
  - 5 个缺 `color:` 的 agent：补 `color:`
  - 全量保持 `model: inherit`
- **依赖**：T2.3（先清重复再统一语法；同改 agents/*.md）
- **provides**：约 16 个 agents/*.md 的 frontmatter
- **consumes**：`fixtures.S2.frontmatter.*`
- **验收标准**：
  1. 全部 agent 含 name/description/tools/model；tools 为逗号分隔（无 `[` 数组语法）；model: inherit（TC-S2-07）
  2. color 缺失仅告警不阻断（fixtures 允许）
- **covers**：`scenarios/S2-agent-system.md#S2-Case4`
- **北极星**：guardrail —— 纯格式统一，不改变 tools 能力集合

#### TT-2.4 S2-d 测试（frontmatter 统一）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T2.4
- **交付物**：新建 `tests/meta-b2-frontmatter.py`（复用 test-suite.py 的 `parse_fm` 逻辑）
- **provides**：`tests/meta-b2-frontmatter.py`
- **consumes**：`fixtures.S2.frontmatter.*`
- **验收标准**：TC-S2-07 通过（RED：数组语法 agent 列表留档）
- **covers**：`scenarios/S2-agent-system.md#S2-Case4`

#### T2.5 code-architect 编号 + /hookify 清理（F8/F12）
- **类型**：实现 ｜ **估时**：0.5h
- **交付物**：
  - `agents/code-architect.md:68/81/94/104` → `### 0/1/2/3/4` 编号连续无重复
  - `agents/conversation-analyzer.md:4` → 去 `/hookify`，改 orch 语境描述
- **依赖**：T2.4（同改 code-architect.md / conversation-analyzer.md）
- **provides**：上述 2 文件
- **consumes**：无
- **验收标准**：
  1. code-architect.md `### 0.` 仅一次；标题编号升序连续无重复（TC-S2-08）
  2. agents/ 内 grep `/hookify` = 0（TC-S2-09）
- **covers**：`scenarios/S2-agent-system.md#S2-Case5`、`#S2-Case6`
- **北极星**：guardrail —— 编号纠错 + 外部命令残留清理

#### TT-2.5 S2-e 测试（编号 + hookify）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T2.5
- **交付物**：新建 `tests/meta-b2-numbering.py`
- **provides**：`tests/meta-b2-numbering.py`
- **consumes**：`fixtures.S2.code_architect.*`、`fixtures.S2.hookify.*`
- **验收标准**：TC-S2-08/09 通过
- **covers**：`scenarios/S2-agent-system.md#S2-Case5`、`#S2-Case6`

---

### Batch3 — S3 Skills 指令

#### T3.1 execute + spec 悬空引用修复（P0）
- **类型**：实现 ｜ **估时**：0.5h
- **交付物**：
  - `skills/execute/SKILL.md:56`：`context-injection-protocol.md` → `context-inheritance-protocol.md`（目标 `../workflow/references/context-inheritance-protocol.md` 已存在）
  - `skills/spec/SKILL.md:194`：`references/diagram-trigger-rules.md` → `../design/references/diagram-trigger-rules.md`
- **依赖**：无
- **provides**：上述 2 文件
- **consumes**：无
- **验收标准**：
  1. execute/SKILL.md 含 `context-inheritance-protocol.md` 且引用目标存在；不含 `context-injection-protocol.md`（TC-S3-01）
  2. spec/SKILL.md 含 `../design/references/diagram-trigger-rules.md` 且目标存在；无本目录悬空引用（TC-S3-02）
  3. skills/ 全部 .md 引用目标交叉校验通过，零悬空（TC-S3-03）
- **covers**：`scenarios/S3-skills-instructions.md#S3-Case1`、`#S3-Case2`
- **北极星**：guardrail —— 引用修复，无行为变更

#### TT-3.1 S3-a 测试（引用交叉校验）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T3.1
- **交付物**：新建 `tests/meta-b3-refs.py`（遍历 skills/**/*.md 提取 `](相对路径)` 与 backtick 路径解析存在性）
- **provides**：`tests/meta-b3-refs.py`
- **consumes**：`fixtures.S3.skill_refs`
- **验收标准**：TC-S3-01/02/03 通过（RED：悬空引用清单留档）
- **covers**：`scenarios/S3-skills-instructions.md#S3-Case1`、`#S3-Case2`

#### T3.2 cost 补 GATE（P1）
- **类型**：实现 ｜ **估时**：0.5h
- **交付物**：`skills/cost/SKILL.md`「## 约束」段（:177-182）追加：
  ```markdown
  <GATE>禁止跨行直接 SUM(cost_usd)——必须每 session 取最新快照（MAX(rowid) GROUP BY session_id）| 禁止硬编码模型定价</GATE>
  ```
- **依赖**：无
- **provides**：`skills/cost/SKILL.md`
- **consumes**：无
- **验收标准**：cost/SKILL.md 含 ≥1 `<GATE>`（TC-S3-04）
- **covers**：`scenarios/S3-skills-instructions.md#S3-Case3`
- **北极星**：guardrail —— 数据正确性护栏，非能力约束

#### TT-3.2 S3-b 测试（cost GATE）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T3.2
- **交付物**：新建 `tests/meta-b3-cost.py`
- **provides**：`tests/meta-b3-cost.py`
- **consumes**：`fixtures.S3.cost.*`
- **验收标准**：TC-S3-04 通过
- **covers**：`scenarios/S3-skills-instructions.md#S3-Case3`

#### T3.3 using-orch 索引补全（P1）
- **类型**：实现 ｜ **估时**：1h
- **交付物**：`skills/using-orch/SKILL.md:87-96`「可用 Skills」表 6 行 → 22 行（与磁盘 skills/ 目录对齐）
- **依赖**：无
- **provides**：`skills/using-orch/SKILL.md`
- **consumes**：磁盘 skills/ 目录清单
- **验收标准**：
  1. 索引表格覆盖全部 22 个 skill（TC-S3-05）
  2. 磁盘 skill 目录 − 索引集合 = 空集（TC-S3-06）
- **covers**：`scenarios/S3-skills-instructions.md#S3-Case4`
- **北极星**：guardrail —— 索引完整性，使模型能发现全部能力

#### TT-3.3 S3-c 测试（using-orch 索引）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T3.3
- **交付物**：新建 `tests/meta-b3-using-orch.py`
- **provides**：`tests/meta-b3-using-orch.py`
- **consumes**：`fixtures.S3.using_orch.*`、`fixtures.S3.all_skill_names`、`fixtures.S3.total_skills`
- **验收标准**：TC-S3-05/06 通过
- **covers**：`scenarios/S3-skills-instructions.md#S3-Case4`

#### T3.4 observer 激活（P2 / ADR-003，S3-Case5）
- **类型**：实现 ｜ **估时**：0.5h
- **交付物**：`skills/continuous-learning/config.json:4` → `"enabled": true`（方案 A 激活，不清理）
- **依赖**：无
- **provides**：`skills/continuous-learning/config.json`
- **consumes**：无
- **验收标准**：config.json 的 `observer.enabled === true`（TC-S3-07 前半段；R-4 说明：文档一致性由 TT-4.2/T6.1 承接）
- **covers**：`scenarios/S3-skills-instructions.md#S3-Case5`、`scenarios/S5-commands-hooks-activation.md#S5-Case2`
- **北极星**：guardrail —— 激活观察层增强学习，`SDD_DISABLED_HOOKS` 可关（不剥夺选择）

#### TT-3.4 S3-d 测试（observer 配置）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T3.4
- **交付物**：新建 `tests/meta-b3-observer.py`
- **provides**：`tests/meta-b3-observer.py`
- **consumes**：`fixtures.S3.observer.*`
- **验收标准**：TC-S3-07 配置半边通过（enabled=true）
- **covers**：`scenarios/S3-skills-instructions.md#S3-Case5`

#### T3.5 16 核心 skill TRIGGER 关键词（P2）
- **类型**：实现 ｜ **估时**：1.5h
- **交付物**：16 个核心 skill 的 `skills/{skill}/SKILL.md` frontmatter `description` 追加 `TRIGGER when: ...` 行（仅文本，不改变 SKILL 名/门控）
- **依赖**：T3.1（execute/spec 的 SKILL.md 亦在 16 核心内，同文件，须先修引用再改 description）
- **provides**：16 个 SKILL.md frontmatter description
- **consumes**：`fixtures.S3.trigger_keywords`、`fixtures.S3.all_skill_names`
- **验收标准**：
  1. 16 个核心 skill 的 description 含 `TRIGGER when`（或等效关键词）（TC-S3-08）
  2. 全部 22 个 skill description 非空（TC-S3-09）
  3. workflow 阶段门控不受影响（T7.1 self-check 复核）
- **covers**：`scenarios/S3-skills-instructions.md#S3-Case6`
- **北极星**：guardrail —— 触发描述增强可发现性，门控不变

#### TT-3.5 S3-e 测试（TRIGGER）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T3.5
- **交付物**：新建 `tests/meta-b3-trigger.py`（解析 22 个 SKILL.md frontmatter description）
- **provides**：`tests/meta-b3-trigger.py`
- **consumes**：`fixtures.S3.trigger_keywords`、`fixtures.S3.all_skill_names`
- **验收标准**：TC-S3-08/09 通过
- **covers**：`scenarios/S3-skills-instructions.md#S3-Case6`

---

### Batch4 — S5 Commands + Hooks 激活

#### T4.1 hooks.json 注册 suggest-compact + observe（F3）
- **类型**：实现 ｜ **估时**：1h
- **交付物**：修改 `hooks/hooks.json`：
  - PreToolUse 追加 `pre:compact`（matcher `Edit|Write`，command `node "${CLAUDE_PLUGIN_ROOT}/scripts/hooks/suggest-compact.js"`，timeout 5）
  - PreToolUse 追加 `pre:observe`、PostToolUse 追加 `post:observe`（command 指向 observe.sh，id 对齐 hook-flags.js）
- **依赖**：无
- **provides**：`hooks/hooks.json`（8 项事件）
- **consumes**：`scripts/hooks/suggest-compact.js`、`scripts/hooks/observe.sh`
- **验收标准**：
  1. `json.load(hooks/hooks.json)` 通过（JSON 有效）
  2. PreToolUse 存在 id 含 suggest-compact、matcher 含 Edit/Write、command 指向 suggest-compact.js 且文件存在（TC-S5-01）
  3. hooks.json 含 pre:observe / post:observe（TC-S5-02 注册半边）
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case1`、`#S5-Case2`
- **北极星**：guardrail —— 注册激活既有能力，非新约束

#### TT-4.1 S5-a 测试（hooks.json 注册）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T4.1
- **交付物**：新建 `tests/meta-b4-hooks-json.py`（json.load + 遍历 PreToolUse/PostToolUse 断言）
- **provides**：`tests/meta-b4-hooks-json.py`
- **consumes**：`fixtures.S5.hooks_file`、`fixtures.S5.hooks.suggest_compact.*`、`fixtures.S5.hooks.observe.*`
- **验收标准**：TC-S5-01 通过；JSON 有效
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case1`

#### T4.2 observe.js + observe.sh 新建（F4 / ADR-003 落地）
- **类型**：实现 ｜ **估时**：2h
- **交付物**：
  - 新建 `scripts/hooks/observe.js`（Node 跨平台）：`readStdin(2000)` 读 hook JSON → 追加观察事件到 `~/.claude/orch-instincts/observations.jsonl`，fail-open；经 `isHookEnabled('pre:observe'/'post:observe')` 门控
  - 新建 `scripts/hooks/observe.sh`（薄 POSIX 包装，`exec node "$DIR/observe.js" "$@"`）
- **依赖**：无（hooks.json 注册由 T4.1；二者文件不相交可并行）
- **provides**：`scripts/hooks/observe.js`、`scripts/hooks/observe.sh`
- **consumes**：`scripts/lib/stdin.js`、`scripts/lib/hook-flags.js`
- **验收标准**：
  1. observe.sh 存在且已注册（激活态），observe.js 可独立运行 fail-open（TC-S5-02）
  2. 空 stdin 运行 observe.js 2s 内退出不抛异常（fail-open 验证）
  3. 门控经 `isHookEnabled`：禁用时 no-op
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case2`
- **北极星**：guardrail —— fail-open + 可关，观察写入不阻塞、不剥夺控制

#### TT-4.2 S5-b 测试（observe 非死引用）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T4.2
- **交付物**：新建 `tests/meta-b4-observe.py`（检查 observe.sh 存在、hooks.json 已注册、hook-flags PROFILES 含 pre/post observe）
- **provides**：`tests/meta-b4-observe.py`
- **consumes**：`fixtures.S5.hooks.observe.*`
- **验收标准**：TC-S5-02 通过（激活态断言）；与 T3.4 config.enabled=true 联动一致
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case2`

#### T4.3 hook-flags 门控对齐
- **类型**：实现 ｜ **估时**：1h
- **目标**：suggest-compact.js 补门控；hook-flags.js PROFILES 与 hooks.json id 对齐（现 PROFILES 已含 pre:observe/post:observe/pre:compact，仅需核对 + 补缺）。
- **交付物**：
  - 修改 `scripts/hooks/suggest-compact.js`：入口加 `isHookEnabled('pre:compact')` 门控，禁用时 no-op 保持 fail-open
  - 核对 `scripts/lib/hook-flags.js`：PROFILES（minimal/standard/strict）覆盖 `pre:compact`、`pre:observe`、`post:observe`；缺失则补齐（当前已含）
- **依赖**：无（对齐校验读 hooks.json 属只读；最终交叉校验由 T6.1 self-check 承接）
- **provides**：`scripts/hooks/suggest-compact.js`、`scripts/lib/hook-flags.js`（如有补丁）
- **consumes**：`scripts/lib/hook-flags.js`
- **验收标准**：
  1. suggest-compact.js 在 `SDD_DISABLED_HOOKS=pre:compact` 时 no-op、无 side effect
  2. hook-flags.js PROFILES 含 pre:compact / pre:observe / post:observe（TC-S5-02 hook-flags 半边）
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case1`、`#S5-Case2`
- **北极星**：guardrail —— 门控可关，fail-open 缺省

#### TT-4.3 S5-c 测试（hook-flags 门控）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T4.3
- **交付物**：新建 `tests/meta-b4-hook-flags.py`（断言 PROFILES 三 id；spawn suggest-compact.js 验证 disabled no-op）
- **provides**：`tests/meta-b4-hook-flags.py`
- **consumes**：`scripts/lib/hook-flags.js`、`scripts/hooks/suggest-compact.js`
- **验收标准**：门控三 id 对齐 + disabled no-op 验证通过
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case1`

---

### Batch5 — S5 文档漂移同步（dep: Batch2+4）

#### T5.1 CLAUDE.md + AGENTS.md + README 同步（F6 / 数量口径）
- **类型**：实现 ｜ **估时**：2h
- **交付物**：
  - `CLAUDE.md`「钩子系统」表改为 hooks.json 实际 8 项脚本：session-start.js / stage-gate.js / workflow-gate.js / suggest-compact.js / observe.sh / pre-compact.js / session-evaluate.js / cost-tracker.js（双向一致）
  - `AGENTS.md`：总数 25→26（tdd-guide 已注册 + deprecated，由 T2.2 先行）
  - `README.md`：`11 professional skills` → `22 Skills`；agents 声明与入口同步（去 `/orch:sdd-dev` 残留，指 `/start-dev`）
  - `.claude-plugin/README.md`：`18 skills/12 commands` → `22 skills/14 commands`；hooks 声明对齐
  - R-1 裁决落地：数量口径维持 22/26/14，追加「另含内部自检命令 `/self-check`」说明
- **依赖**：T2.2（AGENTS.md 26）、T4.1、T4.2（CLAUDE.md 钩子表 8 项）
- **provides**：上述 4 个文档
- **consumes**：`hooks/hooks.json`、`fixtures.S5.claude_md_hooks_table`、`fixtures.S5.docs_counts.*`
- **验收标准**：
  1. CLAUDE.md 钩子表每行脚本均在 hooks.json，hooks.json 每脚本（除禁用）均在表中（TC-S5-03）
  2. README 含 22 skills/26 agents/14 commands 且无 `/orch:sdd-dev` 残留；.claude-plugin/README 含 22/14；AGENTS.md 含 26（TC-S5-04）
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case3`、`#S5-Case4`
- **北极星**：guardrail —— 文档如实反映能力，非约束

#### TT-5.1 S5-d 测试（文档口径）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T5.1
- **交付物**：新建 `tests/meta-b5-docs.py`（双向比对 CLAUDE.md 表 ↔ hooks.json；grep 数量口径）
- **provides**：`tests/meta-b5-docs.py`
- **consumes**：`fixtures.S5.claude_md_hooks_table`、`fixtures.S5.docs_counts.*`
- **验收标准**：TC-S5-03/04 通过（RED：旧 README 11/9 快照留档）
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case3`、`#S5-Case4`

#### T5.2 file-map.yaml + index.json 同步
- **类型**：实现 ｜ **估时**：1h
- **交付物**：
  - `orch-spec/context/file-map.yaml`：补 `scripts/hooks/`（observe.js/observe.sh）、`scripts/lib/`（stage-contracts.js/verdict.js）、`tests/`（meta-* + 正式套件）、`commands/self-check.md`
  - `orch-spec/context/index.json`：增补 skills/agents/commands/hooks/scripts 相关条目与 updated_at
- **依赖**：Batch2、Batch4（新增文件已存在）；self-check 相关由 T6.1 后最终核（file-map 先行登记占位）
- **provides**：`orch-spec/context/file-map.yaml`、`orch-spec/context/index.json`
- **consumes**：磁盘文件清单
- **验收标准**：file-map 含 `scripts/hooks/` `scripts/lib/` `tests/` `self-check` 条目；index.json 条目路径全部存在
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case4`
- **北极星**：guardrail —— 索引完整性

#### TT-5.2 S5-e 测试（file-map/index）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T5.2
- **交付物**：新建 `tests/meta-b5-filemap.py`（校验 file-map/index 中新增条目路径存在）
- **provides**：`tests/meta-b5-filemap.py`
- **consumes**：`orch-spec/context/file-map.yaml`、`orch-spec/context/index.json`
- **验收标准**：全部登记路径存在；index.json 可 json.load
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case4`

#### T5.3 __pycache__ 清理 + .gitignore（F11）
- **类型**：实现 ｜ **估时**：0.5h
- **交付物**：
  - `git rm -r --cached scripts/__pycache__` + 本地删除 `scripts/__pycache__/*.pyc`
  - 新建根 `.gitignore`：含 `__pycache__/` 与 `*.pyc`
- **依赖**：无（Batch5 位置按 design 保留）
- **provides**：`.gitignore`（新建）、git index 清理结果
- **consumes**：git 跟踪状态
- **验收标准**：`git ls-files | grep -E '\.pyc$|__pycache__'` 无匹配；.gitignore 含两模式（TC-S5-05）
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case5`
- **北极星**：guardrail —— 仓库卫生，无行为影响

#### TT-5.3 S5-f 测试（pyc）
- **类型**：测试 ｜ **估时**：0.5h ｜ **depends_on**：T5.3
- **交付物**：新建 `tests/meta-b5-pyc.py`（`git ls-files` 扫描 + .gitignore 内容断言）
- **provides**：`tests/meta-b5-pyc.py`
- **consumes**：`fixtures.S5.pyc.*`
- **验收标准**：TC-S5-05 通过
- **covers**：`scenarios/S5-commands-hooks-activation.md#S5-Case5`

---

### Batch6 — S4 自检与测试闭环（dep: Batch1-5）

#### T6.1 verdict.js + self-check.js + commands/self-check.md
- **类型**：实现 ｜ **估时**：3.5h
- **目标**：插件自检命令（核心交付），可测试判定模块。
- **交付物**：
  - 新建 `scripts/lib/verdict.js`：`judgeCoverage(claimed, actual, threshold=85)` → VERIFIED/PARTIAL；`judgeRate(value, threshold)` → {pass,value,threshold}；`judgeAutoResolve(errorType)` → auto-resolve/pause-for-human/unknown（auto 集：compile failure/test failure/missing file/step retry；manual 集：requirement conflict/acceptance uncertain/HARD-GATE block/cross-repo change）
  - 新建 `scripts/self-check.js`：5 块验证（`orchestration/agents/skills/tdd_loop/commands_hooks`），输出 `{blocks, issues[], summary:{total:5, passed, failed}}`，退出码 0/1，支持 `--json`；`commands_hooks` 块数量口径按 R-1（22/26/14）
  - 新建 `commands/self-check.md`：`/self-check` → `node scripts/self-check.js`
- **依赖**：Batch1-5（自检断言修复后状态）
- **provides**：`scripts/lib/verdict.js`、`scripts/self-check.js`、`commands/self-check.md`
- **consumes**：stage-contracts.js、agents/、skills/、hooks.json、CLAUDE.md、fixtures.S6.self_check.blocks
- **验收标准**：
  1. self-check exit=0 且报告含 PASS 结构（TC-S4-01）
  2. TDD 日志（execution/execution-report.md、tasks/tasks.md、.workflow-eval.json）含 RED/GREEN/REFACTOR/REVIEW 证据（TC-S4-02）
  3. `judgeCoverage(85,87)` → VERIFIED（TC-S4-03）；`judgeCoverage(90,72)` → PARTIAL（TC-S4-04）
  4. `judgeRate(83,80).pass===true`（TC-S6-02）；`judgeRate(75,80).pass===false` 且 action=optimize（TC-S6-03）；`judgeRate(90,90).pass===true`（TC-S6-04）；`judgeRate(85,90).pass===false`（TC-S6-05）
  5. `judgeAutoResolve` 对 auto 集 4 项 → auto-resolve（TC-S6-06）；manual 集 4 项 → pause-for-human（TC-S6-07）
- **covers**：`scenarios/S4-tdd-testing-loop.md#S4-Case1`、`#S4-Case2`、`#S4-Case3`；`scenarios/S6-plugin-verification-loop.md#S6-Case2`、`#S6-Case3`、`#S6-Case6`
- **北极星**：guardrail —— 自检是增强验证能力，verdict 只判不堵

#### TT-6.1 S6-a 测试（self-check + verdict）
- **类型**：测试 ｜ **估时**：1.5h ｜ **depends_on**：T6.1
- **交付物**：新建 `tests/meta-b6-selfcheck.py`（spawn self-check.js 断言 exit=0 与 5 block PASS；require verdict.js 单测边界/特殊值；独立重算覆盖率不读 executor 声明）
- **provides**：`tests/meta-b6-selfcheck.py`
- **consumes**：`fixtures.S4.self_check.*`、`fixtures.S4.tdd_phases`、`fixtures.S4.tdd_log_paths`、`fixtures.S4.coverage.*`、`fixtures.S6.*`
- **验收标准**：TC-S4-01/02/03/04/05 + TC-S6-02..07 全通过
- **covers**：`scenarios/S4-tdd-testing-loop.md#S4-Case1/2/3`、`scenarios/S6-plugin-verification-loop.md#S6-Case2/3/6`

#### T6.2 hooks-smoke.test.js + 落地 test-*.template 全套
- **类型**：实现 ｜ **估时**：4h
- **目标**：插件自身冒烟测试 + test-designer 6 模板落地为可运行正式套件。
- **交付物**：
  - 新建 `tests/hooks-smoke.test.js`（Node）：require stage-contracts 断言 8 key；spawn stage-gate.js 空 stdin 2s 内 allow；json.load hooks.json 断言 suggest-compact/observe
  - 落地 6 个 `.template` → 正式测试文件（覆盖 S1-S6 共 47 TC 的断言）：`test-orchestration.py` / `test-agent-system.py` / `test-skills.py` / `test-commands-hooks.py` / `test-tdd-loop.py` / `test-verification-loop.py`，并吸收 `tests/meta-b{1..6}-*.py`
- **依赖**：Batch1-5
- **provides**：`tests/hooks-smoke.test.js`、6 个正式测试文件
- **consumes**：`tests/*.template`（test-designer 产物）、`fixtures.json`
- **验收标准**：
  1. `node tests/hooks-smoke.test.js` 全过（冒烟行为断言）
  2. 6 个正式测试文件运行 exit=0（S1-S6 TC 全绿）
- **covers**：`scenarios/S4-tdd-testing-loop.md#S4-Case4`（回归风险）+ S1-S5 全场景
- **北极星**：guardrail —— 测试增强，非约束

#### TT-6.2 S6-b 测试（冒烟套件落地验证）
- **类型**：测试 ｜ **估时**：2h ｜ **depends_on**：T6.2
- **交付物**：运行 `node tests/hooks-smoke.test.js` 与 6 个正式测试文件，收集 exit code 矩阵
- **provides**：冒烟运行证据（exit code 矩阵留档）
- **consumes**：`tests/hooks-smoke.test.js`、6 个正式测试文件
- **验收标准**：TC-S4-06 前置（smoke 无失败）；全套件 exit=0
- **covers**：`scenarios/S4-tdd-testing-loop.md#S4-Case4`

#### T6.3 test-suite.py 扩展
- **类型**：实现 ｜ **估时**：1.5h
- **交付物**：修改 `tests/test-suite.py` 追加检查：GATE 22 覆盖、无 project-map.md、无 /hookify、hooks.json 含 suggest-compact/observe、observer.enabled=true、git 无 pyc
- **依赖**：Batch1-5
- **provides**：`tests/test-suite.py`（扩展版）
- **consumes**：`fixtures.json`、各修复后文件
- **验收标准**：`python tests/test-suite.py` exit=0、`errors=0`（TC-S4-06）
- **covers**：`scenarios/S4-tdd-testing-loop.md#S4-Case4`
- **北极星**：guardrail —— 回归护栏

#### TT-6.3 S6-c 测试（test-suite 扩展）
- **类型**：测试 ｜ **估时**：1h ｜ **depends_on**：T6.3
- **交付物**：执行 test-suite.py 并断言 `errors=0`
- **provides**：执行结果留档
- **consumes**：`tests/test-suite.py`、`fixtures.S4.smoke.*`
- **验收标准**：TC-S4-06 通过（exit=0, errors=0）
- **covers**：`scenarios/S4-tdd-testing-loop.md#S4-Case4`

---

### Batch7 — S6 验证闭环（验证型任务，自身即测试）

#### T7.1 自检 5 块全 PASS
- **类型**：验证 ｜ **估时**：2h
- **目标**：全量自检跑通，修复残留 FAIL。
- **交付物**：`node scripts/self-check.js` 输出 5 块全部 PASS（orchestration/agents/skills/tdd_loop/commands_hooks）；对 FAIL 块做最小修复迭代
- **依赖**：T6.1、T6.2、T6.3
- **provides**：自检 PASS 证据（`--json` 输出快照留档）
- **consumes**：`scripts/self-check.js`、`fixtures.S6.self_check.*`
- **验收标准**：5 个 block 全部 PASS，summary `{passed:5, failed:0}`（TC-S6-01）
- **covers**：`scenarios/S6-plugin-verification-loop.md#S6-Case1`
- **北极星**：guardrail —— 验证闭环

#### T7.2 量化度量
- **类型**：验证 ｜ **估时**：1.5h
- **目标**：自动流转率 ≥80%、产出达标率 ≥90%、容错恢复率 ≥80% 证据化。
- **交付物**：以本次元任务工作流为样本，`verdict.judgeRate(flow, 80)` / `judgeRate(pass, 90)` 判定；恢复率以 session-start 自动补偿 + fail-open 钩子为证据；无法测量项标注 `estimate`（S6-Case5 降级）
- **依赖**：T7.1
- **provides**：量化指标表（写入 testing-report 用）
- **consumes**：`.workflow-eval.json`、`.workflow-state.json`、`verdict.js`
- **验收标准**：三项指标达标或标注 estimate 且有修复清单佐证；判定证据（数字 + 来源）新鲜
- **covers**：`scenarios/S6-plugin-verification-loop.md#S6-Case2`、`#S6-Case3`、`#S6-Case4`、`#S6-Case5`
- **北极星**：guardrail —— 指标只测不堵

#### T7.3 testing-report.md
- **类型**：报告 ｜ **估时**：1.5h
- **交付物**：新建 `orch-spec/plugin-capability-optimization/testing/testing-report.md`：TV→Test→Code→Result 闭环矩阵（29 TV / 47 TC 全部对应）、5 块自检结果、量化指标表、遗留 issue 清单
- **依赖**：T7.2
- **provides**：`orch-spec/plugin-capability-optimization/testing/testing-report.md`
- **consumes**：全部 TT 测试结果、T7.1/T7.2 证据
- **验收标准**：29 TV 每项有对应 TC 与 PASS/FAIL 结果；覆盖率口径与 T7.2 一致；文件可被 archive 阶段直接消费
- **covers**：`scenarios/S6-plugin-verification-loop.md#S6-Case1`（闭环落地）
- **北极星**：guardrail —— 记录而非限制

---

## 6. DAG 无环验证（拓扑序）

```
序号  Task    依赖（depends_on）
 1   T1.1     —
 2   T1.4     —
 3   TT-1.1   T1.1
 4   TT-1.4   T1.4
 5   T1.2     T1.1
 6   T1.3     T1.1
 7   TT-1.2   T1.2
 8   TT-1.3   T1.3
 9   T2.1     (Batch1 全部)
10   TT-2.1   T2.1
11   T2.2     T2.1
12   TT-2.2   T2.2
13   T2.3     T2.2
14   TT-2.3   T2.3
15   T2.4     T2.3
16   TT-2.4   T2.4
17   T2.5     T2.4
18   TT-2.5   T2.5
19   T3.1     —
20   T3.2     —
21   T3.3     —
22   T3.4     —
23   TT-3.1   T3.1
24   TT-3.2   T3.2
25   TT-3.3   T3.3
26   TT-3.4   T3.4
27   T3.5     T3.1
28   TT-3.5   T3.5
29   T4.1     —
30   T4.2     —
31   T4.3     —
32   TT-4.1   T4.1
33   TT-4.2   T4.2
34   TT-4.3   T4.3
35   T5.1     T2.2, T4.1, T4.2
36   T5.2     Batch2, Batch4
37   T5.3     —
38   TT-5.1   T5.1
39   TT-5.2   T5.2
40   TT-5.3   T5.3
41   T6.1     Batch1-5
42   T6.2     Batch1-5
43   T6.3     Batch1-5
44   TT-6.1   T6.1
45   TT-6.2   T6.2
46   TT-6.3   T6.3
47   T7.1     T6.1, T6.2, T6.3
48   T7.2     T7.1
49   T7.3     T7.2
```

**无环声明**：所有依赖边均从低序号指向高序号（编号即拓扑深度），`T-x.depends_on ⊆ 前序`；无跨批次反向依赖；TT-x 与 T-x 同批次且仅依赖 T-x。**共 49 Task（26 实现 + 23 测试 + 3 验证/报告）**。

---

## 7. TDD 追踪表模板（executor 按此逐 Task 填写）

```
| Task | TC 映射 | RED 证据（实现前失败输出/文件路径） | GREEN 证据（实现后通过输出） | REFACTOR 记录 | REVIEW 结论 | 覆盖率佐证 | 状态 |
|------|---------|-----------------------------------|-----------------------------|--------------|------------|-----------|------|
| T1.1 | TC-S1-01/02/03 | e.g. STAGE_OUTPUTS 缺 3.5 的 grep 输出 | e.g. meta-b1-workflow-gate.py exit=0 | 去重/简化记录 | 规范+质量审查 | 行/分支数 | ✅ |
| ...  | ...     | ...                               | ...                         | ...          | ...        | ...       | ... |
```

**填写要求**：
- RED/GREEN 证据必须是真实命令输出或文件快照（拒绝"应该/可能"）。
- 每 Task 完成后立即更新 `.workflow-state.json` / `.workflow-eval.json`（状态持久化约定）。
- 覆盖率 ≥85%（verdict.judgeCoverage 独立判定，TC-S4-03/04/05）。
- 全表填充完毕、47 TC 全 PASS、5 块自检 PASS 后方可进入 T7.2/T7.3。

---

## 8. 批次验证钩子（每批完成后立即执行）

| 批次 | 命令 | 期望 |
|------|------|------|
| Batch1 | `node scripts/hooks/stage-gate.js`（空 stdin）| 2s 内输出 `{"decision":"allow"}` 自行退出 |
| Batch1 | `node scripts/hooks/workflow-gate.js`（unknown stage）| exit 0，无 stack trace |
| Batch2 | `grep -r "project-map.md" agents skills` | 0 匹配 |
| Batch3 | `python tests/meta-b3-refs.py` | exit=0（零悬空引用）|
| Batch4 | `python -c "import json;json.load(open('hooks/hooks.json'))"` | 无异常 |
| Batch5 | `git ls-files | grep -c '\.pyc$'` | 0 |
| Batch6 | `node scripts/self-check.js` | 5 块全 PASS |
| Batch7 | `python tests/test-suite.py` | `errors=0` |

---

## 9. 北极星原则审查总表（全部实现 Task）

| Task | 判定 | 理由 |
|------|------|------|
| T1.1-T1.4 | guardrail | 集中化/产出校验/恢复信息/降级 cage 均不限制能力 |
| T2.1-T2.5 | guardrail | 引用修正/注册/幂等去重/格式统一/编号清理 |
| T3.1-T3.5 | guardrail | 引用修复/GATE 数据正确性/索引/激活观察/触发描述 |
| T4.1-T4.3 | guardrail | 注册激活/fail-open/可关门控 |
| T5.1-T5.3 | guardrail | 文档如实反映能力/仓库卫生 |
| T6.1-T6.3 | guardrail | 自检/冒烟/回归护栏 |
| T7.1-T7.3 | guardrail | 验证与记录 |

**红线复核**：本清单无任何 Task 引入「禁止探索 Y / 必须采用 X 方式思考 / 禁止读取跨行文件」等 cage 措辞。stage-gate/workflow-gate 的全部 SKILL_PREREQUISITES 与 GATE 仅约束流程顺序与产出存在。
