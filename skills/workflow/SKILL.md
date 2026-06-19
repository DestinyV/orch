---
name: workflow
description: |
  统一入口 + 流程编排（Workflow-Control 阶段）
  输入：需求描述（文本或需求ID）
  输出：完整工作流执行 + .workflow-state.json（状态追踪）+ .workflow-eval.json（效果评估+Token用量）
  功能：SDD+TDD工作流的唯一入口，接收需求后自动编排所有下游Skill的执行顺序，
  支持模式自动检测、并行分支调度、HARD-GATE卡点管控、自动补偿、中断恢复、效果评估与Token追踪。
---

# workflow — 流程编排引擎


## When to Use

- 新需求入口，自动编排从需求到归档的完整流程
- 需要中断恢复、状态追踪、效果评估

## 职责

SDD+TDD 工作流的**入口编排器**。步骤控制 → `${CLAUDE_PLUGIN_ROOT}/commands/start-dev.md`，内容管理 → 本文件。

## 通用规则

| 规则       | 策略                                                                           |
| ---------- | ------------------------------------------------------------------------------ |
| 失败处理   | 自动重试 1 次；仍失败 → AskUserQuestion（重试/跳过/人工/降级）                 |
| 状态持久化 | 每阶段完成后立即写入 `.workflow-state.json`，不依赖会话内存                    |
| Token 记录 | 每阶段完成后调用 `context-budget` 记录上下文消耗，记录到 `.workflow-eval.json` |
| 上下文监控 | 阶段切换时检测上下文余量，不足时建议 compact 或精简后续步骤                    |

<GATE>禁止在正式流程前执行代码探索，由 spec 内部负责。</GATE>
<GATE>禁止跳过阶段。即使已有 spec 目录，也必须从步骤0开始，由状态检测决定中断恢复。</GATE>

---

## 步骤0: 初始化

> JSON 数据格式定义: [`references/workflow-data-schema.md`](references/workflow-data-schema.md)

1. 接收需求 → 检查 `orch-spec/` 下 `.workflow-state.json`（存在则中断恢复）
2. project-mode：直接 AskUserQuestion 让用户从 [frontend / backend / fullstack / mobile] 中选择，**禁止通过分析项目或需求特征推断**
3. AskUserQuestion 确认：数据库类型/快速或标准/设计图偏好。fullstack 时追加确认：后端仓库路径/前端仓库路径/API base URL → 写入 `orch-spec/{req_id}/req-context/cross-repo.md`
4. 加载知识增强 → `preferences.json` → `always_check[]` 注入 spec
5. **加载自主优化规则** → `preferences.json` → `optimization.rules[]`（仅加载 `active` 且 `confidence ≥ 30` 的规则）：
   - 按 `injection_point` 分组（`workflow_step0` / `spec_prompt` / `design_prompt` / `execute_prompt` / `review_prompt`）
   - `workflow_step0` 规则 → 调整批次调度/并行度/阶段选择
   - 其他 injection_point → 暂存到 `.workflow-state.json` → `injected_optimizations[]`，供对应步骤注入
   - 所有注入规则的 ID 写入 `.workflow-eval.json` → `applied_optimizations[]`
   - <GATE>trial 状态规则（confidence < 30）禁止注入</GATE>
6. 初始化 `.workflow-state.json` + `.workflow-eval.json`
7. **上下文继承基线生成**（避免重复探索）：读取 `orch-spec/context/.exploration-state.json`，执行以下判断：
   - `.exploration-state.json` 不存在 → **首次运行**，步骤1 进入全量探索模式
   - `last_explored_sha` == `git rev-parse HEAD` → **项目代码未变更**，进入增量探索模式（只匹配关键词继承 context，跳过全部代码扫描）
   - `last_explored_sha` ≠ HEAD → **代码有变更**，进入增量探索模式（继承 context + 只扫描 `git diff --name-only` 的变更文件）
   - 然后按 [`references/context-inheritance-protocol.md`](references/context-inheritance-protocol.md) 执行：
     - 从需求描述提取关键词 → 匹配 `index.json` tags → 确定可继承的 context sections
     - 匹配 `requirements.yaml` 中的历史需求 → 确定可继承的相似需求 req-context
     - 生成 `orch-spec/context/.baseline-context.json`（继承基线，供 code-explorer 增量探索使用）
     - 对 code-explorer 的 prompt 注入 `baseline_context: {基线内容}`
