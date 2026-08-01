# 测试规范 — plugin-capability-optimization（插件本体全方位能力优化）

**版本**：1.0
**日期**：2026-08-01
**需求类型**：元任务（meta-task，优化 orch 插件自身，不关注 token）
**测试对象**：插件的 skills/agents/commands/hooks/scripts 定义与 Node 脚本
**测试框架**：Python（静态校验，与 `tests/test-suite.py` 同风格）+ Node 断言（hook 脚本行为）
**输出**：`test-spec.md`（本文件）、`fixtures.json`、`test-*.template`

---

## 1. 测试策略与分层

本次测试针对**插件自身**，无用户业务逻辑。因此测试分层以**静态校验为主、行为断言为辅**：

| 类型 | 占比 | 覆盖内容 | 载体 |
|------|------|---------|------|
| 静态校验（Static） | 70% | frontmatter 格式、引用完整性 grep、注册表口径、JSON 有效性、文档数量口径、GATE 标记 | `test-*.template`（Python） |
| 行为断言（Behavior） | 20% | stage-gate 超时 fail-open、session-start 恢复建议、workflow-gate 产出校验 | Python spawn `node scripts/hooks/*.js` |
| 闭环冒烟（Smoke） | 10% | 自检命令可运行、`tests/test-suite.py` 全绿、5 大块 PASS | `test-verification-loop.template` |

**AAA 模式**：每个 TC 按 Arrange（准备数据/定位文件）→ Act（grep/读取/运行）→ Assert（断言）组织，独立可重复，无共享可变状态。

**数据来源**：`fixtures.json`（有效/边界/特殊值，来自各场景 Mock Data）。

---

## 2. 覆盖率矩阵（TEST-VERIFY ↔ Test Case）

