# executor Token 消耗分析报告

**问题**: orch:executor 每个子任务消耗 ~100K token，产出代码量很少  
**分析日期**: 2026-06-19  
**分析方法**: 静态分析 agent 定义 + skill 编排 + 上下文注入链路

---

## 根因总览（按影响排序）

| # | 根因 | 估算 Token 占比 | 严重度 |
|---|------|----------------|--------|
| 1 | TDD 四阶段固定开销过高 | 35-45K | 🔴 高 |
| 2 | 每 Task 独立派遣 code-reviewer | 20-30K | 🔴 高 |
| 3 | executor 内重复读取已注入上下文 | 10-15K | 🟡 中 |
| 4 | 验证命令运行+输出读取过度 | 10-15K | 🟡 中 |
| 5 | executor agent 定义本身过长 | 5-8K | 🟢 低 |
| 6 | 上下文注入超预期 | 5-15K | 🟡 中 |

---

## 详细分析

### 1. TDD 四阶段固定开销过高（35-45K token/task）

**证据**: `agents/executor.md` 第 91-98 行 + `skills/execute/SKILL.md` 第 132-143 行

每个 Task 强制经历 4 个阶段，每个阶段都要运行命令并读取输出：

| 阶段 | 操作 | Token 消耗 |
|------|------|-----------|
| RED | 读 test template → 写测试 → `npm test` → 读失败输出 → 确认失败信息明确 | ~8-12K |
| GREEN | 写最少实现 → `npm test` → 读通过输出 → 确认无回归 | ~8-12K |
| REFACTOR | 重构代码 → `npm test` → 读输出 → 可能多次迭代 | ~8-12K |
| REVIEW | `npm run lint` + `tsc --noEmit` + `npm test -- --coverage` → 读三项输出 | ~10-15K |

**问题**:
- 对于简单 Task（如"添加一个工具函数"），代码可能只有 20 行，但 TDD 四阶段开销是固定的
- 每个阶段要求"运行命令 + 读取输出 + 分析结果"，这本身就是 token 密集操作
- REFACTOR 阶段可能多次迭代（"每次改完立即运行 test"），每次都是额外开销

**建议**:
- 简单 Task（<50 行代码预期）合并 RED+GREEN 为单阶段
- REVIEW 阶段的 lint/typecheck 批量到批次级别（而非每 Task）
- 允许 executor 对 trivial 变更使用简化流程

---

### 2. 每 Task 独立派遣 code-reviewer（20-30K token/task）

**证据**: `skills/execute/SKILL.md` 第 178-226 行（规范审查 + 质量审查）

原设计是两阶段审查（规范+质量），每阶段各派遣一次 code-reviewer：
- 规范审查: `Agent(subagent_type="orch:code-reviewer", prompt="对 Task-{id} 的代码进行规范审查...")`
- 质量审查: `Agent(subagent_type="orch:code-reviewer", prompt="对 Task-{id} 的代码进行质量审查...")`

虽然后来合并为单次综合审查（`subagent-protocol.md` 提到"两阶段审查合并"），但 code-reviewer agent 的 prompt 仍然很长，且会读取所有变更文件。

**估算**:
- code-reviewer system prompt: ~3K
- 审查 prompt + 文件路径: ~2K
- code-reviewer 读取代码文件: ~5-10K
- 审查报告输出: ~5-10K
- 修复循环（如有问题）: ~10K+

**建议**:
- 将 code-reviewer 从 per-Task 改为 per-Batch（批次级审查）
- 或者仅对标记 `@critical` 的 Task 派遣 code-reviewer
- 简单 Task 使用 executor 自审查（已有 REVIEW 阶段）

---

### 3. executor 内重复读取已注入上下文（10-15K token/task）

**证据**: `agents/executor.md` 第 68-75 行

executor agent 被告知要：
```
阅读 tasks.md 中当前 Task 的目标/交付物/验收标准
理解 design 的设计规范和接口定义
参考 code-architect 的架构蓝图
理解集成点
审查项目约定（CLAUDE.md）
```

但 execute skill 已经声明：
```
上下文由主代理在 prompt 中注入：
- summary.json — 当前 Task 的 project-map 子图 + 相关 decisions + 异常模式缓存
- task-spec — 当前 Task 的目标/交付物/验收标准/provides/consumes
```

**矛盾**: 主代理已经把 task spec 注入 prompt 了，executor 还要"阅读 tasks.md"和"理解 design 的设计规范"——这是重复工作。

**实际开销**: executor 用 Read 工具读取 tasks.md、design.md、project-context.md 等文件 → 每个文件 2-5K token，合计 10-15K。

**建议**:
- executor agent 定义中明确："上下文已注入 prompt，禁止自行读取 tasks.md / design.md / CLAUDE.md"
- 或改为：仅当注入上下文不足时才允许补充读取

---

### 4. 验证命令运行+输出读取过度（10-15K token/task）

**证据**: `skills/execute/references/verification-gate.md` + `agents/executor.md` 第 121-125 行

验证铁律要求每个声称必须附命令输出证据：

| 验证项 | 命令 | Token 消耗 |
|--------|------|-----------|
| 单元测试 | `npm test -- TC-X.X.X` | 输出 1-3K |
| 编译 | `tsc --noEmit` | 输出 0.5-2K |
| Lint | `eslint src/` | 输出 0.5-2K |
| 覆盖率 | `npm test -- --coverage` | 输出 2-5K |
| 类型检查 | `tsc --strict` | 输出 0.5-2K |