8. 检测需求模糊度 → 模糊 > 0.2 时派遣 `clarify`；否则级联 `spec`

### 步骤0.5: 苏格拉底澄清

<GATE>模糊度 > 0.2 时不允许跳过澄清。</GATE>

```bash
Skill("orch:clarify", args="{requirement_desc}")
```

产出校验：`clarification.md` 存在且含 `final_ambiguity`。完成后自动级联 `spec`。

### 流持续化检查

<GATE>检测到未完成状态时提示用户，不允许静默退出。</GATE>

```bash
for f in orch-spec/*/.workflow-state.json; do
  [ -f "$f" ] || continue
  STATUS=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('status',''))" 2>/dev/null)
  [ "$STATUS" = "in_progress" ] && echo "[INFO] 工作流进行中: $(basename $(dirname $f))"
done
```

---

## 步骤1-9: 督导闭环

> 每阶段输入/输出契约、校验、纠正措施: [`references/flow-execution-reference.md`](references/flow-execution-reference.md)
> 每步骤 Agent 派遣: [`references/agent-dispatch-code.md`](references/agent-dispatch-code.md)

每阶段：**前置校验 → 派遣 → 产出校验 → Token记录 → 纠正**。

<GATE>全部步骤 1→9 必须依次执行完毕，禁止在中间步骤停止或声明需求完成。每步完成后立即执行 agent-dispatch-code.md 中的"阶段完成记录"写入 eval.json，再进入下一步。</GATE>

<GATE>每阶段完成后必须写入 `.workflow-eval.json` 追加 stage 数据。stages[] 为空时不允许进入下一阶段。</GATE>

| 步骤                      | 前置                                  | 产出                                                                      | 记录                               | 纠正               |
| ------------------------- | ------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------- | ------------------ |
| 1 spec                    | state.json 已初始化                   | requirement/scenarios/data/business/glossary 非空 + 模式标签 + 异常场景   | stage/stats/agent 写入 eval.json   | 缺失回溯           |
| 2-3 parallel              | scenarios 含 TEST-VERIFY              | test-spec非空+fixtures可解析 / design.md含架构+组件+决策                  | stage/stats/agent×2 写入 eval.json | 缺失重新派遣       |
| 3.5 contract              | design done + fullstack               | contract.md + review-report无blocking                                     | stage/stats 写入 eval.json         | blocking修复后重审 |
| 4 task                    | design.md 存在                        | tasks.md 每Task有 provides/consumes/验收标准/DAG                          | stage/stats 写入 eval.json         | 补全后继续         |
| 5 execute                 | tasks.md存在 + TDD出口验证            | src/非空 + execution-report.md + TDD四阶段日志(RED/GREEN/REFACTOR/REVIEW) | stage/batch_stats 写入 eval.json   | 回溯/补测试/拆批次 |
| 5.5 exception             | 后端/全栈自动                         | 异常代码生成                                                              | —                                  | —                  |
| 6 test                    | src/存在 + report存在                 | testing-report.md存在 + E2E执行                                           | stage/stats/agent×2 写入 eval.json | 失败回execute      |
| 7 archive                 | 全部测试通过                          | 主规范已合并 + archive-log.md                                             | stage/stats 写入 eval.json         | 失败回溯           |
| 8 evaluation | archive done + eval.json 含全阶段数据 | diagnosis字段已写入 + context-budget + cost | 汇总诊断报告 | stages[]为空则回溯 |
| 9 continuous-learning | evaluation done | orch-spec/patterns/ + preferences.json 更新 | — | — |

<GATE>步骤8(evaluation)和步骤9(continuous-learning)不可跳过。archive完成后必须自动执行。</GATE>

---

## Agent 派遣总览

<GATE>以下派遣指令必须逐条执行。读取并执行 `references/agent-dispatch-code.md` 中的全部 Agent() 调用，禁止跳过任何步骤。</GATE>

