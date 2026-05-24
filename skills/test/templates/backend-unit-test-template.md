# 后端单元测试模板

> execute 阶段 TDD 流程中使用。按技术栈选择对应模板。

## 测试策略

| 技术栈 | 测试框架 | Mock库 | 覆盖率工具 |
|--------|---------|--------|-----------|
| Python | pytest | unittest.mock | pytest-cov |
| Go | testing + testify | httptest/gomock | go test -cover |
| Java | JUnit 5 + AssertJ | Mockito | JaCoCo |
| Rust | 内置 #[cfg(test)] | mockall | cargo tarpaulin |

## Python 示例

```python
import pytest
from unittest.mock import patch, MagicMock
from myapp.services import OrderService

class TestOrderService:
    def test_create_order_success(self):
        service = OrderService(repo=MagicMock())
        order = service.create_order(user_id="u1", items=[{"id": "p1", "qty": 2}])
        assert order.status == "pending"
        assert order.user_id == "u1"

    def test_create_order_invalid_quantity(self):
        service = OrderService(repo=MagicMock())
        with pytest.raises(ValueError, match="Quantity must be positive"):
            service.create_order(user_id="u1", items=[{"id": "p1", "qty": 0}])
```

## Go 示例

```go
func TestOrderService_CreateOrder(t *testing.T) {
    repo := &MockOrderRepo{}
    svc := NewOrderService(repo)

    t.Run("success", func(t *testing.T) {
        order, err := svc.CreateOrder("u1", []Item{{ID: "p1", Qty: 2}})
        assert.NoError(t, err)
        assert.Equal(t, "pending", order.Status)
    })

    t.Run("invalid quantity", func(t *testing.T) {
        _, err := svc.CreateOrder("u1", []Item{{ID: "p1", Qty: 0}})
        assert.Error(t, err)
    })
}
```

## Java 示例

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock private OrderRepository repo;
    @InjectMocks private OrderService service;

    @Test
    void createOrder_success() {
        when(repo.save(any())).thenReturn(new Order("pending"));
        Order order = service.createOrder("u1", List.of(new Item("p1", 2)));
        assertThat(order.getStatus()).isEqualTo("pending");
    }

    @Test
    void createOrder_invalidQuantity() {
        assertThatThrownBy(() -> service.createOrder("u1", List.of(new Item("p1", 0))))
            .isInstanceOf(IllegalArgumentException.class);
    }
}
```

## Rust 示例

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use mockall::mock;

    mock! {
        pub OrderRepo {
            fn save(&self, order: Order) -> Result<Order, Error>;
        }
    }

    #[test]
    fn test_create_order_success() {
        let mut repo = MockOrderRepo::new();
        repo.expect_save().returning(|o| Ok(o));
        let svc = OrderService::new(Box::new(repo));
        let order = svc.create_order("u1", vec![Item::new("p1", 2)]).unwrap();
        assert_eq!(order.status, "pending");
    }
}
```

## 通用规则

- 每个测试一个行为 | 断言具体值 | 正常+边界+错误
- Mock 外部依赖，不 Mock 业务逻辑
- 覆盖率 ≥85%（语句/分支/函数）
