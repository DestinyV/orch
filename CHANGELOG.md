# 更新日志

所有重要的项目更新将在此文档中记录。

## [0.11.1] - 2026-08-03

### 优化 - Git Worktree 生命周期管理脚本化

#### 新增
- `scripts/worktree.js` — worktree 生命周期管理 CLI，5 个子命令：
  - `create {task-id} {branch}` — 封装 5 步创建重试协议（清理残留/分支占用/从 HEAD 兜底），返回码 0=成功/1=降级/2=用法错误
  - `merge {task-id} {target-branch}` — cherry-pick commit 序列到目标分支，合并后恢复原分支；冲突保留 CHERRY_PICK_HEAD
  - `cleanup [--target] [--dry-run] [--force]` — 自动清理孤儿 worktree + 已合并分支；未合并项警示（--force 强制）
  - `list` / `status` — 列出 worktree 状态（含孤儿标记），供自检与排查
  - 安全：`execFileSync('git', [...])` 无 shell 防注入；task-id 校验防路径穿越；Windows 兼容

#### 集成
- `scripts/self-check.js` orchestration 块新增 2 项检查：worktree.js 子命令分发存在 + 无孤儿 worktree
- `tests/meta-b7-worktree.py`（新建，14 用例）— 在隔离临时 git 仓库测试全部子命令，不污染主仓库
- `tests/hooks-smoke.test.js` 新增 worktree.js 模块导出断言

#### 文档
- `skills/execute/SKILL.md` 创建协议 + 合并清理改为脚本调用（消除 16+ 处散落 git 命令）
- 4 个 references 文档（git-worktrees-guide / worktree-confirmation-protocol / branch-safety-protocol / quick-reference）指向脚本，注明脚本是护栏（北极星）
- `agents/executor.md` 工作环境准备指向脚本

#### 版本更新
- plugin.json → 0.11.1
- marketplace.json → 0.11.1
- CLAUDE.md → v0.11.1

## [0.11.0] - 2026-08-01

### 新增 - 插件本体全方位能力优化（元任务）

#### 核心原则
- **北极星原则**：约束 = 护栏（防坠落）非牢笼（限奔跑）。在最大化发挥模型自身能力的前提下提供流程约束，绝不因约束限制模型能力。NSP-001~007 审查：2 项 token 时代残留的探索限制约束降级为建议，5 项流程纪律保留。
- 明确"不关注 token 消耗"，专注能力优化。

#### 新增能力
| 文件 | 说明 |
|------|------|
| `scripts/self-check.js` + `commands/self-check.md` | 插件 5 块自检命令（orchestration/agents/skills/tdd_loop/commands_hooks），`node scripts/self-check.js` |
| `scripts/lib/stage-contracts.js` | 阶段契约单一事实源（STAGE_ORDER/STAGE_OUTPUTS/SKILL_PREREQUISITES/EXEMPT_*），消除多处维护漂移 |
| `scripts/lib/verdict.js` | 判定函数库（judgeCoverage/judgeRate/judgeAutoResolve），覆盖率以实测为准 |
| `scripts/hooks/observe.js` + `observe.sh` | instinct 观察层激活（fail-open），注册 pre/post:observe |
| `tests/hooks-smoke.test.js` | hooks 基础设施冒烟测试 |
| `tests/meta-b1~b6-*.py`（14 个） | 各批次 TDD 聚焦测试 |

#### 修复（18 项薄弱环节闭环）
- **P0**：execute/spec 悬空引用修复
- **P1**：cost 补 GATE 硬约束、using-orch 索引 6→22
- **P2**：observer.enabled 激活、16 核心 skill 补 TRIGGER when
- **F1-F12**：project-map.md 引用统一 ×4、tdd-guide 注册+deprecated、Prompt Defense 幂等修复、frontmatter 统一、code-architect 编号、/hookify 清理、suggest-compact 注册激活、CLAUDE.md 钩子表同步、文档数量口径 22/26/14、file-map/index 同步、__pycache__ 清理 + .gitignore、EXEMPT 命令名分离

