# executor Token 优化改动方案

**原则**: 非破坏性增量改动 — 保留所有现有 GATE/流程/约束，仅增加 token 效率指令和可选简化路径。

---

## 改动总览

| 阶段 | 文件 | 改动性质 | 预估节省 |
|------|------|---------|---------|
| A | `agents/executor.md` | 增加效率指令 + 精简冗余 | 15-25K/task |
| B | `skills/execute/SKILL.md` | 增加批量审查选项 + 注入预算 | 20-30K/task (batch) |
| C | `skills/execute/references/token-efficiency-guide.md` | **新建** 效率参考 | 支撑 A+B |
| D | `skills/execute/references/verification-gate.md` | 增加摘要优先策略 | 5-10K/task |

---

## 阶段 A: agents/executor.md（Agent 定义优化）

**文件**: `agents/executor.md`  
**现状**: 148 行，每次派遣 executor 全量加载为 system prompt

### A.1 新增"上下文信任原则"（插入到 Context 段后）

**位置**: 第 27 行后（`## 调用方式` 之前）

**改动**: 新增段落

```markdown
### 上下文信任原则

<GATE>主代理已注入的上下文（Task 规范/project-map 子图/设计决策/测试模板/异常模式缓存）禁止用 Read 工具重复读取。</GATE>

- 已注入上下文在 prompt 中 → 直接引用，不自行 Read
- 仅在注入信息不足以完成当前步骤时，才补充读取
- 补充读取前先判断：是否可以从已注入上下文推导？

**违反此原则的典型行为**：
- ❌ 启动后立即 `Read(orch-spec/{req}/tasks/tasks.md)`（已在 prompt 中）
- ❌ 启动后立即 `Read(orch-spec/{req}/design/design.md)`（已注入 relevant_design）
- ✅ 需要某个未注入的细节时才读取对应文件
```

**理由**: executor 当前第 68-75 行要求"阅读 tasks.md"、"理解 design 的设计规范"——这导致 agent 重复读取已注入 prompt 的文件。新增 GATE 明确禁止此行为。

**影响**: 不改变任何现有流程，仅消除冗余读取。

---

### A.2 精简"任务理解与上下文建立"段

**位置**: 第 68-75 行

**原内容**:
```markdown
### 1. 任务理解与上下文建立

阅读 tasks.md 中当前 Task 的目标/交付物/验收标准 | 理解 design 的设计规范和接口定义 | 参考 code-architect 的架构蓝图 | 理解集成点 | 审查项目约定（CLAUDE.md）。

**TDD 前置依赖**（由 test-designer 提供）：
- `test-spec.md`：完整的 test case 列表、期望行为、Mock 策略
- `fixtures.json`：有效输入、边界值、特殊值、API/DB Mock 定义
- `test-*.template`：测试骨架代码，可直接运行
```

**改为**:
```markdown
### 1. 任务理解与上下文建立

从 prompt 中已注入的上下文（task-spec / relevant_design / test_templates）提取当前 Task 的目标、交付物、验收标准。
仅当注入信息不足以理解集成点或项目约定时，才补充 Read 对应文件。

**TDD 前置依赖**（由 test-designer 提供，已注入 prompt 或按需 Read）：
- `test-spec.md`：完整的 test case 列表、期望行为、Mock 策略
- `fixtures.json`：有效输入、边界值、特殊值、API/DB Mock 定义
- `test-*.template`：测试骨架代码，可直接运行
```

**理由**: 从"主动读取"改为"从注入上下文提取，不足时补充"。保留读取能力但改变默认行为。

**影响**: executor 不再默认 Read 多个文件，但仍可在需要时读取。

---

### A.3 新增"命令输出摘要优先"策略（插入到集成验证段）

**位置**: 第 124 行后（`### 4. 集成验证` 段末）

**改动**: 新增子段

```markdown
#### 4.1 命令输出读取策略（Token 效率）

运行验证命令时，采用摘要优先策略：

| 场景 | 策略 |
|------|------|
| 测试通过 | 只读 exit code + 最后 3 行（`| tail -3`） |
| 测试失败 | 读取完整输出定位失败原因 |
| Lint/类型检查通过 | 只读 exit code + 错误计数行 |
| Lint/类型检查失败 | 读取完整输出定位问题 |
| 覆盖率报告 | 只读 summary 段（`| grep -A5 "Coverage"` 或等效） |

**验证铁律仍然生效**：exit code 和关键输出必须展示为证据。摘要模式只省略通过场景的冗余输出。
```

