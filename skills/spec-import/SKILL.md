---
name: spec-import
description: |
  规范迁移导入 — 将项目中其他目录的各类规范文档迁移整合到 orch-spec/spec/ 主规范库。

  流程：扫描源目录 → 生成临时规范目录（参考 spec 模板）→ 派遣 archiver 归档 → 清理临时目录。
  不改动原有 spec 和 archive skill。
---

# spec-import

## 职责

将散落的规范文档导入 `orch-spec/spec/` 主规范库。先规范化为 spec 标准目录结构，再通过 archiver 归档入库。

## 何时使用

- 项目已有旧规范文档（`docs/`、`wiki/` 等）
- 从其他仓库迁移规范
- 散落的业务规则、数据字典需要汇聚

## 工作流程

### 步骤1: 扫描源目录

扫描指定目录下所有可导入文件：

```
支持的格式: .md / .yaml / .json / .txt
```

对每个文件，按内容特征归类：

| 特征 | 归类 |
|------|------|
| 含 WHEN-THEN / 场景 / 用例 / scenario / use case | `scenario` |
| 含实体 / 字段 / 表结构 / entity / field / table / schema | `data-models` |
| 含规则 / 约束 / 条件 / rule / constraint / 必须 / 禁止 | `business-rules` |
| 含术语 / 定义 / term / definition / glossary | `glossary` |

### 步骤2: 生成临时规范目录

创建 `orch-spec/_import_{timestamp}/`，按 spec 标准结构组织：

```
orch-spec/_import_{ts}/
├── requirement.md        # 导入摘要
└── spec/
    ├── scenarios/
    │   └── {name}.md     # 按 spec-scenario-template.md 格式
    ├── data-models.md    # 按 spec-data-models-template.md 格式
    ├── business-rules.md # 按 spec-business-rules-template.md 格式
    └── glossary.md       # 按 spec-glossary-template.md 格式
```

**生成规范**：
- requirement.md：填写导入来源、文件清单、分类统计。模板参考 `skills/spec/templates/spec-requirement-template.md`
- scenarios/*.md：每条场景按 WHEN-THEN 格式写入。无法转化的自然语言原文前面加 `RAW_IMPORT:` 标记，保留原始内容
- data-models.md：提取实体/字段/关系，按模板表格式写入
- business-rules.md：提取规则/约束文本，逐条写入
- glossary.md：提取术语及定义，按模板格式写入

**模板引用**（保持与 spec 输出格式一致）：

| 文件 | 模板 |
|------|------|
| requirement.md | `../spec/templates/spec-requirement-template.md` |
| scenarios/*.md | `../spec/templates/spec-scenario-template.md` |
| data-models.md | `../spec/templates/spec-data-models-template.md` |
| business-rules.md | `../spec/templates/spec-business-rules-template.md` |
| glossary.md | `../spec/templates/spec-glossary-template.md` |

### 步骤3: 归档到主规范

```bash
Agent(subagent_type="orch:archiver",
      prompt="归档 orch-spec/_import_{ts}/spec/ 到 orch-spec/spec/。场景合并(ID冲突追加不覆盖)、数据模型追加、业务规则追加(冲突标注DECISION_NEEDED)、术语追加(重复跳过)")
```

<HARD-GATE>必须通过 archiver Agent 执行归档，不允许在主上下文直接执行合并。</HARD-GATE>

### 步骤4: 清理 + 报告

1. 生成 `orch-spec/spec/import-log.md`（来源/归类/合并结果/待转化清单）
2. 删除临时目录 `orch-spec/_import_{ts}/`

## 关键约束

<HARD-GATE>冲突项必须 archiver 标注 DECISION_NEEDED 后由用户手动确认</HARD-GATE>
<HARD-GATE>不直接修改 spec 和 archive skill</HARD-GATE>

✅ 必须：扫描全部可导入文件 | 按 spec 模板生成规范目录 | 通过 archiver 归档 | 生成报告
❌ 禁止：跳过冲突 | 直接覆盖已有文件 | 不生成导入报告 | 不清理临时目录