#### 版本更新
- plugin.json → 0.11.0
- marketplace.json → 0.11.0（Agents 口径 25→26）
- CLAUDE.md → v0.11.0

## [2.11.0] - 2026-04-30

### 新增 - 代码设计与编写能力全面增强

#### 新增 7 个参考文档

| 文档 | 内容 |
|------|------|
| design-patterns-guide.md | 17 种设计模式 + 决策树 + 反模式识别（designer） |
| domain-modeling-guide.md | DDD 领域建模完整指南 + 多语言示例（designer） |
| architecture-patterns-guide.md | Clean/Hexagonal/Layered/MVC 对比 + 选择建议（designer） |
| solid-principles-guide.md | SOLID 五原则 + 正反示例 + 多语言实现（execute） |
| dependency-injection-guide.md | 三种注入方式 + 四语言示例 + 反模式（execute） |
| component-extraction-guide.md | 拆分触发器 + 决策流程 + 反模式（designer） |
| architecture-review-checklist.md | 8 大类审查清单 + 三级优先级（designer） |

#### 修改 6 个 skill/agent 文件

| 文件 | 变更 |
|------|------|
| designer/SKILL.md | 新增领域建模、架构原则、组件拆分分析步骤 |
| design-template.md | 新增设计模式、领域模型、架构风格、组件拆分章节 |
| execute/SKILL.md | 新增参考文档引用、严禁注释代替实现铁律 |
| task/SKILL.md | 新增领域模型、设计模式实现、共享组件抽离任务类型 |
| task-template.md | 新增设计模式、架构层字段 |
| code-reviewer.md | 新增 SOLID/设计模式/层边界/注释代替实现审查维度 |

#### 版本更新

- plugin.json → 2.11.0
- skills/package.json → 2.11.0

## [2.9.0] - 2026-04-30

### 重构

- 重命名 `using-superpowers` skill 为 `using-orch`，更准确地反映插件身份
- 更新 skill 名称、描述和内部引用

## [2.8.0] - 2026-04-29

### 新增 - SQL DDL/DML 生成 + 多项目协作 + 后端测试增强 + spec 探索增强

#### 1. SQL DDL/DML 可执行脚本生成
- spec 阶段新增 SQL 方言确认（MySQL/PostgreSQL/SQLite/SQLServer）
- 自动生成 `sql-ddl.md`，包含 4 节：DDL/DML/执行顺序/回滚 SQL
- designer 阶段 2.5 新增独立 SQL 文件生成（`design/sql/` 目录）
- 新增 SQL 方言对照指南（`sql-dialect-guide.md`）
- data-models.md 和 infrastructure.md 增加交叉引用指向 SQL 文件
- 数据库相关 Task 增加 SQL 参考字段

#### 2. 多项目协作工作流
- requirement.md 新增多项目协作声明（协作模式、涉及项目、依赖关系）
- designer 新增阶段 2.6 多项目协作协调，生成 `collaboration-plan.md`
- code-task 新增步骤 1.6 多项目任务分组（按项目分组 + 依赖门控）
- 支持 4 种协作模式：single / monorepo / multi-repo / same-repo
- 新增跨项目执行计划章节（含批次表 + 接口门控表）
- code-execute 新增多项目执行门控（严格按依赖顺序或 Mock 并行）
- contract 新增 Phase 5 跨项目契约验证

#### 3. 后端测试能力增强
- test 新增步骤 3.0 后端测试基础设施检测（无测试能力时 AskUserQuestion 询问添加）
- 新增后端集成测试覆盖范围（Repository/Service/API 层 + 数据库策略）
- 新增 3 个后端测试模板：
  - `backend-api-test.template.ts`（Node.js/Python/Go 多技术栈）
  - `backend-e2e-api-test.template.ts`（完整业务流程验证）
  - `backend-db-migration-test.template.ts`（正向/回滚/数据完整性）