| TV-ID | TEST-VERIFY（验收标准） | TC-ID | 类型 | 断言摘要 |
|-------|------------------------|-------|------|---------|
| TV-S1-01 | workflow-gate STAGE_OUTPUTS 含 3.5/5/6/9 阶段 | TC-S1-01 | Static | STAGE_OUTPUTS 覆盖全部 8 个阶段 key |
| TV-S1-01 | 同上 | TC-S1-02 | Static | 3.5/5/6/9 各含预期产出文件字符串 |
| TV-S1-01 | 同上 | TC-S1-03 | Behavior | 未知 stage 触发 fail-open（不崩溃） |
| TV-S1-02 | in_progress 状态输出自动补偿建议 | TC-S1-04 | Behavior | 生成 mock state → session-start 输出 resume-from-6 |
| TV-S1-02 | 同上 | TC-S1-05 | Behavior | 前置产出缺失 → 输出具体缺失文件清单 |
| TV-S1-02 | 同上 | TC-S1-06 | Behavior | 无进行中工作流 → no-op（不误报） |
| TV-S1-03 | 全部 GATE 无能力限制型约束 | TC-S1-07 | Static | workflow SKILL.md GATE 全部只约束流程顺序/产出存在 |
| TV-S1-04 | stdin 阻塞 2s 后 fail-open | TC-S1-08 | Behavior | 空 stdin 阻塞进程在限时内自行退出并输出 allow |
| TV-S1-04 | 同上 | TC-S1-09 | Behavior | 合法 stdin → 正确 allow/deny 决策 |
| TV-S1-05 | EXEMPT_SKILLS 仅含 Skill 名，命令名已分离 | TC-S1-10 | Static | EXEMPT 命令名全部从 EXEMPT_SKILLS 移除 |
| TV-S1-05 | 同上 | TC-S1-11 | Static | EXEMPT_SKILLS 元素 ∩ 命令列表 = 空集 |
| TV-S2-01 | grep 无 project-map.md 残留 | TC-S2-01 | Static | agents/+skills/ 内 `project-map.md` 匹配数 = 0 |
| TV-S2-01 | 同上 | TC-S2-02 | Static | 3 个指定文件引用 project-map.json |
| TV-S2-02 | AGENTS.md 注册数与磁盘一致 | TC-S2-03 | Static | 磁盘 agent 数（去 `_prompt-defense.md`）= 注册表数 |
| TV-S2-02 | 同上 | TC-S2-04 | Static | AGENTS.md 每个链接文件存在；磁盘 agent 均在注册表（或 deprecated） |
| TV-S2-03 | sync-prompt-defense 幂等 | TC-S2-05 | Behavior | 脚本运行两次，`## Prompt Defense Baseline` 不重复 |
| TV-S2-03 | 同上 | TC-S2-06 | Static | 每个 agent `Prompt Defense` 节 ≤1 次 |
| TV-S2-04 | agent frontmatter 语法统一 | TC-S2-07 | Static | 全部 agent 含 name/description/tools/model；tools 逗号语法；model: inherit |
| TV-S2-05 | code-architect 编号连续 | TC-S2-08 | Static | 无重复 `### 0.`；标题编号升序连续 |
| TV-S2-06 | grep 无 /hookify 引用 | TC-S2-09 | Static | agents/ 内 `/hookify` 匹配数 = 0 |
| TV-S3-01 | 全部 skill 引用无悬空 | TC-S3-01 | Static | execute/SKILL.md 引用 context-inheritance-protocol.md 且文件存在 |
| TV-S3-01 | 同上 | TC-S3-02 | Static | spec/SKILL.md 引用 ../design/references/diagram-trigger-rules.md 且文件存在 |
| TV-S3-01 | 同上 | TC-S3-03 | Static | skills/ 内全部 `.md` 链接目标解析存在（交叉校验） |
| TV-S3-02 | cost 含 <GATE> 标记 | TC-S3-04 | Static | skills/cost/SKILL.md 含 ≥1 个 `<GATE>` |
| TV-S3-03 | using-orch 覆盖 22 个 skill | TC-S3-05 | Static | using-orch 表格列出全部 22 个 skill |
| TV-S3-03 | 同上 | TC-S3-06 | Static | 无 skill 目录从索引遗漏（边界） |
| TV-S3-04 | observer 配置与文档一致 | TC-S3-07 | Static | config.json observer.enabled 与 CLAUDE.md 声明一致 |
| TV-S3-05 | 核心 skill description 含 TRIGGER 关键词 | TC-S3-08 | Static | 核心 skill frontmatter description 含 `TRIGGER when` |
| TV-S3-05 | 同上 | TC-S3-09 | Static | 全部 22 个 skill description 非空 |
| TV-S4-01 | 自检命令输出有效报告 | TC-S4-01 | Behavior | 自检命令 exit=0 且报告含 PASS 结构 |
| TV-S4-02 | TDD 日志含四阶段 | TC-S4-02 | Static | execution-report/tasks/eval 含 RED/GREEN/REFACTOR/REVIEW 证据 |
| TV-S4-03 | 覆盖率验证真实 | TC-S4-03 | Behavior | claimed 85 / actual 87 → VERIFIED（边界） |
| TV-S4-03 | 同上 | TC-S4-04 | Behavior | claimed 90 / actual 72 → PARTIAL（特殊） |
| TV-S4-03 | 同上 | TC-S4-05 | Behavior | 覆盖率独立重算（非 executor 自我报告） |
| TV-S4-04 | 插件冒烟测试无失败 | TC-S4-06 | Behavior | `tests/test-suite.py` exit=0 |
| TV-S5-01 | hooks.json 含 suggest-compact | TC-S5-01 | Static | hooks.json PreToolUse 注册 suggest-compact（matcher Edit/Write） |
| TV-S5-02 | observe 相关配置非死引用 | TC-S5-02 | Static | observe.sh 存在且已注册，或引用全部清理（无死配置） |
| TV-S5-03 | CLAUDE.md 钩子表与 hooks.json 一致 | TC-S5-03 | Static | CLAUDE.md 表每行钩子均在 hooks.json，双向比对 |
| TV-S5-04 | 文档数量口径一致（22/26/14） | TC-S5-04 | Static | README/.claude-plugin/README 数量口径一致 |
| TV-S5-05 | git 无 *.pyc 入库 | TC-S5-05 | Static | `git ls-files` 无 *.pyc；.gitignore 含 __pycache__/ *.pyc |
| TV-S6-01 | 自检 5 大块全部 PASS | TC-S6-01 | Behavior | 自检报告 5 个 block 全部 PASS |
| TV-S6-02 | 自动流转率 ≥80% | TC-S6-02 | Behavior | flow_rate 83 ≥ 80 → pass（边界） |
| TV-S6-02 | 同上 | TC-S6-03 | Behavior | flow_rate 75 < 80 → fail + optimize（特殊） |
| TV-S6-03 | 产出达标率 ≥90% | TC-S6-04 | Behavior | pass_rate 90 ≥ 90 → pass（边界） |
| TV-S6-03 | 同上 | TC-S6-05 | Behavior | pass_rate 85 < 90 → fail（特殊） |
| TV-S6-04 | 规则自决 + 白名单人工边界 | TC-S6-06 | Behavior | 编译/测试失败/缺文件 → auto-resolve |
| TV-S6-04 | 同上 | TC-S6-07 | Behavior | 需求冲突/验收不确定/HARD-GATE/跨仓库 → pause-for-human |

