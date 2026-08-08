/**
 * E2E: Install prompt behavior.
 * Note: beforeinstallprompt cannot be directly triggered in Playwright.
 * These tests verify the basic rendering contract.
 */
import { test, expect } from '@playwright/test';

test.describe('Install Prompt', () => {
  test('no install banner on initial load (no beforeinstallprompt event)', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Should not show the install banner without beforeinstallprompt
    await expect(page.locator('.pwa-install-banner')).not.toBeVisible();
  });

  test('no iOS overlay on non-iOS browser', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Playwright uses Chromium, not Safari, so no iOS overlay
    await expect(page.locator('#pwa-ios-overlay')).not.toBeVisible();
  });
});

test.describe('Responsive Layout', () => {
  test('sidebar is hidden on mobile viewport', async ({ page }) => {
    await page.goto('/');
    // On mobile viewport (Pixel 7), sidebar should be collapsed/hidden
    const sider = page.locator('.ant-layout-sider');
    if (await sider.isVisible()) {
      const box = await sider.boundingBox();
      // Should be zero-width or collapsed
      expect(box.width).toBeLessThanOrEqual(80);
    }
  });
});
