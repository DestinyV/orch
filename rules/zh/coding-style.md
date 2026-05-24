# 编码规范（SDD+TDD）

## 命名约定

- **JS/TS：** 变量/函数使用 camelCase，类/组件使用 PascalCase，常量使用 UPPER_SNAKE_CASE
- **Python：** 变量/函数使用 snake_case，类使用 PascalCase
- 布尔值前缀：`is`、`has`、`should` 或 `can`

## 禁止模式

- **无注释代码** — 禁止编写仅用于承载注释而无实际逻辑的代码。要么实现功能，要么删除注释。
- **无伪代码** — 代码必须可编译可运行。不允许在提交的代码中出现占位符实现。
- **无 TODO 遗留** — 工作流完成前必须消除所有 TODO 标记，或转换为实际任务项。

## SDD+TDD 约定

- 所有生产代码必须可追溯到规范的某个场景（需求文档 → 场景 → 实现）
- 功能开关控制新行为上线；永不交付未经规范覆盖的代码路径
- 每个文件头部必须标注模式标签：`// #mode: frontend` / `# mode: backend` / `# mode: fullstack`
