---
name: compact
description: |
  在逻辑边界建议手动 /compact（阶段切换、里程碑完成、上下文压力），替代任意的自动 compaction。
  TRIGGER when: 会话接近上下文限制（200K+）、多阶段任务切换（研究→计划→实现→测试）、完成主要里程碑、响应变慢。
origin: community
---

# Strategic Compact Skill

在合理逻辑节点建议手动 `/compact`，替代任意的自动 compaction。

## When to Use

- 会话接近上下文限制（200K+ tokens）
- 多阶段任务切换（研究 -> 计划 -> 实现 -> 测试）
- 完成主要里程碑后开始新工作
- 响应变慢或变得不连贯（上下文压力）

## How It Works

在逻辑边界建议手动 /compact，替代任意的自动 compaction。
通过 PreToolUse(Edit/Write) 钩子追踪工具调用次数，达到阈值时触发建议。

## 何时建议 Compact

- 运行长会话接近上下文限制（200K+ tokens）
- 多阶段任务切换（研究 → 计划 → 实现 → 测试）
- 在同一会话中切换不相关任务
- 完成主要里程碑后开始新工作
- 响应变慢或变得不连贯（上下文压力）

## 为什么 Strategic Compaction？

自动 compaction 在任意点触发：
- 经常在任务中间，丢失重要上下文
- 不感知逻辑任务边界
- 可能中断复杂的多步骤操作

逻辑边界 compaction：
- **探索后、执行前** — 压缩研究上下文，保留实现计划
- **完成里程碑后** — 为下一阶段全新开始
- **重大上下文切换前** — 清空探索上下文，进入不同任务

## Compact 决策指南

| Phase Transition | Compact? | Why |
|-----------------|----------|-----|
| 研究 → 规划 | Yes | 研究上下文占空间；计划是蒸馏输出 |
| 规划 → 实现 | Yes | 计划在 TodoWrite 或文件中；释放给代码 |
| 实现 → 测试 | Maybe | 测试引用最近代码时可保留；切换焦点时 compact |
| 调试 → 下一功能 | Yes | 调试痕迹污染无关工作的上下文 |
| 实现中途 | No | 丢失变量名、文件路径、部分状态代价大 |
| 失败方案后 | Yes | 清空死胡同推理再试新方法 |

## Compact 后什么保留

| 保留 | 丢失 |
|------|------|
| CLAUDE.md 指令 | 中间的推理和分析 |
| TodoWrite 任务列表 | 之前读取的文件内容 |
| Memory 文件 (~/.claude/memory/) | 多步会话上下文 |
| Git 状态 | 工具调用历史 |
| 磁盘上的文件 | 用户口述的细微偏好 |

## 最佳实践

1. **规划后 Compact** — 计划在 TodoWrite 确定后，compact 开始新的实现阶段
2. **调试后 Compact** — 清空错误解决上下文再继续
3. **实现中途不 Compact** — 保留相关更改的上下文
4. **写入后 Compact** — 重要上下文先保存到文件或 memory
5. **使用 `/compact` 带摘要** — `/compact Focus on implementing auth middleware next`

## 上下文优化技巧

### 触发器懒加载
不在会话启动时加载完整 skill 内容，而是用触发器表映射关键词到 skill 路径：

| Trigger | Skill | Load When |
|---------|-------|-----------|
| "test", "tdd" | tdd-workflow | 用户提到测试 |
| "security", "auth" | security-review | 安全相关工作 |
| "deploy", "ci/cd" | deployment-patterns | 部署上下文 |

### 重复指令检测
常见重复来源：
- 同一规则同时在 `~/.claude/rules/` 和项目 `.claude/rules/`
- skills 重复 CLAUDE.md 指令
- 多个 skills 覆盖重叠领域

## 与 context-budget 配合

先运行 `/context-budget` 了解当前上下文分布，再决定 compact 策略。

## 关键约束

- ✅ 仅在逻辑边界提出建议，不强制
- ❌ 实现中途不 compact（丢失关键状态的风险）
- ❌ 不自动执行 compact（用户决定）


## Output

compact 建议提示（不修改文件，仅输出建议）。

## Constraints

- 仅在逻辑边界提出建议，不强制
- 实现中途不 compact（丢失关键状态的风险）
- 不自动执行 compact（用户决定）

<HARD-GATE>实现中途禁止 compact | 仅提示建议不自动执行</HARD-GATE>