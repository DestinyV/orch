---
description: 从 SDD+TDD 规范（orch-spec/）中读取需求，生成实现计划与任务清单。等待用户确认后再开始编码。
argument-hint: "[feature description | path/to/spec-dir | path/to/design.md]"
---

# Plan Command (SDD+TDD 适配版)

根据 SDD+TDD 规范（orch-spec/）创建实现计划。从已有的规范文档或设计文档出发，生成结构化的实施清单。

## 数据来源优先级

| 输入 | 来源 | 行为 |
|------|------|------|
| free-form text | 用户描述 | 搜索 `orch-spec/` 匹配的 spec，若无则参考 `/plan` 流程 |
| path to spec dir | `orch-spec/{req}/spec/` | 读取 requirement.md + scenarios/*.md + data-models.md |
| path to design.md | `orch-spec/{req}/design/design.md` | 从设计方案生成实现计划 |
| path to tasks.md | `orch-spec/{req}/tasks/tasks.md` | 对现有任务清单做分步实施计划 |
| `.prd.md` path | PRD 文件 | PRD artifact 模式：创建 `.claude/plans/{name}.plan.md` |

## 与 SDD+TDD 工作流的集成

```
spec → test-design ⟷ design → contract(fullstack) → task
                                                                             ↓
                                                        /plan 在此创建实施计划
```

`/plan` 适合在以下场景调用：
- `/task` 已执行但需要更细粒度分步计划
- 需要跨多个 Task 的协调实施路线图
- 用户想先确认计划再进入 `/execute`
- 快速模式中跳过 `/task` 后直接手动规划

## 流程

### 1. 读取输入

读取指定文件或目录中的规范/设计内容。关键文件：

| 文件 | 用途 |
|------|------|
| `requirement.md` | 需求总览和背景 |
| `scenarios/*.md` | BDD 场景和 TEST-VERIFY 验收标准 |
| `data-models.md` | 数据模型定义 |
| `design.md` | 架构设计和技术方案 |
| `tasks.md` | 现有任务列表（复用/优化） |

### 2. 模式采集

检查 spec 中的 project-mode (frontend/backend/fullstack)，确定：
- 是否需要 contract（fullstack 强制）
- 是否涉及数据库变更（SQL DDL）
- 是否需要异常处理（backend/fullstack）
- 测试策略（单元 ≥85% + 集成/E2E）

### 3. 创建分步计划

生成包含以下内容的计划：

```
# Plan: {Feature Name}

**Source**: {orch-spec/req path}
**Complexity**: {Small | Medium | Large}

## Summary
{2-3 sentences}

## Implementation Steps

### Step 1: {name}
- **Action**: {具体实现}
- **Source**: {引用的 spec/design 段落}
- **Dependencies**: {前置条件}
- **Validate**: {验证命令}

### Step 2: {name}
...

## Files to Change
| File | Action | Reason |
|------|--------|--------|
| `src/...` | CREATE/UPDATE | {reason} |

## Patterns to Mirror
| Category | Source | Pattern |
|----------|--------|---------|
| Naming | `agents/agent.md` | {convention} |
| Error handling | `src/handlers/` | {pattern} |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|

## Acceptance
- [ ] All steps complete
- [ ] Tests pass (unit ≥85%, integration, E2E)
- [ ] Code review passes (规范审查 + 质量审查)
- [ ] Validation commands pass
```

### 4. 等待确认

**关键约束**：必须等待用户明确确认后再执行任何编码。输出计划后显示：

```
Plan created: .claude/plans/{name}.plan.md

WAITING FOR CONFIRMATION: Proceed with this plan? (yes/no/modify)
```

## 输出位置

- 有 `.prd.md` 输入 → `.claude/plans/{kebab-case-name}.plan.md`
- 纯文本输入 → 内联呈现，不写文件（除非用户要求保存）
- 已有 `tasks.md` → 在 `orch-spec/{req}/` 下创建 `implementation-plan.md`

## 模式采集

实施前搜索项目代码库中应遵循的约定，每个分类记录 1-2 个示例：

| 分类 | 采集 | 参考位置 |
|------|------|---------|
| 命名 | 文件名、函数名、类型名、命令名 | `src/` |
| 错误处理 | 如何抛出、返回、记录、处理失败 | `src/`, `CLAUDE.md` |
| 日志 | 级别、格式、内容 | `src/` |
| 数据访问 | Repository/Service/Query 模式 | `src/` |
| 测试 | 框架、Fixture、断言风格 | `tests/`, `CLAUDE.md` |

无相似代码时明确声明，不编造。
