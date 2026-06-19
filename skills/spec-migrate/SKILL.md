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

扫描指定目录下所有可导入文件（`.md` / `.yaml` / `.json` / `.txt`），按内容特征归类。

**扫描范围扩展**：
- 源目录下 `.md` / `.yaml` / `.json` / `.txt` 文件（原有）
- `.json` 文件中的 `preferences` / `always_check` / `optimization.rules` 等结构化字段
- 目录名包含 `context` / `knowledge` / `wiki` / `docs` 时递归扫描全部文件

#### 特征归类表

| 特征 | 归类 |
|------|------|
| 含 WHEN-THEN / 场景 / 用例 / scenario / use case | `scenario` |
| 含实体 / 字段 / 表结构 / entity / field / table / schema | `data-models` |
| 含规则 / 约束 / 条件 / rule / constraint / 必须 / 禁止 | `business-rules` |
| 含术语 / 定义 / term / definition / glossary | `glossary` |
| 含 `# {项目名}` / `## Overview` / 项目介绍/背景/目标 章节 | `project-overview` |
| 含集中列举的技术栈清单：语言/框架/数据库/构建/部署（同章节 ≥3 个技术关键词） | `tech-stack` |
| 含分层描述/模块划分/目录结构图（`├──`/`└──` 或模块名+职责列表） | `architecture` |
| 含命名规范/代码风格约定/编码规则 | `conventions` |
| 含经验教训/历史遗漏/常见错误/用户偏好/always_check/模式总结（**兜底**：未被其他分类匹配的非空段落） | `knowledge` |

**技术关键词参考**：`TypeScript|JavaScript|Python|Go|Java|Rust|React|Vue|Angular|Node|Express|Django|Spring|PostgreSQL|MySQL|MongoDB|Redis|Docker|K8s|Webpack|Vite|npm|pip|maven|gradle`

#### 分类歧义消解

当一段内容同时命中多个特征时，按优先级判定（高→低）：

```
data-models > scenario > business-rules > glossary >
  architecture > tech-stack > conventions > project-overview > knowledge
```

knowledge 优先级最低——未被其他 8 类匹配的"有用信息"均归入 knowledge。

交叉提取：architecture 章包含技术栈关键词时，除归入 architecture 外，额外提取技术栈行追加到 tech-stack。

### 步骤2: 逐条去重

对每条导入内容，与 `orch-spec/` 下对应目标文件对比，标记为 `new` / `duplicate` / `conflict`。

**去重规则**：

| 类型 | 去重逻辑 |
|------|---------|
| scenario | 标题关键词匹配 `orch-spec/spec/scenarios/*.md` |
| data-models | 实体名匹配已定义的 `### Table: {name}` |
| business-rules | 规则文本相似度：≥90%→duplicate；70-90%→conflict |
| glossary | 术语名精确匹配 |
| project-overview | 段落首句相似度：≥80%→duplicate；50-80%→conflict（对比 `architecture.md` 的 `## 项目概览`） |
| tech-stack | 技术项名称精确匹配已有行 |
| architecture | 章节标题匹配 + 结构相似度：相同结构→duplicate；不同结构→conflict |
| conventions | 规则行相似度：≥90%→duplicate；70-90%→conflict |
| knowledge | learnings 段落首句相似度≥80%→duplicate；preferences 键名精确匹配→duplicate |

### 步骤3: AskUserQuestion 确认冲突

仅对 `conflict` 条目提问，新增/重复直接处理。以下类型必须确认冲突：

```
发现 N 条冲突：
  Spec:
    1. data-models.users.phone: 已有 VARCHAR(20)，导入为 VARCHAR(11)
    2. glossary."callback": 已有"回调函数"，导入为"回调接口"
  Context:
    3. architecture."整体分层": 已有 controllers/models 结构，导入为 api/services，需确认
  Knowledge:
    4. preferences."tech_stack": 目标已有值，导入值不同，需确认

[导入全部] [跳过全部] [逐个确认]
```

project-overview / tech-stack / conventions / knowledge 的 learnings 部分通常仅追加无冲突，不需提问。

### 步骤4: 按类型合并写入

#### 步骤 4.0: 目标文件存在性检查

合并前检查目标文件是否存在。不存在时从模板创建：

| 目标文件 | 不存在时的初始化操作 |
|---------|-------------------|
| `orch-spec/context/architecture.md` | 创建 `# 架构\n\n## 项目概览\n\n## 整体分层\n` |
| `orch-spec/context/tech-stack.md` | 创建 `# 技术栈\n\n## 语言\n\n## 框架\n\n## 数据库\n\n## 构建\n\n## 部署\n` |
| `orch-spec/context/conventions.md` | 创建 `# 命名规范与约定\n` |
| `orch-spec/context/learnings.md` | 创建 `# 知识沉淀\n` |
| `orch-spec/context/index.json` | 按 `agent-dispatch-code.md` 步骤1 中的 8 文件模板创建 |
| `orch-spec/user-preferences/preferences.json` | 创建 `{"always_check":[], "rejected_approaches":[], "bottlenecks":[]}` |
| `orch-spec/spec/` 主规范库 | 创建目录结构 `spec/scenarios/` + 空文件 `spec/data-models.md` / `spec/business-rules.md` / `spec/glossary.md` |

