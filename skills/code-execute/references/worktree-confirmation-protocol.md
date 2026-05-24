# Worktree 创建确认协议

**核心原则**：执行前必须 AskUserQuestion 确认 | 不假设任何分支名 | 提供多个选项

## 确认流程

```
AskUserQuestion: "请选择 Task {task-id} 的基础分支："
  - 选项1: 当前分支 ({current})
  - 选项2: master/main
  - 选项3: develop
  - 选项4: 其他（用户输入）
```

## 默认行为

用户未选择时 → 使用当前分支

## 创建命令

```bash
git worktree add .claude/worktrees/{task-id}-{name} {confirmed-branch}
```

## 安全约束

- 严禁跳过确认直接创建
- 严禁使用硬编码分支名
- 创建后记录选择的分支到 TodoList
