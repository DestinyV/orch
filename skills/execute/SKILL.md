---
name: execute
description: |
  代码执行实现（Execute阶段）

  输入：orch-spec/{requirement_desc_abstract}/tasks/tasks.md + tests/（test-design 输出）
  输出：src/ + orch-spec/{requirement_desc_abstract}/execution/execution-report.md

  功能：根据任务列表和设计，通过子代理逐个实现代码，并进行多阶段审查（规范/质量）。
  采用git-worktree隔离每个Task，支持全栈开发的各类代码实现。

  核心特性：每Task独立git-worktree | 模式标签遵循 | 测试环境预检 | 子代理强制 | TDD四阶段追踪 | 两阶段审查 | 执行自检
---

# execute

## 职责

根据 tasks.md，通过独立子代理+隔离worktree逐批实现代码，执行带出口验证的 TDD 循环：
```
RED ──→ GREEN ──→ REFACTOR ──→ REVIEW
  ↑                                  │
  └──── 修复后重新进入循环 ←─────────┘
```
每阶段有明确出口验证标准，不满足则阻塞在该阶段。

**输出**：`orch-spec/{requirement_desc_abstract}/execution/execution-report.md`

## 何时使用

tasks.md 已定义时启动执行。快速模式时直接读取 spec。

### 快速模式

spec 标注 `模式: quick` 时：直接读取 spec → 自主拆解 → 单阶段质量审查 → 精简测试(单元+E2E，覆盖≥60%) → 子代理可选。

## 工作流程

### 读取模式标签

读取 spec/requirement.md 头部的模式标签。
<GATE>未读取到→暂停确认 | standard模式必须严格执行TDD和子代理，不允许降级</GATE>

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

### 批次上下文缓存（Batch Context Cache）

同批次多 Task 派遣时，公共上下文（design-summary / project-map 子图 / exception-patterns）只构造一次，每个 Task 注入 = 公共上下文 + task-spec（差异部分）。

**节省估算**：批次 5 个 Task → 原 5 次读 design.md 减为 1 次 → 省 50-80K 编排器 input token。

### 分析任务列表

从 tasks.md 提取所有Task、依赖关系、并行计划，创建TodoList追踪状态。

### 测试环境验证

<GATE>未确认测试框架状态→不允许开始编码 | standard模式未编写测试文件→不允许写实现代码</GATE>

1. **测试框架可用性**：检查项目是否有测试依赖(jest/vitest/pytest等)。无时 AskUserQuestion 确认添加。
2. **测试模板存在性**：<GATE>standard 模式必须存在 `tests/test-*.template`（由 test-design 阶段生成）。不存在时必须先调用 `Skill("orch:test-design")` 生成，不允许跳过 RED 阶段直接编码。</GATE>
3. **代码审查注入**（standard 模式）：code-reviewer 的 TDD 完整性检查要求注入子代理上下文。
4. **工作模式最终确认**：AskUserQuestion 确认执行模式（标准/快速/仅编码）。模式锁定后不可更改。

### 执行批次（调度由 workflow 管控）

Task 的并行/批次调度由 workflow 步骤5 统一管理。本 skill 关注单 Task 内的 TDD 执行。

详见 `${CLAUDE_PLUGIN_ROOT}/skills/workflow/SKILL.md` 步骤5 派遣代码块。

### 执行单个Task

#### 3.1 创建隔离工作环境

<GATE>standard 模式必须使用子代理 + worktree 隔离执行。worktree 创建失败时必须执行修复协议，不允许直接降级为主上下文串行编码。</GATE>

**worktree 创建协议**（顺序尝试，直到成功）：