**统计**：29 条 TEST-VERIFY → 47 个 Test Case（S1:11 / S2:9 / S3:9 / S4:6 / S5:5 / S6:7），覆盖率 100%。

---

## 3. 详细测试用例

### S1 工作流编排引擎

#### TC-S1-01 STAGE_OUTPUTS 覆盖全部 8 个阶段（TV-S1-01）
- **类型**：Static
- **Arrange**：读取 `scripts/hooks/workflow-gate.js`，取 `const STAGE_OUTPUTS = {...}` 块。
- **Act**：用正则提取块内所有 `'key':`。
- **Assert**：`0_workflow_control`/`1_spec_creation`/`3.5_api_contract`/`4_code_task`/`5_code_execute`/`6_code_test`/`7_spec_archive`/`9_knowledge_continuum` 全部在 keys 中（fixtures `S1.stages_expected.all_stages`）。

#### TC-S1-02 3.5/5/6/9 各含预期产出文件（TV-S1-01）
- **类型**：Static
- **Arrange**：同上。
- **Act**：对 `stage_outputs_map` 每一项，断言 key 存在且对应产出文件字符串出现在 STAGE_OUTPUTS 块内。
- **Assert**：`3.5_api_contract`→`contract.md`,`review-report.md`；`5_code_execute`→`execution-report.md`；`6_code_test`→`testing-report.md`；`9_knowledge_continuum`→`learnings.md`,`completion-report`。

#### TC-S1-03 未知 stage fail-open（TV-S1-01）
- **类型**：Behavior
- **Arrange**：构造 state，`current_stage="unknown"`。
- **Act**：spawn `node scripts/hooks/workflow-gate.js`，stdin 传该 state 的 hook JSON。
- **Assert**：进程 exit 0，不抛异常，stderr 无 stack trace（`validateOutputs` 对未知 key 返回 `[]`，fixtures `S1.stages_expected.special`）。

#### TC-S1-04 in_progress 输出自动补偿建议（TV-S1-02）
- **类型**：Behavior
- **Arrange**：临时目录造 `orch-spec/mock-req/.workflow-state.json`（fixtures `S1.session_start.valid.mock_state`），`CLAUDE_PLUGIN_ROOT=临时目录`。
- **Act**：spawn `node scripts/hooks/session-start.js`，捕获 stdout。
- **Assert**：stdout 含工作流标识、下一阶段续接提示（`resume-from-6` / `/start-dev` 形式的恢复建议）；不静默退出。

#### TC-S1-05 前置产出缺失 → 输出缺失文件清单（TV-S1-02）
- **类型**：Behavior
- **Arrange**：mock state 的下一阶段前置产出 `testing-report.md` 缺失（fixtures `S1.session_start.prereq_missing`）。
- **Act**：spawn session-start.js。
- **Assert**：stdout 提示具体缺失文件 `testing-report.md`，而非仅泛化提示。

#### TC-S1-06 无进行中工作流 → no-op（TV-S1-02）
- **类型**：Behavior
- **Arrange**：临时目录无 `orch-spec` 或全部状态非 in_progress（fixtures `S1.session_start.no_workflow`）。
- **Act**：spawn session-start.js。
- **Assert**：stdout 无恢复建议输出（不误报）。

