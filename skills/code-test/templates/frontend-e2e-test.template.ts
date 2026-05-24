// E2E 端到端测试代码模板
// 基于 Playwright，可直接运行的 E2E 测试模板
// 使用说明：复制此文件到 tests/e2e/ 目录，根据实际需求修改

import { test, expect, Page } from '@playwright/test';
import {
  loginAs,
  fillForm,
  waitForStable,
  mockAPI,
  setupTestData,
  cleanupTestData,
} from '../helpers/browser-test-helpers';

// ============================================================
// E2E: 完整用户操作流程测试
// ============================================================

test.describe('@e2e [功能模块名称] 端到端测试', () => {
  // -------------------------------------------------------
  // 测试生命周期
  // -------------------------------------------------------

  test.beforeEach(async ({ page }) => {
    // 设置测试数据（通过 API 直接初始化）
    await setupTestData(page, {
      // 初始化测试用户
      users: [{ id: 'test-user-001', role: 'user' }],
      // 初始化测试数据
      testData: {
        // 根据实际需求填充
      },
    });
  });

  test.afterEach(async ({ page }) => {
    // 清理测试数据
    await cleanupTestData(page);
  });

  // -------------------------------------------------------
  // Happy Path: 完整主流程
  // -------------------------------------------------------

  test('应该能完成完整的 [业务流程]', async ({ page }) => {
    // Step 1: 登录
    await loginAs(page, 'user');
    await expect(page).toHaveURL(/\/dashboard/);

    // Step 2: 导航到功能页面
    await page.goto('/[功能页面路径]');
    await waitForStable(page);

    // Step 3: 执行主要操作
    await fillForm(page, {
      // 表单字段: data-testid -> 值
      // 'form-field-name': '测试值',
    });
    await page.getByTestId('form-submit').click();

    // Step 4: 验证操作结果
    await expect(page.getByTestId('success-message')).toBeVisible();
    await expect(page.getByTestId('success-message')).toContainText('操作成功');

    // Step 5: 验证数据持久化
    await page.reload();
    await waitForStable(page);
    // 验证数据仍然存在
    await expect(page.getByTestId('[数据元素]')).toBeVisible();
  });

  // -------------------------------------------------------
  // 错误处理: 异常情况
  // -------------------------------------------------------

  test('应该在输入无效时显示错误提示', async ({ page }) => {
    await loginAs(page, 'user');
    await page.goto('/[功能页面路径]');

    // 提交空表单
    await page.getByTestId('form-submit').click();

    // 验证错误提示
    await expect(page.getByTestId('error-[字段名]')).toContainText('不能为空');
  });

  test('应该在网络错误时显示友好提示', async ({ page }) => {
    // Mock API 失败
    await mockAPI(page, '**/api/[endpoint]', {
      status: 500,
      body: { error: '服务器错误' },
    });

    await loginAs(page, 'user');
    await page.goto('/[功能页面路径]');

    // 触发 API 调用
    await page.getByTestId('form-submit').click();

    // 验证错误处理
    await expect(page.getByTestId('error-banner')).toContainText('操作失败，请重试');
  });

  // -------------------------------------------------------
  // 边界情况
  // -------------------------------------------------------

  test('应该处理大量数据列表', async ({ page }) => {
    // 插入大量测试数据
    await setupTestData(page, {
      items: Array.from({ length: 100 }, (_, i) => ({
        id: `item-${i}`,
        name: `测试数据 ${i}`,
      })),
    });

    await loginAs(page, 'user');
    await page.goto('/[列表页面路径]');
    await waitForStable(page);

    // 验证列表渲染
    const items = page.getByTestId('list-item');
    await expect(items).toHaveCount(100);

    // 验证虚拟滚动（如适用）
    const visibleItems = await items.count();
    expect(visibleItems).toBeLessThanOrEqual(20); // 可见项不超过视口容量
  });
});

// ============================================================
// E2E: 多用户交互测试
// ============================================================

test.describe('@e2e 多用户协作测试', () => {
  test('用户A的操作应该实时反映到用户B的页面', async ({ browser }) => {
    // 创建两个独立的浏览器上下文
    const contextA = await browser.newContext();
    const contextB = await browser.newContext();

    const pageA = await contextA.newPage();
    const pageB = await contextB.newPage();

    try {
      // 两个用户分别登录
      await loginAs(pageA, 'user');
      await loginAs(pageB, 'user');

      // 用户A创建数据
      await pageA.goto('/[功能页面路径]');
      await fillForm(pageA, { 'form-name': '共享数据' });
      await pageA.getByTestId('form-submit').click();
      await expect(pageA.getByTestId('success-message')).toBeVisible();

      // 用户B刷新页面验证数据同步
      await pageB.reload();
      await waitForStable(pageB);
      await expect(pageB.getByTestId('[数据元素]')).toContainText('共享数据');
    } finally {
      await contextA.close();
      await contextB.close();
    }
  });
});
