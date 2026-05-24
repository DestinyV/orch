# 严禁只写注释不实现

> code-execute 阶段铁律，违反即删除重写

## 核心原则

```
注释是对代码的说明，不能替代代码实现本身
```

- ✅ **注释 + 实现** — 注释说明代码做什么，代码真正执行逻辑
- ❌ **只有注释** — 注释不能替代函数体、方法体、组件逻辑

## 禁止的模式

### ❌ 错误示例 1：函数体只有注释

```typescript
// ❌ 错误：只写注释不实现
function processOrder(order: Order): Result {
  // 1. 验证订单数据
  // 2. 计算总金额
  // 3. 扣减库存
  // 4. 创建支付记录
  // 5. 返回结果
  throw new Error('Not implemented');
}
```

```typescript
// ❌ 错误：空函数体 + 注释
function calculateDiscount(price: number, rate: number): number {
  // 计算折扣金额
  // 返回最终价格
}
```

```vue
<!-- ❌ 错误：组件只有注释没有模板和逻辑 -->
<script setup lang="ts">
// 订单列表组件
// Props: orders
// 功能: 展示订单列表，支持搜索和筛选
</script>
```

### ✅ 正确示例

```typescript
// ✅ 正确：注释说明 + 完整实现
function processOrder(order: Order): Result {
  // 1. 验证订单数据
  validateOrder(order);

  // 2. 计算总金额
  const total = calculateTotal(order);

  // 3. 扣减库存
  deductStock(order.items);

  // 4. 创建支付记录
  const payment = createPayment(order, total);

  // 5. 返回结果
  return Result.success(payment);
}
```

### ❌ 错误示例 2：注释掉的代码替代实现

```typescript
// ❌ 错误：用注释掉的代码示意"已实现"
function sendNotification(user: User, message: string) {
  // const response = await fetch('/api/notify', {
  //   method: 'POST',
  //   body: JSON.stringify({ userId: user.id, message })
  // });
  // return response.json();
}
```

### ❌ 错误示例 3：TODO 注释替代实现

```typescript
// ❌ 错误：用 TODO 标记替代实现
function exportReport(data: ReportData): File {
  // TODO: 实现报表导出逻辑
  // TODO: 支持 Excel 和 PDF 格式
  throw new Error('TODO');
}
```

## 检查清单

实现完成后必须逐项检查：

- [ ] 每个函数/方法都有真正的实现代码（不能只有注释）
- [ ] 没有 `throw new Error('Not implemented')` 等占位实现
- [ ] 没有空的函数体 + 注释
- [ ] 没有注释掉的代码块替代实现
- [ ] 没有 `// TODO: 实现 xxx` 在最终代码中
- [ ] 组件有完整的 template/script/style 实现
- [ ] 条件分支（if/else）都有真正的代码实现
- [ ] 事件处理函数有真正的逻辑

## 审查检查

规范审查和质量审查时都必须检查此项：

| 审查维度 | 检查点 |
|---------|--------|
| 规范审查 | 代码是否符合 design.md 的实现要求？每个功能点都有代码实现？ |
| 质量审查 | 是否有只有注释没有实现的函数？是否有 TODO 标记未处理？ |

## 违反处理

发现违反此规则的实现：

1. **立即标记为不合格**
2. **必须补充完整实现**
3. **重新审查直到通过**

无例外。
