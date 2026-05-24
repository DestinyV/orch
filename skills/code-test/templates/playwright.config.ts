// Playwright 配置模板 - E2E + 视觉回归测试
// 可直接用于前端项目的 Playwright 测试配置

import { defineConfig, devices } from '@playwright/test';

/**
 * 读取环境变量配置
 * 支持 .env 文件配置测试环境变量
 */
const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:5173';
const CI = !!process.env.CI;

export default defineConfig({
  // 测试目录配置
  testDir: './tests/e2e',

  // 完全并行执行测试文件
  fullyParallel: true,

  // CI 环境下禁止文件并行，避免资源竞争
  forbidOnly: CI,

  // 失败重试次数（CI 环境重试 2 次）
  retries: CI ? 2 : 0,

  // 并行工作进程数（CI 使用一半 CPU，本地使用 50%）
  workers: CI ? '50%' : '50%',

  // 测试报告输出
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['list'],
    ['json', { outputFile: 'test-results/e2e-results.json' }],
  ],

  // 共享配置应用于所有测试
  use: {
    // 应用基础 URL
    baseURL: BASE_URL,

    // 每次测试后追踪，方便调试
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',

    // 超时配置
    actionTimeout: 10_000,
    navigationTimeout: 30_000,

    // 测试用户标识（用于数据隔离）
    testIdAttribute: 'data-testid',
  },

  // Web Server 自动启动（开发服务器）
  webServer: {
    command: 'npm run dev',
    url: BASE_URL,
    reuseExistingServer: !CI,
    timeout: 120_000,
  },

  // 测试项目配置（多浏览器 + 多视口）
  projects: [
    // === E2E 功能测试 ===

    {
      name: 'chromium-e2e',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
      testMatch: /.*\.e2e\.test\.ts/,
      grep: /@e2e/,
    },

    {
      name: 'firefox-e2e',
      use: {
        ...devices['Desktop Firefox'],
        viewport: { width: 1280, height: 720 },
      },
      testMatch: /.*\.e2e\.test\.ts/,
      grep: /@e2e/,
    },

    // === 移动端 E2E 测试 ===

    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 7'] },
      testMatch: /.*\.e2e\.test\.ts/,
      grep: /@e2e/,
    },

    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 14'] },
      testMatch: /.*\.e2e\.test\.ts/,
      grep: /@e2e/,
    },

    // === 视觉回归测试 ===

    {
      name: 'chromium-visual',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
      testMatch: /.*\.visual\.test\.ts/,
      grep: /@visual/,
    },

    // === 组件 UI 测试（使用 Playwright Component Testing） ===

    {
      name: 'chromium-component',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
      testMatch: /.*\.component\.test\.ts/,
      grep: /@component/,
    },
  ],
});
