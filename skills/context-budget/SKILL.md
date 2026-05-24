---
name: context-budget
description: |
  分析 Claude Code 上下文窗口占用情况（agents/skills/MCP/rules/CLAUDE.md），识别膨胀组件，产生优先级化的 Token 节省建议。
  TRIGGER when: 会话响应变慢、刚添加多个组件、运行 /context-budget 命令、想了解还有多少上下文余量。
origin: community
---

# Context Budget

分析与优化 Claude Code 上下文中每个加载组件的 Token 开销。

## 何时使用

- 会话性能感觉拖慢或输出质量下降
- 最近添加了很多 skills、agents 或 MCP servers
- 想了解实际还有多少上下文余量
- 计划添加更多组件，需要知道是否有空间
- 运行 `/context-budget` 命令

## 工作原理

### Phase 1: Inventory

扫描所有组件目录，估算 Token 消耗：

**Agents** (`agents/*.md`)
- 统计每文件的 lines × 1.3 tokens
- 提取 `description` frontmatter 长度
- 标记：>200 lines (heavy)，description >30 词 (bloated)

**Skills** (`skills/*/SKILL.md`)
- 统计每 SKILL.md 的 tokens
- 标记：>400 lines 的文件

**Rules** (`rules/**/*.md`)
- 统计每文件 tokens
- 标记：>100 lines 的文件

**MCP Servers** (`.mcp.json`)
- 统计配置的 servers 和 tool 总数
- 估算 schema overhead ~500 tokens/tool
- 标记：>20 tools 的 server、包装 CLI 的 server

**CLAUDE.md** (项目级 + 用户级)
- 统计每文件 tokens
- 标记：合并 >300 lines

### Phase 2: Classify

| Bucket | Criteria | Action |
|--------|----------|--------|
| **Always needed** | 被 CLAUDE.md 引用、支撑活跃命令 | Keep |
| **Sometimes needed** | 领域特定、未被引用 | Consider on-demand |
| **Rarely needed** | 无命令引用、内容重叠、无项目匹配 | Remove / lazy-load |

### Phase 3: Detect Issues

- **Bloated agent descriptions** — description >30 词 → 每次 Task 工具调用都加载
- **Heavy agents** — >200 lines → 每次 spawn 膨胀上下文
- **Redundant components** — skills 重复 agent 逻辑、rules 重复 CLAUDE.md
- **MCP over-subscription** — >10 servers，或包装 CLI 的 servers
- **CLAUDE.md bloat** — 啰嗦说明、过时章节、应归为 rules 的指令

### Phase 4: Report

```
Context Budget Report
═══════════════════════════════════════

Total overhead: ~XX,XXX tokens
Context window: 200K
Available: ~XXX,XXX tokens (XX%)

Component Breakdown:
┌─────────────────┬────────┬───────────┐
│ Component       │ Count  │ Tokens    │
├─────────────────┼────────┼───────────┤
│ Agents          │ N      │ ~X,XXX    │
│ Skills          │ N      │ ~X,XXX    │
│ Rules           │ N      │ ~X,XXX    │
│ MCP tools       │ N      │ ~XX,XXX   │
│ CLAUDE.md       │ N      │ ~X,XXX    │
└─────────────────┴────────┴───────────┘

Issues Found: N
Top Optimizations:
1. [action] → save ~X,XXX tokens
2. [action] → save ~X,XXX tokens
```

## Token 估算参考

- 散文: `words × 1.3`
- 代码: `chars / 4`
- Agent description: 按实际词数 × 1.3
- MCP tool schema: ~500 tokens/tool

## 最佳实践

- **MCP 是最大杠杆**: 每个 tool schema ~500 tokens; 30-tool server 比所有 skills 总和还贵
- **Agent descriptions 始终加载**: 即使从未调用，description 也存在于每次 Task 工具调用
- **变更后审计**: 每次添加 agent/skill/MCP server 后运行检查
- **与 compact 配合**: 先审计再 compaction 最大化收益

## 关键约束

- ❌ 不读取实际文件内容（仅统计大小）
- ❌ 不修改任何配置（仅报告）
- ✅ 标记问题但不下结论（保留用户判断权）


## Output

Context Budget Report — 包含组件开销分解、问题清单、Top 优化建议。

## Constraints

- 不读取实际文件内容（仅统计大小）
- 不修改任何配置（仅报告）
- 标记问题但不下结论（保留用户判断权）

<HARD-GATE>禁止读取文件内容（仅统计大小） | 禁止修改配置（仅报告）</HARD-GATE>