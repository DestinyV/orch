# 需求可追溯性矩阵（Requirement Trace Matrix）

确保 spec→design→task→execute 每阶段转换不丢失关键需求信息。

## 追溯链

```
spec/scenarios/*.md  ──── 原始需求（BDD WHEN-THEN + 精确错误码）
     │ covers: 字段（在 task 中引用）
     ▼
tasks.md  ──── 每个 Task 的验收标准引用原始场景 ID
     │ resume_from: 字段（executor 直接读 spec）
     ▼
executor  ──── 实现前读 spec 场景原始文本，不依赖 task 二次翻译
     │ code-review 对比
     ▼
code-reviewer  ──── 实现 vs spec 场景行为偏差检测
```

## covers 字段格式

tasks.md 中每个 Task 的验收标准必须包含：

```yaml
- id: "Task-3"
  description: "实现 OrderService.placeOrder()"
  provides: "OrderService"
  consumes: ["InventoryService"]
  acceptance_criteria:
    - "库存不足时返回 OrderError(INSUFFICIENT_STOCK)"
    - "订单创建成功时返回 OrderConfirmation"
  covers:  # ← 新增：引用原始 spec 场景
    - scenario: "scenarios/order.md"
      scene_id: "INSUFFICIENT_STOCK"
      original_text: "WHEN 用户下单 AND 库存不足 THEN 返回 OrderError(INSUFFICIENT_STOCK)"
    - scenario: "scenarios/order.md"
      scene_id: "ORDER_SUCCESS"
      original_text: "WHEN 用户下单 AND 库存充足 THEN 返回 OrderConfirmation"
```

## 各阶段的追溯动作

### Step 1 (spec) → Step 4 (task)
tasker 在生成 Task 时，每个 Task 的 `covers` 字段必须引用 spec 场景的原始文本。

### Step 4 (task) → Step 5 (execute)
executor 在实现前读取 `covers[].original_text`，不依赖 task 的二次翻译。

```python
# executor 实现前：
for covered_scenario in task.covers:
    print(f"  覆盖场景: {covered_scenario.scene_id}")
    print(f"  原始需求: {covered_scenario.original_text}")
```

### Step 5 (execute) → code-review
code-reviewer 在维度4（需求可追溯性）中：
- 读取每个文件的实现逻辑
- 与 `covers[].original_text` 对比
- 标记偏差（如原始需求要求返回 `OrderError` 但实现返回 `Error`）

## 偏差标记格式

```markdown
### 需求追溯偏差
| spec 场景 | 原始需求 | 实现行为 | 偏差 |
|----------|---------|---------|------|
| INSUFFICIENT_STOCK | 返回 OrderError(INSUFFICIENT_STOCK) | throw Error('out of stock') | ❌ 错误类型不同，错误码丢失 |
| ORDER_SUCCESS | 返回 OrderConfirmation | return { orderId } | ✅ 一致 |
```