| 批次      | 步骤    | Agent                                  | 调度策略                                                                       |
| --------- | ------- | -------------------------------------- | ------------------------------------------------------------------------------ |
| 批次1     | 1       | `code-explorer` ×N                     | **根据探索深度分级**：L0(1 Agent) / L1(2 Agent) / L2-L3(3 Agent 并行) 参见 `references/context-inheritance-protocol.md`。全部完成后合并 + 生成 req-context/ + project-map.json |
| **批次2** | **2-3** | **`test-designer` + `code-architect`** | **两 Agent 同时 `run_in_background=true`，互不阻塞**                           |
| —         | 3.5     | `contract-creator`                     | 批次2 全部完成后串行，仅 fullstack                                             |
| —         | 4       | `tasker`                               | 批次2+3.5 完成后串行                                                           |
| 批次3     | 5       | `executor` ×N + `code-reviewer`        | 批次4 完成后，同批次内无依赖 Task 并行启动。**每 batch 完成后执行微进化检查点**（`references/intra-workflow-adaptation.md`） |
| —         | 5.5     | `exception`                            | 步骤5 子过程自动                                                               |
| —         | 6       | `tester` ×3 + `test-verifier`          | **四路并行**（P4.4 优化）：集成/E2E/性能三路 tester 并行，**每个完成后立即启动对应 test-verifier**（不等待全部完成，提前发现失败） |
| —         | 7       | `archiver`                             | 步骤6 完成后串行                                                               |
| —         | 8       | evaluation                             | **双路并行**：`context-budget` 估算 + `cost` DB 实记同时跑，后合并诊断对比     |
| —         | 9       | `knowledge-curator`                    | 步骤8 完成后串行                                                               |

| 辅助 Agent           | 触发条件                                           | 集成点         |
| -------------------- | -------------------------------------------------- | -------------- |
| `clarifier` | 模糊度 > 0.2                                       | clarify        |
| `debug`             | Task 失败 ≥ 2 次                                   | execute        |
| `e2e-runner`         | 前端/全栈 E2E                                      | test           |
| `loop-operator`      | Task > 3 批次                                      | execute        |
| `planner`            | 用户要求                                           | design         |

### 需求上下文双层次

| 层次 | 路径 | 生命周期 | 生成 | 消费 |
|------|------|---------|------|------|
| 项目级 context | `orch-spec/context/` | 跨需求持久 | archive 步骤6 同步 | 步骤1 Layer 1 按关键词匹配 |
| 需求级 req-context | `orch-spec/{req_id}/req-context/` | 单次工作流 | 步骤1 末尾 | design → execute → test 阶段间传递 |

---

## 中断恢复

检测 `orch-spec/{req}/.workflow-state.json`：

1. 无文件 → 新需求，步骤0开始
2. JSON 校验失败 → 默认从上一 done 阶段续接
3. 最后 done → 验证产出文件存在，缺失标记 failed + AskUserQuestion
4. 最后 failed → AskUserQuestion（重试/跳过/查看错误）
5. 步骤5 中断：检测 `execute.status=in_progress` → 列出已完成 Task，从未完成恢复
6. 上下文过大时，中断恢复前先调用 `Skill("orch:context-budget")` 审计 → `Skill("orch:compact")` 建议 compaction 后再继续

## Checkpoint 更新协议（P4.2）

每 batch 完成后必须更新 `.workflow-state.json` 的 progress 字段：

```yaml
# batch 完成后的更新
execute:
  status: in_progress
  current_batch: 2
  progress:
    completed: 3
    total: 5
    checkpoint_reason: "batch-2-completed"  # 标识 checkpoint 原因
    verification_hash: "a1b2c3d"            # 已完成 Task 产物的 git hash
  batches:
    - batch: 1
      tasks: ["Task-1", "Task-2"]
      status: done
      completed_at: "2026-06-19T10:30:00Z"
    - batch: 2
      tasks: ["Task-3", "Task-4", "Task-5"]
      status: in_progress
```

## 快速模式

跳过 test-design | 跳过 contract | execute 单审查/覆盖≥60% | test 精简（集成+E2E）。

## 关键约束

| ✅ 必须                    | ❌ 禁止                     |
| ------------------------- | -------------------------- |
| 状态实时持久化（含Token） | HARD-GATE 失败静默跳过     |
| 卡点暂停用户确认          | 模式锁定后更改             |
| project_mode 步骤0 锁定   | 跨越入口直接调用下游 Skill |
