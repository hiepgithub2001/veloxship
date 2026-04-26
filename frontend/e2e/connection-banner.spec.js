/**
 * E2E: Connection banner behavior.
 * Simulates offline mode in the browser context.
 */
import { test, expect } from '@playwright/test';

test.describe('Connection Banner', () => {
  test('shows Vietnamese warning when offline', async ({ page, context }) => {
    await page.goto('/');
    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Initially online — no banner
    await expect(page.locator('#connection-banner')).not.toBeVisible();

    // Go offline
    await context.setOffline(true);
    // Trigger the offline event
    await page.evaluate(() => window.dispatchEvent(new Event('offline')));

    // Banner should appear
    const banner = page.locator('#connection-banner');
    await expect(banner).toBeVisible();
    await expect(banner).toContainText('Mất kết nối');

    // Go back online
    await context.setOffline(false);
    await page.evaluate(() => window.dispatchEvent(new Event('online')));

    // Banner should disappear
    await expect(banner).not.toBeVisible();
  });
});
