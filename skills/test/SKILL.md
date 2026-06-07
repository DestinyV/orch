---
name: test
description: |
  测试验证和闭环（Test阶段）

  输入：src/ + orch-spec/{requirement_desc_abstract}/
  输出：tests/ + orch-spec/{requirement_desc_abstract}/testing/testing-report.md

  功能：对execute生成的代码进行高层测试（集成、E2E、性能），执行闭环验证。
  单元测试由execute的TDD流程保证，此处不重复。
---

# test

## 职责

对生成代码进行高层测试和闭环验证。

## 何时使用

- execute 完成后需要执行集成/E2E/性能测试
- 需要闭环验证（TEST-VERIFY → Test → Code → Result）

## 工作流程

### 1. 静态分析

> 后端语言静态检查指南: `references/backend-static-analysis.md`

前端: lint + type-check。后端按技术栈对应检查（pylint/mypy | go vet/golangci-lint | checkstyle/mvn compile | cargo clippy）。标准: 0编译错误 / Linter 0严重问题 / 覆盖率≥85%。

### 2. 代码审查

**做什么**：派遣 code-reviewer Agent 对 execute 生成的代码进行全面审查。检查维度：功能完整性/代码质量(SOLID/DRY)/类型安全/性能/架构一致性。仅报告置信度≥80。

**为什么**：独立审查确保代码质量，执行者不自审。

**验证**: 审查报告含 CRITICAL/WARNING/INFO + file:line。

> 审查维度详解: `references/code-reviewer.md`

### 3. 高层测试

**做什么**：派遣 tester Agent 执行集成/E2E/契约/性能测试。

**前置**：读取 `orch-spec/{req}/req-context/key-files.md` 确定测试范围。

> 集成测试设计: `references/integration-test-prompt.md` | E2E 设计: `references/e2e-test-prompt.md` | 性能测试: `references/performance-test-prompt.md`

<HARD-GATE>必须通过 Agent 派遣 tester，不允许主上下文直接运行测试。</HARD-GATE>

**后端/全栈额外**：
- 集成测试: Repository/Service/API 协作、事务边界、缓存。模板: `templates/backend-api-test.template.ts`
- 契约测试（fullstack强制）: `<HARD-GATE>验证后端返回字段/类型/结构与 contract.md 一致</HARD-GATE>`。模板: `templates/contract-test-template.md`
- 基础设施: `templates/backend-unit-test-template.md` | `templates/backend-db-migration-test.template.ts` | `templates/backend-e2e-api-test.template.ts`

**前端/全栈额外**：
- 浏览器 E2E: `npx playwright test --grep "@e2e"`。详参: `references/frontend-browser-testing.md`
- 浏览器辅助: `templates/browser-test-helpers.ts` | `templates/playwright.config.ts` | `templates/mcp-browser-server.md` | `scripts/run-browser-tests.sh`
- UI/视觉（快速模式跳过）: `templates/frontend-e2e-test.template.ts` | `templates/frontend-component-ui.template.ts` | `templates/visual-regression.template.ts`
- 性能测试: 前端加载 / API P95<500ms / P99<1000ms

### 4. 证据驱动验证

<HARD-GATE>每条验收标准必须基于本次运行的命令输出。禁止"应该能工作"类声明。</HARD-GATE>

> 反模式检查: `references/testing-anti-patterns.md`

| 证据层级 | 示例 |
|---------|------|
| 1 测试输出 | `npm test` 输出 0 failures |
| 2 类型/构建 | `tsc --noEmit` exit 0 |
| 3 命令验证 | `curl API` 返回预期 |
| 4 人工确认 | UI 行为确认 |

**目标逆向验证**：从目标反向验证数据真实流动——组件用真实 props(非桩)/API 返回真实数据(非mock)/状态正确传递/错误边界实际捕获异常。

<HARD-GATE>前端未执行浏览器E2E测试前不声明通过。</HARD-GATE>

### 5. 闭环验证

生成验证矩阵：TEST-VERIFY → 测试用例 → 代码实现 → 测试结果 完全对应。

standard 模式: 生成闭环验证图 + 覆盖率雷达图。模板: `templates/diagrams/verification-matrix.md` | `templates/diagrams/coverage-radar.md`。

> 完整流程和示例: `references/workflow-detail.md`

## 输出

- `tests/` — 集成/E2E/性能测试代码
- `orch-spec/{req}/testing/testing-report.md` — 验证矩阵 + 测试结果

## 快速模式

集成+E2E保留 | 跳过视觉/组件/性能 | 覆盖率≥60%。
