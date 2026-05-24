# Test Case Mapping 模板

关联规范中的 TEST-VERIFY 与任务/测试用例。

## 映射表

```markdown
## Test Case Mapping

| Task ID | Task 名称 | TEST-VERIFY | Test Case ID | 测试类型 | Mock Data |
|---------|----------|------------|-------------|---------|----------|
| T1 | 创建订单 | TV-1, TV-2 | TC-1.1, TC-1.2 | 单元+E2E | fixtures/order-valid.json |
| T2 | 取消订单 | TV-3 | TC-3.1, TC-3.2 | 单元 | fixtures/order-pending.json |
```

## 覆盖率要求

- 每个 TEST-VERIFY 至少对应 1 个 Test Case
- 每个 Task 必须关联至少 1 个 TEST-VERIFY
- Mock Data 来源清晰，文件路径明确

## 映射规则

- **正常路径**：至少 1 个 TC
- **边界值**：至少 1 个 TC
- **错误场景**：至少 1 个 TC
- **双向追溯**：TC → TEST-VERIFY 和 TEST-VERIFY → TC