```bash
# 尝试 1: 标准创建
git worktree add .claude/worktrees/{task-id}-{name} {branch} 2>/dev/null ||

# 尝试 2: 目录有残留 → 清理后重试
(rm -rf .claude/worktrees/{task-id}-{name} &&
 git worktree add .claude/worktrees/{task-id}-{name} {branch}) 2>/dev/null ||

# 尝试 3: 分支被占用 → 从 HEAD 创建新分支
(rm -rf .claude/worktrees/{task-id}-{name} &&
 git worktree add -b {task-id}-{name} .claude/worktrees/{task-id}-{name} HEAD) 2>/dev/null ||

# 尝试 4: 清理所有已知冲突后最后一次尝试
(git worktree prune &&
 rm -rf .claude/worktrees/{task-id}-{name} &&
 git worktree add -b {task-id}-{name} .claude/worktrees/{task-id}-{name} HEAD) 2>/dev/null ||

# 尝试 5: 无 worktree 但有子代理（降级但不串行）
echo "[WARN] worktree 创建失败，子代理在同目录工作（仍保持并行）"
```

**降级优先级**：worktree → 子代理同目录 → cp -r 隔离目录。禁止降级到主上下文串行。

详见：`references/git-worktrees-guide.md` | `references/worktree-confirmation-protocol.md`

#### 3.1.5 接口契约验证（fullstack强制）

<GATE>fullstack时每个Task启动时必须验证 provides/consumes 接口在 contract.md 中存在。失败则拒绝执行。</GATE>

验证：读取Task的provides/consumes → 查contract.md → 不存在则报错。接口变更必须先更新版本号、重新审查。

#### 3.1.6 SQL验证（数据库Task强制）

<GATE>数据库Task必须验证 sql-ddl.md：语法正确性 | 回滚脚本存在 | SQL方言一致 | 表设计规范达标。失败则拒绝执行。</GATE>

**验证步骤**：
1. 读取 Task 的 SQL 参考字段，定位 sql-ddl.md 中的对应章节
2. **语法检查**：CREATE/ALTER/INSERT 语句完整且语法正确
3. **表设计规范检查**：
   - 每张表有主键（id 列） | 包含 created_at/updated_at
   - 表名/列名小写下划线命名 | 无保留字 | 外键有级联策略
   - 金额/数量字段有 CHECK 约束
4. **回滚脚本**：每条 DDL/DML 后有对应 ROLLBACK 注释
5. **方言一致性**：SQL 与 requirement.md 声明的方言一致
6. 执行 SQL（如有连接）或输出脚本供审查

#### 3.2 实现子代理：编码和自审查

<GATE>子代理只能修改Task定义中指定的文件路径，禁止创建或修改清单外的文件</GATE>

子代理职责：阅读Task详情 → 执行带出口验证的 TDD 循环 → 编写浏览器测试代码(前端Task，批次完成后由编排层统一运行) → 异常模式扫描(后端/全栈) → 用户确认后git commit（附带 Git Trailers）。

**TDD 出口验证标准**（每阶段不满足则阻塞）：

| 阶段 | 操作 | 出口验证 | 阻塞动作 |
|------|------|---------|---------|
| **RED** | 选一个 TC 写断言，运行确认失败 | 测试失败，且失败信息明确表达期望值 vs 实际值 | 若测试通过(未真正测试) → 重写断言 |
| **GREEN** | 写最少代码让测试通过 | 目标测试通过，且其他已有测试未回归 | 若写过多代码(过度工程) → 回退只保留最少实现 |
| **REFACTOR** | 提取重复/改进命名/优化结构 | 全部测试仍通过，代码行数减少或可读性提升 | 若测试破裂 → 回退重构 |
| **REVIEW** | Lint + 类型检查 + 覆盖率达标（行≥85% / 分支≥75% / 函数≥85% / 语句≥85%） | 0 lint 错误, 0 类型错误, 覆盖率达标, 无 console/print, 无空函数体 | 任一项不满足则阻塞，修复后重检 |

