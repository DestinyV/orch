---
name: test
description: |
  测试验证和闭环（Test阶段）

  输入：src/ + spec-dev/{requirement_desc_abstract}/
  输出：tests/ + spec-dev/{requirement_desc_abstract}/testing/testing-report.md

  功能：对code-execute生成的代码进行全面审查和高层测试（集成、E2E、性能），执行闭环验证。
  单元测试由code-execute的TDD流程保证，此处不重复。
---

# code-test

## When to Use

- code-execute 完成，需要执行高层测试（集成/E2E/性能）
- 需要进行闭环验证（TEST-VERIFY -> Test -> Code -> Result）
- 需要生成测试报告

## Output

- `tests/` — 集成/E2E/性能测试代码
- `testing/testing-report.md` — 验证矩阵 + 测试结果

## 职责

对生成代码进行静态分析、高层测试和闭环验证。

**流程**：静态分析 → 代码审查 → 高层测试 → 闭环验证 → 生成报告
**输出**：`spec-dev/{requirement_desc_abstract}/testing/testing-report.md`

## 工作流程

### 静态分析

前端：`npm run lint && npm run type-check` | 后端按技术栈执行对应检查（Python: pylint+mypy | Go: go vet+golangci-lint | Java: checkstyle+mvn compile | Rust: cargo clippy）。
标准：0编译错误 | Linter 0严重问题 | 覆盖率≥85% | 无虚假测试。

### 代码审查（派遣 code-reviewer Agent）

<HARD-GATE>必须通过 Agent 派遣 code-reviewer 执行代码审查，不允许主上下文直接审查。</HARD-GATE>

```bash
Agent(
  subagent_type="orch:code-reviewer",
  prompt="
    对 code-execute 生成的代码进行全面审查：
    - 源代码: src/
    - 设计规范: spec-dev/{requirement_desc_abstract}/design/design.md
    
    检查维度：
    - 功能完整性：所有 Task 验收标准是否满足
    - 代码质量：SOLID/DRY/命名/注释-only/空框架
    - 类型安全：TypeScript strict / Python mypy / Java checkstyle 等
    - 性能：无 N+1 查询、无不必要重渲染、无内存泄漏
    - 一致性：代码实现与 design.md 架构一致
    
    仅报告置信度 ≥ 80 的问题。返回：问题清单 + 置信度 + file:line + 修复建议。
  ",
  run_in_background=false
)
```

详见 `references/code-reviewer.md`（审查维度详细说明）。

### 高层测试（派遣 code-tester Agent）

<HARD-GATE>必须通过 Agent 派遣 code-tester 执行高层测试运行，不允许主上下文直接运行测试。</HARD-GATE>

```bash
Agent(
  subagent_type="orch:tester",
  prompt="
    对代码执行高层测试：
    - 源代码: src/
    - 测试规范: spec-dev/{requirement_desc_abstract}/tests/test-spec-creation.md
    - 接口契约: spec-dev/{requirement_desc_abstract}/contract/contract.md（fullstack时）

    执行：
    1. 环境检查（Playwright/pytest/go test/mvn test）
    2. 集成测试（Repository/Service/API 协作）
    3. E2E 测试（npx playwright test --grep '@e2e'）
    4. 契约测试（fullstack：验证返回字段/类型/结构）
    5. 性能测试（前端加载/后端 P95<500ms）
    6. 闭环验证（TEST-VERIFY→Test→Code→Result 对应）

    返回：测试报告 + 失败诊断 + 闭环矩阵
  ",
  run_in_background=false
)
```

### 证据驱动验证（新增）

<HARD-GATE>每条验收标准必须有新鲜证据支持才能标记通过。拒绝接受"应该/可能/似乎"类声明。</HARD-GATE>

验证证据层次（优先级从高到低）：

| 优先级 | 证据类型 | 示例 |
|--------|---------|------|
| 1 | 实际测试运行输出 | `npm test` 输出显示 0 failures |
| 2 | 类型检查/构建通过 | `tsc --noEmit` exit 0 |
| 3 | 直接命令验证 | `curl API` 返回预期 200 |
| 4 | 手动验证 | 人工确认 UI 行为 |

**不接受**：代码审查中的"应该能工作"、"看起来正确"、"可能通过了"。

**验证流程**：
1. 对每条验收标准，确定所需证据级别
2. 独立运行验证命令（不接受之前的输出，必须新运行）
3. 记录每条标准的证据和结果
4. 所有验收标准通过 → 声明完成

### 目标逆向验证（新增）

不只看测试是否通过，从目标反向验证数据是否真实流动：

```bash
# 验证清单
# 1. 组件是否接收真实 props（非硬编码桩数据）
# 2. API 端点是否返回真实响应（非 mock 数据）
# 3. 状态管理是否正确传递数据（非断连）
# 4. 错误边界是否实际捕获异常（非空实现）
```

**发现桩组件/假数据/断连状态 → 标记为未通过**，回到修复循环。

### 三层测试分类（新增）

| 层级 | 类型 | 耗时 | 门控 | 说明 |
|------|------|------|------|------|
| T1 | 静态检查（lint/type/format） | < 1s | 阻断 | 每次提交必须通过 |
| T2 | E2E 差异化测试 | ~30s | 阻断 | 每次 PR 必须通过 |
| T3 | LLM 评判式评估 | ~$0.15 | 建议 | 每日/每周运行，不阻断 |

