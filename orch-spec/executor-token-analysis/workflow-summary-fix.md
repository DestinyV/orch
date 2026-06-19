# 工作流执行结果文案和阶段缺失 — 诊断与修复方案

## 症状

用户终端输出的工作流完成总览存在两个问题：

### 问题 1: 文案乱码

```
✅30-0.5:u需求澄清age"  ← 正常应为 "✅ 0.5: 需求澄清"
7,轮苏格拉底访谈           ← 逗号不应出现
uTDDi实现ithout interru    ← 英文单词被截断/插入随机字符
t✅g C│aude's current work  ← 系统提示串入
```

### 问题 2: 流程阶段缺失/过度合并

步骤 0（workflow init）、5.5（exception）、8（evaluation）、9（continuous-learning）在总览表中不可见。步骤 7/8/9 被合并为一行"归档评估"。

---

## 根因分析

### 根因 1: 不存在最终总览模板（主因）

**证据**: 搜索全部 skills/agents/scripts 文件，不存在"最终交付总览"的输出模板。`agent-dispatch-code.md` 步骤9 的出口仅有 `learnings[]非空 + status=completed`，未定义最终输出格式。

**后果**: 工作流编排器（主 LLM）在步骤9 完成后，**自由发挥**生成完成总览。每次格式不同、阶段名称不统一、可能遗漏阶段。

### 根因 2: 上下文截断导致多字节字符损坏

**证据**: 工作流经过 9+ 步骤后上下文窗口接近上限，可能在生成最终总览前触发 compaction。`pre-compact.js` hook 执行时上下文状态不稳定，导致 LLM 输出中的 UTF-8 多字节字符（中文）被截断。

**后果**: 中文字符的某个字节丢失 → 后续字符位移 → 整段文本出现"u需求澄清age"类乱码。

### 根因 3: 阶段分组无规则

**证据**: `flow-execution-reference.md` 定义了 13 个阶段，但 `agent-dispatch-code.md` 的派遣索引中阶段分组规则不一致（2-3 并行故合并显示、7-9 无理由合并）。

**后果**: 编排器自行决定阶段合并策略，导致 7/8/9 三阶段合并为"归档评估"一行。

---

## 修复方案

### 只改 1 个文件: `skills/workflow/references/agent-dispatch-code.md`

在步骤9 之后追加"工作流完成总览"模板，将最终输出从 LLM 自由发挥改为结构化模板。

### 改动内容

#### 位置: `agent-dispatch-code.md` 第 269 行（步骤9 出口行）之后

#### 新增: `## 工作流完成总览（步骤9 完成后必须输出）`

<GATE>全部步骤 1→9 执行完毕且 status=completed 后，必须按以下模板输出最终总览。禁止自由格式发挥。</GATE>

模板要点:
1. **阶段不合并** — 每个阶段独立一行，不因"并行"或"串行末尾"而合并
2. **阶段编号和名称固定** — 不能简写或缩写
3. **产物字段** — 从 `.workflow-eval.json` 和 `.workflow-state.json` 提取
4. **结果** — 只有 ✅/⚠️/❌ 三种状态
5. **模板是中文 unicode 固定字符串** — 直接复用模板字面量，不拼接生成
6. **生成时机** — context-budget 确认余量 > 15K token 后再生成；不足时先 compact

---

### 改动详情

#### A. 新增"工作流完成总览"模板

```markdown
## 工作流完成总览（步骤9 完成后输出）

<GATE>全部步骤 1→9 执行完毕且 status=completed 后，必须输出最终总览。</GATE>

### 生成前自检

1. 确认 `.workflow-state.json` 的 `status` = `completed`
2. 读取 `.workflow-eval.json` 的 `stages[]` 获取每阶段实际状态
3. 检查当前上下文余量 > 15K token（不足则先 compact）

### 输出模板（严格按以下结构，不得自由改格式）

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
| 5 | 代码执行 | {N} Task 完成 / {N} 总 | {✅/⚠️} |
| 5.5 | 异常处理 | 异常代码已集成 | {✅/—} |
| 6 | 测试验证 | 单元{N} 集成{N} E2E{N} | {✅/⚠️} |
| 7 | 规范归档 | 主规范库已合并 | {✅/⚠️} |
| 8 | 效果评估 | 诊断报告 | {✅/⚠️} |
| 9 | 知识复利 | {N} learnings + {N} 优化规则 | {✅/⚠️} |
```

### 占位符填充规则

| 占位符 | 数据来源 | 填充逻辑 |
|--------|---------|---------|
| `{requirement_desc_abstract}` | `.workflow-state.json → requirement_id` | 直接取 |
| `{N} 场景` | eval.json → stage 1_spec 的产物统计 | 统计 `orch-spec/{req}/spec/scenarios/*.md` 文件数 |
| `{N} 测试模板` | eval.json → stage 2_test_design | 统计 `tests/test-*.template` 文件数 |
| `{N} ADR` | eval.json → stage 3 | 统计 `design/decisions.md` 中的 ADR 记录 |
| `{N} 任务` | eval.json → stage 4 | 从 `tasks/tasks.md` 统计 Task 总数 |
| `{N} Task 完成` | eval.json → stage 5 | 从 `execution/execution-report.md` 统计完成数 |
| `{N} learnings` | eval.json → stage 9 | 从 `context/learnings.md` 统计段落数 |
| `{N} 优化规则` | preferences.json → optimization.rules[] | 统计 active 规则数 |

### 状态显示规则

| 状态 | 条件 |
|------|------|
| ✅ | 阶段 status=done，所有 GATE 通过 |
| ⚠️ | 阶段 done 但有 DONE_WITH_CONCERNS 或 GATE trigger |
| ❌ | 阶段 failed 或 skipped（需附原因） |
| — | 条件触发阶段（0.5/3.5/5.5），本需求未触发 |

### 关键约束

- 禁止合并阶段行（即使 2-3 是并行，也分别显示）
- 禁止省略步骤 0 / 5.5 / 8 / 9
- 禁止在产物列使用简写或省略关键数据
- 模板文字必须直接复用（不拼接、不动态翻译、不改字面）
```

#### B. 同步更新步骤9 出口约束

步骤9 原有出口 `learnings[] 非空 + status=completed` 改为包含总览输出：

```diff
- 出口 | learnings[] 非空 + `status=completed`
+ 出口 | learnings[] 非空 + `status=completed` + 工作流完成总览已输出
```

---

## 实施步骤

| 步骤 | 操作 | 验证 |
|------|------|------|
| 1 | 修改 `agent-dispatch-code.md` — 步骤9 后追加"工作流完成总览"模板 | 模板 13 阶段完整 |
| 2 | 修改 `agent-dispatch-code.md` — 步骤9 出口增加总览输出要求 | 出口 3 项 |
| 3 | 回归检查 — GATE 完整性 | 所有 GATE 规则仍在 |
