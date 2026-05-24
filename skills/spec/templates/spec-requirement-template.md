# [需求名称] 需求文档

**版本**：1.0
**日期**：[YYYY-MM-DD]
**状态**：已确认

---

## 工作模式

<!--
  🚧 此模式标识会被后续阶段（design、task、execute）读取并强制执行
  请不要手动修改，由 spec 技能自动生成
-->
- 模式：[standard | quick]
- TDD要求：[必须执行 | 可简化]
- 子代理要求：[必须使用 | 可跳过]
- 测试覆盖要求：[≥85% | ≥70%]
- 设计图：[按需 | 全部 | 跳过]
- 触发原因：[用户明确要求 / 默认标准模式]
- 影响范围：[跳过的步骤清单]

## 项目模式

<!--
  🚧 由 code-architect agent 在 design 阶段自动识别和设置
-->
- **project-mode**: [frontend | backend | fullstack]
- **needs-database**: [true | false]
- **sql-dialect**: [mysql | postgresql | sqlite | sqlserver | 未确定]（needs-database=true 时必填）

> 注：project-mode 和 needs-database 由 code-architect agent 在 design 阶段自动识别和设置。
> sql-dialect 由 spec 通过 AskUserQuestion 确认（needs-database=true 时），或由 design 自动检测。

## 项目文档约束 ⭐🆕

<!--
  🚧 由 spec 阶段的项目探索流程自动提取
  此章节记录项目自身声明的架构约定，后续阶段必须遵循
-->

### 已发现文档

| 文件 | 状态 | 关键内容摘要 |
|------|------|-------------|
| CLAUDE.md | [已读取/未发现] | [1-2 句话概括] |
| README.md | [已读取/未发现] | [1-2 句话概括] |
| ARCHITECTURE.md | [已读取/未发现] | [1-2 句话概括] |

### 项目自述架构

- **架构模式**：[从文档中提取，如 Clean Architecture / MVVM / 分层架构]
- **模块划分**：[从文档中提取]
- **技术栈**：[从文档中提取关键框架/库及版本]
- **关键约定**：
  - [约定1]
  - [约定2]
  - [约定3]

### 文档与代码冲突标注（如有）

| 冲突维度 | 文档声明 | 实际代码 | 处理策略 |
|---------|---------|---------|---------|
| [如：响应格式] | [{code,data,message}] | [纯HTTP状态码] | [以文档为准/以代码为准/待确认] |

---

## 概述

[需求的简要说明]

---

## 核心功能

- [功能1]
- [功能2]
- [功能N]

---

## 场景列表

| 场景 | 描述 | Case数 | 优先级 |
|------|------|--------|--------|
| [场景1] | [描述] | [N] | [优先级] |
| [场景2] | [描述] | [N] | [优先级] |

详见：[场景文档链接](./scenarios/)

---

## 数据模型

[主要数据模型的简要说明]

详见：[data-models.md](./data-models.md)

---

## 业务规则

[主要业务规则的简要说明]

详见：[business-rules.md](./business-rules.md)

---

## 术语表

详见：[glossary.md](./glossary.md)

---

## 确认记录

### 确认轮次1
日期：[YYYY-MM-DD]
- [ ] 需求理解确认
- [ ] 场景列表确认
- [ ] 核心功能确认

### 确认轮次2
日期：[YYYY-MM-DD]
- [ ] 场景细节确认
- [ ] 异常情况确认
- [ ] 数据模型确认

### 确认轮次3
日期：[YYYY-MM-DD]
- [ ] 最终规范确认
- [ ] 无遗漏问题确认

---

## 多项目协作 ⭐🆕

<!--
  当需求涉及多个项目/仓库时由 spec 填充
  单项目场景下标注"不涉及"
-->
- 协作模式：[single | monorepo | multi-repo | same-repo]（默认 single）
- 涉及项目：[不涉及 / project-a, project-b, project-c]
- 协作链路类型：[不涉及 / 上下游服务 | 前后端分离仓库 | 微服务集群 | Monorepo多Package]

> 注：协作模式=single 时，以下字段留空。非 single 时由 design 阶段生成详细协作计划。
