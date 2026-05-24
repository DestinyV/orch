---
description: 需求变更管理 — 在规范/设计/编码完成后需求发生变更时，进行影响分析和增量调整
argument-hint: 变更描述
---

# 需求变更管理

```
/req-change "变更描述"
```

调用 `Skill("orch:req-change", args="{变更描述}")`。

**前置验证**：执行前扫描 `orch-spec/` 列出所有需求，AskUserQuestion 确认修改目标。

**执行流程**：
1. 扫描 orch-spec/ → 列出需求 + 状态（done/in_progress）
2. AskUserQuestion 确认目标需求
3. 影响分析（L1 新增 / L2 修改 / L3 删除 / L4 约束变更）
4. 增量调整 spec → design → tasks
5. 输出变更记录到 changelogs/
