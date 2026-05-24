# SDD+TDD 最佳实践指南

## 核心原则

1. **统一入口** — 从 `/workflow` 启动，自动检测模式并串联所有阶段
2. **规范优先** — 一切从 `/spec` 开始，规范是后续所有阶段的单一事实源
3. **设计驱动** — `/design` 设计审批后才能进入 Task 阶段（数据库先行+接口契约驱动）
4. **TDD 流程** — RED（测试失败）→ GREEN（最小实现）→ REFACTOR（重构）→ REVIEW（验证）
5. **Agent 派遣** — 9 个 Agent 必须通过 `Agent()` 显式派遣，禁止主上下文替代
6. **子代理隔离** — standard 模式每个 Task 必须使用独立子代理 + git-worktree
7. **两阶段审查** — 规范审查（符合 design.md）→ 质量审查（Lint/类型/覆盖率）
8. **中断恢复** — `.workflow-state.json` 持久化状态，支持中断后继续

## 各阶段检查清单

### Workflow-Control 阶段（编排入口）
- [ ] 需求描述明确清晰
- [ ] project-mode 正确检测（frontend/backend/fullstack）
- [ ] 工作模式确认（standard/quick）
- [ ] .workflow-state.json 已初始化
- [ ] 效果评估数据已记录（阶段耗时、Agent状态、卡点统计）

### Spec 阶段
- [ ] 场景使用 WHEN-THEN 格式
- [ ] 每个 Case 有 TEST-VERIFY 验收标准
- [ ] 每个 Case 有 Mock Data 定义
- [ ] 前端场景有 BROWSER-TESTABLE 声明
- [ ] code-explorer Agent 派遣记录

### Test Design 阶段
- [ ] TEST-VERIFY 100% 对应 Test Case
- [ ] fixtures.json 包含有效/边界/特殊值
- [ ] 测试骨架代码可运行
- [ ] test-designer Agent 派遣记录

### Design 阶段
- [ ] fullstack 时完成数据库设计和接口契约
- [ ] 接口契约得到双方确认
- [ ] 设计决策有原因和权衡
- [ ] code-architect Agent 派遣记录

### Api-Contract 阶段（fullstack）
- [ ] 六维度审查全部通过
- [ ] 接口契约版本号正确
- [ ] contract-creator Agent 派遣记录

### Task 阶段
- [ ] 任务粒度适中（≤4h）
- [ ] 依赖关系准确无环（DAG）
- [ ] Test Case 映射完整
- [ ] tasker Agent 派遣记录

### Execute 阶段
- [ ] TDD 四阶段完整执行（RED→GREEN→REFACTOR→REVIEW）
- [ ] 覆盖率 ≥85%（standard）/ ≥60%（quick）
- [ ] 无伪代码/空函数体
- [ ] 后端/全栈已调用 exception
- [ ] code-executor + code-reviewer Agent 派遣记录

### Exception-Handler 阶段（后端/全栈）
- [ ] 项目约定扫描完成（异常类名/错误码格式/RPC模式）
- [ ] 异常场景识别全覆盖
- [ ] 零硬编码（所有约定通过扫描发现）
- [ ] exception Agent 派遣记录

### Test 阶段
- [ ] 前端已执行浏览器 E2E 测试
- [ ] 契约测试通过（fullstack）
- [ ] TEST-VERIFY → 测试 → 代码 完全对应
- [ ] code-reviewer Agent 派遣记录

### Archive 阶段
- [ ] 冲突全部标记 DECISION_NEEDED
- [ ] 归档报告已生成
- [ ] 版本号正确递增
- [ ] archiver Agent 派遣记录

## 常见反模式

- ❌ 跳过 workflow 直接调用下游 Skill
- ❌ 跳过设计直接编码
- ❌ 让测试通过而修改源代码逻辑
- ❌ 发现问题不修复就继续下一个 Task
- ❌ 用 console/print 伪装实现
- ❌ 忽略闭环验证（Task-代码-测试对应）
- ❌ 主上下文直接替代 Agent 派遣
- ❌ HARD-GATE 失败静默跳过
