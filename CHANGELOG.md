# 更新日志

所有重要的项目更新将在此文档中记录。

## [2.11.0] - 2026-04-30

### 新增 - 代码设计与编写能力全面增强

#### 新增 7 个参考文档

| 文档 | 内容 |
|------|------|
| design-patterns-guide.md | 17 种设计模式 + 决策树 + 反模式识别（code-designer） |
| domain-modeling-guide.md | DDD 领域建模完整指南 + 多语言示例（code-designer） |
| architecture-patterns-guide.md | Clean/Hexagonal/Layered/MVC 对比 + 选择建议（code-designer） |
| solid-principles-guide.md | SOLID 五原则 + 正反示例 + 多语言实现（code-execute） |
| dependency-injection-guide.md | 三种注入方式 + 四语言示例 + 反模式（code-execute） |
| component-extraction-guide.md | 拆分触发器 + 决策流程 + 反模式（code-designer） |
| architecture-review-checklist.md | 8 大类审查清单 + 三级优先级（code-designer） |

#### 修改 6 个 skill/agent 文件

| 文件 | 变更 |
|------|------|
| code-designer/SKILL.md | 新增领域建模、架构原则、组件拆分分析步骤 |
| design-template.md | 新增设计模式、领域模型、架构风格、组件拆分章节 |
| code-execute/SKILL.md | 新增参考文档引用、严禁注释代替实现铁律 |
| code-task/SKILL.md | 新增领域模型、设计模式实现、共享组件抽离任务类型 |
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

### 新增 - SQL DDL/DML 生成 + 多项目协作 + 后端测试增强 + spec-creation 探索增强

#### 1. SQL DDL/DML 可执行脚本生成
- spec-creation 阶段新增 SQL 方言确认（MySQL/PostgreSQL/SQLite/SQLServer）
- 自动生成 `sql-ddl.md`，包含 4 节：DDL/DML/执行顺序/回滚 SQL
- code-designer 阶段 2.5 新增独立 SQL 文件生成（`design/sql/` 目录）
- 新增 SQL 方言对照指南（`sql-dialect-guide.md`）
- data-models.md 和 infrastructure.md 增加交叉引用指向 SQL 文件
- 数据库相关 Task 增加 SQL 参考字段

#### 2. 多项目协作工作流
- requirement.md 新增多项目协作声明（协作模式、涉及项目、依赖关系）
- code-designer 新增阶段 2.6 多项目协作协调，生成 `collaboration-plan.md`
- code-task 新增步骤 1.6 多项目任务分组（按项目分组 + 依赖门控）
- 支持 4 种协作模式：single / monorepo / multi-repo / same-repo
- 新增跨项目执行计划章节（含批次表 + 接口门控表）
- code-execute 新增多项目执行门控（严格按依赖顺序或 Mock 并行）
- api-contract 新增 Phase 5 跨项目契约验证

#### 3. 后端测试能力增强
- code-test 新增步骤 3.0 后端测试基础设施检测（无测试能力时 AskUserQuestion 询问添加）
- 新增后端集成测试覆盖范围（Repository/Service/API 层 + 数据库策略）
- 新增 3 个后端测试模板：
  - `backend-api-test.template.ts`（Node.js/Python/Go 多技术栈）
  - `backend-e2e-api-test.template.ts`（完整业务流程验证）
  - `backend-db-migration-test.template.ts`（正向/回滚/数据完整性）
- 重构 `contract-test-template.md`（完整的字段/类型/错误码验证）
- 新增后端性能测试指标和 k6 压测指引
- 新增 testing-anti-patterns.md 参考文档

#### 4. spec-creation 需求探索增强
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
- code-test 新增测试反模式检查参考

### 新建文件
- `skills/spec-creation/templates/spec-sql-ddl-template.md`
- `skills/spec-creation/templates/spec-multi-project-template.md`
- `skills/code-designer/references/sql-dialect-guide.md`
- `skills/code-designer/templates/sql-ddl-template.md`
- `skills/code-designer/templates/collaboration-plan-template.md`
- `skills/code-test/templates/backend-api-test.template.ts`
- `skills/code-test/templates/backend-e2e-api-test.template.ts`
- `skills/code-test/templates/backend-db-migration-test.template.ts`
- `skills/code-execute/references/tdd-iron-laws.md`
- `skills/code-execute/references/verification-gate.md`
- `skills/code-execute/references/subagent-protocol.md`
- `skills/code-test/references/testing-anti-patterns.md`

### 修改文件
- `skills/spec-creation/SKILL.md` - +SQL方言、+多项目检测、+阶段1.5/2.5/4.5、+输出结构
- `skills/spec-creation/templates/spec-requirement-template.md` - +sql-dialect、+多项目协作
- `skills/spec-creation/templates/spec-data-models-template.md` - +交叉引用
- `skills/spec-creation/templates/spec-infrastructure-template.md` - +SQL引用提示
- `skills/spec-creation/templates/spec-scenario-template.md` - +场景间依赖
- `skills/code-designer/SKILL.md` - +阶段2.5.2 SQL生成、+阶段2.6多项目协调、+HARD-GATE
- `skills/code-designer/templates/design-template.md` - +SQL执行计划、+2.14多项目协作
- `skills/code-task/SKILL.md` - +SQL/多项目任务类型、+步骤1.6分组
- `skills/code-task/templates/task-template.md` - +所属项目、SQL参考、跨项目依赖
- `skills/code-task/templates/tasks-document-template.md` - +SQL引用、+多项目执行计划
- `skills/code-task/templates/backend-tasks-guide.md` - +多项目场景后端任务指南
- `skills/code-task/templates/frontend-tasks-guide.md` - +多项目场景前端任务指南
- `skills/code-execute/SKILL.md` - +SQL验证、+多项目门控、+资源引用
- `skills/code-test/SKILL.md` - +后端测试基础设施检测、+集成测试增强、+后端模板引用
- `skills/code-test/templates/contract-test-template.md` - 重构为完整契约测试
- `skills/api-contract/SKILL.md` - +第6维度DB验证、+Phase5跨项目契约验证
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
- standard 模式下必须使用 `Agent(subagent_type="orch:code-executor")` 工具
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
- 不通过不允许生成执行报告、不允许进入 code-test

#### 6. 快速模式/标准模式明确切换
- spec-creation 输出 requirement.md 新增 6 字段模式标签
  - 模式、TDD要求、子代理要求、测试覆盖要求、触发原因、影响范围
- code-task 在 tasks.md 头部继承模式标签
- code-execute/code-test 读取并严格遵循模式标签

### 修改文件
- `skills/code-execute/SKILL.md` - 新增步骤0/1.5/3.7/3.8，强化约束
- `skills/spec-creation/SKILL.md` - 增强模式标签输出
- `skills/code-task/SKILL.md` - 新增模式标签读取和传递
- `skills/code-test/SKILL.md` - 新增模式标签读取
- `skills/code-task/templates/tasks-document-template.md` - 新增 TDD 追踪表
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
