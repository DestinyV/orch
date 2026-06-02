---
name: spec-migrate
description: |
  规范迁移导入 — 将项目中其他目录的各类规范文档迁移整合到 orch-spec/spec/ 主规范库。

  流程：扫描源目录 → 分类去重 → 冲突确认 → 按内容类型各自的合并策略直接写入 orch-spec/spec/ → 生成报告。
  无临时目录、无归档步骤、不依赖 archive skill。
---

# spec-migrate

## 职责

将散落的规范文档导入 `orch-spec/spec/` 主规范库。不创建临时目录，不依赖 archive skill，直接按字段级/行级/文件级合并策略写入。

## 何时使用

- 项目已有旧规范文档（`docs/`、`wiki/` 等）
- 从其他仓库迁移规范
- 散落的业务规则、数据字典需要汇聚

## 工作流程

### 步骤1: 扫描源目录

扫描指定目录下所有可导入文件（`.md` / `.yaml` / `.json` / `.txt`），按内容特征归类：

| 特征 | 归类 |
|------|------|
| 含 WHEN-THEN / 场景 / 用例 / scenario / use case | `scenario` |
| 含实体 / 字段 / 表结构 / entity / field / table / schema | `data-models` |
| 含规则 / 约束 / 条件 / rule / constraint / 必须 / 禁止 | `business-rules` |
| 含术语 / 定义 / term / definition / glossary | `glossary` |

### 步骤2: 逐条去重

对每条导入内容，与 `orch-spec/spec/` 主规范库对比，标记为 `new` / `duplicate` / `conflict`。

**去重规则**：

| 类型 | 去重逻辑 |
|------|---------|
| scenario | 标题关键词匹配 `orch-spec/spec/scenarios/*.md` |
| data-models | 实体名匹配已定义的 `### Table: {name}` |
| business-rules | 规则文本相似度：≥90%→duplicate；70-90%→conflict |
| glossary | 术语名精确匹配 |

### 步骤3: AskUserQuestion 确认冲突

仅对 `conflict` 条目提问，新增/重复直接处理：

```
发现 N 条冲突：
  1. data-models.users.phone: 已有 VARCHAR(20)，导入为 VARCHAR(11)
  2. glossary."callback": 已有"回调函数"，导入为"回调接口"

[导入全部] [跳过全部] [逐个确认]
```

### 步骤4: 按类型合并写入

| 类型 | 合并策略 | 操作 |
|------|---------|------|
| **scenario** | 文件级 | 不重复→`cp` 到 `orch-spec/spec/scenarios/{name}.md`；同名→`{name}-imported.md` |
| **data-models** | **字段级** | 新实体→文件末追加 `### Table:` 完整章节；已有实体→找该实体表格，仅插入不存在的新字段行 |
| **business-rules** | 行级 | 新规则追加到 `business-rules.md` 末尾；重复跳过 |
| **glossary** | 行级 | 新术语追加到 `glossary.md` 末尾；重复跳过 |

#### Data-models 字段级合并说明

```
目标文件 orch-spec/spec/data-models.md：
  ## 数据模型定义
  ### Table: users
  | id | BIGINT UNSIGNED | Y | PK | 主键 |

导入 users 表含 phone 字段：
  → 找到 ### Table: users 表格，在 id 行后插入 phone 行

导入 orders 表（全新）：
  → 在 glossary.md 后追加 ### Table: orders 完整章节
```

### 步骤5: 生成报告

`orch-spec/spec/import-log.md`：

```markdown
## 导入报告 — {date}

来源: {source_dir}

| 类型 | 新增 | 重复 | 冲突 | 已处理 |
|------|------|------|------|--------|
| scenarios | N | N | N | ✅ |
| data-models | N | N | N | ✅ |
| business-rules | N | N | N | ✅ |
| glossary | N | N | N | ✅ |

## 待转化清单

以下内容无法解析为 BDD 格式，记录了原文位置供后续手工处理：
| 文件 | 段落 | 原因 |
|------|------|------|
```

## 关键约束

<HARD-GATE>冲突项必须 AskUserQuestion 确认后写入，不得静默覆盖</HARD-GATE>

✅ 必须：扫描全部可导入文件 | 逐条去重 | 字段级合并 | 生成报告
❌ 禁止：跳过冲突直接写入 | 文件级简单追加 data-models | 不生成导入报告
