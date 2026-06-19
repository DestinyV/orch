---
name: req-change
description: |
  需求变更管理。在规范/设计/编码完成后需求发生变更时，进行影响分析和增量调整。
  输入：变更描述 + 目标需求 ID
  输出：orch-spec/{req_id}/changelogs/change-{ts}.md + 更新后的 spec/design/tasks
---

# req-change — 需求变更管理

## When to Use

- 已创建规范/设计/代码后，需求发生变更
- 用户说"需求变了"、"调整一下"、"追加一个功能"、"这个不要了"
- 代码评审后发现遗漏或偏差

## 职责

分析变更对已有 spec/design/code 的影响，增量更新受影响的文件，标记需要重做的 Task。

## 工作流程

### Phase 0: 前置验证

<GATE>必须先扫描 orch-spec/ 确认目标需求，不允许跳过。</GATE>

1. 扫描 `orch-spec/` 下列出的所有需求目录
2. 读取每个需求的 `.workflow-state.json`，获取状态（done/in_progress/pending）、当前阶段、scenario/Task 数量
3. 用 AskUserQuestion 让用户确认要修改哪个需求：

```json
[{"label": "req-A (done, 阶段9, 3 scenarios, 12 Tasks)", "description": "状态: done"},
 {"label": "req-B (in_progress, 阶段5, 6 scenarios, 26 Tasks)", "description": "状态: in_progress"},
 {"label": "新建需求", "description": "不修改已有需求，直接创建新规范"}]
```

4. 用户选择后锁定目标需求 ID

### Phase 1: 影响分析

读取选中需求的 spec/design/tasks，与变更描述对比：

| 级别 | 特征 | 影响范围 | 策略 |
|------|------|---------|------|
| L1 新增 | 追加新 scenario | spec + design + 新 Task 批次 | 追加，不影响已有 |
| L2 修改 | 修改已有 scenario | spec + design + 标记受影响 Task | 更新 + 标记 needs_rework |
| L3 删除 | 移除已有 scenario | spec + design + 废弃 Task | 标记 obsolete |
| L4 约束 | 改变技术/业务约束 | business-rules + design + 审计全部 Task | 更新 + 全局审计 |

### Phase 2: 增量调整

```
[spec 层]
  ├── L1: 追加 scenario + 更新 data-models/business-rules
  ├── L2: 修改 scenario + 同步 data-models/business-rules
  ├── L3: 标记 scenario 废弃
  └── L4: 更新 business-rules

[design 层]
  ├── L1/L2: 局部更新 design.md 受影响章节
  └── L4: 评审全部架构决策 → 更新 ADR

[tasks 层]
  ├── L1: 追加新 Task 批次
  ├── L2: 标记受影响 Task 为 needs_rework
  └── L3: 标记对应 Task 为 obsolete

[code 层]
  └── 引导用户重新执行受影响 Task（通过 /start-dev 恢复或手动重新派遣）
```

### Phase 3: 变更记录

输出 `orch-spec/{req_id}/changelogs/change-{timestamp}.md`：

```markdown
# 变更记录
- 时间: {ts}
- 级别: L1/L2/L3/L4
- 变更描述: {description}
- 受影响范围:
  - scenarios: [新增N, 修改M, 删除K]
  - tasks: [新增N, needs_rework M, obsolete K]
- 变更后 spec/design/tasks 状态
```

## Output

- `orch-spec/{req_id}/changelogs/change-{ts}.md`
- 更新后的 spec/design/tasks 文件
- 受影响 Task 状态更新

## Constraints

- ✅ 必须先扫描 orch-spec/ 确认目标需求
- ❌ 不直接修改代码（引导用户重新执行 Task）
- ✅ 变更记录必须完整（原值→新值）
- ❌ 不能静默更新（必须展示影响报告）
