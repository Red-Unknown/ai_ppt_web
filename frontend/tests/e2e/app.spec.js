import { test, expect } from '@playwright/test';

test('app loads and shows main interface', async ({ page }) => {
  await page.goto('/');

  // 检查是否存在主聊天区域
  await expect(page.locator('main')).toBeVisible();

  // 检查侧边栏中的 "New Chat" 按钮
  await expect(page.getByRole('button', { name: 'New Chat' })).toBeVisible();

  // 检查侧边栏中的 "Student Profile" 按钮
  await expect(page.getByRole('button', { name: 'Student Profile' })).toBeVisible();
});
