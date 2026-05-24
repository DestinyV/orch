# 单元测试实践

**核心**：测试必须真正验证业务逻辑。

## 禁止

- ❌ 虚假断言如 `expect(true).toBe(true)` | Mock 被测业务逻辑 | 一测多行为

## Mock 策略

只 Mock 外部依赖（API/DB/第三方/时间/随机数），不 Mock 内部业务逻辑/纯函数。

## 结构与要求

Arrange → Act → Assert | 每测一行为 | 正常+边界+错误 | 覆盖率≥85%
