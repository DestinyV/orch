# 流程执行参考（Source of Truth）

各阶段输入/输出契约、校验规则、失败纠正。

## 阶段总览

| 步骤 | Skill | Agent | 输入 | 输出 | 前置条件 | 调度 |
|------|-------|-------|------|------|---------|------|
| 0 | workflow-control | — | 需求描述 | .workflow-state.json + .workflow-eval.json | 无 | 入口 |
| 0.5 | socratic-clarify | socratic-clarifier | 需求描述 | spec/clarification.md | 模糊度 > 0.2 | 条件 |
| 1 | spec-creation | code-explorer | 需求/澄清报告 | spec/{requirement,scenarios,...}.md | 步骤0 done | 自动 |
| 2 | test-design | test-designer | spec/ | tests/test-spec.md + fixtures.json + test-*.template | 步骤1 done | 并行 |
| 3 | code-design | code-architect | spec/ | design/design.md | 步骤1 done | 并行 |
| 3.5 | api-contract | api-contract-creator | design.md | api-contract.md + review-report.md | 步骤3 done + fullstack | 条件 |
| 4 | code-task | code-tasker | design.md | tasks/tasks.md | 步骤3 done [+ 3.5] | 串行 |
| 5 | code-execute | code-executor, code-reviewer | tasks.md | src/ + execution/execution-report.md | 步骤4 done | 串行 |
| 5.5 | exception-handler | exception-handler | src/ | src/（异常处理代码） | 步骤5 内部 | 子过程 |
| 6 | code-test | code-tester, test-verifier | src/ + tasks.md | tests/ + testing/testing-report.md | 步骤5 done | 串行 |
| 7 | spec-archive | spec-archiver | spec/ + tests/ | spec-dev/spec/（已合并）+ archive-log.md | 步骤6 done + 全通过 | 串行 |
| 8 | evaluation | — | .workflow-eval.json | 诊断报告 + context-budget + cost-tracking | 步骤7 done | 串行 |
| 9 | knowledge-continuum | knowledge-curator | .workflow-eval.json | patterns/ + instincts/ + solutions/ | 步骤8 done | 串行 |

### 辅助技能集成

| 技能 | Agent | 集成点 | 触发条件 |
|------|-------|--------|---------|
| trace | tracer | code-execute / code-test | Task 失败 ≥ 2 次 或测试失败 ≥ 2 次 |
| continuous-agent-loop | loop-operator | code-execute | Task 超过 3 批次 |
| context-budget | — | workflow-control 步骤8 | 效果评估时 |
| strategic-compact | — | workflow-control 中断恢复 | 检测到上下文过大 |
| cost-tracking | — | workflow-control 步骤8 | 效果评估时 |
| tdd-guide | — | code-execute 启动时 | standard 模式 |

---

## 各阶段详细契约

### 步骤0: workflow-control

**输入契约**（必须）：
- 需求描述（字符串）

**输出契约**（必须）：
- `.workflow-state.json` — status, current_stage, stages[]
- `.workflow-eval.json` — stages[], events[]

**校验规则**：
1. project-mode 已确认（frontend/backend/fullstack/mobile）
2. .workflow-state.json 已写入且可解析

**失败纠正**：
- 模式推断不准确 → AskUserQuestion 手动选择

---

### 步骤0.5: socratic-clarify

**输入契约**（必须）：
- 需求描述
- .workflow-state.json 已初始化

**输出契约**（必须）：
- `spec/clarification.md` — 含 final_ambiguity 字段

**输出契约**（可选）：
- 拓扑组件清单
- 本体实体列表

**校验规则**：
1. clarification.md 存在
2. 包含 final_ambiguity 且 < 1.0
3. 包含目标/约束/验收标准章节

**失败纠正**：
- 文件缺失 → 重跑 socratic-clarify
- 模糊度未降低 → 继续追问（最多 5 轮额外）

---

### 步骤1: spec-creation

**输入契约**（必须）：
- 需求描述或 `spec/clarification.md`

