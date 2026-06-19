# Token 效率指南

executor 派遣时的 Token 节省最佳实践。

## 核心原则

1. **信任注入上下文** — 主代理已注入的 task-spec/design summary/template 路径，不要重复读取
2. **按需读取** — 仅当注入信息不足以完成当前步骤时，才补充读取
3. **摘要优先** — 命令输出先读尾巴，通过场景不需读全文
4. **就近引用** — 路径已在 prompt 中时直接使用，不 glob 搜索

## 上下文注入结构

每次派遣 executor 时由主代理注入：

| 字段 | 内容 | 预估 Token | 读取策略 |
|------|------|-----------|---------|
| task-spec | id/description/provides/consumes/验收标准/covers | ≤2K | 直接使用 |
| design-summary | 与本 Task 相关的架构决策（≤500字摘要） | ≤1K | 直接使用 |
| template-paths | 相关 test-*.template 文件路径列表 | ≤200 | executor 按需 Read 所需 TC |
| exception-patterns | 项目异常类名/错误码格式/文件位置 | ≤500 | 直接使用 |
| batch-context | 前批次完成的 provides 接口列表 | ≤300 | 直接使用 |

## 命令输出读取对照

| 命令 | 通过时读取 | 失败时读取 |
|------|-----------|-----------|
| `npm test` / `pytest` | exit 0 + 最后 3 行 (summary) | 完整输出 |
| `tsc --noEmit` | exit 0 + 错误计数 "Found 0 errors" | 完整输出 |
| `eslint` | exit 0 + 问题计数 | 完整输出 |
| `npm test -- --coverage` | exit 0 + Coverage summary 段 | 完整输出 |
| `go build` / `cargo check` | exit 0 + 最后 3 行 | 完整输出 |

## 禁止的 Token 浪费模式

| 浪费模式 | 替代做法 |
|---------|---------|
| `Read(tasks.md)` 全文 | 使用 prompt 中已注入的 task-spec |
| `Read(design.md)` 全文 | 使用 prompt 中已注入的 design-summary |
| `Glob("src/**/*.ts")` 全文扫描 | 使用 task-spec 中声明的文件路径 |
| `Bash("cat ... | head -100")` 读百行输出 | 读 tail -5 或 grep summary |
| `Grep("some pattern")` 全局搜索 | 先确认注入上下文是否已有答案 |
