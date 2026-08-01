# Skills 指令深度审计报告

> 审计对象：`E:\YYWorkSpace\projects\orch\skills\`（22 个 Skill）
> 审计方式：全量探索 — 逐 SKILL.md 读取 + 参考文档交叉校验 + 占位符扫描
> 审计日期：2026-08-01
> 目的：能力优化任务的现状摸底，定位指令薄弱环节

---

## 1. 总体概况

| 指标 | 数值 | 说明 |
|------|------|------|
| Skill 目录总数 | **22** | 与 plugin.json 声明一致（22 个专业 Skills） |
| SKILL.md 存在 | **22/22 (100%)** | 无缺失、无空文件、无仅占位 |
| frontmatter（name+description） | 22/22 | 全部含 name 与 description |
| name 与目录名一致 | 22/22 | 无重命名不一致 |
| 含 <GATE> 硬约束 | **21/22** | 仅 cost 缺失 |
| 悬空引用 | **2 处** | execute、spec 各 1 处（详见 §3） |
| 有 references/templates 子目录 | 15/22 | 7 个 Utility skill 为单文件 |
| 占位符/TODO 伪信号 | 0 | 扫描命中的均为正常内容 |

**总体结论：指令完备度处于"高"水平。** 22 个 Skill 均有完整 SKILL.md，核心工作流 skill（spec/design/execute/workflow 等）含多阶段工作流、Agent 派遣代码、GATE 门控与参考文档速查表。无"空 SKILL.md / 缺失 / 仅占位"的严重问题。


---

## 2. 22 个 Skill 清单与质量评估

### 评估分档说明

| 档位 | 判定标准 |
|------|---------|
| **完整** | 有分阶段工作流 + Agent 派遣代码 + GATE 硬约束 + 参考文档/模板齐全 + 产出路径明确 |
| **良好** | 有工作流 + 部分约束，资源子目录较少但满足职责 |
| **需改进** | 存在悬空引用 / 关键信息缺失 / 覆盖不全 |

| # | Skill | 行数 | 职责 | 产出路径 | 质量 | 备注 |
|---|-------|------|------|---------|------|------|
| 1 | **workflow** | 204 | 统一入口 + 流程编排（步骤0-9 督导闭环） | .workflow-state.json + .workflow-eval.json | 完整 | GATE 最密集；含 agent-dispatch-code 派遣总览 |
| 2 | **spec** | 313 | 需求分析 → BDD 规范 | orch-spec/{req_id}/spec/ | **需改进** | 悬空引用 references/diagram-trigger-rules.md（§3.2） |
| 3 | **test-design** | 109 | TEST-VERIFY → 测试规范+fixtures | orch-spec/{req_id}/tests/ | 完整 | GATE: 覆盖率<100% 禁止输出 |
| 4 | **design** | 259 | 架构/组件/API/数据库设计 | orch-spec/{req_id}/design/ | 完整 | 22 个参考资源，最全之一 |
| 5 | **contract** | 96 | 接口契约定义+六维审查（fullstack） | orch-spec/{req_id}/contract/ | 完整 | 仅 fullstack 触发 |
| 6 | **task** | 122 | 设计 → 任务列表 | orch-spec/{req_id}/tasks/tasks.md | 完整 | TDD 任务配对约束 |
| 7 | **execute** | 344 | TDD 代码实现 + 两阶段审查 | src/ + execution/execution-report.md | **需改进** | 悬空引用 context-injection-protocol.md（§3.1） |
| 8 | **exception** | 130 | 异常模式扫描+代码生成（后端/全栈） | src/ + exception-report.md | 完整 | 零硬编码约束 |
| 9 | **test** | 95 | 集成/E2E/性能测试 + 闭环验证 | tests/ + testing/testing-report.md | 完整 | 四路并行（P4.4） |
| 10 | **archive** | 246 | 规范合并到主规范库 | orch-spec/spec/ + archive-log.md | 完整 | 含 context/ 同步脚本 |
| 11 | **continuous-learning** | 252 | 知识复利 + 自主进化规则 | orch-spec/context/learnings.md + preferences.json | 完整 | 5 维知识来源 + 偏差分析 |
| 12 | **scripts** | 254 | 工具优先策略（脚本批处理） | 脚本输出 | 完整 | 6 个内置脚本 |
| 13 | **spec-migrate** | 213 | 外部规范迁移导入主规范库 | orch-spec/spec/ + import-log.md | 完整 | 9 类内容归并策略 |
| 14 | **clarify** | 209 | 苏格拉底需求澄清 | orch-spec/{req_id}/spec/clarification.md | 完整 | 数学化模糊度评分 |
| 15 | **req-change** | 98 | 需求变更影响分析 | orch-spec/{req_id}/changelogs/ | 良好 | 无子目录，内容自洽 |
| 16 | **ralph-loop** | 155 | 自主 Agent 循环模式选择 | 循环执行结果 | 良好 | 社区 origin，TRIGGER 英文 |
| 17 | **context-budget** | 192 | 上下文窗口占用审计 | 报告 + .workflow-eval.json | 良好 | 社区 origin，write-to-eval 模式 |
| 18 | **cost** | 182 | Token 用量/花费查询 | 查询结果 | **需改进** | 唯一无 GATE 的 skill（§3.3） |
| 19 | **depth** | 108 | 响应深度选择（25/50/75/100%） | 响应本身 | 良好 | 社区 origin，DO NOT TRIGGER 明确 |
| 20 | **compact** | 111 | 逻辑边界 compact 建议 | 建议提示 | 良好 | 社区 origin |
| 21 | **debug** | 69 | 因果追踪定位根因 | orch-spec/{req_id}/testing/debug-report.md | 良好 | 篇幅最短但流程完整 |
| 22 | **using-orch** | 97 | 入口导航 + Skill 触发规则 | 索引说明 | **需改进** | 可用 Skills 表仅列 6/22（§3.4） |


---

## 3. 薄弱环节明细

### 3.1 execute — 悬空引用（上下文注入协议）

- 位置：skills/execute/SKILL.md 第 56 行
- 引用：../workflow/references/context-injection-protocol.md
- 实际：workflow/references/ 下不存在该文件，同名文件为 **context-inheritance-protocol.md**
- 影响：executor 按此路径读取"上下文注入格式"会失败，上下文注入模式（4K/task 预算）失去文档支撑
- 根因：文件重命名后引用未同步更新

### 3.2 spec — 悬空引用（设计图触发规则）

- 位置：skills/spec/SKILL.md 「可视化确认」章节
- 引用：references/diagram-trigger-rules.md
- 实际：spec/references/ 下不存在该文件；真实文件在 **skills/design/references/diagram-trigger-rules.md**
- 影响：spec 阶段判断 ER 图/流程图/决策树触发条件时，引用指向不存在的本目录文件
- 对比：task/contract/archive 三个 skill 均正确使用 ../design/references/diagram-trigger-rules.md 相对路径，仅 spec 用错为本地路径
- 修复建议：改为 ../design/references/diagram-trigger-rules.md，或复制一份到 spec/references/

### 3.3 cost — 唯一无 GATE 硬约束

- 位置：skills/cost/SKILL.md
- 现状：约束段仅用 "## 约束" 普通列表（优先使用 cost_usd 列 / 跨行查询先取快照 / 不编造数据 / 不硬编码定价）
- 对比：其余 21 个 skill 均用 <GATE> 标记硬性禁止项
- 影响：约束强度弱于其他 skill，跨行 SUM 高估、硬编码定价等高风险操作缺乏硬门控标识
- 修复建议：将"禁止直接 SUM(cost_usd)"与"禁止硬编码模型定价"提升为 <GATE> 标记

### 3.4 using-orch — 可用 Skills 索引不全

- 位置：skills/using-orch/SKILL.md 「可用 Skills」表格
- 现状：仅列出 6 个核心工作流 skill（spec/design/task/execute/test/archive）
- 实际：插件共 22 个 skill，未列出其余 16 个（workflow/clarify/contract/exception/scripts/spec-migrate/test-design/context-budget/depth/compact/cost/ralph-loop/debug/req-change/continuous-learning/using-orch 自身）
- 影响：该 skill 自称"入口导航，列出所有可用 Skills 及其触发条件"，但 16/22 的 skill 无法通过它被发现；新用户会漏掉 Utility 与异常处理能力
- 修复建议：补全 22 个 skill 的触发条件表，或改为动态引用 plugin 元数据

### 3.5 触发描述格式不统一（系统性观察，非缺陷）

| 类型 | Skill | 特征 |
|------|-------|------|
| **显式 TRIGGER**（英文） | using-orch / cost / depth / compact / context-budget / ralph-loop | description 含 TRIGGER when / DO NOT TRIGGER when，利于跨平台自动触发 |
| **功能式描述**（中文，输入/输出） | spec / design / execute / test / task / test-design / contract / archive / exception / clarify / req-change / continuous-learning / spec-migrate / scripts / debug / workflow | 描述"是什么 + 输入输出"而非"何时触发"；触发主要依赖 workflow 编排，弱于社区 skill 的关键词触发 |
| 说明 | — | 核心工作流 skill 由 workflow 阶段门控调度，不强依赖关键词触发，故**非缺陷**；但移植到非 Claude Code 平台（Cursor/Gemini/Codex）时，缺失 TRIGGER 关键词会削弱自动触发能力 |

### 3.6 continuous-learning — 观测层默认关闭

- 位置：skills/continuous-learning/config.json
- 现状：observer.enabled = false（instinct 学习层 hook 级会话观察未启用）
- 影响：CLAUDE.md 宣称"continuous-learning v2 含 instinct 学习层（hook 级会话观察 + 原子 instincts）"，但观测层默认关闭，instinct 学习实际未运行
- 修复建议：确认是否有意关闭；若能力优化目标含"自主进化"，应启用 observer 或移除未启用配置


---

## 4. 资源分布（references/templates/prompts/scripts 规模）

| Skill | 子目录资源文件数 | 说明 |
|-------|-----------------|------|
| execute | 24 | prompts/ + references/（TDD/质量/Git/设计模式）最全 |
| spec | 24 | references/ + templates/（8 类规范模板 + diagrams） |
| design | 22 | references/（数据库/架构/组件/设计令牌）+ templates/ |
| test | 23 | references/ + templates/ + scripts/（Playwright 辅助） |
| continuous-learning | 19 | patterns/（9 类模式库）+ references/ + assets/ + scripts/ |
| task | 13 | prompts/ + references/ + templates/ |
| workflow | 11 | references/ + scripts/ + templates/ |
| scripts | 8 | scripts/（6 个内置脚本）+ references/ |
| contract | 5 | templates/ |
| test-design | 5 | prompts/ + references/ + templates/ |
| using-orch | 5 | references/（4 平台工具映射） |
| archive | 4 | references/ + templates/（含 diagrams） |
| ralph-loop | 3 | references/ + templates/ |
| exception | 2 | references/ |
| clarify | 2 | templates/ |
| **单文件** | 7 | compact / context-budget / cost / debug / depth / req-change / spec-migrate（职责自洽，无需子目录） |

---

## 5. 建议优先级

| 优先级 | 事项 | 涉及文件 | 动作 |
|--------|------|---------|------|
| **P0** | 修复 execute 悬空引用 | skills/execute/SKILL.md:56 | 改为 context-inheritance-protocol.md |
| **P0** | 修复 spec 悬空引用 | skills/spec/SKILL.md 「可视化确认」 | 改为 ../design/references/diagram-trigger-rules.md |
| **P1** | cost 补 GATE 硬约束 | skills/cost/SKILL.md | 高风险查询约束提升为 <GATE> |
| **P1** | using-orch 补全 22 skill 索引 | skills/using-orch/SKILL.md | 可用 Skills 表补全剩余 16 个 |
| **P2** | 统一触发描述格式 | 核心工作流 16 skill | 迁移时补充 TRIGGER when 关键词 |
| **P2** | continuous-learning observer 状态确认 | skills/continuous-learning/config.json | 确认 enabled=false 是否有意 |

---

## 6. 方法说明

- 全量模式：读取全部 22 个 SKILL.md（69-344 行）
- 交叉校验：提取每个 SKILL.md 中 markdown 链接 + 反引号引用共 **69 处**，逐一校验文件存在性，命中 2 处悬空
- 占位符扫描：TODO/FIXME/占位/lorem 等标记，命中的均为正常内容（约束语句"无遗留TODO"、报告格式示例、占位符扫描自审步骤）
- 未修改任何文件，本文件为唯一新增产物