**输出契约**（必须）：
- `spec/requirement.md` — 含工作模式标签
- `spec/scenarios/*.md` — BDD WHEN-THEN 格式
- `spec/data-models.md`
- `spec/business-rules.md`
- `spec/glossary.md`

**输出契约**（fullstack/后端）：
- `spec/infrastructure.md`
- `spec/deployment.md`
- `spec/backend-monitoring.md`

**输出契约**（needs-database=是）：
- `spec/sql-ddl.md`

**输出契约**（标准模式）：
- `project-context.md`

**校验规则**：
1. requirement.md 头部包含「工作模式: [standard\|quick]」
2. 每个 scenario 至少 1 个异常 Case（无异常 Case → HARD-GATE）
3. 场景间依赖无环（depends-on 不形成循环引用）
4. standard 模式：每个 Case 有 TEST-VERIFY + Mock Data
5. 全部文件非空

**失败纠正**：
- 核心文件缺失 → 回溯 spec-creation 重新生成
- 模式标签缺失 → AskUserQuestion 确认后补入
- 场景无异常 Case → 追加后再校验
- project-context.md 缺失 → 自动派遣 code-explorer 补偿

---

### 步骤2: test-design（与步骤3 并行）

**输入契约**（必须）：
- `spec/scenarios/*.md` — 含 TEST-VERIFY + Mock Data

**输出契约**（必须）：
- `tests/test-spec.md`
- `tests/fixtures.json`

**输出契约**（可选）：
- `tests/test-*.template`（Java/Python/TypeScript）

**校验规则**：
1. test-spec.md 非空
2. fixtures.json 可解析为有效 JSON
3. 每条 TEST-VERIFY 映射到至少 1 个测试用例

**失败纠正**：
- test-spec.md 缺失 → 重新派遣 test-designer
- 并行安全：此步骤失败不阻塞步骤3

---

### 步骤3: code-design（与步骤2 并行）

**输入契约**（必须）：
- `spec/` — 全部 spec 文档

**输出契约**（必须）：
- `design/design.md` — 含架构/组件/决策记录章节

**输出契约**（fullstack）：
- `design/diagrams/*.md` — UML 图

**输出契约**（needs-database=是）：
- `design/sql-ddl.md`

**校验规则**：
1. design.md 包含「架构设计」章节
2. design.md 包含「组件设计」章节
3. design.md 包含「决策记录」章节
4. 设计覆盖 spec 中所有场景
5. fullstack + needs-database: sql-ddl.md 存在

**失败纠正**：
- 章节缺失 → 补全后重新生成
- 设计未覆盖场景 → 追加设计后重新校验
- 并行安全：此步骤失败不阻塞步骤2

---

### 步骤3.5: api-contract（fullstack 条件触发）

**输入契约**（必须）：
- `design/design.md`

**输出契约**（必须）：
- `api-contract/api-contract.md`
- `api-contract/review-report.md`

**校验规则**：
1. api-contract.md 中每个接口有请求/响应结构定义
2. review-report.md 中无 blocking 级别问题
3. 接口命名与项目现有风格一致

**失败纠正**：
- blocking 问题存在 → 修复后重新审查
- 非 fullstack 模式 → 跳过此步骤

---

### 步骤4: code-task

**输入契约**（必须）：
- `design/design.md`

**输出契约**（必须）：
- `tasks/tasks.md`

**校验规则**：
1. 每个 Task 有 provides 和 consumes 声明
2. 每个 Task 有验收标准
3. Task 间依赖关系拓扑无环（DAG）
4. 全部 Task 覆盖所有 design.md 中的组件

**失败纠正**：
- provides/consumes 缺失 → 补全后继续
- 依赖成环 → 重新分析依赖关系
- 覆盖不足 → 追加遗漏 Task

---

### 步骤5: code-execute

**输入契约**（必须）：
- `tasks/tasks.md` — 含 tasks、依赖关系、验收标准

**输入契约**（可选）：
- tests/ — test-design 阶段的输出

**输出契约**（必须）：
- `src/` — 源代码
- `execution/execution-report.md`

