# Token 消耗深度分析 + 优化方案

**数据来源**: `token cost.txt` (2026-06-20)  
**模型**: deepseek-v4-flash  
**本轮成本**: $27.90 | 累计: $35.18

---

## 一、数据逐层剖析

### 1.1 整体分布

```
总 Token 流向（估算）:
┌──────────────────────┬──────────┬───────┬────────────────────────────┐
│ 层次                 │ Token    │ 占比  │ 说明                       │
├──────────────────────┼──────────┼───────┼────────────────────────────┤
│ 主会话 Input         │ 966K     │ —     │ 编排器读取的所有上下文     │
│ 主会话 Output        │ 189K     │ —     │ 编排器自身的输出           │
│ 子代理 Output        │ ~1,850K  │ —     │ 所有派遣 Agent 的输出合计  │
│ Cache Read           │ ~90M     │ —     │ 重复加载的缓存上下文       │
│ 合计有效输出         │ ~2,040K  │ 100%  │ 主会话 + 子代理            │
└──────────────────────┴──────────┴───────┴────────────────────────────┘
```

### 1.2 阶段消耗拆解

```
spec+clarify        9K   ▏ 0.5%  ← 非常高效
test-design+design 143K  ████ 7.8%
contract            65K  ██ 3.5%
task                91K  ██▌ 5.0%
execute (后端)     487K  █████████████ 26.4%  ┐
execute (前端)    1037K  ████████████████████████████ 56.2%  ├ 82.6%
code-review         82K  ██▌ 4.5%
                    ─────
                  1,914K
```

**核心发现**: Execute 阶段独占 82.6%，其中前端是后端的 2.1 倍。

### 1.3 每阶段人均消耗

| 阶段 | 总 Token | Agent 数 | 每 Agent 均耗 | 评估 |
|------|---------|---------|-------------|------|
| spec+clarify | 9K | 1-2 | ~5-9K | ✅ 高效 |
| test-design+design | 143K | 2 | ~72K | ⚠️ 偏高 |
| contract | 65K | 1 | ~65K | ⚠️ fullstack 必须，可接受 |
| task | 91K | 1 | ~91K | ⚠️ 41 任务拆解偏高 |
| execute (后端) | 487K | ~20 | ~24K/任务 | ✅ 低于基线 |
| execute (前端) | 1,037K | ~21 | ~49K/任务 | 🔴 后端2.1倍 |
| code-review | 82K | ? | — | ⚠️ 需看审查次数 |

---

## 二、浪费热点识别

### 🔴 热点 1: 前端 Execute 是后端 2.1 倍（+550K 浪费）

**现象**: 前端每 Task 49K vs 后端 24K

**根因推测**:
1. 浏览器测试（Playwright）每 Task 独立运行 → 每次 5-10K
2. 前端 TDD 循环含 RED-BROWSER → GREEN-BROWSER 额外阶段
3. 组件样式/模板代码通常比后端逻辑更冗长（代码产出多，但产出也是 token）

**优化空间**: 浏览器测试批量到批次级 → 预估省 150-200K

### 🔴 热点 2: Cache Read 90M — 隐藏成本（约 $1.26）

**现象**: 每个 Agent 派遣都重新加载完整上下文（CLAUDE.md + skills + rules + agent prompts）

**计算**:
```
~45 次 Agent 派遣 × ~2M cache read/次 = ~90M
```

每次派遣的 ~2M cache read 包含:
- `CLAUDE.md`（用户级 + 项目级）: ~5K
- 22 skills 的 SKILL.md: 每个 2-15K，合计约 150K
- Agent 定义: 每个 2-10K，合计约 80K
- Rules 文件: ~20K
- 其他 hooks/references: ~30K
- 上下文继承/注入: ~50K
- **总计每次派遣加载约 300-500K 上下文 × 45 次 = 13-22M**
- 其余 70M+ 来自对话历史缓存重读

**优化空间**: 减少 Agent 派遣次数（合并小任务）→ 预估省 20-30M cache read

### 🟡 热点 3: 主会话 Input 966K（编排器过载）

**现象**: 编排器自身消耗 ~1.15M (966K in + 189K out)

**根因**:
- 编排器为每个 Task 构造注入上下文（读 tasks.md + design.md + templates）
- 编排器处理每个子代理的返回结果
- 编排器执行步骤间状态持久化（eval.json 写入）
- 编排器生成最终总览（虽然已添加模板，但仍需读取 eval.json）

**优化空间**: 
- 注入上下文缓存化（同批次 Task 复用注入内容）→ 省 100-150K
- eval.json 增量写入而非全量构造 → 省 50-80K

