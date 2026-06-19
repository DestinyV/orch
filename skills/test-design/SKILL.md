---
name: test-design
description: |
  测试设计和规范生成（Test Design阶段）

  输入：orch-spec/{requirement_desc_abstract}/spec/
  输出：orch-spec/{requirement_desc_abstract}/tests/test-spec.md + fixtures.json + test-*.template

  功能：将规范中的TEST-VERIFY和Mock数据转换为详细测试规范和框架代码。
---

# test-design

## When to Use

- spec 已完成，需要将 TEST-VERIFY 转化为测试用例
- 需要生成 fixtures 和测试框架代码

## 职责

将规范中的TEST-VERIFY和Mock数据转换为可执行的测试规范和框架代码。

**输出**：`orch-spec/{requirement_desc_abstract}/tests/test-spec.md` + `fixtures.json` + `test-*.template`

## 工作流程

### 阶段1: 读取分析

读取：spec中的TEST-VERIFY + Mock Data。通过 Agent 派遣 test-designer 分析每个场景的测试需求和边界值。

**工具优先**：使用 `Skill("orch:scripts")` 调用 `extract-test-verify.py` 从 scenarios/ 提取 TEST-VERIFY JSON，替代 AI 逐文件 Read。

```bash
Agent(
  subagent_type="orch:test-designer",
  prompt="
    对规范中的 TEST-VERIFY 进行测试设计：
    - 规范目录: orch-spec/{requirement_desc_abstract}/spec/
    
    执行：
    1. TEST-VERIFY 提取：识别所有 TEST-VERIFY，理解含义，识别正常/边界/特殊场景
    2. Test Case 设计：每个 TEST-VERIFY 设计 1-3 个 test case（正常/边界/错误），使用 AAA 模式
    3. Mock 策略定义：识别需 Mock 的依赖（API/DB/服务），定义返回值和错误场景
    4. Fixture 生成：从规范提取 JSON 格式，包含有效值/边界值/特殊值
    5. 覆盖率分析：追踪 TEST-VERIFY ↔ test case 对应关系，验证 100% 覆盖
    
    返回：test case 清单、Mock 策略、Fixture 定义、覆盖率矩阵
  ",
  run_in_background=false
)
```

### 阶段2: 生成测试规范

输出 test-spec.md，包含：项目信息 | 测试框架选型 | 测试分层(Unit/Integration/E2E/Browser) | Test Case表格 | Mock/Fixture定义 | 覆盖率分析。

测试分层：
- **Unit**：单函数/组件，Mock外部依赖，测边界值
- **Integration**：多组件协作，API调用，数据流
- **E2E**：完整用户流程，真实场景
- **Browser**（前端/全栈）：Playwright @e2e/@visual/@component，覆盖BROWSER-TESTABLE

### 阶段3: Mock和Fixture定义

生成 fixtures.json，包含：有效输入 | 边界值 | 特殊值 | API Mock | DB Mock | 第三方服务Mock。每个Mock明确为什么Mock、Mock什么、如何Mock。

### 阶段4: 生成框架代码

为每个Task生成 test-*.template，结构：imports → beforeEach(setup+Mock) → test cases → afterEach(cleanup)。支持 Jest/Vitest/Pytest/Go testing/Cypress 等框架。

### 阶段5: 验证覆盖率

检查：所有TEST-VERIFY都有对应test case | 每个test case关联test-case-mapping | Mock/Fixture定义清晰 | 框架代码可执行 | 测试分层合理。

**覆盖率矩阵**：
```
| TEST-VERIFY | TC-ID | 框架代码 | 类型 | Mock | 状态 |
|-------------|-------|---------|------|------|------|
```

## 关键原则

- **TEST-VERIFY优先**：所有测试来自规范，保持一致性
- **完整映射链**：TEST-VERIFY → test-case-mapping → TC-ID → test-*.template
- **分层清晰**：Unit快速反馈 → Integration验证协作 → E2E保证体验
- **Mock策略明确**：为什么Mock | Mock什么 | 如何Mock

<GATE>TEST-VERIFY覆盖率<100%→不允许输出测试规范，必须补充test case直到完全覆盖。</GATE>

## 输出要求

**test-spec.md**：所有TEST-VERIFY有对应test case | 测试分层清晰 | BROWSER-TESTABLE覆盖 | 无broken links
**fixtures.json**：有效值+边界值+特殊值 | API/DB Mock定义 | 格式正确
**test-*.template**：完整setup+cleanup | test case全覆盖 | 代码可运行 | 命名清晰

## 成功标准

TEST-VERIFY覆盖率=100% | 所有Task有框架代码 | fixtures.json可用 | 模板代码可执行 | 格式/命名/注释规范

详见 `references/workflow-detail.md` | `prompts/test-case-designer-prompt.md` | `templates/test-spec-template.md`

## 参考文档速查

| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `prompts/test-case-designer-prompt.md` | test-designer Agent 任务定义 | 阶段1-2 |
| `references/workflow-detail.md` | 完整工作流步骤、示例、最佳实践 | 全部阶段 |
| `templates/test-spec-template.md` | test-spec.md 输出结构 | 阶段2 |
| `templates/fixtures-json-template.md` | fixtures.json 格式定义 | 阶段3 |