#### TC-S1-07 GATE 无能力限制型约束（TV-S1-03，北极星原则）
- **类型**：Static
- **Arrange**：读取 `skills/workflow/SKILL.md` 全部 `<GATE>`/`<HARD-GATE>` 文本 + `scripts/hooks/stage-gate.js` 的 SKILL_PREREQUISITES。
- **Act**：逐条扫描 GATE 文本。
- **Assert**：每条 GATE 仅约束「流程顺序 / 阶段产出存在 / 派遣完整性」，不包含限制思考深度/探索方式/创造性的措辞（如"必须采用X方式思考"、"禁止探索Y"）；违规条目标记为能力限制型（FAIL）。

#### TC-S1-08 stdin 阻塞 2s 后 fail-open（TV-S1-04）
- **类型**：Behavior
- **Arrange**：spawn `node scripts/hooks/stage-gate.js`，stdin 管道打开但不写入（模拟 stdin 数据迟到）。
- **Act**：轮询进程退出，限时 6s（fixtures `S1.stdin_timeout_ms`=2000）。
- **Assert**：进程在限时内自行退出（非被杀），stdout 为 `{"decision":"allow"}`；若阻塞超时→FAIL（修复前 RED 态）。

#### TC-S1-09 合法 stdin → 正确决策（TV-S1-04）
- **类型**：Behavior
- **Arrange**：stdin 写入一个 Skill 调用的 hook JSON（如 tool_name=`Skill`，skill=execute，前置未完成）。
- **Act**：spawn stage-gate.js，写 JSON + 关闭 stdin。
- **Assert**：stdout 为合法 JSON，含 `decision` 字段（allow 或 deny）；无挂起。

#### TC-S1-10 EXEMPT 命令名从 EXEMPT_SKILLS 移除（TV-S1-05）
- **类型**：Static
- **Arrange**：读取 `scripts/hooks/stage-gate.js` 的 `EXEMPT_SKILLS` 数组。
- **Act**：解析数组元素；与 fixtures `S1.exempt.command_names` 比对。
- **Assert**：`checkpoint`/`code-review`/`plan`/`quality-gate`/`session-resume`/`session-save`/`start-dev` 均不在 EXEMPT_SKILLS 中。

#### TC-S1-11 EXEMPT_SKILLS ∩ 命令列表 = 空集（TV-S1-05）
- **类型**：Static
- **Act**：EXEMPT_SKILLS 元素与 `S1.exempt.command_names` 求交集。
- **Assert**：交集为空；文件存在独立的 `EXEMPT_COMMANDS`（或等价分离注释）。

---

### S2 Agent 体系

#### TC-S2-01 无 project-map.md 残留（TV-S2-01）
- **类型**：Static
- **Arrange**：`agents/`、`skills/` 目录递归。
- **Act**：grep `project-map.md`。
- **Assert**：匹配数 = 0（fixtures `S2.project_map.forbidden_ref`）。

#### TC-S2-02 指定文件引用 project-map.json（TV-S2-01）
- **类型**：Static
- **Arrange**：`agents/code-architect.md`、`agents/tasker.md`、`skills/design/SKILL.md`。
- **Act**：逐个读取，grep `project-map.json`。
- **Assert**：每个文件包含 `project-map.json`（fixtures `S2.project_map.files_to_check`）。

#### TC-S2-03 磁盘 agent 数 = 注册表数（TV-S2-02）
- **类型**：Static
- **Arrange**：`agents/*.md` 去 `_prompt-defense.md`；AGENTS.md 注册表。
- **Act**：统计磁盘数 N_disk、注册表链接数 N_reg。
- **Assert**：N_disk = N_reg = 26（fixtures `S2.agent_count`）。

#### TC-S2-04 注册表链接有效 + 磁盘 agent 全覆盖（TV-S2-02）
- **类型**：Static
- **Act**：AGENTS.md 中每个 `agents/xxx.md` 链接检查文件存在；对每个磁盘 agent 检查其在 AGENTS.md 中出现（tdd-guide 若 deprecated 则需显式标注）。
- **Assert**：无断链；无未登记 agent（fixtures `S2.tdd_guide.status=deprecated` 允许）。

