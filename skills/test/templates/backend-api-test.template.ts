# 后端 API 测试模板

> code-test 阶段 3.1.5 API 契约测试使用此模板生成后端 API 测试

## 测试策略

根据项目技术栈选择对应框架：

| 技术栈 | 测试框架 | HTTP 客户端 |
|--------|---------|------------|
| Node.js + Express/Fastify | Jest / Vitest | Supertest |
| Node.js + NestJS | Jest | Supertest |
| Python + Django/FastAPI | Pytest | httpx / requests |
| Java + Spring Boot | JUnit 5 + Mockito | RestAssured |
| Go + Gin/Echo | Go testing + testify | httptest |

## TypeScript/Node.js 模板

```typescript
// backend-api-test.template.ts
// 生成位置: tests/api/{api-name}.test.ts

import request from 'supertest';

describe('API: [端点名称]', () => {
  // ==================== 成功路径 ====================

  describe('成功路径', () => {
    it('应该成功 [操作描述]', async () => {
      const response = await request(app)
        .[method]('[path]')
        .set('Authorization', `Bearer ${validToken}`)
        .send({ /* 来自 api-contract.md 的请求参数 */ })
        .expect(200);

      // 验证响应结构（按 api-contract.md 定义）
      expect(response.body).toMatchObject({
        code: 0,
        data: { /* 必填字段 */ },
        message: 'success',
      });

      // 验证字段类型
      expect(response.body.data).toHaveProperty('id', expect.any(Number));
      expect(response.body.data).toHaveProperty('name', expect.any(String));
    });
  });

  // ==================== 参数校验 ====================

  describe('参数校验', () => {
    it('缺少必填参数时应该返回 400', async () => {
      const response = await request(app)
        .[method]('[path]')
        .send({ /* 缺少必填字段 */ })
        .expect(400);

      expect(response.body).toMatchObject({
        code: expect.any(Number),
        message: expect.any(String),
      });
    });

    it('参数类型错误时应该返回 400', async () => {
      const response = await request(app)
        .[method]('[path]')
        .send({ [field]: 'invalid-type' /* 应为数字却传字符串 */ })
        .expect(400);
    });

    it('参数超出范围时应该返回 400', async () => {
      const response = await request(app)
        .[method]('[path]')
        .send({ [field]: 999999 /* 超出允许范围 */ })
        .expect(400);
    });
  });

  // ==================== 认证与鉴权 ====================

  describe('认证与鉴权', () => {
    it('未提供 Token 时应该返回 401', async () => {
      await request(app).[method]('[path]').expect(401);
    });

    it('提供无效 Token 时应该返回 401', async () => {
      await request(app)
        .[method]('[path]')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);
    });

    it('无权限操作时应该返回 403', async () => {
      await request(app)
        .[method]('[path]')
        .set('Authorization', `Bearer ${userToken}`)
        .expect(403);
    });
  });

  // ==================== 边界情况 ====================

  describe('边界情况', () => {
    it('空列表应该返回空数组', async () => {
      const response = await request(app)
        .[method]('[path]')
        .expect(200);

      expect(response.body.data).toEqual([]);
    });

    it('分页参数边界值', async () => {
      const response = await request(app)
        .[method]('[path]?page=0&pageSize=1')
        .expect(200);
    });

    it('特殊字符处理', async () => {
      const response = await request(app)
        .[method]('[path]')
        .send({ name: '<script>alert("xss")</script>' })
        .expect(200);

      // 验证 XSS 防护
      expect(response.body.data.name).not.toContain('<script>');
    });
  });

  // ==================== 错误处理 ====================

  describe('错误处理', () => {
    it('资源不存在时应该返回 404', async () => {
      await request(app)
        .[method]('[path]/999999')
        .expect(404);
    });

    it('数据库错误时应该返回 500', async () => {
      // Mock 数据库抛出异常
      jest.spyOn(db, 'query').mockRejectedValue(new Error('DB Error'));

      await request(app)
        .[method]('[path]')
        .expect(500);
    });
  });
});
```

## Python 模板

```python
# backend-api-test.template.py
# 生成位置: tests/api/test_{api_name}.py

import pytest
from fastapi.testclient import TestClient  # 或 django 的 Client

def test_[操作描述]_成功(client: TestClient, auth_token: str):
    """验证 [操作] 的成功路径"""
    response = client.[method](
        "[path]",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={ /* 请求参数 */ },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "id" in data["data"]
    assert isinstance(data["data"]["id"], int)

def test_[操作]_参数校验(client: TestClient, auth_token: str):
    """验证缺少必填参数时返回 400"""
    response = client.[method]("[path]", json={})
    assert response.status_code == 400

def test_[操作]_未认证(client: TestClient):
    """验证未提供 Token 时返回 401"""
    response = client.[method]("[path]")
    assert response.status_code == 401
```

## Go 模板

```go
// backend-api-test.template.go
// 生成位置: tests/api/{api_name}_test.go

package api_test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test[OperationName]_Success(t *testing.T) {
	payload, _ := json.Marshal(map[string]interface{}{
		"field1": "value1",
	})

	req := httptest.NewRequest(http.MethodPost, "/api/v1/[path]", bytes.NewBuffer(payload))
	req.Header.Set("Authorization", "Bearer "+validToken)
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var resp map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &resp)
	assert.Equal(t, float64(0), resp["code"])
	assert.NotNil(t, resp["data"])
}

func Test[OperationName]_Unauthenticated(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/api/v1/[path]", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
}
```
