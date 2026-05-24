---
name: spec-archive
description: |
  规范归档和优化（Archive阶段）

  输入：spec-dev/{requirement_desc_abstract}/spec/ + spec-dev/spec/（主规范目录）
  输出：spec-dev/spec/（已合并的主规范）

  功能：在测试通过后，将需求的规范文档合并集成到主规范中，建立企业级规范库。
---

# spec-archive

## 职责

将测试通过的需求规范合并到企业级主规范库中。

**核心流程**：分析 → 对标 → 合并去重 → 一致性检查 → 归档报告。
**输出路径**：`spec-dev/spec/`（主规范目录）

## 何时使用

全部测试通过后执行归档。

## 工作流程

### 分析

读取新需求 spec（场景清单、数据模型、业务规则、术语）和主规范（若存在）。文件读取和比对使用 `Skill("orch:script-writer")` 工具优先策略——Grep 定位场景文件、Python3 批量提取 TEST-VERIFY 和术语列表，减少 Read 调用。

### 步骤1.5: 归档前验证 — spec vs code 一致性

<HARD-GATE>归档前必须验证规范与最终实现的一致性。不一致时 spec 必须更新为匹配实现（spec 是实现的文档，实现是最终事实来源）。</HARD-GATE>

```bash
Agent(subagent_type="orch:code-explorer",
      prompt="扫描 spec-dev/{req}/src/ 提取实际实现的接口路由/数据模型/组件结构:
              1) API 路由和响应格式 vs api-contract.md
              2) 数据模型字段 vs data-models.md
              3) 组件目录结构 vs design.md 组件树
              输出差异报告到 spec-dev/{req}/testing/spec-code-diff.md")
```

**不匹配处理**：
| 类型 | 操作 |
|------|------|
| 实现有但 spec 无 | 追加到 spec（实现是最终事实来源） |
| spec 有但实现无 | 标记为 `FINAL_SPEC_DRIFT`，从 spec 移除或标注未实现 |
| 字段/接口结构不一致 | 更新 spec 匹配实现 |

### 步骤2-4: 派遣 spec-archiver Agent 执行合并

<HARD-GATE>必须通过 Agent 派遣 spec-archiver，不允许主上下文直接执行对标和合并。</HARD-GATE>

```bash
Agent(
  subagent_type="orch:spec-archiver",
  prompt="
    对新需求规范进行归档合并：
    - 新需求 spec: spec-dev/{requirement_desc_abstract}/spec/
    - 主规范: spec-dev/spec/（若不存在则创建）
    
    执行以下任务：
    1. 场景对标：逐场景比对，分类为完全新增/部分重叠/完全覆盖/冲突
    2. 合并：场景/数据模型/业务规则/术语各维度统一（相同→去重 | 新增→添加 | 冲突→标记 DECISION_NEEDED）
    3. 一致性检查：输出各维度统计（已有/新增/冲突数）
    
    返回：对标矩阵、合并结果、冲突清单、一致性检查统计
  ",
  run_in_background=false
)
```

**容错**：Agent 失败则回退主 agent，但必须标注 ⚠️ 未完成自动化归档。

### 归档可视化（按需）

存在 DECISION_NEEDED 冲突时生成合并冲突关系图（冲突类型+严重度+影响范围）；主规范存在且本次有新增时生成规范演进时间线。

模板见 `templates/diagrams/`，输出到 `spec-dev/spec/diagrams/`。触发规则见 `../code-design/references/diagram-trigger-rules.md`。

### 生成归档报告

基于 spec-archiver 返回结果，输出到 `spec-dev/spec/archive-log.md`，包含归档内容、合并结果、一致性检查、规范库当前状态。详见 `references/workflow-detail.md`（归档报告模板 + 合并示例）。

### 可选清理

用户多层确认后，备份并删除原需求目录。

## 参考文档速查

| 参考文档 | 使用场景 | 步骤 |
|---------|---------|------|
| `references/workflow-detail.md` | 完整工作流步骤和归档报告模板 | 步骤5 |

### 设计图模板
| 模板 | 输出文件 | 步骤 |
|------|---------|------|
| `templates/diagrams/merge-conflict.md` | 合并冲突关系图 | 步骤4.5 |
| `templates/diagrams/spec-evolution.md` | 规范演进时间线 | 步骤4.5 |

## 归档合并协议

<HARD-GATE>归档不是只写 log，必须实际合并 spec 文件到主规范库。log 仅用于审计，不能替代合并。</HARD-GATE>

1. **场景合并** — 复制 `scenarios/*.md` 到主规范 `spec-dev/spec/scenarios/`。场景ID冲突时追加新Case到末尾（不覆盖），完全重复则跳过。
2. **数据模型合并** — 新增实体/字段追加到 `spec-dev/spec/data-models.md`。
3. **业务规则合并** — 新增规则追加到 `spec-dev/spec/business-rules.md`。规则冲突标注 `DECISION_NEEDED`。
4. **术语合并** — 新术语追加到 `spec-dev/spec/glossary.md`。重复跳过。
5. **标记已归档** — 在原需求 `requirement.md` 追加 `archived: true`。

## Output

- `spec-dev/spec/` — 已合并的主规范库（场景/模型/规则/术语）
- `spec-dev/spec/archive-log.md` — 归档日志（审计用）

## 关键约束

<HARD-GATE>任何冲突不得静默跳过，必须标记为 DECISION_NEEDED 等待人工确认</HARD-GATE>
<HARD-GATE>禁止只输出 archive-log.md 而不实际执行文件合并</HARD-GATE>

✅ 必须：对标比较找重复/新增 | 处理所有冲突 | 一致性检查通过 | 生成归档报告
❌ 禁止：随意删除已有规范 | 跳过重复检查 | 忽视冲突直接覆盖 | 不备份直接修改
