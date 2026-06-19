# spec-migrate 扩展：context / knowledge 迁移方案 v2

## 现状

当前 `spec-migrate` 只处理 4 种内容类型：scenario / data-models / business-rules / glossary。

需要新增项目上下文和知识沉淀的迁移能力。

## 核心设计决策

### 1. 内容分类从 4 类扩到 9 类（新+5）

新增 5 个分类。原设计中细分的 `context-code-patterns` / `context-file-map` 等不单独分类——它们从属于 context/ 文件，迁移时按文件级处理即可。knowledge 也不拆分为 patterns / learnings / preferences 三类——它们统一归入 knowledge 大类，在合并时根据实际内容写入对应文件。

| # | 类型 | 识别特征 | 目标位置 | 合并策略 |
|---|------|---------|---------|---------|
| 原有 |
| 1 | scenario | WHEN-THEN / 场景 / 用例 | `orch-spec/spec/scenarios/` | 文件级 |
| 2 | data-models | 实体 / 字段 / 表结构 | `orch-spec/spec/data-models.md` | 字段级 |
| 3 | business-rules | 规则 / 约束 / 必须 / 禁止 | `orch-spec/spec/business-rules.md` | 行级 |
| 4 | glossary | 术语 / 定义 | `orch-spec/spec/glossary.md` | 行级 |
| 新增 — context |
| 5 | **project-overview** | `# {项目名}` / `## Overview` / 项目介绍/背景/目标 | `orch-spec/context/architecture.md` → `## 项目概览` | **段落级** |
| 6 | **tech-stack** | 语言/框架/数据库/构建/部署 清单 | `orch-spec/context/tech-stack.md` | **行级** |
| 7 | **architecture** | 分层/模块/目录结构/架构图 | `orch-spec/context/architecture.md` | **章节级**（冲突确认） |
| 8 | **conventions** | 命名规范/约定/规则/编码风格 | `orch-spec/context/conventions.md` | **行级** |
| 新增 — knowledge |
| 9 | **knowledge** | 经验教训/历史遗漏/常见错误/用户偏好/always_check/模式总结 | `orch-spec/context/learnings.md` + `orch-spec/user-preferences/preferences.json` | **段落级**（learnings）+ **键级**（preferences） |

### 2. 分类歧义消解规则

当一段内容同时命中多个特征时，按以下优先级判定：

```
优先级（高→低）：
  data-models > scenario > business-rules > glossary >
    architecture > tech-stack > conventions > project-overview > knowledge
```

理由：
- 结构化数据（data-models / scenario）优先级最高——它们有明确的格式特征，不易误判
- architecture 高于 tech-stack —— 架构章可能提到技术栈，但它是架构文档
- knowledge 优先级最低——它是兜底分类。任何不匹配上述特征的"有用信息"都应归入 knowledge

### 3. 目标文件不存在时的处理

首次迁移时目标文件可能尚不存在：

| 目标文件 | 不存在时的操作 |
|---------|--------------|
| `orch-spec/context/tech-stack.md` 等 8 个 context 文件 | 从模板创建初始文件，然后合并 |
| `orch-spec/spec/` 主规范库 | 按已有逻辑创建（现有能力） |
| `orch-spec/user-preferences/preferences.json` | 创建初始 JSON `{"always_check":[], "rejected_approaches":[]}` |
| `orch-spec/context/learnings.md` | 创建空文件 + `# 知识沉淀` 标题 |

文件创建后立即合并迁移内容。

### 4. project-context 不单独作为迁移目标

`orch-spec/{req_id}/project-context.md` 是请求级文件（由 spec 阶段按需生成），不是项目级沉淀目标。项目概览类文档统一迁移到 `orch-spec/context/architecture.md` 的 `## 项目概览` 章节。`project-context.md` 的内容也可以被 scan 识别后归入 project-overview / tech-stack / architecture 等分类。

---

## 扫描阶段增强

### 步骤 1 扩展：扫描范围