**理由**: 当前每个命令的输出被完整读取（如覆盖率报告可能 100+ 行），大部分内容在通过场景下无意义。摘要策略在失败时仍可读取完整输出。

**影响**: 不改变验证要求，仅改变输出读取范围。

---

### A.4 移动 Worktree 协议细节到引用

**位置**: 第 57-65 行（`### 0.5 工作环境准备`）

**原内容**: 5 种降级尝试的完整命令

**改为**:
```markdown
### 0.5 工作环境准备

<GATE>禁止在主上下文直接编码。必须通过 worktree 或至少子代理隔离执行。</GATE>

worktree 创建按标准协议执行（详见 `skills/execute/references/git-worktrees-guide.md`），降级优先级：
1. 标准 worktree 创建
2. 清理冲突后重试
3. 从 HEAD 新分支创建
4. prune 后重试
5. 降级到隔离目录（禁止降级到主上下文串行）

快速参考：
```bash
git worktree add .claude/worktrees/{task-id}-{name} HEAD
```
```

**理由**: 148 行的 agent prompt 中，worktree 协议占了 9 行（~300 token）。每次派遣 executor 都加载这些细节，但实际只需要知道"按协议创建"即可。保留 GATE 和降级优先级概要，细节引用 reference 文件。

**影响**: executor 仍知道必须创建 worktree 和降级优先级，但具体命令不再占 system prompt。

---

### A.5 移动 Git Trailers 格式到引用

**位置**: 第 40-55 行（`### 0. 提交规范`）

**原内容**:
```markdown
### 0. 提交规范

代码实现完成后，git commit 必须附带 Git Trailers 记录决策上下文：

```
<type>(<scope>): <description>

Constraint: <约束条件>
Rejected: <方案> | <原因>（如有被拒绝方案）
Spec: <scenario-id>
```

trailer 类型详见 `rules/common/git-workflow.md`。
```

**改为**:
```markdown
### 0. 提交规范

代码实现完成后，git commit 必须附带 Git Trailers（格式详见 `rules/common/git-workflow.md`）。
核心 trailer：Constraint / Rejected / Spec。
```

**理由**: 提交格式在 system prompt 中占用 12 行（~250 token），且已有 reference 文件覆盖。

---

### A.6 新增"Task 复杂度自评"（插入到实现规划段前）

**位置**: 第 83 行（`### 2. 实现规划` 之前）

**改动**: 新增段

```markdown
### 1.8 Task 复杂度自评

在进入实现规划前，快速自评 Task 复杂度（不消耗额外 Read）：

| 复杂度 | 特征 | TDD 深度 |
|--------|------|---------|
| **trivial** | 变更 < 30 行，纯函数/单文件/无外部依赖 | RED+GREEN 合并 → REVIEW（跳过 REFACTOR） |
| **simple** | 变更 30-100 行，单模块内 | 标准四阶段 |
| **medium** | 变更 100-300 行，跨模块 | 标准四阶段 + 完整 REVIEW |
| **complex** | 变更 > 300 行，多模块/架构变更 | 标准四阶段 + 逐 test case REVIEW |

自评结果写入 TDD 进度日志首行。trivial Task 的 REFACTOR 阶段标记为 N/A。

<GATE>trivial 判定错误导致质量问题 → 下次同类型 Task 升级为 simple。</GATE>
```

**理由**: 简单 Task（如加一个工具函数）不需要走完整 REFACTOR 流程。保留全部 GATE，仅允许 trivial 合并阶段。

**影响**: 对 trivial Task 节省 REFACTOR 阶段开销（~8-12K），对 simple+ Task 无影响。

---

## 阶段 B: skills/execute/SKILL.md（编排层优化）

**文件**: `skills/execute/SKILL.md`  
**现状**: 366 行

### B.1 上下文注入段增加 Token 预算

**位置**: 第 44-50 行

**原内容**:
```markdown
### 读取需求上下文（分层缓存替换方案）

不自行读取 req-context 文件。上下文由主代理在 prompt 中注入：
- `summary.json` — 当前 Task 的 project-map 子图 + 相关 decisions + 异常模式缓存
- `task-spec` — 当前 Task 的目标/交付物/验收标准/provides/consumes
- 注入 token 约 2K-5K（对比自行读取 10K-25K）

> 上下文注入格式详见 `../workflow/references/context-injection-protocol.md`
```

