# 架构蓝图：plugin-capability-optimization（orch 插件本体能力优化）

**版本**：1.0 ｜ **日期**：2026-08-01 ｜ **模式**：standard ｜ **project-mode**：backend（无 DB/前端，插件自身 Node/Markdown 工具链）

**北极星原则（最高约束，贯穿全部决策）**：约束 = 护栏（防坠落）非牢笼（限奔跑）。每项修改必须审查"是否限制模型思考深度/探索自由/创造性"，若限制则降级为建议。本次所有设计已逐项标注北极星判定（guardrail 保留 / cage 降级）。

**设计对齐约束**：test-designer 已并行产出 `tests/test-spec.md`（47 个 TC）+ `tests/fixtures.json`。本设计的每个改动点必须使对应 TC 可 PASS，自检命令的输出结构必须与 `fixtures.S6.self_check.blocks`（orchestration/agents/skills/tdd_loop/commands_hooks 五块）完全一致。

---

## 0. 现状基线 → 修复映射表

| 编号 | 问题 | 位置 | 修复落点 | 场景 |
|------|------|------|---------|------|
| P0 | execute 悬空引用 | skills/execute/SKILL.md:56 | S3-Case1 | S3 |
| P0 | spec 悬空引用 | skills/spec/SKILL.md:194 | S3-Case2 | S3 |
| P1 | cost 无 GATE | skills/cost/SKILL.md | S3-Case3 | S3 |
| P1 | using-orch 索引 6/22 | skills/using-orch/SKILL.md:87-96 | S3-Case4 | S3 |
| P2 | observer 关闭 | skills/continuous-learning/config.json:4 | S3-Case5 + S5-Case2 | S3/S5 |
| P2 | TRIGGER 缺失 | 16 核心 skill frontmatter | S3-Case6 | S3 |
| F1 | project-map.md 误引用（4 处） | code-architect.md:19 / tasker.md:13 / design/SKILL.md:45 / agent-dispatch-code.md:125 | S2-Case1 | S2 |
| F2 | tdd-guide 孤立 | agents/tdd-guide.md + AGENTS.md | S2-Case2 | S2 |
| F3 | suggest-compact 未注册 | hooks/hooks.json + scripts/hooks/suggest-compact.js | S5-Case1 | S5 |
| F4 | observe.sh 死配置 | hook-flags.js + CLAUDE.md | S5-Case2 | S5 |
| F5 | Prompt Defense 重复 ×9 | agents/*.md + scripts/sync-prompt-defense.py | S2-Case3 | S2 |
| F6 | CLAUDE.md 钩子表脱节 | CLAUDE.md | S5-Case3 | S5 |
| F7 | frontmatter 稀疏/风格不一 | agents/*.md（9 个数组语法） | S2-Case4 | S2 |
| F8 | code-architect 编号重复 | agents/code-architect.md:68/81 | S2-Case5 | S2 |
| F9 | EXEMPT_SKILLS 混命令名 | scripts/hooks/stage-gate.js:99-104 | S1-Case5 | S1 |
| F10 | STAGE_OUTPUTS 缺 3.5/5/6/9 | scripts/hooks/workflow-gate.js:39-44 | S1-Case1 | S1 |
| F11 | __pycache__ 入库 | scripts/__pycache__/*.pyc | S5-Case5 | S5 |
| F12 | /hookify 残留 | agents/conversation-analyzer.md:4 | S2-Case6 | S2 |
| 最大缺口 | 无自检命令 | — | S4-Case1 + S6 | S4/S6 |

---

## 1. S1 工作流编排引擎

### 1.1 架构决策 ADR-002：阶段契约集中化

**修改**：新建 `scripts/lib/stage-contracts.js`，统一导出 `STAGE_ORDER` / `STAGE_OUTPUTS` / `SKILL_PREREQUISITES` / `EXEMPT_SKILLS` / `EXEMPT_COMMANDS`。`workflow-gate.js`、`stage-gate.js`、`session-start.js` 三处删除本地副本，改为 `require('../lib/stage-contracts')`。

**理由**：F10 根因是 workflow-gate 的 STAGE_OUTPUTS 与 stage-gate 的 SKILL_PREREQUISITES 两套阶段映射独立维护导致不对称。集中化后单一事实源（代码侧），与文档侧 `flow-execution-reference.md`（Source of Truth）呼应。直接支撑 S1-Case1"与 stage-gate.js 对称"的要求。

**北极星审查**：guardrail —— 集中化不新增任何约束，仅消除漂移；未来阶段定义变更只改一处，反而降低误伤模型的风险。

### 1.2 Case 1：workflow-gate STAGE_OUTPUTS 补齐 3.5/5/6/9

**文件**：`scripts/lib/stage-contracts.js`（从 workflow-gate.js:39-44 迁出并扩展）

**内容**（对齐 `fixtures.S1.stages_expected.stage_outputs_map`）：
```js
const STAGE_OUTPUTS = {
  '0_workflow_control':     ['.workflow-state.json', '.workflow-eval.json'],
  '1_spec_creation':        ['spec/requirement.md', 'spec/scenarios'],
  '3.5_api_contract':       ['contract/contract.md', 'contract/review-report.md'],
  '4_code_task':            ['tasks/tasks.md'],
  '5_code_execute':         ['execution/execution-report.md'],
  '6_code_test':            ['testing/testing-report.md'],
  '7_spec_archive':         ['archive-log.md'],
  '9_knowledge_continuum':  ['../context/learnings.md', 'completion-report'],
};
```
- `'../context/learnings.md'`：连续学习写入项目级 `orch-spec/context/learnings.md`，`path.join(PLUGIN_ROOT,'orch-spec',reqId,out)` 遇 `..` 天然归一化到 `orch-spec/context/learnings.md`。
- `'completion-report'`：伪产出，需在 `workflow-gate.js` 的 `validateOutputs(stageName, reqId)` 签名扩展为 `validateOutputs(stageName, reqId, state)`，当 `out === 'completion-report'` 时改查 `state.completion_report_generated === true` 而非文件存在。
- 8 个阶段 key（0/1/3.5/4/5/6/7/9）。2/3（并行中间产物由 3.5/4 兜底）、5.5（execute 子过程）、8（写 .workflow-eval.json，已由 0 覆盖）有意不 gate。

**依赖**：无。**北极星**：guardrail —— 只校验"产出存在"，不约束怎么产出。

### 1.3 Case 4：stage-gate stdin 超时防护

**文件**：`scripts/hooks/stage-gate.js:163-177`（stdin 读取段）

**修改**：删除阻塞式 `while ((chunk = fs.readFileSync(fd, 'utf8', 4096)))` 循环，改为主流程异步化并复用 `scripts/lib/stdin.js` 的 `readStdin(2000)`（2s 超时）。超时后返回 `{decision:'allow'}` fail-open，并 stderr 记 `[STAGE-GATE] stdin timeout — fail-open`。`stdin.js:6` 的 `TIMEOUT_MS=2000` 与 `fixtures.S1.stdin_timeout_ms=2000` 一致。

```js
async function main() {
  const raw = await readStdin(2000);          // 超时自动 resolve 已收片段
  if (!raw || !raw.trim()) { process.stdout.write(JSON.stringify({decision:'allow'})); return; }
  ...
}
main().catch(() => process.stdout.write(JSON.stringify({decision:'allow'})));
```

**依赖**：`scripts/lib/stdin.js`。**同模式修复**：`workflow-gate.js:112` 的 `fs.readFileSync(process.stdin.fd)` 同样无超时，一并改 `readStdin(2000)`。

**北极星**：guardrail —— 超时防护是可靠性护栏，杜绝 hook 挂起阻塞模型调用。

### 1.4 Case 5：EXEMPT_SKILLS 命令名分离

**文件**：`scripts/lib/stage-contracts.js`（从 stage-gate.js:99-104 迁出并拆分）

**内容**（对齐 `fixtures.S1.exempt`）：
```js
const EXEMPT_SKILLS = [
  'scripts', 'context-budget', 'depth', 'compact', 'cost',
  'ralph-loop', 'using-orch', 'debug', 'req-change', 'spec-migrate',
];  // 仅真 Skill 名（10 个）
const EXEMPT_COMMANDS = [
  'checkpoint', 'code-review', 'plan', 'quality-gate',
  'session-resume', 'session-save', 'start-dev', 'cost-report', 'self-check',
];  // 命令名分离（含新增 self-check）
```
`stage-gate.js` 的豁免判断 `EXEMPT_SKILLS.includes(skillName)` 保持不变；`EXEMPT_COMMANDS` 仅作文档化分离 + 防御。

**北极星**：guardrail —— 纯命名清理，不改变任何门控行为。

### 1.5 Case 2：session-start 中断恢复自动补偿

**文件**：`scripts/hooks/session-start.js:12-29`

**修改**：`checkWorkflowState` 升级为：
1. 对每个 `in_progress` 工作流，从 `state.stages[]` 找最后一个 `status in (done|completed)` 的阶段（按 STAGE_ORDER 取最大 order）；
2. 由 `STAGE_ORDER` 推下一阶段 `next_stage`（order 最小且 > last_done 且未 done）；
3. 用 `STAGE_OUTPUTS[next_stage]` 检查前置产出：全部存在 → 输出 `resume-from-<N>` + 建议续接 Skill；有缺失 → 逐条输出缺失文件路径；
4. 无 in_progress → no-op（不误报）；
5. 明确不静默自动续接（北极星：模型自主决策，但提供完整恢复信息）。

**依赖**：`scripts/lib/stage-contracts.js`（STAGE_ORDER + STAGE_OUTPUTS）。**北极星**：guardrail —— 提供信息、不剥夺决策权。

### 1.6 Case 3：北极星原则审查（S1-Case3，全场景共用）

**修改**：`commands/start-dev.md:12` 降级 + 审查结论落盘。

| GATE 原文 | 位置 | 判定 | 动作 |
|-----------|------|------|------|
| 收到指令后立即调用 Skill(workflow)，禁止在调用前执行任何代码探索/文件读取/目录扫描/项目分析 | start-dev.md:12 | **cage**（限制探索自由） | 降级为建议 |
| 上下文优先…仅当注入信息不足以确定 Task 边界时才补充 Read 原文 | tasker.md:24 | **cage**（token 时代残留） | 降级为建议 |
| 禁止主上下文直接编码，每 Task 必须通过子代理 | agent-dispatch-code.md:180 | guardrail（并行架构） | 保留 |
| SKILL_PREREQUISITES 全部 | stage-gate.js | guardrail（纯流程顺序/产出存在） | 保留 |
| 不能跳过 RED 阶段 / 覆盖率不低于 85% | tdd-guide.md:23 | guardrail | 保留 |
| TEST-VERIFY 覆盖率 100% 禁止输出 | test-design SKILL | guardrail | 保留 |
| 测试定义 WHAT 不限制 HOW | business-rules 约束4 | 已对齐北极星 | 保留 |

**审查结论写入**：`spec/business-rules.md` 追加「北极星原则审查结论」章节。

---

## 2. S2 Agent 体系

### 2.1 Case 1：project-map 引用统一（F1，4 处）

- `agents/code-architect.md:19`：`project-map.md` → `project-map.json`
- `agents/tasker.md:13`：`project-map.md` → `project-map.json`
- `skills/design/SKILL.md:45`：`project-map.md` → `project-map.json`
- `skills/workflow/references/agent-dispatch-code.md:125`：`project-map.md` → `project-map.json`

### 2.2 Case 2：tdd-guide 处置（ADR-001：注册 + 标注 deprecated）

**决策**：保留文件、注册进 AGENTS.md、标注 deprecated 并划清与 code-reviewer 边界。

- `agents/tdd-guide.md`：frontmatter 后加 deprecated 横幅
- `AGENTS.md`：扩展表追加 tdd-guide → 注册数 25→26
- `agents/code-reviewer.md:30`：补边界注记
- `agent-dispatch-code.md:182` + `flow-execution-reference.md:35`：保留四阶段 GATE 规则，行内注 deprecated

**边界定义**：tdd-guide = 执行期四阶段日志完整性门控规则；code-reviewer = 批次后综合审查，TDD 仅为其维度之一。

### 2.3 Case 3：Prompt Defense 幂等（F5）

**文件**：`scripts/sync-prompt-defense.py:23-30`

**修改**：改为"先全量清除、再单次插入"：
```python
cleaned = re.sub(r'^##\s*Prompt Defense Baseline\n.*?(?=\n## |\Z)', '', orig, count=0, flags=re.DOTALL)
cleaned = re.sub(r'^#{1,3}\s*Prompt Defense Baseline\s*$', '', cleaned, flags=re.MULTILINE)
```
幂等保证：跑两次输出一致；每个 agent `## Prompt Defense Baseline` ≤1。

### 2.4 Case 4：frontmatter 统一（F7）

**文件**：9 个数组语法 agent + `workflow.md` / `spec.md` + 5 个缺 color agent

- 全部 `tools: ["Read", ...]` → `tools: Read, Write, Edit, Bash, Grep, Glob`（逗号分隔）
- `workflow.md` / `spec.md` 补 `model: inherit` + `color:`；tools 补 `Read`
- 5 个缺 color 的 agent 补 `color:`
- `model: inherit` 约定保持全量
- 顺序：先 T2.3 清 Prompt Defense 重复、再 T2.4 统一（同文件两处修改）

### 2.5 Case 5：code-architect 编号（F8）

**文件**：`agents/code-architect.md:68/81/94/104` → `### 0/1/2/3/4` 编号连续无重复

### 2.6 Case 6：/hookify 清理（F12）

**文件**：`agents/conversation-analyzer.md:4` → 改为 orch 语境描述，消除外部命令残留

---

## 3. S3 Skills 指令

### 3.1 Case 1-2：悬空引用（P0）

- `skills/execute/SKILL.md:56`：`context-injection-protocol.md` → `context-inheritance-protocol.md`
- `skills/spec/SKILL.md:194`：`references/diagram-trigger-rules.md` → `../design/references/diagram-trigger-rules.md`

### 3.2 Case 3：cost 补 GATE（P1）

**文件**：`skills/cost/SKILL.md`（"## 约束"段，:177-182）

```markdown
<GATE>禁止跨行直接 SUM(cost_usd)——必须每 session 取最新快照（MAX(rowid) GROUP BY session_id）| 禁止硬编码模型定价</GATE>
```

### 3.3 Case 4：using-orch 索引补全（P1）

**文件**：`skills/using-orch/SKILL.md:87-96` → 「可用 Skills」表从 6 行扩为 22 行。

### 3.4 Case 5 + S5-Case2：observer 激活（ADR-003）

**决策**：激活 instinct 观察层（方案 A），不清理。`skills/continuous-learning/config.json:4` → `"enabled": true`。

### 3.5 Case 6：TRIGGER 关键词（P2）

**文件**：16 个核心 skill 的 SKILL.md frontmatter `description` 追加 `TRIGGER when:` 行。不得破坏 workflow 阶段门控。

---

## 4. S4 TDD 执行与测试闭环

### 4.1 可测试判定模块

**新建** `scripts/lib/verdict.js`：
```js
function judgeCoverage(claimed, actual, threshold = 85) { return actual >= threshold ? 'VERIFIED' : 'PARTIAL'; }
function judgeRate(value, threshold) { return { pass: value >= threshold, value, threshold }; }
function judgeAutoResolve(errorType) {
  const auto = ['compile failure','test failure','missing file','step retry'];
  const manual = ['requirement conflict','acceptance uncertain','HARD-GATE block','cross-repo change'];
  return auto.includes(errorType) ? 'auto-resolve' : manual.includes(errorType) ? 'pause-for-human' : 'unknown';
}
module.exports = { judgeCoverage, judgeRate, judgeAutoResolve };
```

### 4.2 自检命令（核心交付）

**新建** `scripts/self-check.js` + `commands/self-check.md`。命令 `/self-check` → `node scripts/self-check.js`（支持 `--json`）。

**5 块验证规范**：
| 块 | 验证项 |
|----|--------|
| orchestration | STAGE_OUTPUTS 8 阶段 key；EXEMPT_SKILLS∩命令=空；stdin 超时；session-start 补偿逻辑 |
| agents | 无 project-map.md；注册数==磁盘==26；Prompt Defense ≤1；无数组 tools 语法；编号连续；无 /hookify |
| skills | 引用交叉校验；cost 含 GATE；using-orch 22 skill；observer.enabled===true；TRIGGER when |
| tdd_loop | self-check.md 存在；RED/GREEN/REFACTOR/REVIEW；覆盖率有佐证；verdict.js 边界自测 |
| commands_hooks | hooks.json 含 suggest-compact+observe；observe.sh 存在；CLAUDE.md 双向一致；22/26/14；无 pyc |

**输出**：`{ blocks, issues[], summary: {total:5, passed, failed} }`；退出码 0/1。

### 4.3 插件自身冒烟测试

**新建** `tests/hooks-smoke.test.js`（Node）：require stage-contracts 断言、spawn stage-gate 空 stdin 2s 内 allow、json.load hooks.json 断言。

**扩展** `tests/test-suite.py`：追加 GATE 22 覆盖、无 project-map.md、无 /hookify、hooks.json 含 suggest-compact/observe、observer.enabled=true、git 无 pyc。

---

## 5. S5 Commands + Hooks 激活

### 5.1 Case 1：suggest-compact 注册（F3）

**文件**：`hooks/hooks.json` PreToolUse 追加：
```json
{
  "matcher": "Edit|Write",
  "hooks": [{
    "type": "command",
    "command": "node \"${CLAUDE_PLUGIN_ROOT}/scripts/hooks/suggest-compact.js\"",
    "description": "Suggest /compact at logical boundaries after 40 Edit/Write ops",
    "timeout": 5
  }],
  "id": "pre:compact"
}
```
`suggest-compact.js` 自身补 `isHookEnabled('pre:compact')` 门控，保持 fail-open。

### 5.2 Case 2：observe 激活（F4，ADR-003 落地）

**新建** `scripts/hooks/observe.js`（Node 实现，跨平台）：readStdin(2000) 读取 hook JSON → 追加观察事件到 `~/.claude/orch-instincts/observations.jsonl`，fail-open。

**新建** `scripts/hooks/observe.sh`（薄 POSIX 包装）：
```bash
#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec node "$DIR/observe.js" "$@"
```

**hooks.json** PreToolUse + PostToolUse 各追加 `pre:observe` / `post:observe`（id 对齐 hook-flags.js）。

### 5.3 Case 3：CLAUDE.md 钩子表同步（F6）

`CLAUDE.md`「钩子系统」表改为 hooks.json 实际 8 项。

### 5.4 Case 4：文档漂移全面修复

| 文件 | 修改 |
|------|------|
| README.md | 11/9//orch:sdd-dev → 22/26/14//start-dev |
| AGENTS.md | 25→26；注册 tdd-guide |
| .claude-plugin/README.md | 18/12 → 22/14 |
| file-map.yaml | 补 scripts/hooks/hooks//tests//self-check |
| index.json | 增补 skills/agents/commands/hooks/scripts 条目 |

### 5.5 Case 5：__pycache__ 清理（F11）

`git rm -r --cached scripts/__pycache__` + 本地删除；新建 `.gitignore` 含 `__pycache__/` 与 `*.pyc`。

---

## 6. S6 验证闭环

1. **全量自检跑通**：`node scripts/self-check.js` → 5 块全 PASS
2. **自动流转率 ≥80%**：以本次元任务工作流为样本统计，`verdict.judgeRate(flow, 80)` 判定
3. **产出达标率 ≥90%**：二次审查，`judgeRate(pass, 90)` 判定
4. **容错恢复率 ≥80%**：session-start 自动补偿 + fail-open 钩子为证据
5. **无法测量时降级**：证据化验收（修复清单 + 自检 PASS + 指标标注 estimate）
6. **智能 gate**：`verdict.js` 规则自决 + 白名单人工边界验证

---

## 7. 构建序列（批次依赖 DAG）

```
Batch1 ── S1 编排（4 并行）     Batch2 ── S2 Agent（5 并行）    Batch3 ── S3 Skills（5 并行）
 T1.1 stage-contracts +        T2.1 project-map×4 +            T3.1 execute+spec 引用
      workflow-gate STAGE        tasker GATE 降级               T3.2 cost GATE
 T1.2 stage-gate stdin+EXEMPT   T2.2 tdd-guide 注册             T3.3 using-orch 索引
 T1.3 session-start 补偿        T2.3 prompt-defense 幂等        T3.4 observer.enabled=true
 T1.4 北极星审查→business-rules T2.4 frontmatter 统一           T3.5 16 skill TRIGGER
                                T2.5 编号+hookify
        Batch4 ── S5 Hooks（3 并行）
         T4.1 hooks.json 注册(suggest-compact+observe)
         T4.2 observe.js + observe.sh 新建
         T4.3 hook-flags.js 门控对齐
                  │
        Batch5 ── S5 文档同步（depends Batch2+4）
         T5.1 CLAUDE.md 钩子表 + AGENTS.md 26 + README/.claude-plugin/README
         T5.2 file-map.yaml + index.json
         T5.3 pyc 清理 + .gitignore
                  │
        Batch6 ── S4 自检与冒烟（depends Batch1-5）
         T6.1 self-check.js + commands/self-check.md + verdict.js
         T6.2 hooks-smoke.test.js + 落地 test-*.template
         T6.3 test-suite.py 扩展
                  │
        Batch7 ── S6 验证闭环
         T7.1 自检 5 块 PASS → T7.2 量化度量 → T7.3 testing-report.md
```

**并行纪律**：Batch1/2/3/4 内部无依赖 Task 必须 `run_in_background=true` 并行派遣（每批 ≤5）；T2.4 依赖 T2.3 同文件（先清重复再统一语法）；Batch5-7 串行承接。

**每批验证钩子**：Batch1 后 `node scripts/hooks/stage-gate.js`（空 stdin，2s 内 allow）| Batch2 后 grep 校验 | Batch3 后引用交叉校验 | Batch6 后 `node scripts/self-check.js` 全 PASS | Batch7 后 `python tests/test-suite.py` errors=0。

---

## 8. 风险与权衡

| 风险 | 缓解 |
|------|------|
| 北极星降级 start-dev/tasker GATE 可能削弱"阶段纪律"感知 | 仅降级"限制探索"措辞；阶段顺序 HARD-GATE 原样保留 |
| observe.js 观察写入新增 IO | fail-open + JSONL 追加 + `SDD_DISABLED_HOOKS` 可关 |
| stage-contracts 集中化重构引入回归 | 冒烟测试 + 空 stdin 行为断言兜底 |
| self-check 静态 grep 校验可能误报 | 校验项全部对应已有 TC；FAIL 只出建议不阻断 |
| 16 skill TRIGGER 文案可能误触发 | 仅追加 description 文本，SKILL 名与门控不变 |
