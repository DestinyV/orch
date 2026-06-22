<!-- EXECUTE-ME --> 本文件由 workflow 步骤1-9 强制执行。每个步骤中的 Agent 派遣必须执行。

<GATE>全部步骤 1→2→3→4→5→6→7→8→9 必须依次执行完毕，禁止在执行到中间步骤后停止或声明需求完成。每步完成后立即执行"阶段完成记录"写入 eval.json，再进入下一步。</GATE>

# Agent 派遣意图与验证

## 阶段完成记录

每阶段完成后立即执行以下写入，阻止下一阶段前 stages[] 为空：

```bash
python3 -c "
import json, os, time
eval_path = 'orch-spec/{req}/.workflow-eval.json'
state_path = 'orch-spec/{req}/.workflow-state.json'
data = json.load(open(eval_path)) if os.path.exists(eval_path) else {'stages':[], 'token_usage':{}, 'events':[]}
state = json.load(open(state_path)) if os.path.exists(state_path) else {}
stage_name = state.get('current_stage', 'unknown')
# 写入 stage 记录
data['stages'].append({
    'stage': stage_name,
    'status': 'done',
    'tokens_input': 0,
    'tokens_output': 0,
    'completed_at': int(time.time()),
    'agent': state.get('agent', '')
})
data['token_usage'] = data.get('token_usage', {})
json.dump(data, open(eval_path, 'w'), indent=2, ensure_ascii=False)
print(f'[eval] {stage_name} stage recorded')
"
```

替换 `{req}` 为实际需求 ID。

**每步骤执行后必须调用上述脚本**记录阶段完成状态。步骤1-9 的每个步骤派遣完成后立即执行此记录，否则下一阶段无法通过 stages[] 非空校验。

## 步骤0.3: 自主优化规则注入

步骤0 初始化完成后，从 `preferences.json → optimization.rules[]` 加载所有 `active` 且 `confidence ≥ 30` 的优化规则。

**按 injection_point 分发**：
- `workflow_step0` → 当前工作流步骤0 直接使用（调整批次/并行度/阶段选择）
- `spec_prompt` → 暂存到 `.workflow-state.json.injected_optimizations[]`，步骤1 spec agent 派遣时注入 prompt
- `design_prompt` → 步骤3 code-architect 派遣时注入 prompt
- `execute_prompt` → 步骤5 executor 派遣时注入 prompt
- `review_prompt` → code-reviewer 派遣时注入 prompt

**每步骤派遣前**：检查 `.workflow-state.json → injected_optimizations[]`，有匹配 `injection_point` 的规则则注入 agent prompt。

所有注入的规则 ID 记录到 `.workflow-eval.json → applied_optimizations[]`，供下一轮步骤9 评估效果。

<GATE>trial 状态规则（confidence < 30）禁止注入任何阶段</GATE>

## 步骤1: spec — 项目上下文检索

### 做什么

从项目上下文中提取本需求相关的知识。五步按序检索，前一步匹配即止，不继续探索：

1. **project-context** — 检查 `orch-spec/project-context.md`（由 spec 阶段输出），存在则直接使用
2. **历史 spec** — 检查 `orch-spec/spec/` 下归档的规范文档，匹配需求关键词
3. **req-context** — 检查 `orch-spec/` 下历史需求的 `req-context/`，匹配相似需求继承上下文
4. **AI 知识库 / 项目 wiki** — 扫描 `docs/`、`wiki/`、`README.md` 等项目文档，以及 AI 知识库（Claude memory、RAG 索引、项目级 `.md` 知识沉淀），提取架构/约定信息
5. **项目探索** — 使用 Grep/Glob/Read 进行代码扫描，生成 context 文件

生成需求级上下文 `orch-spec/{req_id}/req-context/`（project-map/tech-summary/key-files/decisions/cross-repo）。

<GATE>context/ 不存在时（首次运行），Layer 3 全量探索必须完整生成以下 8 文件，缺一不可：index.json / tech-stack.md / architecture.md / conventions.md / code-patterns.md / file-map.yaml / logic-chains/api-calls.yaml / logic-chains/component-deps.yaml</GATE>

**全量探索产出**（context/ 不存在时首次生成 8 文件）：
- `index.json` — 注册中心，含全部 section 的 tags 标签
- `tech-stack.md` — 技术栈（语言/框架/数据库/存储）
- `architecture.md` — 架构分层 + 模块划分
- `conventions.md` — 命名规范 + API 风格
- `code-patterns.md` — 跨需求代码模式（搜索 `src/` 下最常见的 3-5 个代码模式）
- `file-map.yaml` — 入口 / 关键目录 / 文件锚点（含真实文件路径）
- `logic-chains/api-calls.yaml`（空，归档时填充）
- `logic-chains/component-deps.yaml`（空，归档时填充）