### 🟡 热点 4: Task 阶段 91K（拆解过重）

**现象**: 1 个 tasker agent 消耗 91K 生成 41 个 Task

**分析**: 91K 对于生成结构化 Task 列表偏高。理想水平应在 40-60K。

**根因**: tasker 可能需要读取 design.md / contract.md / spec 才能生成任务。如果 design.md 较长，tasker 的读取量就大。

**优化空间**: tasker 上下文注入精简 → 省 20-30K

---

## 三、优化方案（按收益排序）

### P0: 前端 Execute 浏览器测试批量化

**预期节省**: 150-200K（execute 阶段 -15%）

**方法**: 修改 `agents/executor.md` 和 `skills/execute/SKILL.md`

```
当前: 每个前端 Task 独立运行 Playwright 浏览器测试
改为: 同批次前端 Task 完成后，统一运行一次浏览器测试
```

**影响**: 不改变测试覆盖，仅改变执行时机。对 TDD 快速反馈的影响可通过每 Task 的单元测试弥补。

### P1: 减少 Agent 派遣次数（Cache Read 削减）

**预期节省**: 20-30M cache read（约 $0.30-0.45）

**方法 A**: 合并小 Task
```
当前: 41 个 Task → 41 次 executor 派遣
目标: 合并变更 < 30 行的相邻 Task → 预估 35 次派遣
节省: 6 次 × 2M cache read = 12M
```

**方法 B**: 合并 test-design + design 为一次派遣（当前已并行，但仍是 2 个 Agent）
```
改为: 单一 code-architect agent 同时处理测试设计和架构设计
节省: 1 次 × 2M = 2M
```
⚠️ 此方法需要评估两个 Agent 职责重叠度

**方法 C**: code-review 从 per-Task 改 per-Batch（已在之前方案中设计，此次强化）

### P2: 编排器注入上下文缓存

**预期节省**: 100-150K 主会话 Input

**方法**: 修改 `skills/execute/SKILL.md` 上下文注入段

```
当前: 每个 executor 派遣时，编排器重新读取 tasks.md / design.md 构造注入内容
改为: 同批次 Task 共用一份注入上下文模板，仅替换 task-spec 差异部分
```

**实现**:
```bash
# 批次开始时一次性读取并缓存
batch_context = read(design_summary) + read(project_map) + read(exception_patterns)
for task in batch:
    inject = batch_context + task_spec  # 仅 task_spec 不同
    dispatch(executor, inject)
```

### P3: Task 阶段精简

**预期节省**: 20-30K

**方法**: tasker agent prompt 中明确"上下文已注入，不自行读取 design.md 全文"（与 executor 相同的优化）

---

## 四、优化效果预估

| 优化项 | 当前 | 目标 | 节省 |
|--------|------|------|------|
| 前端 execute | 1,037K | ~850K | 187K (18%) |
| 后端 execute | 487K | ~390K | 97K (20%) |
| 主会话 Input | 966K | ~750K | 216K (22%) |
| Task | 91K | ~60K | 31K (34%) |
| Cache Read | 90M | ~60M | 30M (33%) |
| **总有效 Token** | **~2,040K** | **~1,500K** | **540K (26%)** |
| **估算成本** | **$27.90** | **~$20** | **~$8** |

> 注：execute 节省基于之前已实施的 executor 优化 + 本次浏览器测试批量化叠加。

---

## 五、改动用文件清单

| 文件 | 改动 | 对应优化 |
|------|------|---------|
| `skills/execute/SKILL.md` | 浏览器测试批量化 + 注入上下文缓存化 | P0 + P2 |
| `agents/executor.md` | 前端 Task 浏览器测试指令调整 | P0 |
| `skills/execute/references/token-efficiency-guide.md` | 追加浏览器测试批量化条目 | P0 |
| `skills/workflow/references/agent-dispatch-code.md` | code-review 批次级审查强化 | P1-C |
| `agents/tasker.md` | 上下文用量精简 | P3 |

---

## 六、不改动项

| 排除项 | 理由 |
|--------|------|
| 减少 Task 数量（41→更少） | 任务拆解粒度取决于需求复杂度，不可人为压缩 |
| spec 阶段流程（9K） | 已非常高效，0.5% 占比没有优化价值 |
| contract 阶段（65K） | fullstack 必须，六维度审查不能跳过 |
| test-design + design 合并为单 Agent | 两个 Agent 职责不同（测试 vs 架构），合并可能导致质量下降 |
