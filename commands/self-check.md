---
description: 插件自身 5 块自检（orchestration/agents/skills/tdd_loop/commands_hooks）。运行 node scripts/self-check.js
argument-hint: 可选：--json 输出结构化报告
---

# 插件自检

对 orch 插件自身的 5 大块能力执行验证，确认优化后的状态完整。

## 用法

```bash
# 文本报告
node scripts/self-check.js

# JSON 结构化报告
node scripts/self-check.js --json
```

## 验证范围

| 块 | 验证项 |
|----|--------|
| orchestration | stage-contracts 8 阶段 / EXEMPT 分离 / stdin 超时 / completion-report / session-start 补偿 / worktree 健康 |
| agents | project-map 引用 / 注册表 26 / Prompt Defense ≤1 / frontmatter / 编号 / 无 hookify |
| skills | 引用完整性 / cost GATE / using-orch 22 / observer / TRIGGER |
| tdd_loop | self-check 存在 / verdict 判定函数 / 覆盖率实测 |
| commands_hooks | hooks.json 注册 / observe 激活 / CLAUDE.md 一致 / 数量口径 / 无 pyc |

## 退出码

- `0`：5 块全部 PASS
- `1`：有 FAIL（issues[] 给出具体文件与修复建议）

> 自检为只读验证（fail-safe），FAIL 不阻断工作流，仅输出建议。