**增量更新规则**（context/ 已存在时）：
- Agent A 发现新 **模块名** → 追加到 `architecture.md`
- Agent A 发现新 **命名规范** → 追加到 `conventions.md`
- Agent C 发现新 **代码模式** → 追加到 `code-patterns.md`
- 新目录或入口 → 追加到 `file-map.yaml`
- 不重复追加已有内容（同类追加，不做全量重写）

### 为什么

10 个需求 = 1 次全量 + 9 次按需匹配。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| code-explorer ×3 | `run_in_background=true` | 三路必须并行启动。Agent A 始终执行（增量文档摘要）。Agent B 读 context/requirements.yaml 替代扫描目录。Agent C 仅首次或覆盖不足时执行 |
| — | 预检 | `<GATE> 检查 orch-spec/context/index.json 存在性 + 校验每个注册 section 的文件是否存在。缺失文件必须补生成，不可跳过。index.json 不存在 → Layer 3 全量生成 8 文件。` |
| — | 出口 | `orch-spec/{req_id}/req-context/` 含 3+ 文件 + `project-context.md` 非空 |

---

## 步骤2: test-design

### 做什么

读取 spec/scenarios/ 中的 TEST-VERIFY 生成测试规范和 fixtures。与步骤3 并行。

### 为什么

测试先行——编码前定义验收标准。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| test-designer | `run_in_background=true` | `<GATE> 每条 TEST-VERIFY 必须映射到至少一个测试用例。fixtures.json 必须可解析` |
| — | 出口 | `test-spec.md` 非空 + `fixtures.json` 可解析 |

---

## 步骤3: design

### 做什么

基于 spec 架构设计。优先读 `req-context/project-map.md` 定位关键文件，决策写入 `req-context/decisions.md`。

### 为什么

设计先行——决策记录供后续引用，避免 execute 偏离设计。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| code-architect | `run_in_background=true` | `<GATE> 禁止跳过 project-context.md 直接设计。设计必须覆盖所有 spec 场景。生成后必须 AskUserQuestion 确认，未确认前禁止进入 task 阶段` |
| — | 出口 | `design.md` 含架构设计/组件设计/决策记录 + `decisions.md` 已追加 ADR |

---

## 步骤3.5: contract（fullstack 条件）

### 做什么

将 design 接口定义转化为契约文档，六维度审查。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| contract-creator | — | 仅 fullstack 触发。`<GATE> review-report 有 blocking 问题时禁止进入 task` |
| — | 出口 | `contract.md` + `review-report.md` 存在，0 blocking |

---

## 步骤4: task

### 做什么

将 design 拆解为 Task 清单。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| tasker | — | `<GATE> 即使 1 个 Task 也必须生成 tasks.md。每 Task 标注 provides/consumes/depends_on/验收标准。依赖无环(DAG)` |
| — | 出口 | `tasks.md` 存在，每 Task 有 provides/consumes |

---

## 步骤5: execute

### 做什么

按批次执行 TDD（RED→GREEN→REFACTOR→REVIEW）。执行前读 `req-context/` 了解上下文，执行后追加修改文件到 `key-files.md`。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| executor ×N | `run_in_background=true`, 每 Task 独立 | `<GATE> 禁止主上下文直接编码。每 Task 必须通过子代理。禁止编造测试结果——RED 必有失败输出，GREEN 必有通过输出，REVIEW 必有 lint/typecheck/coverage 命令输出` |
| code-reviewer | 批次完成后 | 批次级综合性审查（规范+质量+TDD完整性），默认批次级。批次内 Task 代码行均<200→批次级审查；单 Task >200 行→追加单独审查。仅报告 confidence≥80 的问题 |
| tdd-guide | 每批次完成 | `<GATE> TDD 四阶段任缺一个命令输出 → 标记 FAILED 驳回` |
| — | 出口 | 每 Task TDD 日志完整 + src/非空 + execution-report.md 存在 |

---

## 步骤5.5: exception（后端/全栈自动）

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| exception | 子过程自动 | 禁止硬编码异常类名/错误码。按项目约定扫描生成 |

---

## 步骤6: test

### 做什么

执行集成/E2E/性能测试并闭环验证。前置读 `key-files.md` 确定测试范围。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| tester ×3 | `run_in_background=true` | `<GATE> 三路必须并行。禁止分析代码后编造结果——报告必须包含命令原文+stdout代码块，禁止推断措辞` |
| test-verifier | tester ×3 完成后 | `<GATE> 独立运行验证命令，不接受历史输出。标记 VERIFIED/PARTIAL/MISSING` |
| — | 出口 | 每条 TEST-VERIFY 对应测试结果，testing-report.md 含 stdout 证据 |

