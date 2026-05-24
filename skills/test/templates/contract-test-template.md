# 接口契约测试模板

> 基于 api-contract.md 生成，验证后端实现与接口契约的一致性。

## 测试策略

验证：响应字段完整性 | 字段类型匹配 | 错误码覆盖 | HTTP 状态码正确

## 测试结构

```typescript
describe('API Contract: {endpoint}', () => {
  it('should return all required fields with correct types', async () => {
    const res = await request(app).get('/api/endpoint');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('id');
    expect(typeof res.body.name).toBe('string');
  });

  it('should return defined error codes', async () => {
    const res = await request(app).post('/api/endpoint').send({ invalid: true });
    expect(res.body.errorCode).toBeDefined();
  });
});
```
