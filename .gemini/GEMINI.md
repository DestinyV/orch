# orch — Gemini CLI Adaptation Guide

SDD+TDD 工作流适配 Gemini CLI。核心差异：Gemini 无子代理工具，所有并行步骤须串行化。

## 工具映射

| Claude Code | Gemini CLI | Notes |
|-------------|------------|-------|
| `Skill` | `activate_skill` | 激活 Skill 的等效工具 |
| `Agent` | (none) | 无子代理；用串行执行替代 |
| `TodoWrite` | `todowrite` | 注意：全小写，无驼峰 |
| `Read`/`Write`/`Edit`/`Bash`/`Glob`/`Grep` | 同名 | 功能一致 |
| `AskUserQuestion` | (direct) | Gemini 直接向用户提问 |

## 串行化适配

因无子代理，并行步骤改为串行：

```
Claude Code:  test-design (并行) design
Gemini CLI:   test-design → design  (顺序执行)

Claude Code:  execute (多 Task 并行子代理)
Gemini CLI:   Task1 → Task2 → ... → TaskN (逐个实现)
```

## Skill 激活

所有 Skill 通过 `activate_skill` 加载：

```
activate_skill orch:workflow "需求描述"
activate_skill orch:spec "需求描述"
```

## 工作流执行

1. 使用 `activate_skill` 替代 Skill 工具激活每个阶段
2. 串行执行所有步骤（等待前一步完成后再激活下一步）
3. 无 Agent 子代理意味着 task 中的并行 Task 也需串行实现
4. 流程状态记录仍在 `.workflow-state.json` 中