- 重构 `contract-test-template.md`（完整的字段/类型/错误码验证）
- 新增后端性能测试指标和 k6 压测指引
- 新增 testing-anti-patterns.md 参考文档

#### 4. spec 需求探索增强
- 新增阶段 1.5 需求深度追问（5 个维度逐个确认）
- 新增阶段 2.5 方案对比选择（复杂需求触发 2-3 种方案）
- 新增阶段 4.5 规范自审查（占位符/一致性/范围/歧义/完整性/SQL/多项目）
- 强化阶段 1 项目探索（code-explorer 从"可选"改为"标准流程必须"）
- 新增场景间依赖关系字段（depends-on / provides-to）
- code-explorer agent 新增"需求探索模式"

#### 5. superpowers 最佳实践集成
- 新增 TDD 铁律参考（tdd-iron-laws.md）：无失败测试不写生产代码
- 新增验证完成前门控（verification-gate.md）：IDENTIFY→RUN→READ→VERIFY→CLAIM
- 新增子代理状态协议（subagent-protocol.md）：DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED
- test 新增测试反模式检查参考

### 新建文件
- `skills/spec/templates/spec-sql-ddl-template.md`
- `skills/spec/templates/spec-multi-project-template.md`
- `skills/designer/references/sql-dialect-guide.md`
- `skills/designer/templates/sql-ddl-template.md`
- `skills/designer/templates/collaboration-plan-template.md`
- `skills/test/templates/backend-api-test.template.ts`
- `skills/test/templates/backend-e2e-api-test.template.ts`
- `skills/test/templates/backend-db-migration-test.template.ts`
- `skills/execute/references/tdd-iron-laws.md`
- `skills/execute/references/verification-gate.md`
- `skills/execute/references/subagent-protocol.md`
- `skills/test/references/testing-anti-patterns.md`

### 修改文件
- `skills/spec/SKILL.md` - +SQL方言、+多项目检测、+阶段1.5/2.5/4.5、+输出结构
- `skills/spec/templates/spec-requirement-template.md` - +sql-dialect、+多项目协作
- `skills/spec/templates/spec-data-models-template.md` - +交叉引用
- `skills/spec/templates/spec-infrastructure-template.md` - +SQL引用提示
- `skills/spec/templates/spec-scenario-template.md` - +场景间依赖
- `skills/designer/SKILL.md` - +阶段2.5.2 SQL生成、+阶段2.6多项目协调、+HARD-GATE
- `skills/designer/templates/design-template.md` - +SQL执行计划、+2.14多项目协作
- `skills/task/SKILL.md` - +SQL/多项目任务类型、+步骤1.6分组
- `skills/task/templates/task-template.md` - +所属项目、SQL参考、跨项目依赖
- `skills/task/templates/tasks-document-template.md` - +SQL引用、+多项目执行计划
- `skills/task/templates/backend-tasks-guide.md` - +多项目场景后端任务指南
- `skills/task/templates/frontend-tasks-guide.md` - +多项目场景前端任务指南
- `skills/execute/SKILL.md` - +SQL验证、+多项目门控、+资源引用
- `skills/test/SKILL.md` - +后端测试基础设施检测、+集成测试增强、+后端模板引用
- `skills/test/templates/contract-test-template.md` - 重构为完整契约测试
- `skills/contract/SKILL.md` - +第6维度DB验证、+Phase5跨项目契约验证
- `agents/code-architect.md` - +多项目协作模式识别
- `agents/code-explorer.md` - +需求探索模式

---

## [2.7.0] - 2026-04-23

### 新增 - 六大强制约束增强

#### 1. HARD-GATE 拦截点
- 在 code-execute 关键节点增加硬拦截机制
- 测试框架可用性确认（无测试框架时 AskUserQuestion 暂停）
- 测试文件存在性检查（standard 模式下无测试文件不允许编码）
- 工作模式最终确认（AskUserQuestion 三选一）

