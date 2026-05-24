---
name: design
description: |
  代码设计规划（Design阶段）

  输入：orch-spec/{requirement_desc_abstract}/spec/
  输出：orch-spec/{requirement_desc_abstract}/design/design.md

  功能：根据规范进行架构和技术设计，生成设计方案。
  核心原则：数据库先行 + 接口契约驱动。
---

# design

## 职责

读取 spec 规范，进行架构分析和组件/API/数据库设计，输出 design.md。

**核心原则**：数据库先行 → 接口契约对齐 → 前后端并行开发 → Mock数据驱动

## 何时使用

快速模式时跳过设计阶段（设计决策内联到 scenarios）。

## 工作流程

### 读取标签和策略

读取 spec/requirement.md 的模式标签（standard/quick, fullstack/frontend-only/backend-only, needs-database, needs-contract）。

<HARD-GATE>fullstack+contract 时必须执行接口契约流程；needs-database 时必须先完成数据库设计。</HARD-GATE>

设计顺序：
| 模式 | 数据库 | 顺序 |
|------|--------|------|
| fullstack | 是 | 数据库→接口契约→前后端各自设计 |
| fullstack | 否 | 接口契约→前后端各自设计 |
| frontend-only | - | 前端组件设计 |
| backend-only | 是 | 数据库→后端服务+API |
| backend-only | 否 | 后端服务+API |

### 需求理解

**优先读取**：`orch-spec/{req_id}/project-context.md`（spec 阶段1的探索结果），直接复用，避免重复扫描。

**项目上下文提取**：若 project-context.md 不存在，使用 `Skill("orch:scripts")` 调用 `extract-project-context.py` 从项目根目录提取技术栈/分层/命名约定。

**补充分析**：基于 spec 文档理解需求，派遣 **code-architect** Agent 进行架构蓝图分析。架构分析中的代码库扫描使用 `Skill("orch:scripts")` 工具优先策略（Grep搜索→Python3批量过滤→兜底Read）。

```bash
Agent(
  subagent_type="orch:code-architect",
  prompt="
    对需求进行架构蓝图分析：
    - 规范文档: orch-spec/{requirement_desc_abstract}/spec/
    - 项目上下文: orch-spec/{requirement_desc_abstract}/project-context.md（如存在）
    - 设计图标签: 读取 spec/requirement.md 的「设计图」标签，按 diagram-trigger-rules.md 阈值生成对应 UML 图
    
    执行：
    1. 代码库模式分析（技术栈/模块边界/文件组织/命名约定）
    2. 架构设计（架构模式选择/设计模式推荐/依赖方向）
    3. 完整实现蓝图（文件路径/组件职责/依赖关系/构建序列）
    4. UML 设计图生成：
       - 用途：根据设计图标签和阈值判断生成（类图/时序图/状态图/组件图/部署图/用例图）
       - 语法：Mermaid
       - 模板：templates/diagrams/（use-case.md, class-diagram.md, sequence-diagram.md, state-diagram.md, component-diagram.md, deployment-diagram.md）
       - 输出路径：orch-spec/{requirement_desc_abstract}/design/diagrams/
       - 附加：在每个图中标注与 spec/ 场景的关系
    
    后端/全栈额外：分析服务依赖/数据库方案/日志可观测性/上线回滚
    前端/全栈额外：构建优化/CDN部署/错误追踪/性能监控/用户埋点
  ",
  run_in_background=false
)
```

### 共识式设计审查（standard 模式，新增）

<HARD-GATE>standard 模式必须执行共识审查循环，不允许单次设计直接交付。</HARD-GATE>

在架构设计后执行多视角审查循环：

```bash
Agent(
  subagent_type="orch:code-architect",
  prompt="
    对设计执行架构审查：
    - 设计方案: orch-spec/{requirement_desc_abstract}/design/design.md
    - 规范文档: orch-spec/{requirement_desc_abstract}/spec/

    审查维度：
    1. 架构合理性：所选模式是否适合当前需求规模
    2. 依赖方向：是否符合分层约束
    3. 完整性：是否覆盖所有 spec 场景
    4. 可实施性：设计是否能直接指导编码

    返回：问题清单 + 置信度 + 修复建议。
    标记 REJECT / REVISE / ACCEPT。
  ",
  run_in_background=false
)
```

**循环规则**：
- 架构师审查 → 发现问题 → 修复设计 → 重新审查 → 最多 3 轮
- 全部 ACCEPT 后进入下一步
- 3 轮未通过 → AskUserQuestion（继续/降级/人工介入）

**输出**：在 design.md 中追加 ADR 章节（Architecture Decision Record）：