#### Spec（原有 4 类，逻辑不变）

| 类型 | 合并策略 | 操作 |
|------|---------|------|
| **scenario** | 文件级 | 不重复→`cp` 到 `orch-spec/spec/scenarios/{name}.md`；同名→`{name}-imported.md` |
| **data-models** | **字段级** | 新实体→文件末追加 `### Table:` 完整章节；已有实体→找该实体表格，仅插入不存在的新字段行 |
| **business-rules** | 行级 | 新规则追加到 `business-rules.md` 末尾；重复跳过 |
| **glossary** | 行级 | 新术语追加到 `glossary.md` 末尾；重复跳过 |

#### Context（新增 4 类）

| 类型 | 合并策略 | 操作 |
|------|---------|------|
| **project-overview** | **段落级** | 以段落为单位，比对 `architecture.md` 的 `## 项目概览` 章节。相似度 < 70% 追加为新段落（注明来源文件） |
| **tech-stack** | **行级** | 每个技术项与 `tech-stack.md` 已有行比对。不存在→追加到对应 `##` 章节；章节不存在→创建章节后追加 |
| **architecture** | **章节级** | 读 `architecture.md` 同 `##` 章节。结构相同→skip；结构不同→conflict（步骤3 已确认后合并）；章节不存在→直接追加完整章节 |
| **conventions** | **行级** | 逐行比对 `conventions.md` 已有规则。新规则→追加到对应 `##` 章节；重复→skip |

#### Knowledge（新增 1 类，内部分流）

| 子类型 | 合并策略 | 操作 |
|--------|---------|------|
| learnings | **段落级** | 提取段落首句摘要，比对 `learnings.md` 已有段落首句。相似度≥80%→skip；<80%→追加段落（含来源文件标注） |
| preferences 检查项 | **键级** | `always_check[]`：新项追加（去重）；已有项 skip |
| preferences 偏好 | **键级** | 已有键→conflict（步骤3 确认）；新键→追加 |
| optimization 规则 | **键级** | `optimization.rules[]`：新规则追加（按 id 去重）；已有 id→skip |

**knowledge 分流判定**：
- 含 `always_check` / `检查项` / `checklist` → preferences → always_check[]
- 含 `偏好` / `preference` → preferences → 对应键
- 含 `优化规则` / `optimization` → preferences → optimization.rules[]
- 其他（经验教训/历史遗漏/模式总结）→ learnings.md

#### Data-models 字段级合并说明（原有，不变）

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

### Spec
| 类型 | 新增 | 重复 | 冲突 | 已处理 |
|------|------|------|------|--------|
| scenarios | N | N | N | ✅ |
| data-models | N | N | N | ✅ |
| business-rules | N | N | N | ✅ |
| glossary | N | N | N | ✅ |

### Context
| 类型 | 新增 | 重复 | 冲突 | 已处理 | 目标文件 |
|------|------|------|------|--------|---------|
| project-overview | N | N | N | ✅ | architecture.md |
| tech-stack | N | N | N | ✅ | tech-stack.md |
| architecture | N | N | N | ✅ | architecture.md |
| conventions | N | N | N | ✅ | conventions.md |

### Knowledge
| 类型 | 新增 | 重复 | 冲突 | 已处理 | 目标文件 |
|------|------|------|------|--------|---------|
| knowledge | N | N | N | ✅ | learnings.md + preferences.json |

### Context 索引更新
| 文件 | 操作 | 状态 |
|------|------|------|
| index.json | tags 索引同步 | ✅ |

## 待转化清单

以下内容无法解析为任何类型，记录了原文位置供后续手工处理：
| 文件 | 段落 | 原因 |
|------|------|------|
```

## 关键约束

<GATE>冲突项必须 AskUserQuestion 确认后写入，不得静默覆盖</GATE>
<GATE>architecture 章节冲突必须 AskUserQuestion 确认，不允许自动覆盖</GATE>
<GATE>preferences.json 已存在的键不可覆盖（仅追加新键），冲突时 AskUserQuestion 确认</GATE>
<GATE>context 文件首次创建后必须同步更新 `orch-spec/context/index.json` 的 tags 索引</GATE>

✅ 必须：扫描全部可导入文件 | 逐条去重 | 字段级合并 | 生成报告 | 更新 index.json
❌ 禁止：跳过冲突直接写入 | 文件级简单追加 data-models | 不生成导入报告 | 覆盖 preferences.json 已有键
