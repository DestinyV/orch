# 后端 E2E API 测试模板

> code-test 阶段 3.1 后端集成测试中使用此模板验证完整业务流程

## 测试策略

后端 E2E 测试不同于前端浏览器 E2E，它验证完整的后端业务流程：
1. 端到端业务流程：从 API 入口到数据库的完整链路
2. 多服务协作：多个服务/模块间的协作正确性
3. 数据一致性：跨表/跨服务的数据一致性
4. 异步流程：消息队列、定时任务等异步场景

## Node.js + Supertest 模板

```typescript
// tests/e2e/api/{feature}.e2e.test.ts

import request from 'supertest';
import { app } from '../../src/app';
import { db } from '../../src/db';

describe('E2E: {功能名称}', () => {
  beforeEach(async () => {
    // 每个测试前清空数据库
    await db.table('orders').delete();
    await db.table('users').delete();
  });

  afterAll(async () => {
    await db.destroy();
  });

  it('完整业务流程: 用户注册 → 登录 → 创建订单 → 查询订单', async () => {
    // 步骤1: 用户注册
    const registerRes = await request(app)
      .post('/api/v1/auth/register')
      .send({ username: 'testuser', email: 'test@example.com', password: 'Pass123!' });

    expect(registerRes.status).toBe(200);
    const userId = registerRes.body.data.id;

    // 步骤2: 用户登录
    const loginRes = await request(app)
      .post('/api/v1/auth/login')
      .send({ email: 'test@example.com', password: 'Pass123!' });

    expect(loginRes.status).toBe(200);
    const token = loginRes.body.data.token;

    // 步骤3: 创建订单
    const orderRes = await request(app)
      .post('/api/v1/orders')
      .set('Authorization', `Bearer ${token}`)
      .send({
        items: [{ productId: 1, quantity: 2, price: 99.99 }],
        shippingAddress: 'Test Address',
      });

    expect(orderRes.status).toBe(200);
    const orderId = orderRes.body.data.id;
    expect(orderRes.body.data.totalAmount).toBe(199.98);

    // 步骤4: 查询订单
    const getRes = await request(app)
      .get(`/api/v1/orders/${orderId}`)
      .set('Authorization', `Bearer ${token}`);

    expect(getRes.status).toBe(200);
    expect(getRes.body.data.id).toBe(orderId);
    expect(getRes.body.data.items).toHaveLength(1);
    expect(getRes.body.data.status).toBe('pending');
  });

  it('并发操作: 多用户同时创建订单不应该互相影响', async () => {
    const users = await Promise.all([
      createUserAndLogin(app),
      createUserAndLogin(app),
      createUserAndLogin(app),
    ]);

    const orders = await Promise.all(
      users.map(async ({ token }) => {
        return request(app)
          .post('/api/v1/orders')
          .set('Authorization', `Bearer ${token}`)
          .send({ items: [{ productId: 1, quantity: 1, price: 50 }], shippingAddress: 'Test' });
      })
    );

    orders.forEach(res => {
      expect(res.status).toBe(200);
    });

    // 验证每个用户的订单独立
    const userIds = users.map(u => u.userId);
    const orderUserIds = orders.map(r => r.body.data.userId);
    expect(new Set(orderUserIds).size).toBe(3); // 3个不同的用户
  });
});

// 辅助函数
async function createUserAndLogin(app) {
  const username = `user_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  // 注册 + 登录 + 返回 token
  // ...
}
```

## Python + Pytest + httpx 模板

```python
# tests/e2e/api/test_{feature}_e2e.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_{feature}_complete_flow(client: AsyncClient, db_session):
    """验证完整业务流程"""
    # 步骤1: 注册
    resp = await client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Pass123!",
    })
    assert resp.status_code == 200

    # 步骤2: 登录
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "Pass123!",
    })
    assert resp.status_code == 200
    token = resp.json()["data"]["token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 步骤3: 创建资源
    resp = await client.post("/api/v1/{resource}", headers=headers, json={
        "name": "Test Item",
    })
    assert resp.status_code == 200
    resource_id = resp.json()["data"]["id"]

    # 步骤4: 查询资源
    resp = await client.get(f"/api/v1/{resource}/{resource_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == resource_id
    assert resp.json()["data"]["name"] == "Test Item"
```
