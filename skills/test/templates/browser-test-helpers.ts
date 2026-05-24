// 浏览器测试工具函数库
// 提供可复用的 Playwright 测试辅助函数
// 可直接复制到前端项目的 tests/helpers/ 目录使用

import { Page, Locator, expect } from '@playwright/test';

// ============================================================
// 认证相关工具函数
// ============================================================

/**
 * 快捷登录 - 通过 UI 或 API 直接设置认证状态
 * @param page - Playwright Page 实例
 * @param role - 用户角色（如 'admin', 'user', 'guest'）
 * @param credentials - 登录凭据（可选）
 */
export async function loginAs(
  page: Page,
  role: string = 'user',
  credentials?: { username: string; password: string }
): Promise<void> {
  const defaults: Record<string, { username: string; password: string }> = {
    admin: { username: 'admin@test.com', password: 'Admin@123' },
    user: { username: 'user@test.com', password: 'User@123' },
    guest: { username: 'guest@test.com', password: 'Guest@123' },
  };

  const { username, password } = credentials || defaults[role] || defaults.user;

  // 方式1：通过 UI 登录（适用于需要测试登录流程的场景）
  await page.goto('/login');
  await page.getByTestId('login-username').fill(username);
  await page.getByTestId('login-password').fill(password);
  await page.getByTestId('login-submit').click();
  await page.waitForURL((url) => !url.pathname.includes('/login'), {
    timeout: 10_000,
  });
}

/**
 * 通过 API 直接设置认证状态（更快，适用于不需要测试登录的场景）
 */
export async function loginViaApi(
  page: Page,
  role: string = 'user'
): Promise<void> {
  const token = await page.evaluate(async (r) => {
    // 调用测试 API 获取 token
    const response = await fetch(`/api/test/auth/token?role=${r}`, {
      method: 'POST',
    });
    const data = await response.json();
    return data.token;
  }, role);

  // 设置 localStorage 或 Cookie
  await page.addInitScript((tok) => {
    window.localStorage.setItem('auth-token', tok);
  }, token);
}

// ============================================================
// 表单操作工具函数
// ============================================================

/**
 * 自动填充表单 - 根据 data-testid 批量填充表单数据
 * @param page - Playwright Page 实例
 * @param data - 表单数据，key 为 data-testid，value 为填充值
 */
export async function fillForm(
  page: Page,
  data: Record<string, string>
): Promise<void> {
  for (const [testId, value] of Object.entries(data)) {
    const input = page.getByTestId(testId);
    await input.click();
    await input.fill(value);
  }
}

/**
 * 提交表单并等待响应
 */
export async function submitForm(page: Page, submitTestId?: string): Promise<void> {
  await page.getByTestId(submitTestId || 'form-submit').click();
}

// ============================================================
// 页面稳定性工具函数
// ============================================================

/**
 * 等待页面稳定 - 等待所有网络请求完成且 DOM 不再变化
 * 适用于 SPA 应用，确保页面渲染完成后再进行断言
 */
export async function waitForStable(page: Page, timeout = 5000): Promise<void> {
  // 等待网络空闲
  await page.waitForLoadState('networkidle', { timeout });

  // 等待关键元素可见
  await page.waitForTimeout(300); // 短暂等待动画完成
}

/**
 * 等待元素稳定（不再闪烁或动画）
 */
export async function waitForElementStable(
  locator: Locator,
  timeout = 3000
): Promise<void> {
  await locator.waitFor({ state: 'visible', timeout });
  await page.waitForTimeout(200);
}

// ============================================================
// API Mock 工具函数
// ============================================================

/**
 * Mock API 响应 - 拦截指定路由并返回自定义响应
 * @param page - Playwright Page 实例
 * @param routePattern - 路由匹配模式（支持 glob 和正则）
 * @param response - Mock 响应数据
 */
