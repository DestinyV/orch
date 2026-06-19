# orch 全栈SDD+TDD开发工作流

[English](./README_EN.md) | 中文

![overview](./docs/img/overview.png)

**快速导航**：
- 📖 [使用指南](./docs/USAGE.md) - 详细的使用场景和步骤
- 🛠️ [最佳实践](./docs/BEST_PRACTICES.md) - 核心原则和最佳做法
- 🔧 [安装说明](./docs/INSTALLATION.md) - 安装和故障排查
- 🏗️ [技术指南](./CLAUDE.md) - Claude工作指南（架构和设计原则）
- 🔀 [Git-Worktrees指南](./skills/execute/references/git-worktrees-guide.md) - 隔离工作环境指南
- ⚡ [Worktrees快速参考](./skills/execute/references/quick-reference.md) - 日常使用快速查询卡片

## 📌 概述

**orch** 是一个企业级Claude Code插件，提供AI辅助开发的**完整全栈工作流**。通过11个专业的skills，覆盖从需求到归档的全生命周期。帮助团队快速建立规范框架、进行设计规划、定义测试标准、分解任务、生成代码、处理异常、验证功能、归档规范。支持前端、后端、数据库、移动、微服务等多类型项目。

**工作流**：
```
/start "需求" → /spec (规范) → /test-design (测试规范) ⟷ /design (设计) → /contract (契约) → /task (任务) → /execute (编码) → /exception (异常) → /test (测试) → /archive (归档) → 完成
```

> `/test-design` 和 `/design` 可并行执行（均依赖 spec 输出）。
> `/exception` 在后端/全栈项目中自动触发（零硬编码，项目约定扫描）。

---

## ✨ 核心特性

### 🎯 规范驱动开发（SDD）
- ✅ 定义全栈设计规范和参考实现（前端、后端、数据库等）
- ✅ 参考实现作为架构和代码标准
- ✅ AI根据规范生成设计和代码
- ✅ 支持多种技术栈（React/Vue、Node.js/Python/Go/Java、PostgreSQL/MongoDB等）

### 📋 完整工作流
- ✅ **Spec阶段**：定义设计规范
- ✅ **Design阶段**：需求分析 + 方案设计
- ✅ **Task阶段**：任务分解 + 清单定义
- ✅ **Execute阶段**：代码生成 + 多阶段审查
- ✅ **Test阶段**：测试生成 + 闭环验证

### 🔄 质量保证机制
- ✅ 规范审查：确保代码符合规范
- ✅ 质量审查：确保代码质量
- ✅ TDD实现：RED-GREEN-REFACTOR-REVIEW四阶段TDD流程
- ✅ 测试覆盖：单元测试≥80%，集成/E2E/性能测试全覆盖
- ✅ 闭环验证：确保TEST-VERIFY→Test→Code→Result完全对应

### ⚡ 立即可用
- ✅ 交互式问卷引导（支持多种技术栈选择）
- ✅ 自动生成设计规范和任务清单
- ✅ 详细的使用说明和最佳实践
- ✅ 支持前端、后端、数据库、微服务等多类型项目

---

## 📦 包含的11个Skills

