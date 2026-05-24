# 前端浏览器测试指南

## 测试类型

| 类型 | 标签 | 目标 | 工具 |
|------|------|------|------|
| E2E | `@e2e` | 完整用户流程 | Playwright |
| 视觉回归 | `@visual` | UI 截图对比 | Playwright screenshots |
| 组件 UI | `@component` | 单组件渲染 | Playwright component |

## 实践要点

- `data-testid` 选择器 | `waitForSelector` 非固定延迟
- 多视口测试（桌面/平板/手机）| 失败自动截图

## 环境

```bash
npx playwright install && npx playwright --version
npx playwright test --grep "@e2e"
```
