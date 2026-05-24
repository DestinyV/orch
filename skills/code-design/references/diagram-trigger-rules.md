# 设计图触发规则

## 全局控制

在 `requirement.md` 模式标签中：

```
## 设计图: [按需|全部|跳过]
```

| 值 | 行为 |
|----|------|
| `按需` | 阶段内复杂度达阈值自动生成，否则跳过 |
| `全部` | 忽略阈值，生成所有可用图 |
| `跳过` | 全阶段不生成图 |

## 各阶段触发阈值

### spec-creation

| 图 | 触发条件 | 阈值 |
|----|---------|------|
| ER 图 | 数据实体数 | ≥3 个 |
| 场景流程图 | 场景总数 或 单场景 Case 数 | ≥5 个场景 或 ≥4 Case/场景 |
| 业务规则决策树 | 规则数 或 嵌套条件 | ≥5 条 或 规则含嵌套 IF-THEN |

### code-design

| 图 | 触发条件 | 阈值 |
|----|---------|------|
| 用例图 | 场景数 | ≥5 个 |
| 类图 | 数据实体数 | ≥3 个 |
| 时序图 | 跨组件/服务交互 | ≥2 个服务交互 |
| 状态图 | 实体有明确状态流转 | ≥3 个状态 |
| 组件图 | 架构分层数 | ≥3 层 |
| 部署图 | fullstack + needs-database | 同时满足 |

### api-contract

| 图 | 触发条件 | 阈值 |
|----|---------|------|
| 接口依赖图 | API 端点总数 | ≥8 个 |
| 响应结构图 | 响应 JSON 嵌套层级 | ≥3 层 |

### code-task

| 图 | 触发条件 | 阈值 |
|----|---------|------|
| 任务依赖 DAG | Task 总数 | ≥6 个 |
| provides/consumes 图 | provides/consumes 对数 | ≥3 对 |

### code-test

| 图 | 触发条件 | 阈值 |
|----|---------|------|
| 闭环验证矩阵 | standard 模式 | 始终 |
| 覆盖率雷达图 | standard 模式 | 始终 |

### spec-archive

| 图 | 触发条件 | 阈值 |
|----|---------|------|
| 合并冲突关系图 | DECISION_NEEDED 冲突数 | ≥1 个 |
| 规范演进时间线 | 主规范存在 + 本次有新增 | 同时满足 |

## 模型自主判断

阈值是参考线而非硬约束。模型可根据上下文自主判断：接近阈值且信息密度高 → 生成；低于阈值但用户明确需要 → 生成；信息过于简单 → 即使超过阈值也可跳过。

## 输出路径规范

| 阶段 | 输出路径 | 说明 |
|------|---------|------|
| spec-creation | `spec-dev/{req_id}/spec/diagrams/` | ER图、场景流程图、决策树 |
| code-design | `spec-dev/{req_id}/design/diagrams/` | UML 6类图（用例/类/时序/状态/组件/部署） |
| api-contract | `spec-dev/{req_id}/api-contract/diagrams/` | 接口依赖图、响应结构图 |
| code-task | `spec-dev/{req_id}/tasks/diagrams/` | 任务依赖DAG、provides/consumes图 |
| code-test | `spec-dev/{req_id}/testing/diagrams/` | 闭环验证矩阵、覆盖率雷达图 |
| spec-archive | `spec-dev/spec/diagrams/` | 合并冲突关系图、规范演进时间线 |

> 各阶段使用自己的 diagrams/ 目录，避免跨阶段文件冲突。code-design 阶段应优先检查 spec/diagrams/ 是否已有所需图（来自 spec-creation），避免重复生成。
