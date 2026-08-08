/**
 * App version constants — sourced from Vite build-time injection.
 */

/* eslint-disable no-undef */
export const APP_VERSION = typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : '0.0.0';
export const APP_GIT_SHA = typeof __APP_GIT_SHA__ !== 'undefined' ? __APP_GIT_SHA__ : 'dev';
export const APP_BUILT_AT = typeof __APP_BUILT_AT__ !== 'undefined' ? __APP_BUILT_AT__ : '';
/* eslint-enable no-undef */

/**
 * Format the version string in Vietnamese for display.
 * Returns e.g. "Phiên bản: v0.2.0 (a1b2c3d)"
 */
export function formatVersion() {
  return `Phiên bản: v${APP_VERSION} (${APP_GIT_SHA})`;
}
