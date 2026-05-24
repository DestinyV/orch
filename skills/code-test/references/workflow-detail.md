# code-test 详细工作流

## 步骤1: 代码质量静态分析

**前端**：`npm run lint && npm run type-check` | 0 Lint错误 | 0 TS错误
**后端**：Python(pylint+mypy) | Go(go vet+golangci-lint) | Java(checkstyle+mvn compile) | Rust(cargo clippy)

**单元测试真实性验证**：覆盖正常+边界+错误 | 每测试一行为 | 断言明确 | TEST-VERIFY 都有对应测试。

## 步骤2: 代码审查

检查维度：功能完整性 | 代码质量 | 类型安全 | 性能 | 一致性(design.md)。详见 `references/code-reviewer.md`。

## 步骤3: 高层测试

**后端/全栈**：基础设施检测 → 集成测试(Repository/Service/API) → 契约测试(fullstack强制)
**前端/全栈**：E2E 浏览器测试(`@e2e`) → 视觉回归(`@visual`) → 组件UI(`@component`) → 性能测试

详见：`references/integration-test-prompt.md` | `references/e2e-test-prompt.md` | `references/performance-test-prompt.md` | `references/frontend-browser-testing.md`

## 步骤4: 闭环验证

生成验证矩阵：TEST-VERIFY → 测试用例 → 代码实现 → 测试结果。

## 步骤5: 生成测试报告

<HARD-GATE>前端未执行浏览器E2E不声明通过</HARD-GATE>
验证铁律：必须实际运行所有测试，捕获输出。
