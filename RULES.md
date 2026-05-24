# orch — 项目规则

## 规则目录

| 路径 | 语言 | 范围 |
|------|------|------|
| `rules/common/` | 通用 | 所有项目 |
| `rules/typescript/` | TypeScript | TS/JS 项目 |
| `rules/python/` | Python | Python 项目 |
| `rules/zh/` | 中文 | 中文项目通用规则 |

## 规则文件

每种语言目录包含标准化规则文件：

- `coding-style.md` — 代码格式、命名、结构
- `patterns.md` — 设计模式和惯用写法
- `testing.md` — 测试实践和标准
- `security.md` — 安全指南
- `git-workflow.md` — Git 实践（仅 common）

## 规则加载方式

规则由 Claude Code 在会话启动时从项目 `.claude/rules/` 加载。
为多平台兼容，`.cursor/rules/` 等目录镜像了相关子集。
