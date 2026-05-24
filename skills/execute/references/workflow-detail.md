# execute 详细工作流

## 步骤1: 分析任务列表

读取 `tasks.md`，提取 Task 名称/优先级/依赖关系。

## 步骤2: 制定并行执行计划

按依赖分批：Batch 1（无依赖）→ Batch 2（依赖Batch1）→ ...
批次内无依赖 Task 并行，批次间串行。详见 `references/subagent-protocol.md`。

## 步骤3: 执行 Task

每 Task：创建 worktree → 接口契约验证(fullstack) → SQL验证(数据库) → TDD编码(RED→GREEN→REFACTOR→REVIEW) → 浏览器测试(前端) → 两阶段审查(规范→质量) → 修复循环 → 完成验证。

详见 SKILL.md 步骤3 完整说明。

## 步骤3.8: 执行完成前自检

TDD流程✓ | 测试文件✓ | 测试实际运行✓ | 子代理使用✓ | RED阶段✓ | 覆盖率达标✓ | 审查完成✓ | 修复循环✓ | 分支安全✓ | 无伪代码✓ | TDD日志✓ | 模式标签遵循✓

## 步骤4: 生成执行报告

输出：所有 Task 状态 | 修复循环记录 | 代码统计 | 质量指标 | TDD 总览。
