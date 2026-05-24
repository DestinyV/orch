# TDD实现提示词

指导实现子代理遵循TDD（RED-GREEN-REFACTOR-REVIEW）流程编码。

## 前置要求

test-spec.md ✓ | fixtures.json ✓ | test-*.template ✓ | design.md测试性设计(前端) ✓ | spec的BROWSER-TESTABLE(前端) ✓

**后端测试模板**：`../code-test/templates/backend-unit-test-template.md`（Python/Go/Java/Rust）

## RED阶段 - 写失败的测试

1. 从test-spec.md选一个test case
2. 在test-*.template中找到对应框架，填充具体内容
3. 运行确保失败（`npm test -- TC-X.X.X`）
4. 一次一个test，确保失败信息清晰

关键点：一次一个 | 确保失败 | 使用fixtures/Mock | 失败信息明确

## GREEN阶段 - 写最小化实现

写最少代码让当前test通过。可以hardcode/复制粘贴，目标是通过测试。不做过度工程化、不猜测未来需求。写完一个test的实现再做下一个。

## REFACTOR阶段 - 改进代码质量

在所有test通过前提下小步重构：提取重复代码 | 改进命名 | 提取工具函数 | 添加类型注解 | 添加注释文档。每次重构后立即运行test确保仍通过。不回退行为，不改函数签名(除非更新对应test)。

## REVIEW阶段 - 质量审查

检查：所有test通过 | Lint通过 | TS检查通过 | 覆盖率达标 | 无hardcoded值 | 无TODO | 代码风格一致 | 命名清晰。发现问题按严重程度处理：严重→回GREEN | 中度→REFACTOR修复 | 轻微→直接补充。

## 代码完整性检查（GREEN和REFACTOR阶段）

所有代码必须是完整的生产级代码：
- ❌ 禁止：样式块只有注释 | 函数只有TODO | 空事件处理器 | 条件分支只有if没有else | 空对象属性
- ✅ 要么完整实现，要么完全删除。不能留"半成品"。

详见：`references/code-completeness-checklist.md` | `references/no-comment-only-code.md`

## 浏览器测试 TDD（前端/全栈）

RED-BROWSER → 写Playwright测试验证BROWSER-TESTABLE → GREEN-BROWSER → 实现UI使测试通过。使用data-testid选择器，覆盖所有BROWSER-TESTABLE标准。

模板参考：`skills/code-test/templates/frontend-e2e-test.template.ts` | `visual-regression.template.ts` | `frontend-component-ui.template.ts`

## 验证模式

任何声称"通过"前必须实际运行验证命令并展示证据：
- 测试通过 → 必须展示测试命令输出（0 failures）
- 构建成功 → 必须展示编译命令 exit 0
- 浏览器测试 → 必须展示 Playwright 输出
- 子代理 → 检查git diff验证改动，不直接信任报告

详见：`references/verification-gate.md`
