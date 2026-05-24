# test-design 详细工作流

## 阶段1: 读取和分析需求

读取 `spec-dev/{req}/spec/` 目录，提取 TEST-VERIFY 验收标准和 Mock Data。分析每个场景的 WHEN/THEN 条件、数据模型、业务规则。

## 阶段2: 测试用例设计

**TEST-VERIFY → Test Case 转换规则**：
1. 每个 TEST-VERIFY 分解为 1-N 个 Test Case（正常路径至少1个，边界/错误各至少1个）
2. TC-ID 格式：`TC-{TV序号}-{场景序号}-{变体序号}`
3. 每个 TC 必须可隔离、可断言、可复现

**测试分层**：
| 层级 | 目标 | Mock 策略 |
|------|------|----------|
| 单元 | 单函数/方法 | Mock 所有外部依赖 |
| 集成 | 多模块协作 | Mock 第三方服务 |
| E2E | 完整用户流程 | Mock 不稳定外部API |

## 阶段3: 测试数据设计

从 WHEN 条件提取有效/边界/无效值。fixtures.json 结构：`{id, type, scenario, data{valid/boundary/invalid}, mock{api/db}}`。

## 阶段4: 生成测试规范

输出 test-spec-creation.md：TC 表格 | Mock 策略 | Fixture 引用 | 覆盖率分析。
输出 fixtures.json：测试数据 + Mock 定义。
输出 test-*.template：测试骨架代码。

## 关键原则

- **100% TEST-VERIFY 覆盖**：每个 WHEN-THEN 至少对应 1 个 TC
- **Mock 最小化**：只 Mock 外部依赖（API/DB/第三方），不 Mock 内部业务逻辑
- **数据独立**：每个 TC 使用独立 fixture，互不影响
- **命名规范**：TC-ID 与 TEST-VERIFY 可双向追溯
