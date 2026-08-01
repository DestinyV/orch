# 插件本体全方位能力优化 需求文档

**版本**：1.0
**日期**：2026-08-01
**状态**：已确认
**需求类型**：元任务（meta-task）— 优化 orch 插件自身

---

## 澄清状态: socratic_done
## 最终模糊度: 20%
## 实体稳定性: 47%

## 工作模式

- 模式：standard
- TDD要求：必须执行
- 子代理要求：必须使用
- 测试覆盖要求：≥85%
- 设计图：跳过
- 触发原因：用户明确要求（全方位优化，不关注 token）
- 影响范围：无跳过步骤

## 项目模式

- **project-mode**: backend（插件本体为 Node/TypeScript 工具链）
- **needs-database**: false
- **sql-dialect**: 不适用

## 项目文档约束

### 已发现文档

| 文件 | 状态 | 关键内容摘要 |
|------|------|-------------|
| CLAUDE.md | 已读取 | 22 Skills/25 Agents/14 Commands 声明；13 步工作流；阶段纪律 |
| README.md | 已读取（过时） | 宣称 11 skills/9 agents、/orch:sdd-dev 入口（实际 22/26、/start-dev） |
| AGENTS.md | 已读取（过时） | 宣称 25 agents（磁盘实际 26，缺 tdd-guide） |
| .claude-plugin/README.md | 已读取（过时） | 宣称 18 skills/12 commands（实际 22/14） |

### 项目自述架构

- **架构模式**：SDD+TDD 13 步工作流编排（定义层→编排层→运行时层→校验层→配置层→持久层）
- **模块划分**：skills/（22）+ agents/（26+1）+ commands/（14）+ hooks/（6）+ scripts/lib（8）
- **技术栈**：Node.js + TypeScript 工具链（Markdown 指令 + Node 脚本 + Python 辅助）
- **关键约定**：
  - `<GATE>...</GATE>` HARD-GATE 阶段纪律
  - Conventional Commit + Git Trailers
  - 每阶段完成立即写 .workflow-state.json / .workflow-eval.json

### 文档与代码冲突标注

| 冲突维度 | 文档声明 | 实际代码 | 处理策略 |
|---------|---------|---------|---------|
| Skills 数量 | README: 11 / AGENTS.md: 25 | 磁盘 22 | 以实际为准，同步文档 |
| Agents 数量 | AGENTS.md: 25 | 磁盘 26（含 tdd-guide） | 修复注册表口径 |
| Commands 数量 | .claude-plugin/README: 12 | 磁盘 14 | 以实际为准，同步文档 |
| Hooks 数量 | CLAUDE.md: observe.sh/suggest-compact | hooks.json: 6 项（二者未注册） | F3/F4/F6 修复 |
| 入口命令 | README: /orch:sdd-dev | 实际 /start-dev | 同步文档 |

---

## 概述

**北极星原则（最高优先级）**：插件存在的意义是在**最大化发挥模型自身能力**的前提下提供项目实现的约束；约束绝不能造成模型能力被限制。约束 = 护栏（防坠落），不是牢笼（限奔跑）。本次所有优化必须用此原则审查——任何流程/阶段纪律/格式要求，若削弱模型思考深度、探索自由或创造性，即为反模式。

对 orch 插件本体进行全方位能力优化（**不关注 token 消耗**），系统化改进 5 大块，修复探索审计发现的 18 项薄弱环节（P0×2 / P1×2 / P2×2 / F1-F12），并建立插件自身的验证闭环。

---

## 核心功能（5 大块优化）

1. **工作流编排引擎** — 状态机 / 中断恢复 / HARD-GATE 卡点 / 调度逻辑
2. **Agent 体系（26 个）** — 提示词质量 / 派遣策略 / 审查能力 / 注册表口径
3. **Skills 指令（22 个）** — SKILL.md 完整性 / 可执行性 / 触发准确性 / 索引覆盖
4. **TDD 执行与测试闭环** — execute/test 阶段闭环 / 覆盖率验证 / 插件自身自检
5. **Commands + Hooks** — 14 命令 / hooks 注册表 / 自动化事件激活

---

## 场景列表

| 场景 | 描述 | Case数 | 优先级 |
|------|------|--------|--------|
| S1 工作流编排引擎优化 | 阶段门控完整性/中断恢复/HARD-GATE | 5 | 高 |
| S2 Agent 体系优化 | 注册表口径/frontmatter统一/Prompt防御幂等 | 5 | 高 |
| S3 Skills 指令优化 | 悬空引用修复/索引补全/GATE 对齐 | 5 | 高 |
| S4 TDD 执行与测试闭环 | 插件自检命令/覆盖率验证闭环 | 4 | 高 |
| S5 Commands + Hooks 激活 | 未注册 hook 激活/命令命名空间/文档同步 | 4 | 中 |
| S6 插件验证闭环建立 | 自检命令/CI 风格验证/全量跑通 | 3 | 高 |

详见：[场景文档](./scenarios/)

---

## 数据模型

本次优化不涉及用户业务数据持久化。数据模型为插件自身状态/配置结构（optimization.rules[]、hook 注册表、agent 注册表、stage 输出校验表）。

详见：[data-models.md](./data-models.md)

---

## 业务规则

核心约束：北极星原则审查、自动化边界（规则自决+白名单人工）、验收量化阈值、命名/格式约定对齐。

详见：[business-rules.md](./business-rules.md)

---

## 术语表

详见：[glossary.md](./glossary.md)

---

## 确认记录

### 确认轮次1（澄清）
日期：2026-08-01
- [x] 需求理解确认（全方位优化，不关注 token）
- [x] 拓扑确认（全量优化 5 大块）
- [x] 验收标准量化确认（流转率≥80%/达标率≥90%/恢复率≥80%/验证闭环/智能 gate）

### 确认轮次2（澄清）
日期：2026-08-01
- [x] 智能 gate 机制确认（规则自决+白名单人工）
- [x] 北极星原则确认（约束不限制模型能力）

### 确认轮次3（探索基线）
日期：2026-08-01
- [x] 综合发现清单确认（P0×2/P1×2/P2×2/F1-F12）
- [x] 场景列表确认（S1-S6）
- [x] 优化优先级确认（核心 spec 已确认）

---

## 多项目协作

- 协作模式：single
- 涉及项目：不涉及（插件自身单仓库）

---

## 归档状态

- **archived**: true
- **归档日期**: 2026-08-01
- **归档去向**: orch-spec/spec/（主规范库 v1.0）
- **归档日志**: orch-spec/spec/archive-log.md
