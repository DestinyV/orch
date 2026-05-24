// 视觉回归测试代码模板
// 基于 Playwright 的截图对比功能
// 使用说明：复制此文件到 tests/e2e/ 目录，根据实际需求修改

import { test, expect } from '@playwright/test';

// ============================================================
// 视觉回归: 页面布局截图对比
// ============================================================

test.describe('@visual 页面视觉回归测试', () => {
  // -------------------------------------------------------
  // 首页布局测试
  // -------------------------------------------------------

  test('首页桌面端布局应该正常', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/');

    // 等待页面完全加载
    await page.waitForLoadState('networkidle');

    // 全页面截图对比
    await expect(page).toHaveScreenshot('homepage-desktop.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
      fullPage: true,
    });
  });

  test('首页移动端布局应该正常', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('homepage-mobile.png', {
      maxDiffPixels: 50,
      threshold: 0.2,
      fullPage: true,
    });
  });

  test('首页平板端布局应该正常', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');

    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('homepage-tablet.png', {
      maxDiffPixels: 80,
      threshold: 0.2,
      fullPage: true,
    });
  });

  // -------------------------------------------------------
  // 关键页面截图对比
  // -------------------------------------------------------

  test('[关键页面名称] 布局应该正常', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/[页面路径]');

    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('[page-name]-desktop.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
    });
  });

  // -------------------------------------------------------
  // 组件级视觉回归
  // -------------------------------------------------------

  test('[组件名称] 渲染应该一致', async ({ page }) => {
    await page.goto('/[包含组件的页面]');
    await page.waitForLoadState('networkidle');

    // 截取特定组件元素
    const component = page.getByTestId('[组件的data-testid]');
    await expect(component).toHaveScreenshot('[component-name].png', {
      maxDiffPixels: 20,
      threshold: 0.15,
    });
  });

  // -------------------------------------------------------
  // 状态视觉回归
  // -------------------------------------------------------

  test('组件的不同状态视觉应该正确', async ({ page }) => {
    await page.goto('/[页面路径]');
    await page.waitForLoadState('networkidle');

    // 默认状态
    await expect(page).toHaveScreenshot('[component]-default.png', {
      maxDiffPixels: 10,
    });

    // Hover 状态
    await page.getByTestId('[元素]').hover();
    await expect(page).toHaveScreenshot('[component]-hover.png', {
      maxDiffPixels: 10,
    });

    // 禁用状态
    await page.getByTestId('[元素]').click();
    await expect(page).toHaveScreenshot('[component]-active.png', {
      maxDiffPixels: 10,
    });
  });

  // -------------------------------------------------------
  // 暗色/亮色主题视觉回归
  // -------------------------------------------------------

  test('暗色主题布局应该正常', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // 切换到暗色主题
    await page.getByTestId('theme-toggle').click();
    await page.waitForTimeout(500); // 等待动画完成

    await expect(page).toHaveScreenshot('homepage-dark-theme.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
    });
  });
});