**T3 评估内容**：由 Agent 评判生成的代码是否符合设计规范、是否有潜在逻辑缺陷。非阻断，但结果记入 testing-report.md。

**输出格式**（追加到 testing-report.md）：

```markdown
## 证据驱动验证报告
| 验收标准 | 证据类型 | 命令/方法 | 结果 | 新鲜度 |
|---------|---------|----------|------|--------|
| TC-001 登录成功 | 测试运行 | pytest tests/test_login.py | ✅ PASS | 本次运行 |
| TC-002 密码错误 | 测试运行 | pytest tests/test_login.py | ✅ PASS | 本次运行 |
```

**后端/全栈**：
- 3.0 基础设施检测：测试框架 | HTTP工具 | DB测试配置
- 3.1 集成测试：Repository/Service/API 协作、事务边界、缓存
- 3.1.5 契约测试（fullstack强制）：<HARD-GATE>验证后端返回字段/类型/结构与 api-contract.md 一致</HARD-GATE>

**前端/全栈**：
- 3.2 浏览器 E2E：`npx playwright test --grep "@e2e"` | 详见 `references/frontend-browser-testing.md`
- 3.3-3.5 视觉回归/组件UI/MCP探索性（快速模式跳过）
- 3.6 性能测试：前端加载时间 | 后端API P95<500ms | P99<1000ms | 错误率<1%

### 闭环验证 + 可视化

生成验证矩阵：TEST-VERIFY → 测试用例 → 代码实现 → 测试结果 完全对应。

standard 模式下生成闭环验证矩阵图（TEST-VERIFY→Test Case→Code→Result 关系图）和覆盖率雷达图（Unit/Integration/E2E/Browser/Performance 5维分布）。

模板见 `templates/diagrams/`，输出到 `spec-dev/{req_id}/testing/diagrams/`。

### 生成测试报告

<HARD-GATE>前端未执行浏览器E2E测试前，不声明通过</HARD-GATE>
验证铁律：未运行测试命令→不能声称通过。

## 快速模式

精简：集成+E2E保留 | 跳过视觉/组件/性能 | 覆盖率≥60%。

## 关键约束

Lint+TS全部通过 | 高层测试全覆盖 | 闭环验证100% | 禁止跳过浏览器测试 | 禁止反向修改代码适配测试

## 参考文档速查

### 审查和反模式
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `references/code-reviewer.md` | 代码审查维度（功能/质量/类型/性能/一致性） | 步骤2 |
| `references/testing-anti-patterns.md` | 测试反模式检查 | 步骤1/5 |
| `references/workflow-detail.md` | 完整工作流步骤和闭环验证示例 | 步骤4-5 |
| `references/backend-static-analysis.md` | 后端静态分析指南（各语言栈检查维度） | 步骤1 |

### 高层测试
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `references/integration-test-prompt.md` | 集成测试设计（Repository/Service/API 协作） | 步骤3.1 |
| `references/e2e-test-prompt.md` | E2E 测试场景设计和 Playwright 实践 | 步骤3.2 |
| `references/performance-test-prompt.md` | 性能测试（前端加载/后端API P95/P99） | 步骤3.6 |
| `references/frontend-browser-testing.md` | Playwright 浏览器测试类型和环境 | 步骤3.2 |

### 模板
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `templates/backend-api-test.template.ts` | 后端集成测试模板 | 步骤3.1 |
| `templates/backend-unit-test-template.md` | 后端单元测试模板（Python/Go/Java/Rust） | 步骤1 |
| `templates/backend-db-migration-test.template.ts` | 数据库迁移测试模板 | 步骤3.1 |
| `templates/backend-e2e-api-test.template.ts` | 后端 API E2E 测试模板 | 步骤3.1 |
| `templates/contract-test-template.md` | 接口契约测试模板（fullstack 强制） | 步骤3.1.5 |

### 浏览器测试
| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `templates/browser-test-helpers.ts` | 浏览器测试辅助函数（data-testid选择器/等待策略） | 步骤3.2 |
| `templates/frontend-e2e-test.template.ts` | 前端 E2E 测试模板 | 步骤3.2 |
| `templates/frontend-component-ui.template.ts` | 前端组件 UI 测试模板 | 步骤3.3 |
| `templates/visual-regression.template.ts` | 视觉回归测试模板 | 步骤3.4 |
| `templates/playwright.config.ts` | Playwright 配置文件模板 | 步骤3.2 |
| `templates/mcp-browser-server.md` | MCP 浏览器服务器配置 | 步骤3.5 |
| `${CLAUDE_PLUGIN_ROOT}/skills/test/scripts/run-browser-tests.sh` | 浏览器测试运行脚本 | 步骤3.2 |

### 设计图模板
| 模板 | 输出文件 | 步骤 |
|------|---------|------|
| `templates/diagrams/verification-matrix.md` | 闭环验证矩阵（TV→TC→Code→Result） | 步骤4 |
| `templates/diagrams/coverage-radar.md` | 测试覆盖率雷达（5维分布） | 步骤4 |
