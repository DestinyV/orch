# Token 优化详细改动方案

**基准数据**: 本轮 2,040K token / $27.90 | 目标: 1,500K / ~$20  
**原则**: 不改 GATE / 不改 TDD 流程 / 不改覆盖率阈值 / 所有改动增量可回退

---

## 改动总览

| # | 优化项 | 涉及文件 | 行数变化 | 预期节省 |
|---|--------|---------|---------|---------|
| P0 | 前端浏览器测试批量化 | executor.md + execute SKILL.md + token-efficiency-guide.md | +30 | 150-200K |
| P1 | 强化批次级审查 + Task 合并 | agent-dispatch-code.md + tasker.md | +40 | 20-30M cache |
| P2 | 编排器注入上下文批次缓存 | execute SKILL.md | +25 | 100-150K input |
| P3 | Tasker 上下文信任 | tasker.md | +15 | 20-30K |

---

## P0: 前端浏览器测试批量化

### 现状

```
每个前端 Task → 独立运行 Playwright → RED-BROWSER → GREEN-BROWSER → 验证
```

每个 Task 的浏览器测试消耗 5-10K token。21 个前端 Task 合计 ~200K。

### 目标

```
同批次前端 Task 完成 → 统一运行 Playwright → 验证全部 BROWSER-TESTABLE
```

### 文件 1: `agents/executor.md`

**位置**: 第 147 行

**原文**:
```
- 前端/全栈 Task：在单元测试通过后，还需进行浏览器测试 TDD 循环（RED-BROWSER→GREEN-BROWSER→验证）
```

**改为**:
```
- 前端/全栈 Task：单元测试通过后，记录 BROWSER-TESTABLE 覆盖清单。浏览器测试在**批次完成后统一执行**（非每 Task 独立运行）。executor 仅确保 `data-testid` 选择器和 Playwright 测试代码已编写，实际浏览器运行由批次级验证统一触发。
```

### 文件 2: `skills/execute/SKILL.md`

**位置 A**: 第 135 行

**原文**:
```
子代理职责：阅读Task详情 → 执行带出口验证的 TDD 循环 → 浏览器测试(前端Task) → 异常模式扫描(后端/全栈) → 用户确认后git commit（附带 Git Trailers）。
```

**改为**:
```
子代理职责：阅读Task详情 → 执行带出口验证的 TDD 循环 → 编写浏览器测试代码(前端Task，批次完成后统一运行) → 异常模式扫描(后端/全栈) → 用户确认后git commit（附带 Git Trailers）。
```

**位置 B**: 第 176-179 行

**原文**:
```
**浏览器测试（前端/全栈）**：
- TDD循环：RED-BROWSER→GREEN-BROWSER→验证
- 使用 data-testid 选择器 | 覆盖 BROWSER-TESTABLE | 测试命名 `[feature].e2e.test.ts`
- 类型：`@e2e`(端到端) | `@visual`(视觉回归) | `@component`(组件UI)
```

**改为**:
```
**浏览器测试（前端/全栈）**：
- 每 Task 编写 Playwright 测试代码（`data-testid` 选择器 / BROWSER-TESTABLE 覆盖 / 命名 `[feature].e2e.test.ts`）
- 类型：`@e2e`(端到端) | `@visual`(视觉回归) | `@component`(组件UI)
- **批次级执行**：同批次前端 Task 全部完成后，由 execute 编排层统一运行 `npx playwright test` 验证全部 BROWSER-TESTABLE
- executor 仅确保测试代码已编写、选择器已定义，不自行跑浏览器
```

### 文件 3: `skills/execute/references/token-efficiency-guide.md`

**追加条目**（在"禁止的 Token 浪费模式"表后）:

```markdown
## 浏览器测试批量化

| 浪费模式 | 批量化做法 |
|---------|-----------|
| 每 Task 独立 `npx playwright test` | 批次完成后统一运行一次 |
| 每 Task 独立启动/关闭浏览器 | 复用浏览器实例 |
| executor 读 Playwright 完整输出 | 仅确认测试代码存在，实际输出由批次级验证读取 |
```

---

## P1: 强化批次级审查 + Task 合并

### 现状

code-reviewer 批次级审查已作为"推荐"选项加入，但无强制约束。Task 拆解中无合并小任务的规则。

### 目标

批次级审查从"推荐"升级为"默认"。Tasker 在拆解时自动合并变更 < 30 行的相邻 Task。

### 文件 4: `skills/workflow/references/agent-dispatch-code.md`

**位置**: 步骤 5 的 code-reviewer 行

**原文**:
```
| code-reviewer | 批次完成后 | 两阶段审查（规范+质量），仅报告 confidence≥80 的问题 |
```

**改为**:
```
| code-reviewer | 批次完成后 | 批次级综合性审查（规范+质量+TDD完整性），仅报告 confidence≥80 的问题。批次内 Task 代码行均<200 时使用批次级审查；单 Task >200 行时追加单独审查 |
```

### 文件 5: `agents/tasker.md`

**位置 A**: 步骤 2 "分解任务" 段（第 52-60 行后）

**新增段**（在第 60 行 `**粒度**：推荐 4 小时内完成。` 后）:

```markdown
**小任务合并规则**（Token 效率）：
- 预估变更 < 30 行且修改同一文件 → 合并为一个 Task
- 同一组件的样式 + 逻辑 + 测试 → 合并为一个 Task（避免拆分同一文件的不同关注面）
- 合并后 Task 仍需保持 provides/consumes 声明一致
```

**位置 B**: 步骤 1 "分析设计"（第 33-37 行）

**原文**:
```
- 读取 design.md 理解架构（分层/模块/组件/数据流）
- 读取 spec/requirement.md 中的项目约定（目录结构/分层/命名/编码规范）
- 读取 contract.md（fullstack 时）理解接口契约
```