#### 2. 子代理派遣强制化
- standard 模式下必须使用 `Agent(subagent_type="orch:executor")` 工具
- 提供具体的工具调用模板
- 快速模式可选子代理或直接主上下文执行

#### 3. TDD 状态追踪机制
- 每个 Task 必须输出 TDD 四阶段日志（RED→GREEN→REFACTOR→REVIEW）
- 执行报告包含 TDD 总览表
- tasks.md 模板新增 TDD 追踪表

#### 4. 测试基础设施检查前置
- code-execute 步骤1.5 新增测试环境验证
- 无测试框架时自动暂停并询问用户
- 支持 Jest/Vitest/Pytest 多种框架选择

#### 5. 执行流程自检清单
- code-execute 结尾强制 12 项自检
- 自检不通过 → 回到对应 Task 重新执行
- 不通过不允许生成执行报告、不允许进入 test

#### 6. 快速模式/标准模式明确切换
- spec 输出 requirement.md 新增 6 字段模式标签
  - 模式、TDD要求、子代理要求、测试覆盖要求、触发原因、影响范围
- code-task 在 tasks.md 头部继承模式标签
- execute/test 读取并严格遵循模式标签

### 修改文件
- `skills/execute/SKILL.md` - 新增步骤0/1.5/3.7/3.8，强化约束
- `skills/spec/SKILL.md` - 增强模式标签输出
- `skills/task/SKILL.md` - 新增模式标签读取和传递
- `skills/test/SKILL.md` - 新增模式标签读取
- `skills/task/templates/tasks-document-template.md` - 新增 TDD 追踪表
- `skills/package.json` - 版本升级，key_features 更新
- `CLAUDE.md` - 版本升级，工作流特色更新

---

## [1.0.0] - 2026-02-09

### 新增
- ✅ **spec-generator skill** - 帮助团队快速生成ai-doc规范
  - 交互式问卷引导
  - 支持用户自定义业务模式
  - 自动生成README.md和使用指南

- ✅ **ai-planning skill** - 需求分析和方案设计
  - 需求分析
  - 技术设计
  - 问题确认
  - 输出ExecutionGuide

- ✅ **ai-code-execution skill** - 代码生成和实现
  - 加载ExecutionGuide
  - 参考Class驱动
  - 代码生成
  - 微调治理
  - 输出执行报告

- ✅ **ai-test-creation skill** - 测试生成和验证
  - 功能点提取
  - 测试用例设计
  - 测试代码生成
  - 闭环验证
  - 输出测试报告

### 文档
- ✅ README.md - 项目总体介绍
- ✅ 安装说明 - 详细的安装步骤
- ✅ 使用指南 - 详细的使用方式和场景
- ✅ CHANGELOG.md - 更新日志

### 特性
- ✅ 完全通用的规范框架（无任何硬编码的业务逻辑）
- ✅ 参考Class驱动的开发方式
- ✅ 完整的Plan-Exe-Test三阶段工作流
- ✅ 支持任何技术栈和行业

---

## 版本计划

### v1.1.0（计划中）
- 支持更多的技术栈示例（Go、Rust等）
- 增强的错误处理和提示
- 更完善的文档

### v1.2.0（计划中）
- 支持多team的规范共享
- 规范版本管理
- 开发流程的可视化

### v2.0.0（计划中）
- 完全的AI驱动的设计系统
- 自动化的代码review
- 生产环境的完全自动化

---

## 贡献指南

欢迎提交Issue和Pull Request！

### 报告Bug
- 描述问题的详细步骤
- 提供错误日志和截图
- 说明你的环境信息

### 建议功能
- 描述用例
- 说明期望的行为
- 提供参考链接（如有）

### 提交Pull Request
1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. Commit更改 (`git commit -m 'Add some AmazingFeature'`)
4. Push到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

---
