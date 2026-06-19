---
name: debug
description: |
  Bug 修复辅助技能。通过证据驱动的因果追踪定位根因，适用于 execute 或 test 阶段的失败诊断。
  
  输入：bug 描述 + 相关文件路径
  输出：根因分析 + 修复建议
---

# trace — 因果追踪

## 职责

当测试失败或 Bug 报告出现时，通过多假设竞争式追踪定位根因。

## When to Use

- test 阶段测试失败，需要定位根因
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

### Step 2.5: CodeGraph MCP 辅助追踪（如已安装）

CodeGraph MCP 工具可用时，优先使用以下工具代替手动 grep/Read：

```bash
# 追踪调用链
codegraph_trace "疑似异常方法" "可能根因方法"

# 查找调用者
codegraph_callers "失败方法名" --depth 2

# 了解模块上下文
codegraph_context "异常相关模块的接口和依赖"

# 批量搜索符号
codegraph_search "关键字或模式名"
```

### Step 3: 修复建议

基于收敛的假设，生成最小的修复方案。

## 关键约束

- ❌ 不直接修改代码（仅分析）
- ✅ 每个假设必须有正反证据
- ✅ 输出必须包含具体的验证步骤
- ✅ 修复建议必须经过 debug 验证

## 输出

输出到 `orch-spec/{req_id}/testing/debug-report.md`。


## Constraints

- 不直接修改代码（仅分析）
- 每个假设必须有正反证据
- 输出必须包含具体的验证步骤

<GATE>禁止直接修改代码（仅分析） | 每个假设必须有正反证据</GATE>