#### TC-S2-05 sync-prompt-defense 幂等（TV-S2-03）
- **类型**：Behavior
- **Arrange**：运行 `python scripts/sync-prompt-defense.py`。
- **Act**：连跑两次（fixtures `S2.prompt_defense.expected_runs`=2）。
- **Assert**：第二次运行后，任何 agent 的 `## Prompt Defense Baseline` 出现次数不增加（幂等）。

#### TC-S2-06 每个 agent Prompt Defense 节 ≤1（TV-S2-03）
- **类型**：Static
- **Act**：遍历 agents/*.md，统计 `## Prompt Defense Baseline` 出现次数。
- **Assert**：全部 ≤1（fixtures `S2.prompt_defense.max_occurrences`）。

#### TC-S2-07 frontmatter 统一（TV-S2-04）
- **类型**：Static
- **Arrange**：解析每个 agent 的 frontmatter（复用 `test-suite.py` 的 `parse_fm` 逻辑）。
- **Act**：校验 required_keys、tools 语法、model 值。
- **Assert**：全部含 `name/description/tools/model`；`tools` 为逗号分隔（`"Glob, Grep"`）非数组（`["Read"]`）；`model: inherit`；`color` 缺失仅警告（fixtures `S2.frontmatter`）。

#### TC-S2-08 code-architect 编号连续（TV-S2-05）
- **类型**：Static
- **Act**：读取 `agents/code-architect.md`，正则匹配 `^### N.` 标题。
- **Assert**：`### 0.` 仅出现一次；编号升序连续，无重复（fixtures `S2.code_architect`）。

#### TC-S2-09 无 /hookify 引用（TV-S2-06）
- **类型**：Static
- **Act**：grep `agents/` 中 `/hookify`。
- **Assert**：匹配数 = 0（fixtures `S2.hookify.forbidden`）。

---

### S3 Skills 指令

#### TC-S3-01 execute 引用修正（TV-S3-01）
- **类型**：Static
- **Act**：读取 `skills/execute/SKILL.md`，grep `context-inheritance-protocol.md`。
- **Assert**：文件包含 `context-inheritance-protocol.md` 且该引用目标存在（`../workflow/references/context-inheritance-protocol.md`）；不含 `context-injection-protocol.md`（fixtures `S3.skill_refs[0]`）。

#### TC-S3-02 spec 引用修正（TV-S3-01）
- **类型**：Static
- **Act**：读取 `skills/spec/SKILL.md`，grep `../design/references/diagram-trigger-rules.md`。
- **Assert**：引用存在且目标文件存在；不含本目录 `references/diagram-trigger-rules.md` 悬空引用（fixtures `S3.skill_refs[1]`）。

#### TC-S3-03 skills/ 全部链接交叉校验（TV-S3-01）
- **类型**：Static
- **Arrange**：遍历 `skills/**/*.md`。
- **Act**：提取所有 `](相对路径)` 与 backtick 引用路径；解析并检查存在性。
- **Assert**：全部引用目标存在（悬空引用 = FAIL）。

#### TC-S3-04 cost 含 <GATE>（TV-S3-02）
- **类型**：Static
- **Act**：读取 `skills/cost/SKILL.md`，计数 `<GATE>`。
- **Assert**：≥1（fixtures `S3.cost.min_gate_count`）。

#### TC-S3-05 using-orch 覆盖 22 个 skill（TV-S3-03）
- **类型**：Static
- **Act**：读取 `skills/using-orch/SKILL.md`「可用 Skills」表，提取表内 skill 名；与磁盘 `skills/` 目录名比对。
- **Assert**：索引覆盖全部 22 个 skill（fixtures `S3.using_orch.indexed`）。

#### TC-S3-06 无 skill 目录遗漏（TV-S3-03，边界）
- **类型**：Static
- **Act**：磁盘 skill 目录集合 − 索引集合。
- **Assert**：差集为空。

#### TC-S3-07 observer 配置与文档一致（TV-S3-04）
- **类型**：Static
- **Act**：读取 `skills/continuous-learning/config.json` 的 `observer.enabled`；扫描 CLAUDE.md 中 instinct/observer 声明。
- **Assert**：若 enabled=false 则文档不得宣称"已启用"；若 enabled=true 则文档宣称一致且 observe 配置非死引用（与 S5 联动）。

#### TC-S3-08 核心 skill description 含 TRIGGER 关键词（TV-S3-05）
- **类型**：Static
- **Arrange**：16 个核心工作流 skill（fixtures `S3.all_skill_names` 中除 6 社区 skill 外）。
- **Act**：解析 frontmatter description。
- **Assert**：description 含 `TRIGGER when`（或等效关键词，fixtures `S3.trigger_keywords`）。

#### TC-S3-09 全部 22 个 skill description 非空（TV-S3-05）
- **类型**：Static
- **Act**：遍历 22 个 SKILL.md frontmatter。
- **Assert**：description 全部非空。

---

### S4 TDD 执行与测试闭环

#### TC-S4-01 自检命令可运行（TV-S4-01）
- **类型**：Behavior
- **Arrange**：自检命令（`commands/self-check.md` 或 `tests/test-suite.py` / `orch:self-check`）。
- **Act**：运行自检命令。
- **Assert**：exit=0，输出含 PASS（fixtures `S4.self_check`）。

#### TC-S4-02 TDD 日志含四阶段证据（TV-S4-02）
- **类型**：Static
- **Act**：对 `execution/execution-report.md`、`tasks/tasks.md`、`.workflow-eval.json` 扫描 RED/GREEN/REFACTOR/REVIEW。
- **Assert**：四阶段关键字在 TDD 日志中均有出现（fixtures `S4.tdd_phases`）。

#### TC-S4-03 覆盖率边界 → VERIFIED（TV-S4-03）
- **类型**：Behavior
- **Act**：调用覆盖率判定函数（claimed=85, actual=87）。
- **Assert**：verdict=VERIFIED（fixtures `S4.coverage.boundary`）。

#### TC-S4-04 覆盖率特殊 → PARTIAL（TV-S4-03）
- **类型**：Behavior
- **Act**：调用覆盖率判定函数（claimed=90, actual=72）。
- **Assert**：verdict=PARTIAL（fixtures `S4.coverage.valid`）。

#### TC-S4-05 覆盖率独立重算（TV-S4-03）
- **类型**：Behavior
- **Act**：不读 executor 声明，独立从测试输出/覆盖率文件统计实测值。
- **Assert**：实测值存在且可作为判定输入（拒绝"应该/可能"式声明）。

#### TC-S4-06 插件冒烟测试无失败（TV-S4-04）
- **类型**：Behavior
- **Act**：运行 `tests/test-suite.py`。
- **Assert**：exit=0，`errors=0`（fixtures `S4.smoke`）。

---

### S5 Commands + Hooks 激活

#### TC-S5-01 hooks.json 含 suggest-compact（TV-S5-01）
- **类型**：Static
- **Act**：`json.load(hooks/hooks.json)`，遍历 PreToolUse。
- **Assert**：存在 id=`suggest-compact`，matcher 含 Edit/Write，command 指向 `scripts/hooks/suggest-compact.js` 且文件存在（fixtures `S5.hooks.suggest_compact`）。

#### TC-S5-02 observe 非死引用（TV-S5-02）
- **类型**：Static
- **Act**：检查 `scripts/hooks/observe.sh` 是否存在；hooks.json 是否注册 observe；hook-flags.js PROFILES 是否含 pre/post observe；CLAUDE.md 是否引用。
- **Assert**：非死引用——要么 observe.sh 存在且已注册（激活态），要么全部引用（hook-flags/CLAUDE.md/hooks.json）已清理（处置态）。

#### TC-S5-03 CLAUDE.md 钩子表与 hooks.json 一致（TV-S5-03）
- **类型**：Static
- **Act**：解析 CLAUDE.md「钩子系统」表列出的脚本名；解析 hooks.json 全部 command 中的脚本名。
- **Assert**：双向一致——CLAUDE.md 表中每个脚本都在 hooks.json 中，hooks.json 中每个脚本（除禁用）都在 CLAUDE.md 表中（fixtures `S5.claude_md_hooks_table`）。

#### TC-S5-04 文档数量口径一致（TV-S5-04）
- **类型**：Static
- **Act**：grep README.md / .claude-plugin/README.md / AGENTS.md 的数量声明；与磁盘实际数比对。
- **Assert**：README 含 22 skills/26 agents/14 commands 且无 `/orch:sdd-dev` 残留；.claude-plugin/README 含 22/14；AGENTS.md 含 26（fixtures `S5.docs_counts`）。

#### TC-S5-05 git 无 *.pyc 入库（TV-S5-05）
- **类型**：Static
- **Act**：`git ls-files | grep -E '\.pyc$|__pycache__'`；检查 .gitignore 是否含 `__pycache__`/`*.pyc`。
- **Assert**：git ls-files 无匹配；.gitignore 含对应模式（fixtures `S5.pyc`）。

---

### S6 插件验证闭环

#### TC-S6-01 自检 5 大块全部 PASS（TV-S6-01）
- **类型**：Behavior
- **Act**：运行统一自检命令。
- **Assert**：报告的 blocks 含 `orchestration/agents/skills/tdd_loop/commands_hooks` 五项且全部 PASS（fixtures `S6.self_check.blocks`）。

#### TC-S6-02 自动流转率 ≥80% 达标（TV-S6-02，边界）
- **类型**：Behavior
- **Act**：调用流转率判定函数（value=83, threshold=80）。
- **Assert**：pass=true（fixtures `S6.flow_rate.boundary`）。

#### TC-S6-03 自动流转率 <80% 定位优化（TV-S6-02，特殊）
- **类型**：Behavior
- **Act**：调用流转率判定函数（value=75, threshold=80）。
- **Assert**：pass=false，action=optimize（fixtures `S6.flow_rate.special`）。

#### TC-S6-04 产出达标率 ≥90% 达标（TV-S6-03，边界）
- **类型**：Behavior
- **Act**：调用达标率判定函数（value=90, threshold=90）。
- **Assert**：pass=true（fixtures `S6.pass_rate.boundary`）。

#### TC-S6-05 产出达标率 <90% 打回（TV-S6-03，特殊）
- **类型**：Behavior
- **Act**：调用达标率判定函数（value=85, threshold=90）。
- **Assert**：pass=false（fixtures `S6.pass_rate.special`）。

#### TC-S6-06 规则自决（TV-S6-04）
- **类型**：Behavior
- **Act**：对 `S6.auto_resolve.auto_cases`（compile failure/test failure/missing file/step retry）调用裁决函数。
- **Assert**：verdict=auto-resolve（自动补偿，重试/补建/降级）。

#### TC-S6-07 白名单人工边界（TV-S6-04）
- **类型**：Behavior
- **Act**：对 `S6.auto_resolve.manual_cases`（requirement conflict/acceptance uncertain/HARD-GATE block/cross-repo change）调用裁决函数。
- **Assert**：verdict=pause-for-human（暂停等人工）。

---

## 4. fixtures.json 数据说明

- **有效输入**：正常路径数据（如 stage=6_test → testing-report.md）。
- **边界值**：阈值临界（flow_rate=83/80、pass_rate=90/90、coverage 85/87）。
- **特殊值**：异常输入（unknown stage、coverage 90/72、flow_rate 75、/hookify 残留）。
- 全部可 JSON 解析（已用 `json.load` 验证）。

---

## 5. 运行方式

```bash
# 静态+行为校验（S1-S5）
python tests/test-orchestration.template   # 或按 executor 约定改名为 test-orchestration.py
python tests/test-agent-system.template
python tests/test-skills.template
python tests/test-commands-hooks.template

# TDD 闭环 + 验证闭环（S4/S6）
python tests/test-tdd-loop.template
python tests/test-verification-loop.template

# 全量冒烟（S4 Case4 / S6 前置）
python tests/test-suite.py
```

> 注：`.template` 后缀为 spec 阶段骨架；executor 在 execute 阶段按 TDD 落地为可运行测试文件（RED → GREEN → REFACTOR → REVIEW）。

---

## 6. GATE 自检

- [x] 每条 TEST-VERIFY（S1:5 / S2:6 / S3:5 / S4:4 / S5:5 / S6:4 = 29）至少映射 1 个 Test Case（实际 47 个）。
- [x] fixtures.json 可解析（`json.load` 通过）。
- [x] TC-ID 命名清晰，AAA 模式，独立可重复。
- [x] 边界值与特殊值全部覆盖。