<GATE>RED 未通过(测试未写或测试通过而非失败) → 禁止进入 GREEN</GATE>
<GATE>GREEN 未通过(测试仍失败) → 禁止进入 REFACTOR</GATE>
<GATE>REVIEW 未通过(任一检查失败) → 该 Task 视为未完成</GATE>

**异常处理要求**（后端/全栈 Task）：
- <GATE>后端/全栈编码时必须调用 exception Skill 进行异常模式扫描和代码生成</GATE>
- 详见 [`../exception/SKILL.md`](../exception/SKILL.md)

**代码实现要求**：
- TypeScript strict模式 | 遵循项目命名规范 | 无遗留TODO | 无伪代码(console/print)
- **后端语言质量要求**（T5：只注入 `project-map.json → tech_stack` 对应的语言，其他语言的检查清单不注入 prompt）：
  - 从主代理注入的 `summary.json.tech_stack` 读取当前项目技术栈
  - 只执行该技术栈对应的静态检查命令，其他语言的清单不读、不用、不注入
- 详见 references: `design-principles.md` | `architecture-patterns.md` | `design-patterns-catalog.md` | `component-extraction-guide.md` | `ddd-basics.md` | `no-comment-only-code.md`

**异常处理要求**（后端/全栈 Task）：
- 编码前执行异常模式扫描，发现项目约定（异常类名、错误码格式、RPC调用模式）
  - 详见 [`../exception/references/exception-pattern-discovery.md`](../exception/references/exception-pattern-discovery.md)
- 自动识别异常场景：数据库操作返回 null、RPC 调用失败、JSON 解析异常、参数校验失败
- 根据项目约定生成异常代码（异常类名、错误码通过扫描发现，禁止硬编码）
- RPC 调用一律使用远程异常，业务场景使用业务异常，参数校验使用参数异常，系统异常使用系统异常
- 详见 [`../exception/SKILL.md`](../exception/SKILL.md)

**单元测试约束**：
- 覆盖率达标（行≥85% / 分支≥75% / 函数≥85% + @critical 路径 100%）| 正常路径+边界+错误处理 | 每测试一行为
- 禁止mock业务逻辑 | 禁止修改代码适配测试 | 禁止虚假测试 | 禁止always-true断言
- Mock策略：mock外部依赖和第三方库，不mock内部逻辑
- 详见：`references/unit-test-real-practices.md` | `references/tdd-iron-laws.md`
- **后端模板**：`../test/templates/backend-unit-test-template.md`（Python/Go/Java/Rust 完整示例）

**浏览器测试（前端/全栈）**：
- 每 Task 编写 Playwright 测试代码（`data-testid` 选择器 / BROWSER-TESTABLE 覆盖 / 命名 `[feature].e2e.test.ts`）
- 类型：`@e2e`(端到端) | `@visual`(视觉回归) | `@component`(组件UI)
- **批次级执行**：同批次前端 Task 全部完成后，由 execute 编排层统一运行 `npx playwright test` 验证全部 BROWSER-TESTABLE，减少浏览器启动/关闭开销和 token 消耗
- executor 仅确保测试代码已编写、选择器已定义，不自行启动浏览器

#### 3.3 综合性代码审查（单次派遣）

<GATE>standard 模式必须通过 Agent 派遣 code-reviewer，不允许主上下文直接审查。</GATE>

**批次级审查（推荐）**：同批次全部 Task 完成后，一次性派遣 code-reviewer 审查批次 diff。
- 适用：批次内 Task ≥ 2，且各 Task 代码 < 200 行
- 节省：每额外 Task 节省一次 code-reviewer 派遣（~25K token）

**单 Task 审查（兜底）**：每 Task 单独派遣 code-reviewer。
- 适用：单 Task 代码 > 200 行，或 @critical 标记的 Task