**校验规则**：
1. src/ 非空
2. execution-report.md 存在
3. standard 模式：每个 Task 有 TDD 四阶段日志（RED→GREEN→REFACTOR→REVIEW）
4. standard 模式：覆盖率 ≥ 85%；quick 模式：覆盖率 ≥ 60%
5. 编译/类型检查 0 错误

**失败纠正**：
- src/ 为空 → 回溯 code-execute
- 覆盖率不足 → 补充测试后重新验证
- 编译错误 → 修复后重新构建
- 超时 → 拆分未完成 Task 到新批次

---

### 步骤5.5: exception-handler（后端/全栈自动触发）

**输入契约**（必须）：
- `src/` — code-execute 输出的源代码

**输出契约**：
- `src/` — 添加异常处理后的代码

**校验规则**：
1. 数据库操作用远程异常包装
2. JSON 解析用参数异常包装
3. 异常类名与项目约定一致（无硬编码）

**失败纠正**：
- 约定扫描失败 → 降级为标准异常处理

---

### 步骤6: code-test

**输入契约**（必须）：
- `src/` — 源代码
- `tasks/tasks.md` — 验收标准

**输出契约**（必须）：
- `tests/` — 集成/E2E/性能测试
- `testing/testing-report.md` — 验证矩阵 + 测试结果

**校验规则**：
1. testing-report.md 存在
2. 集成测试通过（0 failures）
3. 前端/全栈: 浏览器 E2E 已执行（0 failures）
4. 闭环验证：每条 TEST-VERIFY 对应测试结果
5. standard 模式：覆盖率 ≥ 85%

**失败纠正**：
- 测试失败 → 返回 code-execute 修复
- E2E 未执行 → 先执行 E2E
- 覆盖不足 → 补充测试用例

---

### 步骤7: spec-archive

**输入契约**（必须）：
- `spec-dev/{req_id}/spec/` — 需求规范

**输入契约**（必须）：
- `testing/testing-report.md` — 全部测试通过

**输出契约**（必须）：
- `spec-dev/spec/` — 已合并的主规范库（场景/模型/规则/术语文件）
- `spec-dev/spec/archive-log.md`

**归档合并协议**（非仅 log）：
1. 场景合并 — 复制 `scenarios/*.md` 到主规范，ID冲突追加不覆盖
2. 数据模型合并 — 新增实体/字段追加到 `spec-dev/spec/data-models.md`
3. 业务规则合并 — 新增规则追加，冲突标注 `DECISION_NEEDED`
4. 术语合并 — 新术语追加，重复跳过
5. 标记已归档 — 在原需求 `requirement.md` 追加 `archived: true`

**校验规则**：
1. 全部测试通过（testing-report.md 中 0 failures）
2. 主规范文件已更新（非仅 log）
3. archive-log.md 存在

**失败纠正**：
- 测试未全部通过 → 回溯 code-test，不允许进入
- 冲突 → AskUserQuestion 确认合并策略

---

### 步骤8: evaluation

**输入契约**（必须）：
- `.workflow-eval.json` — 含 stages[] 和 events[]

**输出契约**（必须）：
- `.workflow-eval.json`（更新） — 含 diagnosis 字段

**校验规则**：
1. .workflow-eval.json 存在
2. stages[] 中所有 stage 的 status 非空
3. diagnosis 字段已写入

**诊断维度**：
- HARD-GATE ≥ 3 → 前置过严
- 派遣 = 0 → 反模式（未使用 Agent）
- 覆盖率 < 85% → TDD 不严格

**失败纠正**：
- stages 数据不完整 → 标记 diagnosis 后继续（WARN 不阻断）

---

### 步骤9: knowledge-continuum

**输入契约**（必须）：
- `.workflow-eval.json` — 含 diagnosis

**输出契约**（必须）：
- patterns/ — 模式文件更新
- user-preferences/preferences.json — always_check[] 更新

**输出契约**（可选）：
- instincts/ — 新 instinct 文件
- solutions/ — 解决方案文档

**校验规则**：
1. pattern-index.json 非空（frequency 有非零值或有新增）
2. preferences.json 已更新

**失败纠正**：
- pattern-index.json 为空 → 初始化索引，不阻塞