```markdown
## ADR 记录
| 决策 | 选项 | 选择 | 理由 | 后果 |
|------|------|------|------|------|
| 架构模式 | Layered/Clean/Hexagonal | Clean | 复杂度高需隔离 | 增加初始代码量 |
| 数据库 | MySQL/PostgreSQL | MySQL | 团队熟悉度 | 无特殊扩展需求 |
```

整合：以 code-architect 为主体，project-context.md 补充项目约定。容错：Agent 失败回退主 agent。

**关键澄清点**：前端构建/监控/测试性设计 | 服务上下游 | 数据库 | SQL DDL/DML | 多项目架构 | 设计模式 | 架构风格 | 领域建模 | 组件拆分 | 中间件 | 配置 | 日志 | 上线 | 监控。详见 `references/clarification-points.md`（10 个维度的澄清问题清单）。

### 领域建模（后端/全栈，needs-database=是 且业务逻辑复杂时）

**何时使用**：需求涉及多个业务实体、存在聚合关系、有跨领域操作。

提取实体/值对象/聚合根，划定聚合边界，定义仓储接口。详见 `references/domain-modeling-guide.md`（DDD何时使用、建模步骤、示例）。

### 架构原则应用（后端/全栈，standard 模式）

**何时使用**：确定分层结构、定义模块间依赖方向、选择设计模式。

- 选择架构模式（Clean/Hexagonal/Layered）→ `references/architecture-patterns-guide.md`（架构风格对比表、选择指南）
- 应用设计模式（Factory/Strategy/Observer 等）→ `references/design-patterns-guide.md`（模式决策树、常用模式速查）
- 定义DI点 → `references/architecture-patterns-guide.md` 中的依赖注入章节

### 组件拆分分析（前端/全栈）

**何时使用**：需求涉及 UI 组件、需要确定组件边界和 Props/Events 接口。

按职责拆分组件/服务，设计Props/Events接口。详见 `references/component-extraction-guide.md`（拆分触发器阈值、组件层次、命名规范）。

### 数据库设计（needs-database=是时）

**前置**：SQL 方言确认（若 spec/requirement.md 中未确定，用 AskUserQuestion 确认）。

**执行流程**：
1. SQL 方言对照 → `references/sql-dialect-guide.md`（MySQL/PostgreSQL/SQLite 差异速查）
2. 表结构设计 → `references/database-design-guide.md`（命名约定 | 数据类型 | 约束规则 | 索引规则）
3. 用户确认
4. DDL 生成 → `templates/sql-ddl-template.md`

<HARD-GATE>未完成数据库设计并得到用户确认前，不得进入接口契约和组件设计。</HARD-GATE>

### UML 设计图生成（按需）

<HARD-GATE>设计图=全部 或 按需触发阈值达标时，必须生成对应的 UML 图文件到磁盘；快速模式跳过。生成后校验 diagrams/ 目录文件数是否匹配预期图类型数。</HARD-GATE>

读取「设计图」标签，按 `references/diagram-trigger-rules.md` 判断触发条件：

| 图类型 | 触发条件 |
|--------|---------|
| 用例图 | 场景 ≥5 |
| 类图 | 数据实体 ≥3 |
| 时序图 | ≥2 服务交互 |
| 状态图 | ≥3 状态流转 |
| 组件图 | ≥3 架构分层 |
| 部署图 | fullstack + needs-database |

使用 Mermaid 语法，模板见 `templates/diagrams/`，输出到 `orch-spec/{req_id}/design/diagrams/`。UML 标准参考 `references/uml-diagram-guide.md`。

**生成后校验**：
```bash
# 验证输出文件存在且非空
ls -la orch-spec/{req_id}/design/diagrams/
```
- 匹配预期图类型数，若少于预期需要原因说明
- 每个 .md 文件须包含有效的 Mermaid 代码块
- 图文件须标注与 spec/scenarios 的对应关系

### 多项目协作（requirement.md 中多项目=是时）

读取 requirement.md 多项目章节，构建项目依赖图(DAG)，定义跨项目API契约，生成 collaboration-plan.md。模板见 `templates/collaboration-plan-template.md`。

### 设计系统对齐（frontend/fullstack）

<HARD-GATE>frontend/fullstack 模式必须确定设计系统后才能生成 UI 方案。</HARD-GATE>

在生成前端设计方案前，确定 UI 风格约束：

1. **检测项目根是否存在 `DESIGN.md`**
   - 存在 → 读取设计令牌（colors/typography/spacing），作为 UI 生成约束
   - 不存在 → 检查 `spec/requirement.md` 中是否有「设计偏好」章节

