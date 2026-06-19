---
name: contract
description: |
  接口契约定义与审查（Api-Contract 阶段）

  输入：orch-spec/{requirement_desc_abstract}/design/design.md
  输出：orch-spec/{requirement_desc_abstract}/contract/contract.md + review-report.md

  功能：将设计阶段的接口清单转化为正式的接口契约文档，进行审查。
  确保前后端接口定义一致、命名规范、类型匹配、错误处理完整。
  仅在 project-mode: fullstack 时触发。
---

# API Contract

## When to Use

- fullstack 模式下 design 阶段完成
- 需要将 design.md 中的接口定义转化为正式契约文档
- 需要审查接口命名/类型/错误处理的一致性

## Output

- `contract/contract.md` — 接口契约文档
- `contract/review-report.md` — 六维度审查报告

## 职责

读取 design.md 中的接口清单，生成 contract.md（接口契约）和 review-report.md（审查报告）。
fullstack 项目强制环节。

## 工作流程

### 读取设计文档

读取 requirement.md 确认 project-mode（必须为 fullstack）| 读取 design.md 提取项目约定和接口清单 | 读取 scenarios 提取接口交互需求。

**工具优先**：使用 `Skill("orch:scripts")` 调用 `extract-api-list.py` 从 design.md 提取接口清单 JSON，替代 AI 逐文件 Read。

### 步骤 2-4: 派遣 contract-creator Agent

<GATE>fullstack 模式下必须通过 Agent 派遣 contract-creator，不允许主上下文直接执行接口审查。</GATE>

```bash
Agent(
  subagent_type="orch:contract-creator",
  prompt="
    执行接口契约定义与六维度审查：
    - 设计文档: orch-spec/{requirement_desc_abstract}/design/design.md
    - 规范文档: orch-spec/{requirement_desc_abstract}/spec/
    - 现有项目 API 约定（从 design.md 提取）
    
    执行：
    1. 生成接口契约（contract.md）：路径+方法/功能描述/认证/请求参数/成功响应/错误响应/关联数据库表
    2. 六维度审查（review-report.md）：
       - 完整性：每个前端交互有对应后端接口
       - 命名规范：RESTful风格一致性
       - 类型一致性：前后端类型匹配
       - 错误处理：每个接口定义错误码
       - 项目约定：响应/认证/分页格式一致
       - 数据库验证：接口字段与数据库定义一致
    3. 审查判定：6项全部通过→PASS | 任一项不通过→FAIL+修复建议
    
    模板见 templates/contract-template.md 和 templates/review-report-template.md
  ",
  run_in_background=false
)
```

**容错**：Agent 失败则回退主 agent，但必须标注 ⚠️ 未完成自动化接口审查。

### 接口可视化（按需）

API 端点 ≥8 个时生成接口依赖图（前后端调用关系）；响应 JSON 嵌套 ≥3 层时生成响应结构图（字段树形结构）。

模板见 `templates/diagrams/`，输出到 `orch-spec/{req_id}/contract/diagrams/`。触发规则见 `../design/references/diagram-trigger-rules.md`。

## 关键约束

<GATE>fullstack 模式下必须执行接口审查，任一项不通过 → 拒绝进入 task</GATE>

✅ 必须：参数和响应明确定义 | 错误码完整 | 遵循现有约定
❌ 禁止：定义 spec 外的接口 | 跳过审查 | 不通过时进入下一阶段 | 不更新版本号改接口

## 参考文档速查

| 参考文档 | 使用场景 | 阶段 |
|---------|---------|------|
| `templates/contract-template.md` | contract.md 输出结构（路径/方法/参数/响应/错误码） | Phase 2 |
| `templates/review-report-template.md` | review-report.md 审查报告结构 | Phase 3-4 |

### 设计图模板
| 模板 | 输出文件 | Phase |
|------|---------|-------|
| `templates/diagrams/api-dependency.md` | 接口依赖图（前端→API→服务） | Phase 5 |
| `templates/diagrams/response-structure.md` | 响应结构图（嵌套JSON） | Phase 5 |