| Skill | 阶段 | 功能 | 输出 |
|-------|------|------|------|
| **scripts** | 工具 | 工具优先策略：Grep/Bash/Glob/Edit 优先完成文件搜索/提取/编辑/校验，仅脚本无法处理时兜底Read | 脚本化文件操作 |
| **workflow** | 编排器 | 统一入口+流程编排：自动检测模式、串联9个Skill、HARD-GATE卡点、中断恢复 | .workflow-state.json + 全流程自动执行 |
| **spec** | Spec | 需求分析和规范生成，输出BDD格式规范文档（WHEN-THEN格式） | orch-spec/{requirement_desc_abstract}/spec/ |
| **test-design** | Test-Design | 从TEST-VERIFY生成测试规范、数据和框架代码 | test-spec.md + fixtures.json + test-*.template |
| **design** | Design | 根据规范进行代码设计规划，生成架构和技术方案 | orch-spec/{requirement_desc_abstract}/design/design.md |
| **contract** | Api-Contract | 接口契约定义与审查（fullstack强制） | contract.md + review-report.md |
| **task** | Task | 将设计转换为代码级别任务列表，支持前后端、数据库、微服务任务 | orch-spec/{requirement_desc_abstract}/tasks/tasks.md |
| **execute** | Execute | 通过子代理执行任务，支持多语言多框架，进行规范+质量两阶段审查，TDD流程保证单元测试。**v2.3.1+**：使用git-worktree为每个Task创建隔离工作环境，确保修复循环的安全性、可追踪性和可恢复性 | src/ + orch-spec/{requirement_desc_abstract}/execution/execution-report.md |
| **exception** | Exception | 异常场景识别 + 项目约定扫描 + 异常代码生成（后端/全栈，零硬编码） | src/** (添加异常处理) |
| **test** | Test | 高层测试（集成/E2E/性能测试）和闭环验证 | tests/ + orch-spec/{requirement_desc_abstract}/testing/testing-report.md |
| **archive** | Archive | 规范归档和优化，将需求规范通过场景拆分合并到主规范中 | orch-spec/spec/ (已合并的主规范) |

详细说明：[查看skills详细文档](./skills/README.md)

## 🤖 核心Agents

orch 包含9个专业的Agents，在各个Skills中协同工作：

| Agent | 职责 | 应用场景 |
|-------|------|--------|
| **code-architect** | 通过分析现有代码库的模式和约定，设计功能架构并提供完整的实现蓝图 | 在design阶段，分析项目结构、提取设计模式、规划架构 |
| **code-explorer** | 通过追踪执行路径、映射架构层、识别设计模式，深入分析现有代码实现 | 在spec和design阶段，提取架构约定和可复用代码 |
| **executor** | 根据详细的实现任务，通过TDD流程（RED-GREEN-REFACTOR-REVIEW）编写高质量代码 | 在execute阶段，每个Task派遣独立子代理在git-worktree中实现 |
| **code-reviewer** | 针对bug、逻辑错误、安全漏洞和代码质量进行审查，置信度过滤（≥80） | 在execute阶段3.3/3.4和test阶段2：规范审查+质量审查 |
| **archiver** | 规范归档专家，对标分析、冲突检测、智能合并、一致性验证 | 在archive阶段派遣执行场景对标、合并和一致性检查 |
| **test-designer** | 将TEST-VERIFY转换为测试用例，定义Mock策略，生成fixtures和测试框架代码 | 在test-design阶段分析场景、设计测试用例、生成测试模板 |
| **exception** | 项目约定扫描 + 异常场景识别 + 异常代码生成，零硬编码设计 | 在execute阶段后端/全栈Task自动触发，添加异常处理 |
| **contract-creator** | 接口契约定义和六维度审查（完整性/命名/类型/错误/约定/数据库） | 在contract阶段fullstack强制，生成契约文档和审查报告 |
| **tasker** | 设计→任务拆解 + 依赖分析 + 并行执行规划 + Test Case映射 | 在task阶段将设计分解为可执行任务和依赖DAG |

---

## 🚀 快速开始

### 前置要求
- Claude Code 已安装

### 安装
```bash
1、进入 Claude
2、添加市场 /plugin -> Marketplaces -> +Add Marketplace ->
3、粘贴 https://github.com/DestinyV/orch.git
4、安装plugin 再进入 /plugin -> Marketplaces -> DestinyV-marketplace Enter选中 -> Browse plugins -> orch Enter安装
```

### 使用流程

#### 第0步：进入插件（用户操作）

```bash
/orch:sdd-dev

根据提示输入需求内容
```

---

#### 第1步：需求规范化（用户操作）

```bash
/spec
```

与插件进行交互式对话，进行需求分析和确认：
1. 需求分析和初步拆解
2. 场景细化和多轮确认
3. 生成BDD格式规范

生成结果：`orch-spec/{requirement_desc_abstract}/spec/` 目录
- requirement.md (需求文档总览 - **入口文件**)
- scenarios/*.md (BDD场景 - WHEN-THEN格式)
- data-models.md (数据模型定义)
- business-rules.md (业务规则和约束)
- glossary.md (术语表)

---

#### 第2-7步：自动执行（后续步骤自动执行，无需用户干预）

规范确认后，后续步骤将**自动执行**：

**第2步：测试设计** (自动，与第3步并行)
- 从规范中提取TEST-VERIFY和Mock数据
- 生成测试规范、测试数据和框架代码
- 输出：`orch-spec/{requirement_desc_abstract}/tests/` (test-spec.md + fixtures.json + test-*.template)

**第3步：代码设计** (自动，与第2步并行)
- 读取规范文档，分配code-architect分析项目
- 生成设计方案：`orch-spec/{requirement_desc_abstract}/design/design.md`

**第3.5步：接口契约** (自动，fullstack强制)
- 定义接口契约并进行五维度审查
- 输出：`orch-spec/{requirement_desc_abstract}/contract/`

**第4步：任务列表** (自动)
- 基于设计方案自动分解任务
- 生成任务清单：`orch-spec/{requirement_desc_abstract}/tasks/tasks.md`

**第5步：代码执行** (自动)
- 为每个Task分配子代理并行实现
- **v2.3.1+**：为每个Task创建独立git-worktree，隔离工作环境
  - 编码和修复都在worktree中进行
  - 修复失败可删除worktree重新开始
  - worktree commit历史清晰记录修复过程
  - 支持cherry-pick或squash merge两种提交方案
- 进行多阶段审查（规范审查 + 质量审查）
- TDD流程：RED-GREEN-REFACTOR-REVIEW
- 生成执行报告：`orch-spec/{requirement_desc_abstract}/execution/execution-report.md`
- 输出源代码到 `src/` 目录

**第5.5步：异常处理** (自动，后端/全栈)
- 扫描项目约定发现异常处理模式
- 自动识别异常场景并生成异常处理代码
- 零硬编码：所有约定通过扫描动态发现

**第6步：测试验证** (自动)
- 进行代码质量审查和高层测试（集成/E2E/性能）
- 生成测试报告和闭环验证矩阵
- 生成测试报告：`orch-spec/{requirement_desc_abstract}/testing/testing-report.md`
- 输出测试代码到 `tests/` 目录

**第7步：规范归档** (自动)
- 当所有测试通过后，自动触发规范归档流程
- 分配archiver进行对标分析和智能合并
- 将需求规范通过场景拆分集成到主规范库
- 生成归档报告：`orch-spec/spec/archive-log.md`
- 更新主规范：`orch-spec/spec/` (data-models、business-rules、glossary等)

---

#### 整个工作流耗时估算

| 阶段 | 输入 | 输出 | 耗时 |
|------|------|------|------|
| Spec | 需求描述 | spec/ | 用户交互 |
| Design | spec/ | design.md | 自动执行 |
| Task | design.md | tasks.md | 自动执行 |
| Execute | tasks.md | src/ + 执行报告 | 自动执行 |
| Test | tasks.md | tests/ + 测试报告 | 自动执行 |
| Archive | spec/ | orch-spec/spec/ + 归档报告 | 自动执行 |

总体耗时：规范化阶段取决于用户交互，后续全流程自动执行（通常2-5分钟）

---

## 📖 完整文档

- [安装说明](./docs/INSTALLATION.md) - 详细的安装步骤和故障排查
- [使用指南](./docs/USAGE.md) - 详细的使用方式和常见场景
- [最佳实践](./docs/BEST_PRACTICES.md) - 全栈SDD最佳实践和检查清单
- [使用指南](./docs/USAGE.md) - 详细使用场景和步骤
- [安装指南](./docs/INSTALLATION.md) - 安装和故障排查

---

## 💡 使用示例

### 场景1：React项目 - 新增订单表单

```bash
# 0. 进入插件
/orch:sdd-dev
# 输入需求：需要在订单管理系统中新增订单表单，支持搜索、排序、分页、批量操作

# 1. 分析需求并生成规范文档
/spec
# 输出：orch-spec/order-form/spec/ (requirement.md, scenarios/*.md, data-models.md等)

# 2. 根据规范进行架构设计
/design 需要新增订单表单
# 输出：orch-spec/order-form/design/design.md

# 3. 将设计分解为具体任务
/task orch-spec/order-form/design/design.md
# 输出：orch-spec/order-form/tasks/tasks.md

# 4. 执行代码实现（带两阶段审查）
/execute orch-spec/order-form/tasks/tasks.md
# 输出：src/... + orch-spec/order-form/execution/execution-report.md

# 5. 测试验证和闭环检查
/test orch-spec/order-form/tasks/tasks.md
# 输出：tests/... + orch-spec/order-form/testing/testing-report.md
```

### 场景2：Vue项目 - 新增仪表板组件

```bash
# 0. 进入插件
/orch:sdd-dev
# 输入需求：需要创建数据仪表板，支持实时数据、多图表展示、自定义面板

# 1. 分析需求并生成规范文档
/spec
# 输出：orch-spec/dashboard/spec/ (requirement.md, scenarios/*.md等)

# 2. 根据规范进行架构设计
/design 需要创建数据仪表板
# 输出：orch-spec/dashboard/design/design.md

# 3. 将设计分解为具体任务
/task orch-spec/dashboard/design/design.md
# 输出：orch-spec/dashboard/tasks/tasks.md

# 4. 执行代码实现
/execute orch-spec/dashboard/tasks/tasks.md
# 输出：src/... + orch-spec/dashboard/execution/execution-report.md

# 5. 测试验证和闭环检查
/test orch-spec/dashboard/tasks/tasks.md
# 输出：tests/... + orch-spec/dashboard/testing/testing-report.md
```

---

## 🎯 工作流程图

```
┌──────────────────────────────────────────────────────────┐
│  Step 0: /orch:sdd-dev 进入插件               │
│  - 根据提示输入需求内容                                  │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 1: /spec 需求分析和规范生成              │
│  - 分析需求和初步拆解                                    │
│  - 场景细化和多轮确认                                    │
│  - 输出：orch-spec/{name}/spec/                          │
│    (requirement.md, scenarios/*.md, data-models.md等)   │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 2: /design 架构和技术设计                  │
│  - 分配code-architect分析项目模式                       │
│  - 进行架构设计和技术方案规划                             │
│  - 输出：orch-spec/{name}/design/design.md              │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 3: /task 任务分解和定义                       │
│  - 将设计方案分解为编码任务                               │
│  - 定义每个Task的目标、交付物、验收标准                   │
│  - 输出：orch-spec/{name}/tasks/tasks.md                 │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  🔍 用户审查和确认                                        │
│  - 审查设计方案和任务列表                                 │
│  - 确认无误后进入Execute阶段                             │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 4: /execute 代码实现和多阶段审查             │
│  - 为每个Task分配code-executor子代理                    │
│  - **v2.3.1+**：创建git-worktree隔离工作环境           │
│    • 编码和修复在worktree中进行                        │
│    • 每次修复作为独立commit便于追踪                     │
│    • 修复完成后cherry-pick/squash merge到main          │
│    • 清理worktree释放资源                              │
│  - 规范审查：验证代码符合design.md                      │
│  - 质量审查：检查代码质量和类型安全                       │
│  - 输出：src/ + execution-report.md                    │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 5: /test 测试和闭环验证                       │
│  - 代码质量审查（Lint、TypeScript strict check）        │
│  - 设计和执行单元、集成、E2E测试                         │
│  - 闭环验证（Task-代码-测试对应）                        │
│  - 输出：tests/ + testing-report.md                    │
└────────────────┬─────────────────────────────────────────┘
                 │
      ✅ 所有测试通过，自动触发
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  Step 6: /archive 规范归档和优化                    │
│  - 分配archiver进行规范对标分析                    │
│  - 通过场景拆分和智能合并集成到主规范                     │
│  - 冲突检测和决策处理                                    │
│  - 输出：orch-spec/spec/ + archive-report.md            │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│  ✅ 完全完成！                                            │
│  - 代码质量达标，可以上线                                │
│  - 规范已沉淀到企业级规范库                               │
│  - 可用于后续需求的参考和对标                             │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 核心原则

### ✅ 必须做
- 第0步：使用 `/orch:sdd-dev` 进入插件输入需求
- 第1步：运行spec进行需求分析和规范生成
- 第2步：在design阶段分配code-architect进行架构设计
- 第3步：在task阶段进行任务分解和定义
- 第4步：遵循任务清单严格执行execute，完成规范+质量两阶段审查
- 第5步：进行完整的测试验证和闭环检查
- 第6步：测试通过后自动执行archive，将规范沉淀到企业级规范库

### ❌ 不能做
- 跳过第0步直接调用各个Skill（应该通过插件入口）
- 跳过设计和任务定义阶段直接进行编码
- 在execute中跳过规范或质量审查
- 修改生成的源代码逻辑来让测试通过
- 忽视Task和代码之间的一致性
- 跳过test阶段的闭环验证
- 跳过规范归档流程，导致规范库无法完善和沉淀

---

## 🤝 如何定制工作流

Skill可能和项目存在上下文、背景、依赖的绑定，所以，这套skill可能不是很适配你的场景。

### 调整设计和规范

修改以下Skill的SKILL.md文件，让其适应你的项目需求：

1. **spec** - 定义项目的设计模式和参考组件收集方式
2. **design** - 调整设计分析的维度和深度
3. **task** - 调整任务分解的粒度和验收标准

### 调整执行和审查

修改execute中的提示词文件：

- `implementer-prompt.md` - 调整代码实现的风格和要求
- `spec-reviewer-prompt.md` - 调整规范审查的维度
- `code-quality-reviewer-prompt.md` - 调整代码质量标准

### 调整测试策略

修改test的SKILL.md文件：

- 调整测试框架和工具
- 调整测试覆盖率要求
- 调整闭环验证的标准

---

## 📝 更新日志

### v2.3.1 (2026-03-23) Git-Worktrees隔离工作环境
- ✅ **Worktree隔离机制** - 为execute每个Task创建独立git-worktree
- ✅ **安全修复循环** - 修复失败可删除worktree重新开始，不污染main分支
- ✅ **完整修复历史** - worktree commit清晰记录"问题→修复→验证"链条
- ✅ **并行Task支持** - 多Task同时执行无git冲突风险
- ✅ **Worktree指南** - 完整的Worktree工作流指南（git-worktrees-guide.md）
- ✅ **快速参考卡** - quick-reference.md便于日常使用和查询
- ✅ **约束更新** - 新增8条关键约束 + 新增4条危险信号

### v2.3.0 (2026-03-23) ✨ TDD完整实现
- ✅ **TDD实现体系** - 完成Phase 2 TDD实现阶段（RED-GREEN-REFACTOR-REVIEW）
- ✅ **高层测试体系** - 完成Phase 3 集成、E2E、性能测试优化
- ✅ **职责清晰化** - execute处理单元测试，test处理高层测试
- ✅ **高层测试prompt** - 集成、E2E、性能测试专项设计指南
- ✅ **最佳实践更新** - BEST_PRACTICES.md新增Phase 3最佳实践
- ✅ **闭环验证完善** - TEST-VERIFY→Test→Code→Result完整链条

### v2.2.0 (2026-03-20)
- ✅ **规范归档流程** - 新增archive技能和archiver Agent
- ✅ **规范沉淀机制** - 将验证通过的需求规范自动归档到企业级主规范库
- ✅ **场景拆分合并** - 支持通过场景拆分和智能合并策略集成新规范
- ✅ **冲突检测机制** - 自动检测和处理规范冲突，提供决策建议
- ✅ **规范对标分析** - 新增场景、数据模型、业务规则、术语的对标分析
- ✅ **版本管理** - 支持规范版本追踪和演进历史记录

### v2.1.0 (2026-03-10)
- ✅ 全栈开发能力扩展
- ✅ 支持前端、后端、数据库、微服务、移动端等多类型项目
- ✅ 技术栈扩展：Node.js、Python、Go、Java、PostgreSQL、MongoDB等
- ✅ 数据库设计：SQL/NoSQL 数据模型设计和迁移脚本
- ✅ API设计：REST/GraphQL API 规范和验证
- ✅ 微服务支持：服务边界、通信协议、部署方案
- ✅ 多框架测试：Jest、Pytest、JUnit、Cypress、k6等
- ✅ 完整的全栈示例和最佳实践

### v2.0.0 (2026-03-09)
- ✅ 完全重构为 Spec-Design-TestDesign-Task-Execute-Test-Archive 工作流
- ✅ 7个核心Skills：spec、design、test-design、task、execute、test、archive
- ✅ 多阶段审查机制和闭环验证
- ✅ 前端优先支持（React/Vue/Angular/Svelte）
- ✅ 完整的文档和最佳实践指南

### v1.0.0 (2026-02-09)
- 初始版本，包含spec-generator、ai-planning、ai-code-execution、ai-test-creation

---

## 🎓 学习路径

### 新手入门
1. 阅读本 README.md 理解整个工作流
2. 查看 [使用指南](./docs/USAGE.md)
3. 执行 `/orch:sdd-dev` 进入插件
4. 根据提示输入需求内容
5. 逐步执行 spec → design → test-design → task → execute → test → archive
6. 选择一个小功能进行完整流程试运行

### 📚 深入学习
1. 理解 [快速开始](#-快速开始) 中的9个步骤和9个Agents
2. 阅读 [最佳实践](./docs/BEST_PRACTICES.md) 了解每个阶段的最佳做法
3. 阅读 [使用指南](./docs/USAGE.md) 了解详细工作流
4. 学习 [Git-Worktrees指南](./skills/execute/references/git-worktrees-guide.md) 掌握隔离工作环境机制
5. 理解架构设计和工作流内部机制
9. 学习如何 [定制工作流](#如何定制工作流)

### 团队推广
1. 确保团队成员理解SDD工作流的核心原则
2. 为项目编写定制化的设计规范（通过spec）
3. 编写团队的最佳实践和编码风格指南
4. 配置execute和test的审查规则
5. 培训团队成员按照规范使用整个工作流
6. 建立基于spec-design的代码审查流程

---

## 📧 联系方式

- 📖 [文档](./docs/)
- 🐛 [问题反馈](https://github.com/your-org/orch/issues)
- 💬 [讨论交流](https://github.com/your-org/orch/discussions)

---

## 📄 许可证

MIT License - 详见 [LICENSE](./LICENSE)

---

## 🙏 致谢

这个工作流是基于SDD（Spec-Driven Development）原则，结合了：
- Claude Code的AI能力
- 企业级开发的最佳实践
- 前端工程化的经验教训

感谢所有贡献者和用户的支持！

---

**让AI辅助的全栈开发变得规范、高效、可信赖！** 🚀

