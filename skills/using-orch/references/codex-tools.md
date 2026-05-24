# Codex 工具映射

本文档将 Claude Code 工具名映射到 Codex（OpenAI）等效工具。

## 工具映射表

| Claude Code | Codex | 说明 | 差异 |
|------------|-------|------|------|
| `Read` | `read_file` | 读取文件内容 | 功能相同 |
| `Write` | `write_file` | 写入/创建文件 | 功能相同 |
| `Edit` | `edit_file` | 编辑文件内容 | 功能相同 |
| `Bash` | `shell` | 执行 Shell 命令 | 功能相同 |
| `Glob` | `glob` | 文件模式匹配搜索 | 功能相同 |
| `Grep` | `grep` | 文件内容搜索 | 功能相同 |
| `Agent` | `spawn_agent` | 启动子代理 | 参数格式不同 |
| `Skill` | （原生发现） | 加载 Skill 内容 | Codex 原生支持 Skill 发现 |
| `TodoWrite` | `update_plan` | 更新计划/任务状态 | 功能类似 |
| `AskUserQuestion` | （无） | 向用户提问 | Codex 直接向用户提问 |
| `WebFetch` | `web_fetch` | 获取网页内容 | 功能类似 |
| `WebSearch` | `web_search` | 网络搜索 | 功能类似 |

## 注意事项

1. **Skill 发现**：Codex 有原生 Skill 发现机制，不需要 Skill 工具
2. **子代理**：`spawn_agent` 的参数格式与 Claude Code 的 `Agent` 不同
3. **计划更新**：`update_plan` 对应 Codex 的计划系统
4. **文件编辑**：Codex 的 `edit_file` 支持类似的文件编辑操作

## 使用指南

在 Skill 文档中：
- 默认使用 Claude Code 工具名
- 在 Codex 环境中，参照此映射表使用等效工具
- 对于 Codex 原生支持的功能（Skill 发现），使用 Codex 原生机制
