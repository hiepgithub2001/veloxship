/**
 * E2E: PWA manifest and service worker registration.
 */
import { test, expect } from '@playwright/test';

test.describe('PWA Manifest & SW', () => {
  test('serves valid manifest.webmanifest', async ({ page }) => {
    const response = await page.goto('/manifest.webmanifest');
    expect(response.status()).toBe(200);
    const manifest = await response.json();
    expect(manifest.name).toContain('VeloxShip');
    expect(manifest.lang).toBe('vi-VN');
    expect(manifest.display).toBe('standalone');
    expect(manifest.icons.length).toBeGreaterThanOrEqual(3);
  });

  test('index.html links to manifest', async ({ page }) => {
    await page.goto('/');
    const link = await page.$('link[rel="manifest"]');
    expect(link).toBeTruthy();
    const href = await link.getAttribute('href');
    expect(href).toContain('manifest.webmanifest');
  });

  test('has theme-color meta tag', async ({ page }) => {
    await page.goto('/');
    const meta = await page.$('meta[name="theme-color"]');
    expect(meta).toBeTruthy();
    const content = await meta.getAttribute('content');
    expect(content).toBe('#c0392b');
  });

  test('has apple-mobile-web-app-capable meta', async ({ page }) => {
    await page.goto('/');
    const meta = await page.$('meta[name="apple-mobile-web-app-capable"]');
    expect(meta).toBeTruthy();
  });

  test('has apple-touch-icon link', async ({ page }) => {
    await page.goto('/');
    const link = await page.$('link[rel="apple-touch-icon"]');
    expect(link).toBeTruthy();
  });
});
