# 项目级学习沉淀 — orch 插件

> 由 continuous-learning 步骤9 沉淀。本文件为**插件自身能力优化模式**的知识库，供后续插件迭代复用。
> 最近更新：2026-08-01（plugin-capability-optimization 元任务）

---

## 北极星原则（最高优先，本元任务核心成果）

**约束 = 护栏（防坠落），不是牢笼（限奔跑）。**

插件存在的意义是在**最大化发挥模型自身能力**的前提下提供项目实现的流程约束；任何约束若削弱模型思考深度、探索自由或创造性，即为反模式（cage），需降级为建议或移除。

审查准则：
```
IF 约束仅限定"流程顺序/产出存在"   → guardrail（护栏），保留
IF 约束限制"思考深度/探索方式"     → cage（牢笼），降级为建议
```

### 北极星审查结论（NSP-001~007）— 2 降级 + 5 保留

| constraint_id | 约束 | 判定 | 处置 |
|---------------|------|------|------|
| NSP-001 | 收到指令后立即调用 Skill(workflow)，禁止调用前任何代码探索（start-dev.md:12） | **cage** | 降级为建议 |
| NSP-002 | 上下文优先…仅当注入信息不足时才补充 Read 原文（tasker.md:24） | **cage** | 降级为建议 |
| NSP-003 | 禁止主上下文直接编码，每 Task 通过子代理 | guardrail | 保留 |
| NSP-004 | SKILL_PREREQUISITES 阶段门控 | guardrail | 保留 |
| NSP-005 | 不能跳过 RED 阶段 / 覆盖率 ≥85% | guardrail | 保留 |
| NSP-006 | TEST-VERIFY 覆盖率 100% 禁止输出 | guardrail | 保留 |
| NSP-007 | 测试定义 WHAT 不限制 HOW | guardrail | 保留 |

**教训**：NSP-001/002 均为 token 时代残留——为省 token 而限制探索，如今成本不关注时应立即清理。任何新约束上线前必须过北极星审查。

---

## 架构决策（ADR，2026-08-01 沉淀）

| ADR | 决策 | 价值 |
|-----|------|------|
| ADR-002 | **stage-contracts 集中化**：scripts/lib/stage-contracts.js 单源维护 STAGE_ORDER/STAGE_OUTPUTS/SKILL_PREREQUISITES/EXEMPT_*，workflow-gate/stage-gate/session-start 共用 | 消除两处阶段映射漂移（F10 根因） |
| ADR-008 | **verdict.js 判定函数集中**：judgeCoverage/judgeRate/judgeAutoResolve，覆盖率以实测为准不接受自我报告 | 支撑 TC-S4-03/04、TC-S6-02..07 行为断言 |
| ADR-001 | tdd-guide 保留文件 + 注册 AGENTS.md + 标注 deprecated + 划清与 code-reviewer 边界 | 弃用组件软下线，三态并存 |
| ADR-004 | 自检入口 = Node 脚本 scripts/self-check.js + commands/self-check.md，命令目录自动发现 | 复用 hooks Node 基础设施 |
| ADR-005 | 北极星审查：start-dev.md:12 与 tasker.md:24 降级为建议，其余 GATE 保留 | 见北极星原则 |
| ADR-003 | instinct observer 激活（observe.js + observe.sh + hooks.json 注册） | 元任务含自主进化能力优化 |
| ADR-006 | STAGE_OUTPUTS[9] 用项目级相对路径 '../context/learnings.md' + 伪产出 completion-report | path.join 归一化 |
| ADR-007 | sync-prompt-defense.py 全量清除再单次插入（count=0 幂等） | 修复 F5 重复节清不净 |

---

## 质量模式（插件自检回归）

**自检命令**：`node scripts/self-check.js` — 5 大块验证（orchestration/agents/skills/tdd_loop/commands_hooks），`--json` 输出结构化报告。配套 `tests/test-suite.py`（Python 冒烟）+ `tests/hooks-smoke.test.js`（hook 行为）。

**本元任务质量数据**：47 TC 全 PASS；29 TV 独立复核 28 VERIFIED + 1 PARTIAL（TV-S6-02 流转率原值需活体工作流复测）；18 项薄弱环节全部闭环（P0×2/P1×2/P2×2/F1-F12）；self-check 5/5 PASS。

**模式规则**：
- **插件变更后必须运行 `node scripts/self-check.js` 回归**（护栏，防回归）
- 判定函数以实测为准，不接受 execute/tester 自我报告（verdict.js 原则）
- 覆盖率高必须有命令输出，修复必须有 grep/运行验证（拒绝"应该/可能"）

---

## 插件能力优化模式（本类元任务专属）

对插件本体做能力优化时，采用以下模式：

1. **探索审计先行**：agents-audit / skills-audit / key-files 三份审计定位薄弱环节（P0/P1/P2/F1-F12），再动刀。
2. **只修审计定位项**：不做无关重构（约束1）。
3. **18 项薄弱环节分类**：悬空引用（P0）、缺 GATE/索引（P1）、未激活配置（P2）、注册表/命名/文档漂移（F1-F12）。
4. **集中化消除漂移**：阶段映射、判定函数、prompt 防御均收敛到单源文件（ADR-002/007/008）。
5. **弃用软下线**：deprecated 标记而非硬删除（ADR-001）。
6. **回归闭环**：self-check 5 块 + test-suite.py + hooks-smoke 三件套。

---

## 用户关键决策（本元任务）

| 决策 | 内容 | 沉淀位置 |
|------|------|---------|
| 拓扑 | 全量优化 5 大块（workflow 编排/agent 体系/skills 指令/TDD 闭环/commands+hooks） | 后续元任务继承 |
| 模式 | standard + needs_database=false（插件自身无需数据库） | preferences |
| 智能 gate | 规则自决（auto 4 类自动补偿）+ 白名单人工（manual 4 类暂停） | preferences |
| 北极星 | 约束 = 护栏非牢笼，不限制模型能力 | always_check |
| token | 不关注 token 消耗，专注能力优化（规则4） | 元任务特有 |