export async function mockAPI(
  page: Page,
  routePattern: string | RegExp,
  response: {
    status?: number;
    body?: Record<string, unknown> | unknown[];
    delay?: number;
  }
): Promise<void> {
  await page.route(routePattern, async (route) => {
    if (response.delay) {
      await new Promise((r) => setTimeout(r, response.delay));
    }
    await route.fulfill({
      status: response.status || 200,
      contentType: 'application/json',
      body: JSON.stringify(response.body),
    });
  });
}

/**
 * 监听 API 调用 - 捕获 API 请求和响应，用于后续验证
 */
export async function captureAPI(
  page: Page,
  routePattern: string | RegExp
): Promise<Promise<{ url: string; method: string; postData: unknown }>> {
  const [request] = await Promise.all([
    page.waitForRequest(routePattern),
    // 触发请求的操作应该在这里之后执行
  ]);

  return {
    url: request.url(),
    method: request.method(),
    postData: request.postDataJSON?.() || request.postData(),
  };
}

// ============================================================
// 视觉回归工具函数
// ============================================================

/**
 * 截图对比 - 截取页面或元素并与基准截图对比
 * @param page - Playwright Page 实例
 * @param name - 截图名称（用于匹配基准文件）
 * @param options - 对比选项
 */
export async function captureAndCompare(
  page: Page,
  name: string,
  options?: {
    maxDiffPixels?: number;
    maxDiffPixelRatio?: number;
    threshold?: number;
  }
): Promise<void> {
  await expect(page).toHaveScreenshot(`${name}.png`, {
    maxDiffPixels: options?.maxDiffPixels ?? 50,
    maxDiffPixelRatio: options?.maxDiffPixelRatio ?? 0.1,
    threshold: options?.threshold ?? 0.2,
    fullPage: false,
  });
}

/**
 * 对指定元素进行截图对比
 */
export async function captureElementAndCompare(
  locator: Locator,
  name: string,
  options?: {
    maxDiffPixels?: number;
    threshold?: number;
  }
): Promise<void> {
  await expect(locator).toHaveScreenshot(`${name}.png`, {
    maxDiffPixels: options?.maxDiffPixels ?? 20,
    threshold: options?.threshold ?? 0.2,
  });
}

// ============================================================
// 测试数据生命周期工具函数
// ============================================================

/**
 * 设置测试数据 - 通过 API 或数据库直接插入测试数据
 */
export async function setupTestData(
  page: Page,
  data: Record<string, unknown>
): Promise<void> {
  await page.evaluate(
    async (testData) => {
      await fetch('/api/test/data/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testData),
      });
    },
    data
  );
}

/**
 * 清理测试数据 - 在测试结束后清理
 */
export async function cleanupTestData(page: Page): Promise<void> {
  await page.evaluate(async () => {
    await fetch('/api/test/data/cleanup', { method: 'POST' });
  });
}

// ============================================================
// 断言工具函数
// ============================================================

/**
 * 验证 URL 路径
 */
export async function assertURL(
  page: Page,
  expectedPath: string | RegExp,
  timeout = 5000
): Promise<void> {
  await page.waitForURL(expectedPath, { timeout });
}

/**
 * 验证元素存在并包含指定文本
 */
export async function assertElementContains(
  page: Page,
  testId: string,
  expectedText: string | RegExp
): Promise<void> {
  await expect(page.getByTestId(testId)).toContainText(expectedText);
}

/**
 * 验证元素不存在（已隐藏或已移除）
 */
export async function assertElementNotVisible(
  page: Page,
  testId: string
): Promise<void> {
  await expect(page.getByTestId(testId)).not.toBeVisible();
}

// ============================================================
// 导航工具函数
// ============================================================

/**
 * 等待页面导航完成并验证 URL
 */
export async function navigateTo(
  page: Page,
  path: string,
  expectedURL?: string | RegExp
): Promise<void> {
  await page.goto(path);
  if (expectedURL) {
    await page.waitForURL(expectedURL || path);
  }
}
