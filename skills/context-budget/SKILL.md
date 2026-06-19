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

## Write-to-Eval 模式（workflow 步骤8 使用）

当传入 `write-to-eval` 参数时，context-budget 会将估算结果写入 `.workflow-eval.json`：

```bash
Skill("orch:context-budget", args="write-to-eval")
```

**写入内容**（追加到 `stages[]` 或更新 evaluation stage）：

```json
{
  "stage": "evaluation",
  "status": "done",
  "estimated_tokens": {
    "agents": { "count": 25, "tokens": 8500 },
    "skills": { "count": 21, "tokens": 32000 },
    "rules":  { "count": 12, "tokens": 4800 },
    "mcp":    { "count": 0,  "tokens": 0 },
    "claude_md": { "count": 1, "tokens": 2400 },
    "total": 47700
  },
  "actual_tokens": null,
  "agent": "context-budget"
}
```

**扫描估算逻辑**：

```bash
# Agents 估算
echo "agents: $(cat agents/*.md 2>/dev/null | wc -l) lines × 1.3"
for f in agents/*.md; do
  lines=$(wc -l < "$f")
  tokens=$((lines * 13 / 10))
  echo "  $(basename $f): ~${tokens}tok"
done

# Skills 估算
echo "skills: $(wc -l skills/*/SKILL.md 2>/dev/null | tail -1)"
for d in skills/*/; do
  [ -f "${d}SKILL.md" ] || continue
  lines=$(wc -l < "${d}SKILL.md")
  tokens=$((lines * 13 / 10))
  echo "  $(basename $d): ~${tokens}tok"
done
```

**写入命令**：

```bash
python3 -c "
import json, os, pathlib

root = '${CLAUDE_PLUGIN_ROOT:-.}'
eval_path = pathlib.Path('orch-spec') / '.workflow-eval.json'
if not eval_path.exists():
    eval_path = pathlib.Path('.workflow-eval.json')

estimates = {}
for cat, pattern in [('agents', 'agents/*.md'), ('skills', 'skills/*/SKILL.md'), ('rules', 'rules/**/*.md')]:
    files = list(pathlib.Path(root).glob(pattern))
    total_lines = sum(len(f.read_text().splitlines()) for f in files if f.is_file())
    estimates[cat] = {'count': len(files), 'tokens': int(total_lines * 1.3)}

estimates['total'] = sum(v['tokens'] for v in estimates.values() if isinstance(v, dict))

data = json.loads(eval_path.read_text()) if eval_path.exists() else {'stages': [], 'token_usage': {}}
stage = {'stage': 'evaluation', 'status': 'done', 'estimated_tokens': estimates, 'actual_tokens': None}
data['stages'] = [s for s in data.get('stages', []) if s['stage'] != 'evaluation'] + [stage]
data['token_usage']['estimated'] = estimates
eval_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print('Written estimates to ' + str(eval_path))
"
```

## 关键约束

- ❌ 不读取实际文件内容（仅统计大小）
- ✅ `write-to-eval` 模式下写入 `.workflow-eval.json`（仅追加估计值，不修改实际消耗）
- ✅ 标记问题但不下结论（保留用户判断权）

## Output

- 默认模式：Context Budget Report — 组件开销分解、问题清单、Top 优化建议
- `write-to-eval` 模式：估算数据写入 `.workflow-eval.json` 的 `stages[].estimated_tokens`

<GATE>禁止读取文件内容（仅统计大小） | 禁止修改工作流配置 | write-to-eval 仅允许写入 estimated_tokens 字段</GATE>