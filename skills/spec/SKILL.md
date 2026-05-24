---
name: spec
description: |
  需求分析和规范生成（Spec阶段）

  输入：需求描述
  输出：orch-spec/{requirement_desc_abstract}/spec/ 目录

  功能：接收需求内容，通过交互式分析进行多次确认，输出BDD格式的规范文档（WHEN-THEN格式）。
  支持全栈开发（前端、后端、移动端、全栈应用）的需求规范化。

  输出内容：
  - requirement.md (需求文档总览)
  - scenarios/*.md (BDD场景 - WHEN-THEN格式 + TEST-VERIFY验收标准 + BROWSER-TESTABLE浏览器可执行断言)
  - data-models.md (数据模型定义)
  - business-rules.md (业务规则和约束)
  - glossary.md (术语表)
  - infrastructure.md (后端/全栈：基础设施和依赖)
  - deployment.md (后端/全栈：上线和回滚方案)
  - backend-monitoring.md (后端/全栈：监控和可观测性)
  - security.md (可选：安全与合规方案)
  - frontend-deployment.md (前端/全栈：构建和部署)
  - frontend-monitoring.md (前端/全栈：前端监控)
  - sql-ddl.md (needs-database=是：DDL+DML可执行脚本)
  - diagrams/ (按需：ER图/场景流程图/决策树)
  - project-context.md (标准模式，位于上级目录 {requirement_desc_abstract}/，供 design 复用)

  输出供 test-design 和 design 并行消费。
---

# spec

## 职责

接收需求，交互式分析拆解为BDD场景，生成规范文档到 `orch-spec/[需求ID]/spec/`。

## 工作流程

### When to Use

- 收到新需求描述
- 需要将模糊需求转化为 BDD 规范文档
- 需要生成 TEST-VERIFY 和 Mock Data

## Output

- `orch-spec/{req_id}/spec/` — 完整规范目录（requirement.md + scenarios/*.md + data-models.md + business-rules.md + glossary.md）

## Phase 0: 苏格拉底澄清检测（前置）

<HARD-GATE>检测到 clarification.md 存在时必须读取；不存在时必须检测需求模糊度决定是否派遣 clarify。</HARD-GATE>

在进入标准流程前，先检测是否已有苏格拉底澄清结果：

1. 检查 `orch-spec/{req_id}/spec/clarification.md` 是否存在
2. **存在** → 读取澄清报告，直接进入 Phase 1（跳过需求理解问卷，从澄清报告提取目标/约束/验收标准）
3. **不存在** → 评估需求描述模糊度：
   - 需求描述包含具体文件路径、函数名、验收标准 → 模糊度低，直接进入 Phase 1
   - 需求描述模糊/开放/不确定 → 模糊度高，建议用户先运行 clarify
4. 在 `requirement.md` 头部写入澄清状态：

```yaml
## 澄清状态: [socratic_done | skipped | not_needed]
## 最终模糊度: {score}%
## 实体稳定性: {ratio}%
```

### 工作模式

开始前确认模式。**标准模式**为默认；仅用户明确要求时用**快速模式**。

| 标签 | standard | quick |
|------|----------|-------|
| 流程 | spec→design→task→execute→test | spec→execute(精简)→test(精简) |
| TDD | 必须 | 可跳过 |
| 子代理 | 必须使用 | 可选 |
| 审查 | 两阶段 | 单阶段 |
| 测试 | 单元+E2E+视觉+组件+性能 | 单元+E2E |

<HARD-GATE>快速模式仅在用户明确要求时启用（如"快速模式"、"跳过设计"、"快速修复"）。不确定时用标准模式。</HARD-GATE>

### 模式确认输出

在 `requirement.md` 中必须标注：
```
## 工作模式: [standard|quick] | TDD: [必须|跳过] | 子代理: [必须|可选] | 测试: [≥85%|≥60%|跳过]
## 全栈模式: [fullstack|frontend-only|backend-only] | 数据库: [是|否] | SQL方言: [mysql|pg|sqlite|未确定]
## 接口契约: [是|否] | 多项目: [是|否] | 设计图: [按需|全部|跳过]
```

### 需求理解

- 读取需求（描述或文档），识别核心功能点和场景
- **模式自动检测**：根据需求文本推断 project-mode（该逻辑由 workflow 统一处理，若直接调用 spec 则自主执行）：

| 需求特征 | 推断模式 |
|---------|---------|
| 涉及 UI/页面/组件/交互 | frontend 或 fullstack |
| 涉及 API/数据库/服务/存储 | backend 或 fullstack |
| 同时涉及 UI + 后端 | fullstack（强制 contract + exception） |

- 用 AskUserQuestion 与用户确认推断结果（模式/数据库需求/SQL方言/快速或标准），结果写入 requirement.md 的「模式标签」。

- **项目探索**（标准模式必须，三路并行，失败不阻塞）：
  1. 文档探索 → `Agent(subagent_type="orch:code-explorer", prompt="扫描 CLAUDE.md/README.md/docs/ 提取架构约定和项目文档摘要。工具优先：使用 Skill('orch:scripts') 进行文件定位和关键词提取", run_in_background=true)`
  2. 历史需求探索 → general-purpose subagent 扫描 orch-spec/ 最近3-5个需求
  3. 代码模式探索 → `Agent(subagent_type="orch:code-explorer", prompt="扫描 src/ 提取架构约定和代码模式。工具优先：使用 Skill('orch:scripts') 进行批量检索", run_in_background=true)`
  - 小型项目(<200文件)保持串行
  - 两路 code-explorer 可并行派遣（`run_in_background=true`）
  - 探索过程使用 scripts 工具优先策略：搜索→Grep，批量过滤→Python3，兜底→Read

**探索结果输出**：标准模式将三路探索结果写入 `orch-spec/{req_id}/project-context.md`，供下游 design 直接读取，避免重复扫描。

**数据库需求判定**（当需求涉及数据持久化时）：
```
## 数据库设计需求
- 需要数据库设计：[是 | 否]
- 判定依据：
  - [ ] 新增数据表/集合：[列出]
  - [ ] 修改现有表结构：[列出]
  - [ ] 新增/修改索引：[列出]
  - [ ] 数据迁移需求：[列出]
  - [ ] 纯展示层调整（无表结构变更）
```
- SQL方言确认（needs-database时）：使用 AskUserQuestion 确认（mysql/postgresql/sqlite/sqlserver/未确定）
- 多项目协作检测（可选）

### 需求深度追问

场景拆解前对需求进行结构化追问，确保需求**澄清**（无歧义）且**闭环**（可验证满意）。

<HARD-GATE>维度 1-4 必问且必须标记「已澄清」后，才能进入阶段2。</HARD-GATE>

| 维度 | 追问要点 | 闭环验证 |
|------|---------|---------|
| 1. 用户与干系人 | 谁使用？谁审批？多角色权限？ | 干系人确认名单 |
| 2. 核心意图 | 用户目标是什么？当前怎么做的？新问题还是改进？ | 意图与方案一致性校验 |
| 3. 成功标准 | 如何判断"做对了"？关键指标？最小可接受标准？ | 可衡量指标定义 |
| 4. 范围边界 | OUT of scope 明确？第一版vs后续？与现有功能关系？ | 范围文档签字确认 |
| 5. 数据与规模 | 涉及实体？数据量级？保留周期？合规要求？ | 数据模型可支撑 |
| 6. 技术约束 | 栈限制？兼容性？外部API依赖？ | 技术可行性确认 |
| 7. 非功能性 | 性能/安全/可访问性/国际化？ | NFR 可测试验证 |
| 8. 时间与优先级 | 交付时间？优先级排序？外部里程碑？ | 排期可行性确认 |
| 9. 异常与边界 | 最易出错环节？系统不可用时的降级？极端输入？ | 异常场景已识别 |
| 10. 闭环验证 | 谁验证效果？不达预期是回滚还是迭代？需A/B或灰度？需培训文档？ | 上线后验证计划 |

每个维度追问后标注状态：`[已澄清] / [待确认] / [N/A]`，结果写入 requirement.md「确认记录」章节。

详见 `references/deep-dive-questions.md`（每维度 3-5 个具体追问 + 反例）。

### 场景拆解

按 8 个维度系统拆解为 BDD 场景，确保**覆盖全面**。

<HARD-GATE>每个场景至少包含 1 个异常 Case + 场景间依赖已声明且无环（DAG）。</HARD-GATE>

| 维度 | 拆解方法 | 最低覆盖 |
|------|---------|---------|
| 1. 角色/用户类型 | 识别所有角色，为每个角色创建独立场景 | 每个角色 ≥1 场景 |
| 2. 业务流程 | 主流程(Happy Path) + 替代(Alternative) + 中断(Interrupt) + 重试(Retry) | 主+替代必覆盖 |
| 3. 数据状态 | CRUD 生命周期 + 状态流转 + 状态边界 + 空数据 | 每实体完整CRUD |
| 4. 异常与边界 | 输入校验/权限不足/资源不存在/并发冲突/外部失败/数据边界 | 每场景 ≥1 异常 Case |
| 5. 权限边界 | 角色A可X，角色B不可X；资源归属隔离；Feature Flag | 横向越权必覆盖 |
| 6. 时空条件 | 时区/过期/定时/离线弱网 | 按需覆盖 |
| 7. 前后端交互 | Loading/Empty/Error/Success/Partial 5状态 | 前端场景全部覆盖 |
| 8. 数据一致性 | 跨服务事务/异步处理/缓存一致性 | 按需覆盖 |

每个场景聚焦单一行为，头部声明依赖：
```
**场景间依赖**：
- depends-on: [依赖场景ID]
- provides-to: [被依赖场景ID]
```

场景模板见 `templates/spec-scenario-template.md`（含 BROWSER-TESTABLE/异常Case/验证清单）。

详见 `references/scenario-decomposition-guide.md`（8 维度拆解方法论 + 依赖图规范 + 检查清单）。

### 可视化确认（按需）

<HARD-GATE>设计图=全部 或 按需触发阈值达标时，生成对应图供用户确认。快速模式跳过。</HARD-GATE>

读取 `requirement.md` 中的「设计图」标签，按 `references/diagram-trigger-rules.md`（引用自 design）判断触发条件：

| 图类型 | 触发条件 | 确认对象 |
|--------|---------|---------|
| ER 图 | 数据实体 ≥3 个 | 数据模型关系是否正确 |
| 场景流程图 | 场景 ≥5 或 单场景 Case ≥4 | 流程是否有遗漏路径 |
| 业务规则决策树 | 规则 ≥5 条 或 嵌套 IF-THEN | 规则逻辑是否互斥 |

模板见 `templates/diagrams/` 目录，输出到 `orch-spec/{req_id}/spec/diagrams/`。

### 方案对比（复杂需求）

存在多种实现路径时，提出2-3种方案，列trade-offs，与用户确认后进入细化。

### TDD 测试标准定义（standard 模式必须）

<HARD-GATE>standard 模式下，每个场景的每个 Case 必须定义 TEST-VERIFY 和 Mock Data，否则不进入下一阶段。</HARD-GATE>

每个 Case 后紧跟：
```
### TEST-VERIFY（可测试的验收标准）
- [ ] 应该[动作]，[期望结果]

### Mock Data
**有效输入**：{ JSON }  **边界值**：...  **特殊值**：...
```

详见 `references/test-verify-template.md`（TEST-VERIFY/Mock Data 格式要求 + 基础/表单/API/数据库四种场景模板 + TDD完整链路图 + 质量审查清单）。

### 规范细化

按8个维度组细化，每个维度组对应一个文件：

| 维度组 | 输出文件 | 检查项 |
|--------|---------|-------|
| 功能 | scenarios/*.md | 场景覆盖、交互流程 |
| 数据 | data-models.md | 模型一致性、字段对应 |
| 规则 | business-rules.md | 约束边界、异常场景 |
| 基础设施 | infrastructure.md | 服务上下游、中间件 |
| 部署 | deployment.md | 上线、回滚、灰度 |
| 监控 | backend-monitoring.md + frontend-monitoring.md | 后端+前端监控 |
| 安全 | security.md | 认证、加密、合规(可选) |
| 测试性 | scenarios/*.md 中 BROWSER-TESTABLE | 可测试性声明 |

### 生成文档

输出结构：
```
orch-spec/[需求ID]/
├── spec/
│   ├── requirement.md              # 入口文件+导航
│   ├── scenarios/*.md              # BDD场景(功能名命名)
│   ├── data-models.md              # 数据模型
│   ├── business-rules.md           # 业务规则
│   ├── glossary.md                 # 术语表
│   ├── infrastructure.md           # [后端/全栈]基础设施
│   ├── deployment.md               # [后端/全栈]部署方案
│   ├── backend-monitoring.md       # [后端/全栈]后端监控
│   ├── security.md                 # [可选]安全与合规
│   ├── frontend-deployment.md      # [前端/全栈]前端部署
│   ├── frontend-monitoring.md      # [前端/全栈]前端监控
│   ├── sql-ddl.md                  # [needs-database=是]SQL脚本
│   └── diagrams/                   # [按需]ER图/流程图/决策树
└── project-context.md              # [标准模式]架构探索结果，供 design 复用
```

模板见 `templates/` 目录。

### 规范自审查

交付前检查：占位符扫描 → 内部一致性(字段/规则/依赖对应) → 范围聚焦 → 歧义检查 → 完整性 → SQL一致性 → 多项目一致性 → 项目约定对齐。

**TEST-VERIFY 质量审查**（standard 模式）：详见 `references/test-verify-template.md` 审查清单。

### 交付确认

<HARD-GATE>前端/全栈场景中，未为每个UI交互定义BROWSER-TESTABLE验收标准前，不生成最终规范。</HARD-GATE>

**交付清单**：requirement.md ✓ | 全部scenarios ✓ | data-models ✓ | business-rules ✓ | glossary ✓ | [后端]infrastructure+deployment+monitoring ✓ | [前端]frontend-deployment+monitoring ✓ | [可选]security ✓ | [DB]sql-ddl ✓ | [按需]diagrams ✓ | [标准模式]project-context.md ✓ | 无遗漏矛盾 ✓

## 关键约束

- 所有场景必须使用WHEN-THEN格式 | 至少3轮确认 | 输出到 `orch-spec/[需求ID]/spec/`

## 参考文档速查

### 分析和格式
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `references/bdd-format.md` | BDD WHEN-THEN 格式要求和示例 | 阶段2-3 |
| `references/deep-dive-questions.md` | 需求深度追问 10 维度框架 + 反例 + 闭环验证 | 阶段1.5 |
| `references/scenario-decomposition-guide.md` | 场景拆解 8 维度方法论 + 依赖图 + 检查清单 | 阶段2 |
| `references/quality-checklist.md` | 规范自审查检查清单 | 阶段4.5 |
| `references/test-verify-template.md` | TEST-VERIFY/Mock Data 格式 + 四种场景模板 + 质量审查清单 | 阶段2.75/4.5 |
| `references/project-convention-discovery.md` | code-explorer Agent 项目约定扫描流程 | 阶段1 |

### 模板
| 模板 | 输出文件 | 阶段 |
|------|---------|------|
| `templates/spec-requirement-template.md` | requirement.md | 阶段4 |
| `templates/spec-scenario-template.md` | scenarios/*.md | 阶段2-4 |
| `templates/spec-data-models-template.md` | data-models.md | 阶段3-4 |
| `templates/spec-business-rules-template.md` | business-rules.md | 阶段3-4 |
| `templates/spec-glossary-template.md` | glossary.md | 阶段4 |
| `templates/spec-infrastructure-template.md` | infrastructure.md（后端/全栈） | 阶段4 |
| `templates/spec-deployment-template.md` | deployment.md（后端/全栈） | 阶段4 |
| `templates/spec-backend-monitoring-template.md` | backend-monitoring.md（后端/全栈） | 阶段4 |
| `templates/spec-security-template.md` | security.md（可选） | 阶段4 |
| `templates/spec-frontend-deployment-template.md` | frontend-deployment.md（前端/全栈） | 阶段4 |
| `templates/spec-frontend-monitoring-template.md` | frontend-monitoring.md（前端/全栈） | 阶段4 |
| `templates/spec-sql-ddl-template.md` | sql-ddl.md（needs-database=是） | 阶段4 |
| `templates/spec-multi-project-template.md` | 多项目协作配置 | 阶段1 |

### 设计图模板
| 模板 | 输出文件 | 阶段 |
|------|---------|------|
| `templates/diagrams/er-diagram.md` | ER 图（实体关系） | 阶段2.5 |
| `templates/diagrams/flow-diagram.md` | 场景流程图 | 阶段2.5 |
| `templates/diagrams/decision-tree.md` | 业务规则决策树 | 阶段2.5 |
