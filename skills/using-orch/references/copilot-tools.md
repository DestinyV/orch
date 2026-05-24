# Copilot CLI 工具映射

本文档将 Claude Code 工具名映射到 Copilot CLI 等效工具。

## 工具映射表

| Claude Code | Copilot CLI | 说明 | 差异 |
|------------|-------------|------|------|
| `Read` | `view` | 读取文件内容 | 功能相同 |
| `Write` | `edit` | 写入/创建文件 | Copilot 用 edit 替代 write |
| `Edit` | `edit` | 编辑文件内容 | 功能相同 |
| `Bash` | `bash` | 执行 Shell 命令 | 功能相同 |
| `Glob` | `find` | 文件模式匹配搜索 | 功能类似，语法不同 |
| `Grep` | `search` | 文件内容搜索 | 功能相同 |
| `Agent` | `task` | 启动子代理 | 子代理机制类似 |
| `Skill` | （无） | 加载 Skill 内容 | Copilot 无等效 Skill 工具 |
| `TodoWrite` | （无） | 写入 Todo 列表 | Copilot 无等效工具 |
| `AskUserQuestion` | （无） | 向用户提问 | Copilot 无等效工具 |
| `WebFetch` | `web_fetch` | 获取网页内容 | 功能类似 |
| `WebSearch` | `web_search` | 网络搜索 | 功能类似 |

## 注意事项

1. **Skill 加载**：Copilot CLI 无 Skill 工具，Skills 通过上下文注入方式加载
2. **TodoWrite**：在 Copilot 中用文本列表替代，不依赖工具
3. **AskUserQuestion**：直接向用户提问，不需要专用工具
4. **Edit 工具**：Copilot 的 edit 工具可能不支持 `replace_all` 参数

## 使用指南

在 Skill 文档中：
- 默认使用 Claude Code 工具名（Read, Write, Bash 等）
- 在 Copilot 环境中，参照此映射表使用等效工具
- 对于 Copilot 无等效的工具，使用文本/对话方式替代
