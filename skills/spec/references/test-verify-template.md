# TEST-VERIFY 定义指南

在规范阶段将需求转化为可测试的验收标准。

## 理论基础

- **验收测试驱动开发（ATDD）**：在编码前定义验收标准，形成开发目标——先定义"什么叫完成"，再开始实现
- **测试金字塔原则**：验收标准应能转化为不同层级的测试（单元→集成→E2E），而非仅支持手动验证
- **可测试性设计（Design for Testability）**：系统行为必须可被外部观察，而非仅依赖内部状态检查
- **Mock 隔离原则**：测试应隔离外部依赖（API/DB/第三方），每个 TEST-VERIFY 关联明确的 Mock 数据

## 基础结构

每个场景 Case 后紧跟 TEST-VERIFY 和 Mock Data：

```markdown
### TEST-VERIFY
标识符: TV-{序号}: {简短描述}
**WHEN** [触发条件] **THEN** [可观察的预期结果]

### Mock Data
**有效输入** | **边界值** | **特殊值** | **依赖Mock**
```

## 设计原则

| 原则 | 含义 |
|------|------|
| 可测试 | 每个 WHEN-THEN 能转化为具体断言，非主观判断 |
| 可隔离 | 每个 test case 独立执行，不依赖其他 test case 的顺序 |
| 可断言 | 预期结果明确，可判断通过/失败——无"大概"、"应该" |
| 可追踪 | TEST-VERIFY ID 贯穿 test-design → execute → test 全链路 |

## Mock 数据命名约定

- 有效数据：`fixtures/{场景}-valid.json`
- 边界数据：`fixtures/{场景}-boundary.json`
- 无效数据：`fixtures/{场景}-invalid.json`

## 覆盖要求

- 每个场景 Case 至少 1 个 TEST-VERIFY
- 覆盖正常输入 + 边界值 + 无效输入三类
- Mock 数据与 TEST-VERIFY 一一对应
