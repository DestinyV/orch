---
name: task
description: |
  任务列表生成（Task阶段）

  输入：orch-spec/{requirement_desc_abstract}/design/design.md
  输出：orch-spec/{requirement_desc_abstract}/tasks/tasks.md

  功能：将设计方案转换为详细的代码级别任务列表，为开发者定义具体的实现任务和交付物。
  支持全栈开发的各类任务拆解（前端、后端、数据库、微服务等）。
---

# task

## 职责

根据设计方案，分解为可独立实现的编码任务，规划并行执行计划。

**输出**：`orch-spec/{requirement_desc_abstract}/tasks/tasks.md`

## 何时使用

前置条件：design 已完成，design.md 已确认。
⚠️ 快速模式时跳过（execute 自主拆解）。

## 工作流程

### 分析设计 + 读取约定

读取 design.md 理解架构，读取 spec/requirement.md 中的项目约定（目录结构、分层、命名、编码规范），确保任务分解与项目现有结构一致。

### 全栈依赖链校验

<HARD-GATE>fullstack+接口契约时验证依赖链：数据库设计→接口契约→前后端任务，接口字段与数据库一致。任一不满足则暂停，回 design。</HARD-GATE>

**数据库设计验证**（needs-database=是时）：
- [ ] design.md 中数据库设计章节已完成且用户已确认
- [ ] sql-ddl.md 已生成（含 DDL+DML+回滚脚本）
- [ ] 每张表有主键、created_at/updated_at
- [ ] 外键级联策略已定义
- [ ] 索引覆盖高频查询场景
- [ ] DDL 语法与声明的 SQL 方言一致

### 多项目任务分组

多项目场景读取 collaboration-plan.md，按项目依赖图分组任务，建立执行顺序和跨项目门控。

### 步骤2-5: 派遣 tasker Agent

<HARD-GATE>standard 模式必须通过 Agent 派遣 tasker 执行任务拆解，不允许主上下文直接拆解。</HARD-GATE>

```bash
Agent(
  subagent_type="orch:tasker",
  prompt="
    将设计方案拆解为编码任务列表：
    - 设计文档: orch-spec/{requirement_desc_abstract}/design/design.md
    - 接口契约: orch-spec/{requirement_desc_abstract}/contract/contract.md（fullstack时）
    - 规范文档: orch-spec/{requirement_desc_abstract}/spec/（提取项目约定和TEST-VERIFY）
    - 测试规范: orch-spec/{requirement_desc_abstract}/tests/test-spec.md（如存在）
    
    执行：
    1. 分析架构和项目约定
    2. 全栈依赖链校验（fullstack时验证数据库→接口契约→任务依赖链）
    3. 分解任务（数据库→接口契约→后端+前端Mock→联调，粒度≤4h）
    4. 定义任务详情（目标/交付物/依赖/provides-consumes/验收标准/估时）
    5. Test Case映射（TEST-VERIFY→TC-ID→Browser Test ID→Mock Data）
    6. 并行执行规划（按依赖分批，判断文件交集/接口依赖/共享状态/任务类型）
    
    模板见 templates/task-template.md 和 templates/tasks-document-template.md
  ",
  run_in_background=false
)
```

### 任务可视化（按需）

Task ≥6 个时生成任务依赖 DAG（拓扑排序批次图）；provides/consumes ≥3 对时生成接口依赖图。

模板见 `templates/diagrams/`，输出到 `orch-spec/{req_id}/tasks/diagrams/`。触发规则见 `../design/references/diagram-trigger-rules.md`。

### 生成文档

基于 tasker 返回结果，输出 `tasks.md`，头部标注模式标签（继承自 requirement.md）。模板见 `templates/tasks-document-template.md`。

## 关键约束

- 任务独立可实现 | 依赖关系准确无环 | 验收标准可验证 | Test Case 100%覆盖 | 无遗留TODO

**TDD 任务排序规则**（standard 模式）：
<HARD-GATE>每实现 Task 必须在同批次配测试 Task。禁止将所有测试 Task 集中到最后批次。</HARD-GATE>
测试 Task 的 `depends_on` 指向同批次实现 Task，确保 RED→GREEN→REFACTOR→REVIEW 在同一批次完成。

- 任务不宜过大(>8h)或过小

## Output

- `tasks/tasks.md` — 任务清单（含 provides/consumes/验收标准）
## 参考文档速查

| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `references/parallel-dispatch.md` | 并行判断标准（文件交集/接口依赖/共享状态/任务类型） | 步骤5 |
| `references/workflow-detail.md` | 完整工作流步骤和估时技巧 | 全部阶段 |
| `templates/task-template.md` | 单个 Task 定义模板（目标/交付物/依赖/验收标准/估时） | 步骤3 |
| `templates/tasks-document-template.md` | tasks.md 完整输出结构 | 步骤6 |
| `templates/test-case-mapping-template.md` | TEST-VERIFY → Test Case 映射表 | 步骤4 |
| `templates/backend-tasks-guide.md` | 后端任务类型和依赖链指南 | 步骤2 |
| `templates/frontend-tasks-guide.md` | 前端任务类型和接口契约依赖指南 | 步骤2 |

### 设计图模板
| 模板 | 输出文件 | 步骤 |
|------|---------|------|
| `templates/diagrams/task-dag.md` | 任务依赖 DAG（拓扑排序批次） | 步骤5.5 |
| `templates/diagrams/provides-consumes.md` | provides/consumes 接口依赖图 | 步骤5.5 |

### 提示词
| 提示词 | 使用场景 | 阶段 |
|---------|---------|------|
| `prompts/implementer-prompt.md` | 代码实现子代理提示词 | 步骤2 |
| `prompts/spec-reviewer-prompt.md` | 规范审查子代理提示词 | 步骤2 |
| `prompts/code-quality-reviewer-prompt.md` | 代码质量审查子代理提示词 | 步骤2 |
