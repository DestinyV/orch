# Fixtures JSON 模板

测试数据与 Mock 定义的结构模板。

```json
{
  "fixtures": [
    {
      "id": "fixture_001",
      "name": "正常场景数据",
      "tcIds": ["TC-001-001-001"],
      "data": {
        "input": { "field1": "value1" },
        "expected": { "result": "expectedValue" }
      }
    }
  ],
  "mocks": [
    {
      "id": "mock_001",
      "name": "API 响应 Mock",
      "target": "external",
      "endpoint": "/api/resource",
      "method": "GET",
      "statusCode": 200,
      "response": { "data": [] },
      "delay": 0
    }
  ]
}
```

## 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| fixtures[].id | ✅ | 唯一标识 |
| fixtures[].tcIds | ✅ | 关联的 TC-ID 列表 |
| fixtures[].data.input | ✅ | 测试输入数据 |
| fixtures[].data.expected | ✅ | 期望输出/结果 |
| mocks[].id | ✅ | 唯一标识 |
| mocks[].target | ✅ | external/internal |
| mocks[].endpoint | 外部 | 被 Mock 的 API 路径 |
| mocks[].response | ✅ | Mock 返回内容 |