原有扫描范围：
- 源目录下 `.md` / `.yaml` / `.json` / `.txt` 文件

新增扫描范围：
- 源目录下 `.md` / `.yaml` / `.json` / `.txt` 文件（同原有）
- `.json` 文件中的 `preferences` / `always_check` / `optimization.rules` 等结构化字段
- 目录名包含 `context` / `knowledge` / `wiki` / `docs` 时递归扫描全部文件

### 步骤 1 扩展：特征识别

在原有 4 类特征识别后追加：

```
# 新增 — project overview
含 "# {项目名}" / "## Overview" / "## 项目介绍" / "## 项目背景" / "## 项目目标"
  → 归入 project-overview

# 新增 — tech stack  
含集中列举的技术栈（语言/框架/数据库/构建/部署/依赖）清单
  → 归入 tech-stack
  判定：同一章节内出现 ≥ 3 个技术关键词时确认归类
  技术关键词：TypeScript|JavaScript|Python|Go|Java|Rust|React|Vue|Angular|
               Node|Express|Django|Spring|PostgreSQL|MySQL|MongoDB|Redis|
               Docker|K8s|Webpack|Vite|npm|pip|maven|gradle

# 新增 — architecture
含分层描述/模块划分/目录结构图
  → 归入 architecture
  判定：出现目录树（├── / └──）或模块清单（≥ 3 个模块名 + 职责描述）

# 新增 — conventions
含命名规范/代码风格约定/编码规则
  → 归入 conventions
  判定：出现"命名" / "规范" / "约定" / "必须" / "禁止" + 具体规则描述

# 新增 — knowledge（兜底）
含经验教训/历史遗漏/常见错误/用户偏好/模式总结
 或：不匹配上述任何分类但非空的段落
  → 归入 knowledge
  判定：出现"历史" / "遗漏" / "教训" / "常见错误" / "注意" / "偏好" / "always"
  或：内容未被其他 8 类匹配
```

### 分类歧义示例

```
源文档：
  ## 技术架构
  - 前端: React + TypeScript
  - 后端: Node.js + Express
  - 数据库: PostgreSQL
  - 分层: Controller → Service → Repository

判定：
  → 同时命中 tech-stack（React/TypeScript/Node/PostgreSQL）和 architecture（分层描述）
  → architecture 优先级 > tech-stack → 归入 architecture
  → 但 tech-stack 信息也有价值 → architecture 合并后，提取其中的技术栈行追加到 tech-stack.md
```

---

## 合并策略详细设计

### Type 5: project-overview → architecture.md `## 项目概览`

**合并策略**: 段落级

```
源文档：
  # MyProject
  ## 项目背景
  MyProject 是一个电商平台...

目标 orch-spec/context/architecture.md：

  若无 ## 项目概览 章节 → 创建此章节，追加内容
  若已有 ## 项目概览 → 检查段落相似度：
    相似度 < 70% → 追加为新段落（注明来源文件）
    相似度 ≥ 70% → 标记 duplicate，跳过
```

### Type 6: tech-stack → tech-stack.md

**合并策略**: 行级

```
源文档提取到的技术栈：
  - 语言: Python, Go
  - 框架: Django, Gin
  - 数据库: PostgreSQL

目标 orch-spec/context/tech-stack.md：
  - 每个技术项与现有行比对
  - 已存在 → skip
  - 不存在 → 追加到对应章节（如 "## 语言"）
  - 章节不存在 → 创建章节后追加
```

### Type 7: architecture → architecture.md

**合并策略**: 章节级

```
源文档：
  ## 整体分层
  src/
  ├── api/       # API 层
  ├── services/  # 服务层

目标 architecture.md：
  已有 ## 整体分层 章节 → 读出现有内容：
    结构相同（api/services）→ duplicate, skip
    结构不同 → AskUserQuestion 确认合并方式
  无 ## 整体分层 章节 → 直接追加完整章节
```

