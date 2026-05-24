# 并行派遣判断标准

## 单一判断表

| 维度 | ✅ 可并行 | ❌ 不可并行 |
|------|----------|-----------|
| **文件交集** | 无重叠文件或目录 | 修改同一文件/类型定义 |
| **接口依赖** | 无 provides/consumes 交叉 | T1 provides API，T2 consumes |
| **共享状态** | 无共享全局状态/DB 表 | 同一表的 schema 变更/迁移 |
| **任务类型** | 独立模块/组件实现 | 联调/集成/配置变更 |

## 快速判断规则

1. 文件交集为空 → 可并行
2. 任一 Task 标注 `consumes` 且提供者未在本批次 → 不可并行
3. 同一 Task 类型为「联调」/「集成」 → 不可并行

## 批次划分示例

```
tasks.md:
T1: 订单模型（provides: OrderModel）
T2: 用户模型（provides: UserModel）
T3: 订单API（consumes: OrderModel, depends: T1）
T4: 用户API（consumes: UserModel, depends: T2）
T5: 前端联调（consumes: OrderAPI+UserAPI, depends: T3+T4）

→ Batch 1: T1, T2（无依赖，无文件交集）
→ Batch 2: T3, T4（依赖 Batch 1，但互不依赖）
→ Batch 3: T5（依赖 Batch 2，联调任务必须串行）
```
