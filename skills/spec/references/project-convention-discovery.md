# 项目文档发现指南

> 适用于 orch 工作流中所有需要理解项目上下文的阶段。

## 理论基础

- **约定优于配置（Convention over Configuration）**：项目通过自描述文档声明约定，减少对代码推断的依赖
- **权威源原则（Single Source of Truth）**：文档声明的约定优先级高于代码推断——文档是项目意图的权威表达，代码可能偏离意图
- **最小上下文原则**：在 AI 辅助开发中，精准提取项目约定的成本远低于从代码中逆向推导

## 核心原则

文档声明的约定 > 代码推断的约定

## 文档优先级体系

按信息密度和 AI 编码相关性分层，最多读取 10 个文档：

| 层级 | 文档类型 | 信息价值 |
|------|---------|---------|
| P0 | CLAUDE.md / AGENTS.md / GEMINI.md | AI 编码的最高指令：架构原则、禁止事项、开发流程约束 |
| P1 | README.md / ARCHITECTURE.md / CONTRIBUTING.md | 项目核心知识：技术栈、模块边界、编码规范、分支策略 |
| P2 | docs/*.md / wiki/*.md / .cursor/rules/** | 深度领域文档：模块设计、API 规范、数据库规范 |
| P3 | package.json / pom.xml / go.mod | 技术栈声明：框架版本、依赖图谱、构建工具 |

## 提取维度

不同文档类型承载不同信息类别，提取时关注：

| 信息类别 | 来源文档 | 影响范围 |
|---------|---------|---------|
| 架构约束 | CLAUDE.md / ARCHITECTURE.md | 后续所有阶段的架构决策边界 |
| 编码规范 | CLAUDE.md / CONTRIBUTING.md | execute 的代码生成规则 |
| 测试要求 | CLAUDE.md / CONTRIBUTING.md | test-design / execute 的覆盖率基线 |
| 目录约定 | README.md / ARCHITECTURE.md | execute 的文件创建路径 |
| API 约定 | ARCHITECTURE.md / docs | contract 的接口设计约束 |
| 技术栈 | package.json / pom.xml | design 的技术选型边界 |

## 冲突处理

当文档声明与代码实现不一致时：

- 文档有近期更新痕迹 → 以文档为准（代码未同步）
- 文档引用的技术栈已废弃 → 以代码为准，标注"文档过时"
- 无法判断 → 标记 `DECISION_NEEDED`，提示用户确认

## 输出约定

项目分析输出应前置「项目文档摘要」，包含：已发现文档清单 | 项目自述架构 | 关键约定 | 冲突标注（如有）

Token 控制：最多 10 个文档，每文档 1-2 句摘要，不全文引用。
