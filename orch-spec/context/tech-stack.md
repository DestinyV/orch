# 技术栈

## 项目类型
Claude Code 插件（企业级 SDD+TDD 工作流编排）

## 语言
- TypeScript（Node.js 脚本和钩子）
- Python（辅助脚本）
- Bash/Shell（CLI 操作）
- Markdown（全部文档和配置）

## 框架
- 无前端框架（纯 SDK 插件）
- SDD+TDD 工作流引擎（自研）

## 构建
- 无构建工具（原生 Markdown + 脚本）

## 测试
- Python unittest（测试套件）

## 存储
- JSONL + SQLite（成本追踪）
- JSON Schema（工作流状态和评估）
- YAML（配置和逻辑链路）

## 依赖
- Node.js >= 18（hooks 和 scripts）
- sqlite3 CLI（cost 追踪查询）
- codegraph（可选，代码图谱加速）
