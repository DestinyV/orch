# 组件抽离指南

## 何时拆分

单一职责（多变化理由）| 复用性（多处使用）| 可读性（单文件>200行）| 可测试性（逻辑难单独测）

## 拆分类型

| 类型 | 标准 | 示例 |
|------|------|------|
| UI 组件 | 可复用视觉元素 | Button, Modal, Table |
| 逻辑组件 | 独立业务逻辑 | useOrderHook, Validator |
| 布局组件 | 页面结构 | Layout, Sidebar, Header |

## 命名

组件：PascalCase | Hook：useXxx | 工具：camelCase
