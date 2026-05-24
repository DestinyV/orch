# Task 定义模板

## Task [ID]: [Task 名称]

**类型**：[组件实现/Hooks/工具/样式/API集成/构建配置/CDN部署/前端监控/数据库DDL/数据库DML/数据库迁移/中间件/日志/监控埋点/部署配置/联调]

**架构层** ⭐🆕：
- 层级：[表现层/应用层/领域层/基础设施层]（标注此 Task 属于哪个架构层）
- 依赖方向：只能依赖下层，禁止依赖上层或同层同级

**设计模式** ⭐🆕（如有）：
- 模式名称：[如 Factory Method、Strategy、Observer 等]
- 使用位置：[在哪个文件/类中使用]
- 使用原因：[为什么选择此模式]

**所属项目** ⭐🆕（多项目场景必填）：[project-a / project-b / ... / 单项目留空]

**目标**：[这个任务实现什么功能]

**接口标记** ⭐🆕（fullstack 模式必填）：
- provides: [接口列表]（后端 Task，如 `[GET /api/users, POST /api/users]`）
- consumes: [接口列表]（前端 Task，如 `[GET /api/users]`）

> 注：provides/consumes 必须与 api-contract.md 中定义的接口完全一致

**跨项目依赖** ⭐🆕（多项目场景必填）：
- 依赖项目：[project-x]
- 依赖接口：[GET /api/v1/xxx]
- 依赖 Task：[T-X3]

**交付物**：
- [ ] `src/path/to/file.ts` - [文件说明]
- [ ] `src/path/to/file.css` - [文件说明]

**SQL 参考** ⭐🆕（当类型=数据库DDL/数据库DML/数据库迁移时必填）：
- SQL 脚本路径：[spec-dev/{req}/sql-ddl.md](../../spec-dev/{req}/sql-ddl.md) 第[X]节
- 回滚脚本：[spec-dev/{req}/sql-ddl.md](../../spec-dev/{req}/sql-ddl.md) 第4节
- SQL 方言：[mysql | postgresql]

**依赖**：
- 依赖 Task: [T1, T2, ...] 或 无

**验收标准**：
- [ ] [验收条件1]
- [ ] [验收条件2]

**测试用例**：
- TEST-VERIFY: [TV-X.X]
- Test Case ID: [TC-X.X.X]
- Mock Data: [mock_xxx.json]

**估时**：[X]h

**详细说明**（可选）：
[实现思路、注意事项]