每个命令的输出被完整读取到 executor 的上下文中，合计 5-14K token。而且 REVIEW 阶段失败时可能重复运行。

**建议**:
- 命令输出只读取 exit code + summary line（如 ` | tail -5`）
- 仅在失败时才读取完整输出
- 覆盖率报告只读取 summary，不读取逐文件详情

---

### 5. executor agent 定义本身过长（5-8K token/次）

**证据**: `agents/executor.md` 共 148 行

agent system prompt 包含：
- 完整的 TDD 四阶段说明（含表格和示例）
- worktree 创建协议（5 种降级策略）
- 异常处理流程
- 代码完整性要求（含反例）
- 提交规范（Git Trailers）
- TDD 进度日志格式

每次派遣 executor 都要加载这 148 行作为 system prompt，约 5-8K token。

**建议**:
- 将 worktree 创建协议移到 reference 文件（按需读取）
- 将 Git Trailers 格式移到 reference 文件
- 合并重复的 TDD 说明（agent 和 SKILL.md 都在说）

---

### 6. 上下文注入超预期（5-15K token/task）

**证据**: `skills/execute/SKILL.md` 第 46-50 行

SKILL.md 声称注入 token 约 2K-5K，但实际注入内容包含：

```json
{
  "task": {
    "description": "详细任务描述",
    "provides": "提供的接口",
    "consumes": ["依赖的接口"],
    "acceptance_criteria": ["验收标准1", "验收标准2"],
    "covers": {"scenario": "...", "scene_id": "..."}
  },
  "context": {
    "relevant_design": "设计决策摘要",
    "relevant_spec": "BDD 场景摘要",
    "test_templates": ["test-*.template 内容"],
    "previous_batch_results": ["前批次结果"]
  }
}
```

当 design.md 包含详细的接口定义、test template 较长、或 project-map 子图较大时，实际注入轻松超过 10K token。

**建议**:
- 对注入内容做 token 预算限制（如 max 3K）
- test template 只注入路径，由 executor 按需读取
- design context 做更激进的摘要压缩

---

## Token 流向估算图（单个 Task）

```
┌─────────────────────────────────────────────┐
│ executor system prompt          ~5-8K       │
├─────────────────────────────────────────────┤
│ 上下文注入 (task+design+templates) ~8-12K   │
├─────────────────────────────────────────────┤
│ executor "理解与规划" 阶段        ~10-15K    │  ← 重复读取已注入上下文
│   - 读 tasks.md                              │
│   - 读 design.md                             │
│   - 审查项目约定                              │
├─────────────────────────────────────────────┤
│ RED 阶段                          ~8-12K     │
│   - 读 test template                         │
│   - 写测试代码                                │
│   - 运行测试 + 读失败输出                      │
├─────────────────────────────────────────────┤
│ GREEN 阶段                        ~8-12K     │
│   - 写实现代码                                │
│   - 运行测试 + 读通过输出                      │
├─────────────────────────────────────────────┤
│ REFACTOR 阶段                     ~8-12K     │
│   - 重构 + 测试                               │
├─────────────────────────────────────────────┤
│ REVIEW 阶段                       ~10-15K    │
│   - lint + typecheck + coverage               │
├─────────────────────────────────────────────┤
│ 实现总结输出                       ~3-5K     │
├─────────────────────────────────────────────┤
│ code-reviewer 派遣                 ~20-30K   │
│   - system prompt + 读代码 + 审查报告         │
├─────────────────────────────────────────────┤
│ 修复循环（条件）                   ~10-20K   │
├─────────────────────────────────────────────┤
│ 总计                             ~90-140K   │
│ 实际代码产出                       ~0.5-2K   │  ← 代码量很少
└─────────────────────────────────────────────┘
```

---

## 改进建议优先级

### P0: 立即见效

1. **executor 禁止重读已注入上下文** — 修改 `agents/executor.md`，明确"上下文已在 prompt 中，禁止用 Read 工具重复读取 tasks.md / design.md / CLAUDE.md"。预估节省 10-15K/task。

2. **命令输出只读摘要** — 修改验证门控：lint/typecheck/coverage 只读取 exit code + 最后 5 行（失败时才读全文）。预估节省 5-10K/task。

### P1: 短期优化

3. **code-reviewer 从 per-Task 改为 per-Batch** — 同批次的所有 Task 合并为一次审查派遣。预估节省 (N-1)×25K，N=批次 Task 数。

4. **简单 Task 跳过 REFACTOR 阶段** — 变更 <30 行时，GREEN 通过直接进入 REVIEW。

5. **上下文注入加 token 上限** — 注入内容 >5K 时自动截断 design context 和 test template 内容。

### P2: 架构改进

6. **executor agent system prompt 精简** — 将 worktree 协议、Git Trailers 格式移到 reference 文件按需读取。预估节省 2-3K/task。

7. **引入 Task 复杂度分级** — trivial/simple/medium/complex，trivial 使用极简流程（单阶段实现+自审查），预估节省 40-60K/trivial-task。

---

## 核心结论

executor 的 token 浪费不是单一原因，而是**"每 Task 独立全流程"设计在简单 Task 上的固定开销过大**。主要矛盾是：

> **固定流程开销 (~90K) vs 实际代码产出 (~1K)**

对于复杂 Task（200+ 行代码），这个比例可以接受；但对于简单 Task（10-30 行），开销/产出比高达 100:1。

最有效的改进方向是**引入 Task 复杂度分级**，让简单 Task 走轻量流程，将完整 TDD + code-reviewer 保留给复杂 Task。
