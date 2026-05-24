# OpenCode 工具映射

本文档将 Claude Code 工具名映射到 OpenCode 等效工具。

## 工具映射表

| Claude Code | OpenCode | 说明 | 差异 |
|------------|----------|------|------|
| `Read` | `Read` | 读取文件内容 | 功能相同 |
| `Write` | `Write` | 写入/创建文件 | 功能相同 |
| `Edit` | `Edit` | 编辑文件内容 | 功能相同 |
| `Bash` | `Bash` | 执行 Shell 命令 | 功能相同 |
| `Glob` | `Glob` | 文件模式匹配搜索 | 功能相同 |
| `Grep` | `Grep` | 文件内容搜索 | 功能相同 |
| `Agent` | `@mention` | 启动子代理 | 通过 @mention 触发 |
| `Skill` | `skill` | 加载 Skill 内容 | 功能相同，名称不同 |
| `TodoWrite` | `TodoWrite` | 写入 Todo 列表 | 功能相同 |
| `AskUserQuestion` | （无） | 向用户提问 | OpenCode 直接向用户提问 |
| `WebFetch` | `WebFetch` | 获取网页内容 | 功能相同 |
| `WebSearch` | `WebSearch` | 网络搜索 | 功能相同 |

## 注意事项

1. **子代理**：通过 `@mention` 机制触发 agent，而非独立的 Agent 工具
2. **Skill 加载**：使用 `skill` 工具替代 Claude Code 的 `Skill` 工具
3. **插件系统**：OpenCode 通过 `.opencode/plugins/superpowers.js` 加载插件
4. **工具命名**：OpenCode 工具名与 Claude Code 大部分相同（首字母大写）

## 插件加载

OpenCode 通过以下方式加载 Superpowers 插件：

```javascript
// .opencode/plugins/superpowers.js
// System prompt transform + skill registration
```

## 使用指南

在 Skill 文档中：
- 默认使用 Claude Code 工具名
- 在 OpenCode 环境中，工具名基本相同（首字母大写）
- Skill 通过 `skill` 工具加载
- 子代理通过 `@mention` 触发
