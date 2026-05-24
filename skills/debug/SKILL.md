---
name: debug
description: |
  Bug 修复辅助技能。通过证据驱动的因果追踪定位根因，适用于 code-execute 或 code-test 阶段的失败诊断。
  
  输入：bug 描述 + 相关文件路径
  输出：根因分析 + 修复建议
---

# trace — 因果追踪

## 职责

当测试失败或 Bug 报告出现时，通过多假设竞争式追踪定位根因。

## When to Use

- code-test 阶段测试失败，需要定位根因
- Bug 报告需要多假设竞争式因果追踪
- 需要区分症状和根因

## 工作流程

### Step 1: 症状分析

读取 Bug 描述、错误日志、测试输出。识别：
- 可复现条件
- 首次出现时间
- 影响范围

### Step 2: 假设生成

```bash
Agent(
  subagent_type="orch:debug",
  prompt="
    分析以下 Bug 的根因：
    - 症状: {bug_description}
    - 相关文件: {file_paths}
    - 日志: {error_logs}

    执行因果追踪流程并返回报告。
  ",
  run_in_background=false
)
```

### Step 3: 修复建议

基于收敛的假设，生成最小的修复方案。

## 关键约束

- ❌ 不直接修改代码（仅分析）
- ✅ 每个假设必须有正反证据
- ✅ 输出必须包含具体的验证步骤
- ✅ 修复建议必须经过 tracer 验证

## 输出

输出到 `spec-dev/{req_id}/testing/debug-report.md`。


## Constraints

- 不直接修改代码（仅分析）
- 每个假设必须有正反证据
- 输出必须包含具体的验证步骤

<HARD-GATE>禁止直接修改代码（仅分析） | 每个假设必须有正反证据</HARD-GATE>