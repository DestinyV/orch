// 组件 UI 测试代码模板
// 基于 Playwright 组件测试模式（也适用于 Vitest + Testing Library）
// 使用说明：复制此文件到 tests/components/ 目录，根据实际需求修改

import { test, expect } from '@playwright/test';

// ============================================================
// 组件 UI: [组件名称] 渲染和交互测试
// ============================================================

test.describe('@component [组件名称] 组件测试', () => {
  // -------------------------------------------------------
  // 渲染测试
  // -------------------------------------------------------

  test('应该正确渲染组件的基本结构', async ({ page }) => {
    // 挂载组件（根据项目实际情况调整）
    await page.goto('/__components/[component-path]');

    // 验证组件存在
    await expect(page.getByTestId('[component-testid]')).toBeVisible();

    // 验证关键子元素
    await expect(page.getByTestId('[child-element]')).toBeVisible();
  });

  test('应该根据 Props 正确渲染内容', async ({ page }) => {
    await page.goto('/__components/[component-path]?title=测试标题&count=42');

    // 验证文本渲染
    await expect(page.getByTestId('[title-element]')).toContainText('测试标题');
    await expect(page.getByTestId('[count-element]')).toContainText('42');
  });

  // -------------------------------------------------------
  // Props 验证测试
  // -------------------------------------------------------

  test('应该在缺少必填 Props 时显示默认内容', async ({ page }) => {
    await page.goto('/__components/[component-path]');

    // 验证默认值
    await expect(page.getByTestId('[element]')).toHaveText('默认值');
  });

  test('应该在 Props 变化时更新渲染', async ({ page }) => {
    await page.goto('/__components/[component-path]?title=初始值');

    await expect(page.getByTestId('[title-element]')).toContainText('初始值');

    // 修改 Props
    await page.evaluate(() => {
      // 模拟 Props 更新（根据项目状态管理方式调整）
      window.dispatchEvent(
        new CustomEvent('update-props', {
          detail: { title: '更新值' },
        })
      );
    });

    await expect(page.getByTestId('[title-element]')).toContainText('更新值');
  });

  // -------------------------------------------------------
  // 事件触发测试
  // -------------------------------------------------------

  test('点击按钮时应该触发点击事件', async ({ page }) => {
    await page.goto('/__components/[component-path]');

    // 设置事件监听
    const eventPromise = page.evaluate(() => {
      return new Promise((resolve) => {
        window.addEventListener('test-event', (e) => {
          resolve((e as CustomEvent).detail);
        });
      });
    });

    // 触发点击
    await page.getByTestId('[button-element]').click();

    // 验证事件触发
    const eventData = await eventPromise;
    expect(eventData).toBeTruthy();
  });

  test('表单提交时应该发送正确的数据', async ({ page }) => {
    await page.goto('/__components/[component-path]');

    // 填写表单
    await page.getByTestId('form-username').fill('testuser');
    await page.getByTestId('form-email').fill('test@example.com');

    // 监听表单提交事件
    const submitPromise = page.evaluate(() => {
      return new Promise((resolve) => {
        window.addEventListener('form-submit', (e) => {
          resolve((e as CustomEvent).detail);
        });
      });
    });

    // 提交表单
    await page.getByTestId('form-submit').click();

    // 验证提交数据
    const submitData = await submitPromise;
    expect(submitData).toMatchObject({
      username: 'testuser',
      email: 'test@example.com',
    });
  });

  // -------------------------------------------------------
  // 交互行为测试
  // -------------------------------------------------------

  test('鼠标悬停时应该显示提示', async ({ page }) => {
    await page.goto('/__components/[component-path]');

    // 初始状态：提示不可见
    await expect(page.getByTestId('[tooltip-element]')).not.toBeVisible();

    // 悬停
    await page.getByTestId('[trigger-element]').hover();

    // 验证提示显示
    await expect(page.getByTestId('[tooltip-element]')).toBeVisible();
  });

  test('点击切换时应该切换展开/收起状态', async ({ page }) => {
    await page.goto('/__components/[component-path]');

    // 初始状态：收起
    await expect(page.getByTestId('[content-element]')).not.toBeVisible();

    // 点击展开
    await page.getByTestId('[toggle-button]').click();
    await expect(page.getByTestId('[content-element]')).toBeVisible();

    // 点击收起
    await page.getByTestId('[toggle-button]').click();
    await expect(page.getByTestId('[content-element]')).not.toBeVisible();
  });

  // -------------------------------------------------------
  // 键盘可访问性测试
  // -------------------------------------------------------

  test('应该支持键盘导航', async ({ page }) => {
    await page.goto('/__components/[component-path]');

    // Tab 导航
    await page.keyboard.press('Tab');
    await expect(page.getByTestId('[first-focusable]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.getByTestId('[second-focusable]')).toBeFocused();
  });

  test('回车键应该触发点击', async ({ page }) => {
    await page.goto('/__components/[component-path]');

    // 聚焦按钮
    await page.getByTestId('[button-element]').focus();

    // 按回车
    await page.keyboard.press('Enter');

    // 验证点击效果
    await expect(page.getByTestId('[result-element]')).toBeVisible();
  });

  // -------------------------------------------------------
  // 快照测试
  // -------------------------------------------------------

  test('组件渲染快照应该一致', async ({ page }) => {
    await page.goto('/__components/[component-path]');
    await page.waitForLoadState('networkidle');

    const component = page.getByTestId('[component-testid]');
    await expect(component).toHaveScreenshot('[component-name]-snapshot.png', {
      maxDiffPixels: 20,
    });
  });
});