---

## 步骤7: archive

### 做什么

规范合并到主规范库 + req-context 沉淀到项目级 context/。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| archiver | — | `<GATE> 归档前置：读取 req-context/ 全部文件沉淀到 context/。冲突必须标注 DECISION_NEEDED 后用户确认。禁止只写 log 不更新文件` |
| — | 出口 | 主规范已更新 + context/ 已同步 + archive-log.md 存在 |

---

<!-- ⏩ 步骤7 完成后必须立即继续步骤8，禁止停止或声明完成 -->

<GATE>archive 完成后禁止停止。步骤7 "阶段完成记录" 写入 eval.json 后必须：</GATE>
<GATE>1. 立即执行步骤8（evaluation），不允许步骤7→8 之间有用户交互或暂停</GATE>
<GATE>2. 步骤7 产出验证必须在状态描述中注明 "步骤8已自动级联"</GATE>
<GATE>3. 仅在步骤9 完成报告输出后，才允许标记 status=completed</GATE>

<!-- ⏩ 步骤7 完成后必须立即继续步骤8，禁止停止或声明完成 -->

## 步骤8: evaluation

<GATE>archive 完成后禁止跳过 evaluation。不执行则 .workflow-eval.json 无 diagnosis，步骤9 无法提取 learnings。</GATE>

### 做什么

诊断工作流质量（三维度九指标），数据来自 `.workflow-eval.json` 的 `stages[]` 和 `~/.claude/orch-costs/usage.db`。

**数据来源**：
- 成功度：`stages[]` → 阶段完成数/用户干预事件/HARD-GATE触发/回退记录
- 效率：`usage.db`（按 stage 分组查询 token 消耗和耗时）
- 质量：execute REVIEW 输出（覆盖率）/ code-reviewer 报告（审查评分）/ archive 报告（冲突数）

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| 双路 | `run_in_background=true` | `<GATE> archive 后禁止跳过。cost DB 存在时从 DB 读取实际 tokens；不存在时用 context-budget 估算` |

---

<!-- ⏩ 步骤8 完成后必须立即继续步骤9，禁止停止或声明完成 -->

## 步骤9: continuous-learning

<GATE>evaluation 完成后禁止跳过 continuous-learning。learnings[] 为空不允许标记 status=completed。</GATE>

### 做什么

从工作流提取可复用知识（四维沉淀），写入 context/learnings.md 和 preferences.json。
同时执行**自主进化规则提取**：从 `.workflow-eval.json` → `diagnosis.deviation` → 遍历所有 `deviation > 20%` 的指标 + `events[].type=user_intervention` → 生成/更新 `optimization.rules[]`。

**效果评估**：对比已注入规则的 deviation 变化，更新每条规则的 confidence（有效+15，无效-20，不变-10）。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| knowledge-curator | — | `<GATE> evaluation 后禁止跳过。learnings[] 为空不允许标记 status=completed` |
| — | 出口 | learnings[] 非空 + **完成报告已按 completion-table.md 模板输出** + `status=completed` + `completion_report_generated: true` |

### 步骤9 完成：生成报告

<GATE>learnings[] 写入 + optimization.rules[] 更新后，必须生成完成报告。</GATE>

读取 `templates/completion-table.md` 模板，按 4 段输出：
1. 📋 流程执行总结（从 eval.json → stages[] 填表，13 步必全）
2. 📊 效率评估（vs baseline，偏差>20% 标注）
3. 🧠 知识沉淀（learnings + 规则变化）
4. 🔧 下次优化建议（diagnosis.recommendations[]）

报告输出后 → `.workflow-state.json` → `status: completed` + `completion_report_generated: true`。

<GATE>完成报告未输出（13步表格不全 / 步骤8/9数据缺失）→ 工作流视为未完成。禁止标记 completed。</GATE>

---

## 派遣索引

| 批次 | 步骤 | Agent | 调度 |
|------|------|-------|------|
| 批次1 | 1 | code-explorer ×3 | 三路 `run_in_background=true` |
| 批次2 | 2-3 | test-designer + code-architect | 两 Agent 并行 |
| — | 3.5 | contract-creator | 批次2 后串行，仅 fullstack |
| — | 4 | tasker | 串行 |
| 批次3 | 5 | executor ×N + code-reviewer | 批次内 `run_in_background=true` |
| — | 5.5 | exception | executor 子过程自动 |
| — | 6 | tester ×3 + test-verifier | 三路并行 → 统一验证 |
| — | 7 | archiver | 串行 |
| — | 8 | evaluation | 双路并行 |
| — | 9 | knowledge-curator | 串行 |

