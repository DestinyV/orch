<!-- EXECUTE-ME --> 本文件由 workflow 步骤1-9 强制执行。每个步骤中的 Agent 派遣必须执行。

<HARD-GATE>全部步骤 1→2→3→4→5→6→7→8→9 必须依次执行完毕，禁止在执行到中间步骤后停止或声明需求完成。每步完成后立即执行"阶段完成记录"写入 eval.json，再进入下一步。</HARD-GATE>

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
    'duration_seconds': int(time.time()),
    'agent': state.get('agent', '')
})
data['token_usage'] = data.get('token_usage', {})
json.dump(data, open(eval_path, 'w'), indent=2, ensure_ascii=False)
print(f'[eval] {stage_name} stage recorded')
"
```

替换 `{req}` 为实际需求 ID。

**每步骤执行后必须调用上述脚本**记录阶段完成状态。步骤1-9 的每个步骤派遣完成后立即执行此记录，否则下一阶段无法通过 stages[] 非空校验。

## 步骤1: spec — 项目上下文检索

### 做什么

从项目上下文中提取本需求相关的知识。三层检索：注册中心匹配 → CodeGraph 代码图谱补全（零文件扫描）→ 全量探索兜底。

生成需求级上下文 `orch-spec/{req_id}/req-context/`（project-map/tech-summary/key-files/decisions/cross-repo）。

**全量探索产出**（context/ 不存在时首次生成 8 文件）：
- `index.json` — 注册中心，含全部 section 的 tags 标签
- `tech-stack.md` — 技术栈（语言/框架/数据库/存储）
- `architecture.md` — 架构分层 + 模块划分
- `conventions.md` — 命名规范 + API 风格
- `code-patterns.md` — 跨需求代码模式
- `file-map.yaml` — 入口 / 关键目录 / 文件锚点
- `logic-chains/api-calls.yaml`（空，归档时填充）
- `logic-chains/component-deps.yaml`（空，归档时填充）

**增量更新规则**（context/ 已存在时）：
- Agent A 文档探索：新发现追加到 `tech-stack.md` / `architecture.md` / `conventions.md`
- Agent C 代码探索：新代码模式追加到 `code-patterns.md`；新目录或入口追加到 `file-map.yaml`
- 不重复追加已有内容（同类追加，不做全量重写）

### 为什么

10 个需求 = 1 次全量 + 9 次按需匹配。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| code-explorer ×3 | `run_in_background=true` | 三路必须并行启动。Agent A 始终执行（增量文档摘要）。Agent B 读 context/requirements.yaml 替代扫描目录。Agent C 仅首次或覆盖不足时执行 |
| — | 预检 | `<HARD-GATE> 禁止在未检查 orch-spec/context/index.json 前执行全量探索` |
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
| test-designer | `run_in_background=true` | `<HARD-GATE> 每条 TEST-VERIFY 必须映射到至少一个测试用例。fixtures.json 必须可解析` |
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
| code-architect | `run_in_background=true` | `<HARD-GATE> 禁止跳过 project-context.md 直接设计。设计必须覆盖所有 spec 场景。生成后必须 AskUserQuestion 确认，未确认前禁止进入 task 阶段` |
| — | 出口 | `design.md` 含架构设计/组件设计/决策记录 + `decisions.md` 已追加 ADR |

---

## 步骤3.5: contract（fullstack 条件）

### 做什么

将 design 接口定义转化为契约文档，六维度审查。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| contract-creator | — | 仅 fullstack 触发。`<HARD-GATE> review-report 有 blocking 问题时禁止进入 task` |
| — | 出口 | `contract.md` + `review-report.md` 存在，0 blocking |

---

## 步骤4: task

### 做什么

将 design 拆解为 Task 清单。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| tasker | — | `<HARD-GATE> 即使 1 个 Task 也必须生成 tasks.md。每 Task 标注 provides/consumes/depends_on/验收标准。依赖无环(DAG)` |
| — | 出口 | `tasks.md` 存在，每 Task 有 provides/consumes |

---

## 步骤5: execute

### 做什么

按批次执行 TDD（RED→GREEN→REFACTOR→REVIEW）。执行前读 `req-context/` 了解上下文，执行后追加修改文件到 `key-files.md`。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| executor ×N | `run_in_background=true`, 每 Task 独立 | `<HARD-GATE> 禁止主上下文直接编码。每 Task 必须通过子代理。禁止编造测试结果——RED 必有失败输出，GREEN 必有通过输出，REVIEW 必有 lint/typecheck/coverage 命令输出` |
| code-reviewer | 批次完成后 | 两阶段审查（规范+质量），仅报告 confidence≥80 的问题 |
| tdd-guide | 每批次完成 | `<HARD-GATE> TDD 四阶段任缺一个命令输出 → 标记 FAILED 驳回` |
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
| tester ×3 | `run_in_background=true` | `<HARD-GATE> 三路必须并行。禁止分析代码后编造结果——报告必须包含命令原文+stdout代码块，禁止推断措辞` |
| test-verifier | tester ×3 完成后 | `<HARD-GATE> 独立运行验证命令，不接受历史输出。标记 VERIFIED/PARTIAL/MISSING` |
| — | 出口 | 每条 TEST-VERIFY 对应测试结果，testing-report.md 含 stdout 证据 |

---

## 步骤7: archive

### 做什么

规范合并到主规范库 + req-context 沉淀到项目级 context/。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| archiver | — | `<HARD-GATE> 归档前置：读取 req-context/ 全部文件沉淀到 context/。冲突必须标注 DECISION_NEEDED 后用户确认。禁止只写 log 不更新文件` |
| — | 出口 | 主规范已更新 + context/ 已同步 + archive-log.md 存在 |

---

## 步骤8: evaluation

### 做什么

诊断工作流质量（三维度九指标）。context-budget + cost 并行 → 对比评分。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| 双路 | `run_in_background=true` | `<HARD-GATE> archive 后禁止跳过` |
| — | 出口 | `diagnosis.成功度/效率/质量` 均有评分 + `diagnosis.score` 0-100 |

---

## 步骤9: continuous-learning

### 做什么

从工作流提取可复用知识（四维沉淀），写入 context/learnings.md 和 preferences.json。

### 派遣约束

| Agent | 派遣参数 | 约束 |
|-------|---------|------|
| knowledge-curator | — | `<HARD-GATE> evaluation 后禁止跳过。learnings[] 为空不允许标记 status=completed` |
| — | 出口 | learnings[] 非空 + `status=completed` |

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