### Type 8: conventions → conventions.md

**合并策略**: 行级

```
源文档提取到的约定：
  - 文件名小写下划线
  - API 路径 /api/v1/ 前缀

目标 conventions.md：
  - 逐行比对 → 已有 skip，新行追加到对应 ## 章节
```

### Type 9: knowledge → learnings.md + preferences.json

**合并策略**: 按内容子类型分流

```
knowledge 条目分析：
  含 "always_check" / "检查项" / "checklist"
    → 提取检查项 → preferences.json → always_check[]
  含 "偏好" / "preference"
    → 提取偏好 → preferences.json → 对应键
  含 "优化规则" / "optimization"
    → 提取规则 → preferences.json → optimization.rules[]
  其他（经验教训/历史遗漏/模式总结）
    → learnings.md → 按主题追加段落
```

**learnings.md 段落去重规则**：
- 提取段落首句作为摘要
- 与 learnings.md 已有段落的首句比对
- 相似度 ≥ 80% → duplicate，跳过
- 相似度 < 80% → 追加段落

---

## 实现改动

### 涉及文件

| 文件 | 改动 |
|------|------|
| `skills/spec-migrate/SKILL.md` | **唯一需要改动的文件**（不再动 commands） |

### SKILL.md 改动详情

#### 步骤 1 扫描

**原内容** — 特征归类表（4 行）

**改为** — 特征归类表（9 行）+ 分类歧义消解规则 + 扫描范围扩展

#### 步骤 2 去重

**原有逻辑不变**（4 类去重保持）

**新增** — 9 种类型各自的去重逻辑（合并到原有步骤 2 的去重表格后）

#### 步骤 3 冲突确认

**原内容** — 仅对 data-models / glossary 的 conflict 提问

**改为** — 增加 architecture 和 preferences 的冲突提问。project-overview / tech-stack / conventions / knowledge 通常无冲突（仅追加），不需要提问。

#### 步骤 4 合并写入

**原内容** — 4 行合并策略表

**改为** — 9 行合并策略表（原有 4 + 新增 5）+ 目标文件不存在时的创建逻辑

#### 步骤 5 报告

**原内容** — 4 行统计表

**改为** — 按分组展示：Spec / Context / Knowledge 三组统计数据

#### 约束

追加 3 个 `<GATE>`：

```
<GATE>architecture 章节冲突必须 AskUserQuestion 确认</GATE>
<GATE>preferences.json 已存在的键不可覆盖（仅追加新键）</GATE>
<GATE>context 文件首次创建后必须同步更新 orch-spec/context/index.json 的 tags 索引</GATE>
```

---

## 预期效果

迁移前：`/spec-migrate "old-specs/"` 输出：
```
| scenarios | N | N | N | ✅ |
| data-models | N | N | N | ✅ |
| business-rules | N | N | N | ✅ |
| glossary | N | N | N | ✅ |
```

迁移后：`/spec-migrate "old-specs/"` 输出：
```
## Spec
| scenarios | N | N | N | ✅ |
| data-models | N | N | N | ✅ |
| business-rules | N | N | N | ✅ |
| glossary | N | N | N | ✅ |

## Context
| project-overview | N | N | N | ✅ |
| tech-stack | N | N | N | ✅ |
| architecture | N | N | N | ✅ |
| conventions | N | N | N | ✅ |

## Knowledge
| knowledge | N | N | N | ✅ |  (→ learnings.md + preferences.json)
```

---

## 与现有设计的兼容性

- **原有 4 类处理完全不变**：scenario / data-models / business-rules / glossary 的逻辑一行不改
- **入口不变**：`/spec-migrate "source_dir"` 用法不变，参数不变
- **报告向后兼容**：原有报告格式保留，新增 Context 和 Knowledge 两个分组在下方
- **不依赖新脚本**：所有合并逻辑在 SKILL.md 中以自然语言描述，knowledge-curator / context-inheritance 等现有机制自然使用迁移后的数据