---

<!-- ⏩ 步骤9 完成后必须输出工作流完成总览，禁止省略。所有步骤执行完毕且 status=completed 是输出前提。 -->

## 工作流完成总览（步骤9 完成后必须输出）

<GATE>全部步骤 0→9 执行完毕且 status=completed 后，必须按此模板输出最终总览。禁止自由格式发挥、禁止合并阶段行、禁止省略任何阶段。</GATE>

### 生成前自检

1. 确认 `.workflow-state.json` 的 `status` = `completed`
2. 确认 `.workflow-eval.json` 的 `stages[]` 包含全部阶段记录
3. 检查当前上下文余量 > 15K token（不足则先 `Skill("orch:compact")`）

### 输出模板

```
🎉 SDD+TDD 工作流完成 — {requirement_desc_abstract}

## 最终交付总览

| # | 阶段 | 关键产物 | 状态 |
|---|------|---------|------|
| 0 | 工作流初始化 | .workflow-state.json + .workflow-eval.json | {✅/⚠️} |
| 0.5 | 需求澄清 | clarification.md（模糊度 {N}%） | {✅/—} |
| 1 | 规范生成 | {N} 场景 / {N} 测试标准 | {✅/⚠️} |
| 2 | 测试设计 | {N} 测试模板 + fixtures.json | {✅/⚠️} |
| 3 | 架构设计 | design.md + {N} ADR | {✅/⚠️} |
| 3.5 | 接口契约 | contract.md + review-report.md | {✅/—} |
| 4 | 任务拆解 | {N} 任务 / {N} 批次 | {✅/⚠️} |
| 5 | 代码执行 | {N}/{N} Task 完成 | {✅/⚠️} |
| 5.5 | 异常处理 | 异常代码已集成 | {✅/—} |
| 6 | 测试验证 | 单元{N} 集成{N} E2E{N} | {✅/⚠️} |
| 7 | 规范归档 | 主规范库已合并 | {✅/⚠️} |
| 8 | 效果评估 | 诊断报告 + deviation | {✅/⚠️} |
| 9 | 知识复利 | {N} learnings + {N} 优化规则 | {✅/⚠️} |
```

### 占位符填充规则

| 占位符 | 数据来源 | 填充方法 |
|--------|---------|---------|
| `{requirement_desc_abstract}` | `.workflow-state.json → requirement_id` | 直接取 |
| `{N} 场景` | 统计 `orch-spec/{req}/spec/scenarios/*.md` 文件数 | Bash `ls | wc -l` |
| `{N} 测试标准` | 统计 spec scenarios 文件中的 `TEST-VERIFY` 条数 | Grep 计数 |
| `{N} 测试模板` | 统计 `tests/test-*.template` 文件数 | Bash `ls | wc -l` |
| `{N} ADR` | 统计 `design/design.md` 中 `### ADR` 出现次数 | Grep 计数 |
| `{N} 任务` | 从 `tasks/tasks.md` 统计 Task 总数（`### Task` 标题数） | Grep 计数 |
| `{N} 批次` | 从 `tasks/tasks.md` 统计批次数或从 `workflow-state.json` 读 | 读 state |
| `{N}/{N} Task 完成` | 从 `execution/execution-report.md` 取完成数/总数 | 读报告 |
| `单元{N} 集成{N} E2E{N}` | 从 `testing/testing-report.md` 取各层测试通过数 | 读报告 |
| `{N} learnings` | 统计 `context/learnings.md` 中的段落数 | Bash `grep -c "## "` |
| `{N} 优化规则` | 读取 `preferences.json → optimization.rules[]` 的 active 规则数 | Python3 脚本 |

### 状态显示规则

| 状态 | 条件 |
|------|------|
| ✅ | eval.json 该阶段 `status=done`，所有 GATE 通过 |
| ⚠️ | eval.json 该阶段有 GATE trigger 或 agent retry |
| — | 条件触发阶段（0.5/3.5/5.5），本需求未触发 |

### 关键约束

- **禁止合并阶段行** — 即使步骤2-3并行也分开显示；7/8/9 也不合并
- **禁止省略步骤0 / 5.5 / 8 / 9** — 每个阶段独立一行
- **产物列从文件系统提取** — 不凭空编造数字（如 `scenarios/*.md` 文件数通过 Bash 统计）
- **模板文字直接复用** — 不拼接字符串，不动态翻译字母部分
- **阶段名称固定** — 不简写、不缩写、不改字面