**改为**:
```markdown
### 读取需求上下文（分层缓存替换方案）

不自行读取 req-context 文件。上下文由主代理在 prompt 中注入：
- `summary.json` — 当前 Task 的 project-map 子图 + 相关 decisions + 异常模式缓存
- `task-spec` — 当前 Task 的目标/交付物/验收标准/provides/consumes

**注入 Token 预算**（主代理约束）：
- 每 Task 注入上限 **4K token**（约等于 task-spec 2K + design summary 1K + templates 引用 1K）
- test template 只注入文件路径，不注入完整内容（executor 按需 Read 所需 test case）
- design 上下文注入摘要（≤500 字），不注入完整 design.md 章节
- 对比自行读取 10K-25K，注入模式目标 ≤4K/task

> 上下文注入格式详见 `../workflow/references/context-injection-protocol.md`
```

**理由**: 当前声称 2K-5K 但没有硬约束，实际常超 8K。增加预算上限并明确 template 只传路径。

**影响**: 主代理在构造 executor prompt 时需遵循预算，不影响 executor 自身行为。

---

### B.2 代码审查段增加批次级选项

**位置**: 第 178-226 行（规范审查 + 质量审查两段）

**改动**: 在两段审查之前插入选项说明

```markdown
#### 3.3-3.4 代码审查策略

<GATE>standard 模式必须通过 Agent 派遣 code-reviewer，不允许主上下文直接审查。</GATE>

**批次级审查（推荐）**：同批次全部 Task 完成后，一次性派遣 code-reviewer 审查批次 diff。
- 适用：批次内 Task ≥ 2，且各 Task 代码 < 200 行
- 节省：每额外 Task 节省一次 code-reviewer 派遣（~25K token）

**单 Task 审查（兜底）**：每 Task 单独派遣 code-reviewer。
- 适用：单 Task 代码 > 200 行，或 @critical 标记的 Task

以下为两种模式均遵循的审查 prompt 模板：
```

**理由**: 不删除 per-Task 审查，但在多 Task 批次时提供更高效的选项。保留 GATE。

**影响**: 主代理在执行批次时可以选择批次级审查，executor 行为不变。

---

### B.3 自检清单增加 Token 效率项

**位置**: 第 285 行（`### 执行完成前自检` 段末）

**改动**: 在已有 12 项自检后追加

```markdown
- Token 效率：上下文注入未超预算✓ | executor 未重复读取已注入文件✓ | 命令输出采用摘要模式✓
```

---

## 阶段 C: 新建 token-efficiency-guide.md

**文件**: `skills/execute/references/token-efficiency-guide.md`（新建）

**内容**:

```markdown
# Token 效率指南

executor 派遣时的 Token 节省最佳实践。

## 核心原则

1. **信任注入上下文** — 主代理已注入的 task-spec/design summary/template 路径，不要重复读取
2. **按需读取** — 仅当注入信息不足以完成当前步骤时，才补充读取
3. **摘要优先** — 命令输出先读尾巴，通过场景不需读全文
4. **就近引用** — 路径已在 prompt 中时直接使用，不 glob 搜索

## 上下文注入结构

每次派遣 executor 时由主代理注入：

| 字段 | 内容 | 预估 Token | 读取策略 |
|------|------|-----------|---------|
| task-spec | id/description/provides/consumes/验收标准/covers | ≤2K | 直接使用 |
| design-summary | 与本 Task 相关的架构决策（≤500字摘要） | ≤1K | 直接使用 |
| template-paths | 相关 test-*.template 文件路径列表 | ≤200 | executor 按需 Read 所需 TC |
| exception-patterns | 项目异常类名/错误码格式/文件位置 | ≤500 | 直接使用 |
| batch-context | 前批次完成的 provides 接口列表 | ≤300 | 直接使用 |

## 命令输出读取对照

| 命令 | 通过时读取 | 失败时读取 |
|------|-----------|-----------|
| `npm test` / `pytest` | exit 0 + 最后 3 行 (summary) | 完整输出 |
| `tsc --noEmit` | exit 0 + 错误计数 "Found 0 errors" | 完整输出 |
| `eslint` | exit 0 + 问题计数 | 完整输出 |
| `npm test -- --coverage` | exit 0 + Coverage summary 段 | 完整输出 |
| `go build` / `cargo check` | exit 0 + 最后 3 行 | 完整输出 |

## 禁止的 Token 浪费模式

| 浪费模式 | 替代做法 |
|---------|---------|
| `Read(tasks.md)` 全文 | 使用 prompt 中已注入的 task-spec |
| `Read(design.md)` 全文 | 使用 prompt 中已注入的 design-summary |
| `Glob("src/**/*.ts")` 全文扫描 | 使用 task-spec 中声明的文件路径 |
| `Bash("cat ... \| head -100")` 读百行输出 | 读 tail -5 或 grep summary |
| `Grep("some pattern")` 全局搜索 | 先确认注入上下文是否已有答案 |
```

