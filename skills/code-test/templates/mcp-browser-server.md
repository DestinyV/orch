# MCP Browser Server 配置和使用指南

## 概述

MCP (Model Context Protocol) Browser Server 让 Claude 能通过 MCP 协议直接操控浏览器，在 code-test 阶段进行探索性测试、截图验证和交互式 UI 验证。

## 安装

### 方式1: Playwright MCP Server（推荐）

```bash
# 安装 Playwright MCP Server
npm install -g @playwright/mcp-server

# 或使用 npx 直接运行（无需全局安装）
npx @playwright/mcp-server
```

### 方式2: 浏览器 MCP Server

```bash
# 使用 community-driven 的 browser-use MCP Server
npm install -g @anthropic/mcp-server-browser
```

## Claude Code 配置

在项目的 `.mcp.json` 或 Claude Code 全局配置中添加：

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp-server"],
      "env": {
        "PLAYWRIGHT_BROWSERS_PATH": "0"
      }
    }
  }
}
```

## 支持的 MCP 工具

| 工具名 | 说明 | 输入参数 |
|--------|------|---------|
| `browser_navigate` | 导航到指定 URL | `{ url: string }` |
| `browser_click` | 点击页面元素 | `{ selector: string }` |
| `browser_type` | 在输入框中打字 | `{ selector: string, text: string }` |
| `browser_screenshot` | 截取页面截图 | `{ name?: string, fullPage?: boolean }` |
| `browser_evaluate` | 执行 JavaScript 并返回结果 | `{ script: string }` |
| `browser_get_text` | 获取元素文本内容 | `{ selector: string }` |
| `browser_hover` | 鼠标悬停 | `{ selector: string }` |
| `browser_select_option` | 选择下拉选项 | `{ selector: string, value: string }` |
| `browser_press_key` | 按键操作 | `{ key: string }` |
| `browser_wait` | 等待指定时间 | `{ time?: number }` |

## 在 code-test 阶段的使用流程

### 步骤1: 启动 MCP Server

在 code-test 开始前，确保 MCP Browser Server 已配置并可连接。

### 步骤2: 导航到待测应用

Claude 使用 `browser_navigate` 导航到开发服务器：
```
→ browser_navigate({ url: "http://localhost:5173" })
```

### 步骤3: 执行探索性测试

Claude 通过 MCP 工具进行交互式测试：

```
→ browser_click({ selector: "[data-testid='nav-products']" })
→ browser_screenshot({ name: "products-page", fullPage: true })
→ browser_get_text({ selector: "[data-testid='product-count']" })
→ browser_evaluate({ script: "document.cookie" })
```

### 步骤4: 截图验证

Claude 对关键页面进行截图并与预期对比：

```
→ browser_screenshot({ name: "homepage-desktop", fullPage: true })
→ browser_screenshot({ name: "homepage-mobile", fullPage: true })
```

### 步骤5: 状态验证

Claude 验证页面状态和数据：

```
→ browser_get_text({ selector: "[data-testid='welcome-message']" })
→ browser_evaluate({ script: "localStorage.getItem('user')" })
→ browser_evaluate({ script: "fetch('/api/health').then(r=>r.json())" })
```

## 完整测试示例

### 测试登录流程

```
1. browser_navigate({ url: "http://localhost:5173/login" })
2. browser_screenshot({ name: "login-page" })
3. browser_type({ selector: "[data-testid='username']", text: "test@example.com" })
4. browser_type({ selector: "[data-testid='password']", text: "password123" })
5. browser_click({ selector: "[data-testid='login-submit']" })
6. browser_wait({ time: 2000 })
7. browser_screenshot({ name: "after-login" })
8. browser_get_text({ selector: "[data-testid='welcome-message']" })
   → 预期包含 "欢迎"
9. browser_evaluate({ script: "window.location.pathname" })
   → 预期不是 "/login"
```

### 测试表单验证

```
1. browser_navigate({ url: "http://localhost:5173/register" })
2. browser_click({ selector: "[data-testid='register-submit']" })
3. browser_wait({ time: 500 })
4. browser_screenshot({ name: "form-validation-errors" })
5. browser_get_text({ selector: "[data-testid='error-username']" })
   → 预期包含 "不能为空"
```

## 注意事项

1. **Dev Server 必须运行**：MCP Browser 需要目标应用在本地运行
2. **headless 模式**：默认使用无头浏览器，调试时可设置 `headless: false`
3. **超时处理**：浏览器操作有默认超时时间，复杂页面可能需要 `browser_wait`
4. **安全性**：MCP Server 只允许访问 localhost 和配置的白名单域名
5. **数据隔离**：每次测试使用独立的浏览器上下文，避免数据污染

## 与 Playwright 脚本的配合

| 方式 | 适用场景 | 优势 |
|------|---------|------|
| Playwright 脚本 | 重复执行的回归测试 | 稳定、可自动化、可 CI |
| MCP Browser | 探索性测试、一次性验证 | 灵活、AI 驱动、可交互 |

**推荐策略**：
- 核心回归测试用 Playwright 脚本自动化（步骤 3.2）
- 探索性测试和快速验证用 MCP Browser（步骤 3.5）
- 两者互补，覆盖不同测试需求
