# orch — CodeBuddy 适配

## 概述

CodeBuddy 使用上下文注入而非 `Skill` 工具。SDD+TDD skills 通过符号链接或复制 SKILL.md 文件到 CodeBuddy 配置目录加载。

## 安装

运行安装脚本：

```bash
node .codebuddy/install.js
```

## 工具映射

| Claude Code | CodeBuddy | 说明 |
|-------------|-----------|------|
| `Skill` | (上下文注入) | Skills 通过配置预加载 |
| `Agent` | `task` | 子代理派遣 |
| `TodoWrite` | (文本列表) | 使用 markdown 待办清单代替 |
| `AskUserQuestion` | (直接提问) | 直接询问用户 |

详见 `references/copilot-tools.md`（CodeBuddy 与 Copilot 共享工具模型）。

## 工作流

CodeBuddy 无 `Skill` 工具，工作流阶段通过引用预链接的 SKILL.md 文件加载。
阶段顺序执行：完成一个阶段后再加载下一个。

## 文件说明

- `.codebuddy/skills/` — 各工作流阶段的 SKILL.md 符号链接
- `.codebuddy/AGENTS.md` — 用于 `task` 调用的 Agent 描述
- `.codebuddy/tools-mapping.md` — 详细工具映射参考
