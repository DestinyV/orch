# 子代理状态协议与模型选择

> 参考 superpowers:subagent-driven-development 最佳实践

## 子代理状态协议

子代理完成后返回以下状态之一：

| 状态 | 含义 | 控制器处理 |
|------|------|-----------|
| `DONE` | 任务完成，无问题 | 进入下一步 |
| `DONE_WITH_CONCERNS` | 任务完成但有遗留事项 | 审查遗留事项，决定是否修复 |
| `NEEDS_CONTEXT` | 缺少必要上下文 | 补充上下文后重新派遣 |
| `BLOCKED` | 被阻塞（依赖缺失、指令不清） | 分析阻塞原因，决定是否升级 |

### 状态扩展字段（协作协议）

`DONE` 和 `DONE_WITH_CONCERNS` 可附加以下字段：

```yaml
artifacts: [file paths]     # 本 Task 产生的文件清单
provides: [api names]        # 提供给下游的 API/接口
context: { key: value }      # 传递给下游的上下文
failed_phase: RED|GREEN|REFACTOR|REVIEW  # 失败阶段（用于增量恢复 P1.3）
current_artifacts: {...}     # 当前产物快照（增量恢复时传递已完成部分）

# DONE_WITH_CONCERNS 额外
concerns: [description]      # 遗留问题
severity: low|medium|high    # 严重程度

# BLOCKED 额外
blocked_by: [reason]         # 阻塞原因
suggested_action: str        # 建议处理方式
```

## Standard SubagentContext（P4.1 标准化）

所有 Agent 派遣使用以下标准化上下文 JSON 格式（由主代理注入 prompt，非自行读取文件）：

```json
{
  "task": {
    "id": "Task-3",
    "description": "实现 OrderService.placeOrder()",
    "provides": "OrderService",
    "consumes": ["InventoryService"],
    "acceptance_criteria": ["库存不足时返回 OrderError"],
    "covers": {"scenario": "scenarios/order.md", "scene_id": "INSUFFICIENT_STOCK"}
  },
  "context": {
    "relevant_design": "OrderService 调用 InventoryService.check()",
    "relevant_spec": "WHEN 用户下单 AND 库存不足 THEN 返回 OrderError",
    "test_templates": ["tests/test-order.template"],
    "previous_batch_results": ["Task-1: API contract defined"]
  },
  "artifacts": {
    "source_files": [],
    "test_files": [],
    "commit_sha": null
  }
}
```

## 两阶段审查合并

> code-reviewer 已重构为单次综合性审查（规范合规 + 代码质量 + TDD 完整性一并执行）。不再需要两次串行派遣。

## 模型选择策略

| 任务类型 | 模型选择 | 理由 |
|---------|---------|------|
| 机械任务（代码格式化、简单重构） | 廉价模型 | 规则明确，无需深度推理 |
| 集成任务（API 对接、数据层实现） | 标准模型 | 需要理解接口和数据流 |
| 架构任务（设计决策、复杂模块拆分） | 最强模型 | 需要多方案权衡和判断 |
| 审查任务（规范审查、质量审查） | 标准模型 | 需要逐项检查清单 |

## 并行派遣规则

- **批次级并行**：同一批次内无依赖的多个 Task 可同时派遣多个子代理实例
- **禁止同一 Task 多子代理并行**（会导致改动冲突）
- **批次间严格串行**：前一批所有 Task 完成后才能派遣下一批
- **失败传播**：批次内任一 Task 失败，阻塞该批次其余 Task，不继续下一批

## 禁止项

- **禁止跳过规范审查直接执行质量审查**
- **禁止在未解决 concerns 的情况下进入下一个 Task**

## 子代理派遣流程

```
1. 准备上下文（spec、design、tasks）
2. 派遣子代理执行 Task
3. 接收子代理状态报告
4. 检查状态：
   - DONE → 进入下一步
   - DONE_WITH_CONCERNS → 审查并决定是否修复
   - NEEDS_CONTEXT → 补充上下文后重新派遣
   - BLOCKED → 分析原因，必要时人工介入
5. 执行两阶段审查（规范 → 质量）
6. 审查未通过 → 修复循环
7. 审查通过 → 标记 Task 完成
```

## 检查点协议

Task 执行过程中的关键节点使用检查点控制流程：

| 类型 | 触发条件 | 操作 |
|------|---------|------|
| 人工验证 | 涉及关键决策 / 架构变更 | AskUserQuestion 确认后继续 |
| 自动提交 | 编译通过 + 测试通过 | 自动 git commit，继续下一个 Task |
| 阻塞等待 | 依赖外部输入 / 未完成的依赖 | 暂停，记录当前上下文，等待依赖就绪 |