---

## 阶段 D: skills/execute/references/verification-gate.md（验证策略补充）

**文件**: `skills/execute/references/verification-gate.md`

**改动**: 在第 37 行后（`## 验证对照表` 前）插入

```markdown
## Token 效率验证策略

当验证命令通过时，采用摘要模式读取输出。完整输出仅在验证失败时读取。

### 摘要读取示例

```bash
# 测试 — 只读 summary
npm test 2>&1 | tail -5
# 期望看到: "Tests: 5 passed, 5 total" 或 exit 0

# 类型检查 — 只读错误计数
tsc --noEmit 2>&1 | tail -3
# 期望看到: "Found 0 errors" 或 exit 0

# 覆盖率 — 只读 summary 表
npm test -- --coverage 2>&1 | grep -A10 "Coverage summary"
# 期望看到: 行/分支/函数/语句覆盖率 ≥ 85%

# Lint — 只读问题计数
eslint src/ 2>&1 | tail -3
# 期望看到: "0 errors, 0 warnings" 或 exit 0
```

### 摘要读取判定

- exit code = 0 **且** summary 行显示 0 errors/failures → 通过，无需读全文
- exit code ≠ 0 **或** summary 行无法确认 → 读取完整输出定位问题

**此策略不影响验证铁律**：仍然运行命令 + 读取输出 + 展示证据。仅改变读取范围。
```

---

## 实施计划

### 第 1 步: 新建 token-efficiency-guide.md（无依赖，无风险）

- 创建 `skills/execute/references/token-efficiency-guide.md`
- **验证**: 文件存在，内容完整

### 第 2 步: 修改 agents/executor.md（A.1-A.6）

按顺序逐个改动，每改完一个检查 diff：
1. A.1 — 新增"上下文信任原则"段（插入 27 行后）
2. A.2 — 精简"任务理解与上下文建立"段（替换 68-75 行）
3. A.3 — 新增"命令输出摘要优先"段（插入 124 行后）
4. A.4 — 精简 Worktree 协议段（替换 57-65 行）
5. A.5 — 精简 Git Trailers 段（替换 40-43 行）
6. A.6 — 新增"Task 复杂度自评"段（插入 83 行前）

**验证**: `wc -l agents/executor.md` 行数变化 < 10%（148 → 约 135-160）

### 第 3 步: 修改 skills/execute/SKILL.md（B.1-B.3）

1. B.1 — 上下文注入段增加 Token 预算（替换 44-50 行）
2. B.2 — 代码审查段增加批次级选项（插入 178 行前）
3. B.3 — 自检清单增加 Token 效率项（追加到 285 行后）

**验证**: 所有 GATE 规则和流程步骤仍然存在

### 第 4 步: 修改 skills/execute/references/verification-gate.md（D）

- 在验证对照表前插入摘要读取策略

**验证**: 验证铁律原文不变

### 第 5 步: 全量回归检查

```bash
# 检查所有 GATE 规则仍然存在
grep -n "<GATE>" agents/executor.md skills/execute/SKILL.md

# 检查所有流程步骤未丢失
grep -n "RED\|GREEN\|REFACTOR\|REVIEW" agents/executor.md

# 检查 reference 引用路径有效
ls skills/execute/references/token-efficiency-guide.md
```

---

## 预期效果

| 场景 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| trivial Task (<30行) | ~90K | ~40K | 55% |
| simple Task (30-100行) | ~100K | ~70K | 30% |
| medium Task (100-300行) | ~110K | ~85K | 23% |
| 批次 3 Tasks + 批次级审查 | ~330K | ~230K | 30% |

---

## 不改动的内容（明确排除）

| 排除项 | 理由 |
|--------|------|
| TDD 四阶段流程 | 核心方法论，不可简化 |
| `<GATE>` 规则 | HARD-GATE 是质量保障基础 |
| worktree 隔离要求 | 代码隔离是安全底线 |
| code-reviewer 派遣要求 | standard 模式必须独立审查 |
| 覆盖率阈值 (85%) | 不降低质量标准 |
| 验证铁律 | 证据驱动完成验证不可妥协 |
| RED 必须先于 GREEN | TDD 核心约束 |
