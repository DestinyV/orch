# orch Cursor 工具映射

| Claude Code | Cursor 等价 | 说明 |
|-------------|------------|------|
| Skill("orch:...") | 聊天中 @orch | 使用 @提及 调用 skills |
| Agent(subagent_type=...) | Cursor Agent + rules | 通过 .cursor/rules/ 配置 |
| Bash | 终端 | 原生终端支持 |
| Write/Edit | 文件编辑 | 内置功能 |
| Grep | 搜索 | 内置功能 |
| Glob | 文件浏览器 | 手动操作 |
| Read | 文件预览 | 内置功能 |

## 配置

将此插件的 `.cursor/rules/` 文件添加到你的 Cursor 项目，即可使用 SDD+TDD 工作流规则。
