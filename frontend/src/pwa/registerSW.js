/**
 * Service worker registration wrapper around vite-plugin-pwa.
 * Exports registerAppSW() and an event-bus for onNeedRefresh.
 */

/** @type {Array<Function>} */
let needRefreshListeners = [];

/** @type {Function|null} */
let updateSWFn = null;

/**
 * Subscribe to the "need refresh" event.
 * Returns an unsubscribe function.
 */
export function onNeedRefresh(callback) {
  needRefreshListeners.push(callback);
  return () => {
    needRefreshListeners = needRefreshListeners.filter((fn) => fn !== callback);
  };
}

/**
 * Trigger the service worker update (skipWaiting + reload).
 * @param {boolean} reloadPage
 */
export function updateSW(reloadPage = true) {
  if (updateSWFn) {
    updateSWFn(reloadPage);
  }
}

/**
 * Register the service worker. Call once after React mounts.
 *
 * @param {{ onNeedRefresh?: Function, onOfflineReady?: Function }} callbacks
 */
export async function registerAppSW({ onNeedRefresh: onNeedRefreshCb, onOfflineReady } = {}) {
  // Only register in production or when explicitly enabled
  if (!('serviceWorker' in navigator)) return;

  try {
    const { registerSW } = await import('virtual:pwa-register');

    updateSWFn = registerSW({
      immediate: true,
      onNeedRefresh() {
        // Notify all subscribers
        needRefreshListeners.forEach((fn) => fn());
        // Also call the direct callback if provided
        if (onNeedRefreshCb) onNeedRefreshCb();
      },
      onOfflineReady() {
        // No-op — we are online-only.
        if (onOfflineReady) onOfflineReady();
      },
    });
  } catch {
    // In dev mode or test, virtual:pwa-register may not be available
    console.debug('[PWA] Service worker registration skipped (dev mode).');
  }
}