```bash
Agent(
  subagent_type="orch:code-reviewer",
  prompt="
    对 Task-{id} 的代码执行**综合性审查**（一次性覆盖规范 + 质量 + TDD 完整性）：
    - 代码路径: src/{task-files}
    - 设计规范: orch-spec/{requirement_desc_abstract}/design/design.md
    
    审查维度：
    1. 规范合规：架构符合性、接口一致性、错误处理策略、命名规范
    2. 代码质量：Bug 检测、DRY/SOLID、安全漏洞、竞态条件、内存泄漏
    3. TDD 完整性：RED→GREEN→REFACTOR→REVIEW 四阶段命令输出是否完整
    4. 覆盖率验证：行≥85% / 分支≥75% / 函数≥85%（@critical 路径 100%）
    5. 需求追溯：实现行为是否与 spec 场景一致（covers 字段）
    
    仅报告置信度 ≥ 对应阈值的问题（CRITICAL≥50 / WARNING≥60 / INFO≥80）。
    返回：问题清单（按严重度分组）+ 置信度 + 修复建议 + 覆盖率 raw output。
  ",
  run_in_background=false
)
```


#### 3.5 修复循环

基于 3.3 和 3.4 的审查结果：发现问题→修复→重新派遣 code-reviewer 审查→直到通过。

##### 偏差处理规则

| 规则 | 触发条件 | 操作 |
|------|---------|------|
| 自动修复 | 编译错误 / lint 错误 / 类型错误 | 自动修复后继续，不暂停 |
| 自动补全 | 缺失 loading/empty/error 状态等关键组件 | 自动添加后继续 |
| 架构阻断 | 涉及架构变更 / 模块重组 | AskUserQuestion（继续/回退/调整设计） |
| 阈值退出 | 同一问题修复失败 3 次 | 暂停并上报，等待人工介入 |

详见：`references/code-implementation-quality.md` | `references/code-completeness-checklist.md`

#### 3.6 完成验证

任何Task标记"完成"前必须实际运行验证命令：IDENTIFY→RUN→READ→VERIFY→CLAIM。

| 声称 | 必须提供 |
|------|---------|
| 单元测试通过 | 测试命令输出: 0 failures |
| 代码编译成功 | 编译命令: exit 0（前端: tsc / 后端: go build / mvn compile / cargo check / python -m py_compile） |
| 静态检查通过 | Lint 0错误（前端: ESLint / 后端: pylint / golangci-lint / checkstyle / clippy） |
| 浏览器测试通过 | Playwright输出: 0 failures |
| Task完成 | 验收标准逐项核对+证据 |

详见：`references/verification-gate.md`

#### 3.7 TDD状态追踪

每个Task必须记录四阶段日志：
```
| 阶段 | 状态 | 详情 |
| RED | ✅ | test.ts 已创建，FAIL (3 tests, 3 failed) |
| GREEN | ✅ | impl.ts 已创建，PASS (3 tests, 3 passed) |
| REFACTOR | ✅ | 重构完成，PASS |
| REVIEW | ✅ | 规范✅ 质量✅ 覆盖率92% |
```

<GATE>standard模式缺失任何阶段→该Task视为未完成</GATE>

**MainAgent TDD验证**：同 executor.md 4.2 节（注入上下文自检 + 复杂度加权抽样 + raw output 验证）。

### 执行完成前自检

生成报告前必须自检：TDD流程✓ | 测试文件✓ | 测试实际运行✓ | 子代理使用✓ | RED阶段✓ | 覆盖率达标✓ | 审查完成✓ | 修复循环✓ | 分支安全✓ | 无伪代码✓ | TDD日志✓ | 模式标签遵循✓ | Token效率✓

不通过→暂停回到对应Task重新执行，不允许进入 test。

### Worktree 合并和清理

所有 Task 完成后：
1. **合并**：将每个 worktree 的 commit cherry-pick 到目标分支（按依赖顺序）
2. **验证**：运行全量测试确认合并成功
3. **删除**：`git worktree remove .claude/worktrees/{task-id}-{name}`
4. **清理孤立**：`git worktree list` 检查并 `git worktree prune` 删除遗留 worktree
5. **更新需求上下文**：将实际修改的文件清单追加到 `orch-spec/{req}/req-context/key-files.md` 的 `## execute 阶段`，全栈时跨仓库修改追加到 `cross-repo.md`

