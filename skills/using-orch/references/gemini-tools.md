# Gemini CLI 工具映射

本文档将 Claude Code 工具名映射到 Gemini CLI 等效工具。

## 工具映射表

| Claude Code | Gemini CLI | 说明 | 差异 |
|------------|------------|------|------|
| `Read` | `read_file` | 读取文件内容 | 功能相同 |
| `Write` | `write_file` | 写入/创建文件 | 功能相同 |
| `Edit` | `edit_file` | 编辑文件内容 | 功能相同 |
| `Bash` | `bash` | 执行 Shell 命令 | 功能相同 |
| `Glob` | `glob` | 文件模式匹配搜索 | 功能相同 |
| `Grep` | `grep` | 文件内容搜索 | 功能相同 |
| `Agent` | （无） | 启动子代理 | Gemini 无子代理工具 |
| `Skill` | `activate_skill` | 加载 Skill 内容 | 功能相同，名称不同 |
| `TodoWrite` | `todowrite` | 写入 Todo 列表 | 功能相同，名称不同 |
| `AskUserQuestion` | （无） | 向用户提问 | Gemini 直接向用户提问 |
| `WebFetch` | `web_fetch` | 获取网页内容 | 功能类似 |
| `WebSearch` | `web_search` | 网络搜索 | 功能类似 |

## 注意事项

1. **子代理**：Gemini 无子代理功能，需要用串行方式替代并行子代理
2. **Skill 激活**：使用 `activate_skill` 替代 Claude Code 的 `Skill` 工具
3. **Todo 列表**：使用 `todowrite`（无驼峰命名）
4. **工作流调整**：无子代理意味着 SDD 流程需要调整为串行执行

## SDD 工作流适配

在没有子代理的情况下，SDD 工作流调整为：

```
原始流程（有子代理）：
Task 1 → 子代理A → 子代理B（并行）→ 审查 → 合并

Gemini 适配流程（无子代理）：
Task 1 → 直接实现 → 审查 → Task 2 → 直接实现 → 审查 → 合并
```

## 使用指南

在 Skill 文档中：
- 默认使用 Claude Code 工具名
- 在 Gemini 环境中，参照此映射表使用等效工具
- 对于无等效工具（Agent），用串行执行替代