**改为**:
```
- 上下文（design 摘要 / spec 场景 / contract 接口）已由编排器注入 prompt，优先使用注入内容
- 仅在注入信息不足以确定 Task 边界时补充读取 design.md 原文
- 读取 spec/requirement.md 中的项目约定（目录结构/分层/命名/编码规范）
```

---

## P2: 编排器注入上下文批次缓存

### 现状

```
for task in batch:
    context = read(tasks.md) + read(design.md) + read(project-map)
    dispatch(executor, prompt=context + task_spec)
```

每次 dispatch 都重新读文件，同批次的 design.md / project-map 被读 N 次。

### 目标

```
batch_context = read(design_summary) + load(project_map_subgraph) + load(exception_patterns)
for task in batch:
    dispatch(executor, prompt=batch_context + task_spec)
```

### 文件 6: `skills/execute/SKILL.md`

**位置**: 第 44-54 行（上下文注入段）

**当前内容已追加注入预算。在其后新增**:

```markdown
### 批次上下文缓存（Batch Context Cache）

同批次多 Task 派遣时，公共上下文只构造一次：

1. 读取批次公共上下文（design-summary / project-map 子图 / exception-patterns / batch-context）
2. 对批次内每个 Task，注入 = 公共上下文 + task-spec（仅差异部分）
3. 公共上下文在当前批次全部 Task 派遣完成后释放

**实施方式**（编排器侧）：
```
# 批次开始时一次性构造
batch_ctx = {
    "design_summary": "<从 design.md 提取的本批次相关摘要 ≤ 500 字>",
    "project_map_subgraph": "<与批次 provides/consumes 相关的模块路径>",
    "exception_patterns": "<从 req-context/exception-patterns.md 直接取>",
    "previous_batch_provides": ["Task-1: API-A", "Task-2: API-B"]
}

# 每个 Task 仅替换 task_spec
for task in batch:
    injection = json.dumps({**batch_ctx, "task": task_spec(task)})
    Agent(subagent_type="orch:executor", prompt=injection)
```

**节省估算**: 批次 5 个 Task → 原 5 次读 design.md 减为 1 次 → 省 50-80K 编排器 input
```

---

## P3: Tasker 上下文信任

### 现状

tasker agent 启动后自行读取 design.md / contract.md / spec 全文。91K 中相当部分用于读取文件。

### 目标

tasker 优先使用编排器注入的上下文，减少自行读取。

### 已在 P1 文件 5 的位置 B 中实现

（见上方 tasker.md 步骤 1 的改动，无需额外文件改动）

**额外**：在 tasker 的约束段追加:

### 文件 7: `agents/tasker.md` 约束段

**位置**: 第 19-22 行（`## 约束` 段）

**原文**:
```
## 约束

<GATE>每个 Task 必须有 provides/consumes 声明 | 依赖关系必须无环（DAG）</GATE>
<GATE>standard 模式: 每实现 Task 必须在同批次配测试 Task（TDD: 测试与实现在同一批次）。禁止将所有测试 Task 集中到最后批次。</GATE>
<GATE>standard 模式: 测试 Task 的 depends_on 必须指向同批次实现 Task，确保测试先于实现执行（RED→GREEN）。</GATE>
```

**改为**:
```
## 约束

<GATE>每个 Task 必须有 provides/consumes 声明 | 依赖关系必须无环（DAG）</GATE>
<GATE>standard 模式: 每实现 Task 必须在同批次配测试 Task（TDD: 测试与实现在同一批次）。禁止将所有测试 Task 集中到最后批次。</GATE>
<GATE>standard 模式: 测试 Task 的 depends_on 必须指向同批次实现 Task，确保测试先于实现执行（RED→GREEN）。</GATE>
<GATE>上下文优先：编排器已注入 design 摘要 + contract 摘要 + spec 场景引用。仅当注入信息不足以确定 Task 边界时才补充 Read 原文。</GATE>
```

---

## 执行计划

### 第 1 批: P0 + P3（改动范围小，独立验证）

| 步骤 | 文件 | 改动 | 验证 |
|------|------|------|------|
| 1 | `agents/executor.md` | L147 浏览器测试指令 | 改动后行匹配 |
| 2 | `skills/execute/SKILL.md` | L135 + L176-179 浏览器测试段 | 改动后行匹配 |
| 3 | `skills/execute/references/token-efficiency-guide.md` | 追加浏览器测试条目 | 文件末尾新增段落 |
| 4 | `agents/tasker.md` | 约束段 + 步骤1 + 步骤2 合并规则 | GATE 数量检查 |

**验证**: 
```bash
grep -n "浏览器" agents/executor.md skills/execute/SKILL.md
grep -n "<GATE>" agents/tasker.md
```

### 第 2 批: P1 + P2（改动关联）

| 步骤 | 文件 | 改动 | 验证 |
|------|------|------|------|
| 5 | `skills/workflow/references/agent-dispatch-code.md` | code-reviewer 行强化 | 行匹配 |
| 6 | `skills/execute/SKILL.md` | 注入段后追加批次缓存段 | 行数增加 |

**验证**:
```bash
grep -n "批次级\|batch.*context\|公共上下文" skills/execute/SKILL.md
grep -n "code-reviewer.*批次" skills/workflow/references/agent-dispatch-code.md
```

### 第 3 批: 全量回归

```bash
grep -rn "<GATE>" agents/ skills/execute/ | wc -l  # GATE 总数不变或增加
grep -rn "RED\|GREEN\|REFACTOR\|REVIEW" agents/executor.md | wc -l  # TDD 阶段完整
```