### 生成执行报告

输出：所有Task状态 | 修复循环记录 | 代码统计 | 质量指标 | TDD总览。详见 `references/workflow-detail.md`。

## 关键约束

- 每Task独立worktree | 最大并发≤5 | 子代理文件范围锁定 | 严禁跨分支提交
- standard模式：必须子代理 + 完整TDD + 综合性审查（规范+质量一次完成）| 覆盖率达标（行≥85%/分支≥75%/函数≥85%/语句≥85%/@critical 100%）
- quick模式：子代理可选 | 覆盖率≥60%
- 后端/全栈 Task 必须调用 exception Skill | 代码必须通过项目技术栈对应静态检查
- 完成前必须自检 + 前端Task必须浏览器测试

## Output

- `src/` — 实现代码
- `execution/execution-report.md` — 执行报告
## 参考文档速查

### TDD 流程
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `references/tdd-flow.md` | TDD 四阶段循环（RED→GREEN→REFACTOR→REVIEW） | 步骤3.2 |
| `references/tdd-iron-laws.md` | TDD 铁律和原则 | 步骤3.2 |
| `references/unit-test-real-practices.md` | 单元测试实践：Mock 策略、结构要求 | 步骤3.2 |

### 代码质量
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `references/code-implementation-quality.md` | 禁止伪代码、真实性要求 | 步骤3.3 |
| `references/code-completeness-checklist.md` | 完整性检查清单（空框架/TODO/分支） | 步骤3.3 |
| `references/no-comment-only-code.md` | 严禁只写注释不实现 | 步骤3.2 |

### Git/Worktree
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `references/git-worktrees-guide.md` | Worktree 创建/合并/删除全流程 | 步骤3.1/3.9 |
| `references/worktree-confirmation-protocol.md` | Worktree 创建确认协议 | 步骤3.1 |
| `references/branch-safety-protocol.md` | 分支安全协议（严禁跨分支提交） | 步骤3.1/3.9 |

### 设计模式
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `references/design-principles.md` | SOLID/DRY/KISS/YAGNI 原则 | 步骤3.2/REFACTOR |
| `references/architecture-patterns.md` | Clean Architecture/MVC/微服务 | 步骤3.2 |
| `references/design-patterns-catalog.md` | 工厂/策略/观察者/装饰器 | 步骤3.2 |
| `references/component-extraction-guide.md` | 组件拆分触发器和类型 | 步骤3.2 |
| `references/ddd-basics.md` | DDD 限界上下文/聚合根/值对象 | 步骤3.2 |
| `references/dependency-injection-guide.md` | 构造函数/属性/方法注入 | 步骤3.2 |

### 执行控制
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `references/subagent-protocol.md` | 子代理状态协议、并行派遣规则 | 步骤2 |
| `references/verification-gate.md` | 完成验证门控（IDENTIFY→RUN→READ→VERIFY→CLAIM） | 步骤3.6 |
| `references/token-efficiency-guide.md` | Token 节省最佳实践（注入信任/摘要优先/浏览器测试批量化） | 步骤3.2-3.6 |
| `references/quick-reference.md` | Worktree 快速参考卡 | 步骤3.1 |
| `references/workflow-detail.md` | 完整工作流步骤和示例 | 步骤4 |
| `prompts/tdd-implementer-prompt.md` | executor Agent TDD实现提示词 | 步骤3.2 |

### 跨 Skill
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `../exception/SKILL.md` | 异常处理场景和类型判断 | 步骤3.2 |
| `../exception/references/exception-pattern-discovery.md` | 异常模式扫描流程 | 步骤3.2 |