2. **读取设计偏好**（从 spec 或直接询问）：
   - 风格倾向：简洁 / 丰富 / 极简 / 自定义
   - 主色调、字体倾向、布局偏好

3. **生成临时设计令牌**（无 DESIGN.md 时）：
   - 根据风格倾向生成基础颜色/字体/间距令牌
   - 写入 `design/design-tokens.md` 供 UI 生成使用

4. **注入设计方案**：
   - 在 `design.md` 中增加「设计系统」章节
   - 引用设计令牌约束组件样式
   - UI 代码引用令牌而非硬编码值

详见 `references/design-tokens-guide.md`。

### 接口契约对齐（fullstack 且 needs-contract=是时）

**前置**：数据库设计已完成且用户确认。

<HARD-GATE>接口契约未得到双方确认前，不得进入前端组件设计和后端服务设计。</HARD-GATE>

基于数据库设计，定义API接口。参考项目现有API模式：
- 路由命名、HTTP Method、前缀与现有保持一致
- 请求/响应包装格式一致
- 错误码体系一致
- 分页/排序格式一致

输出：接口契约文档 + Mock数据，需前后端双方确认。

### 步骤4-5: 参考分析 + 差异分析

分析参考组件实现，比对需求与参考的差异。新功能默认完全参考现有设计，仅差异处让用户确认。

### 生成设计方案

**前置检查**：
- 后端/全栈：数据库设计✓ | 接口契约✓ | 架构原则✓
- 前端/全栈：组件拆分✓ | 测试性设计✓

<HARD-GATE>前端/全栈场景中，未完成测试性设计（data-testid策略、可测试交互路径）前，不输出最终方案。</HARD-GATE>

输出 design.md，结构：需求分析 → 设计方案（架构/设计模式/分层/组件/数据流） → 参考对比 → 技术方案 → 实现清单 → 决策记录 → 风险。模板见 `templates/design-template.md`。

### 审批与交付

展示 design.md，用户确认/修改后交付。

## 关键约束

- 参考优先：完全参考现有设计，只说明新增
- 完整性：设计足够详细能直接指导编码
- 可验证：每个决策有原因
- 数据库按需执行 | 接口契约驱动 | 禁止无契约独立开发

## Output

- `design/design.md` — 架构设计方案
- `design/diagrams/*.md` — UML 设计图（按需）
- `design/sql-ddl.md` — DDL 脚本（needs-database=是）
## 参考文档速查

| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `references/clarification-points.md` | 需求理解阶段的关键澄清问题 | 阶段1 |
| `references/domain-modeling-guide.md` | 后端/全栈复杂业务的领域建模 | 阶段2.2 |
| `references/architecture-patterns-guide.md` | 架构风格选择 + 依赖注入 | 阶段2.3 |
| `references/design-patterns-guide.md` | 设计模式决策和应用 | 阶段2.3 |
| `references/component-extraction-guide.md` | 前端组件拆分和边界划定 | 阶段2.4 |
| `references/sql-dialect-guide.md` | SQL 方言差异速查 | 阶段2.5 |
| `references/database-design-guide.md` | 表结构设计和命名约定 | 阶段2.5 |
| `templates/design-template.md` | design.md 输出结构 | 阶段6 |
| `templates/sql-ddl-template.md` | DDL 脚本生成 | 阶段2.5 |
| `templates/collaboration-plan-template.md` | 多项目协作计划 | 阶段2.7 |
| `references/design-tokens-guide.md` | 设计令牌指南（颜色/字体/间距/组件样式） | 阶段2.8 |
| `references/architecture-review-checklist.md` | 架构审查检查清单（代码审查Agent使用） | 审查阶段 |
| `references/uml-diagram-guide.md` | UML 2.x 标准 + Mermaid 语法速查 + 6类图模板 | 阶段2.6 |
| `references/diagram-trigger-rules.md` | 各阶段设计图触发阈值和按需策略（全阶段共享） | 阶段2.6 |

### 设计图模板
| 模板 | 输出文件 | 阶段 |
|------|---------|------|
| `templates/diagrams/use-case.md` | 用例图 | 阶段2.6 |
| `templates/diagrams/class-diagram.md` | 类图 | 阶段2.6 |
| `templates/diagrams/sequence-diagram.md` | 时序图 | 阶段2.6 |
| `templates/diagrams/state-diagram.md` | 状态图 | 阶段2.6 |
| `templates/diagrams/component-diagram.md` | 组件图 | 阶段2.6 |
| `templates/diagrams/deployment-diagram.md` | 部署图 | 阶段2.6 |
