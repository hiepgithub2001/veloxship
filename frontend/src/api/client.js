/**
 * Axios instance with JWT bearer interceptor and auto-refresh on 401.
 *
 * Access tokens are short-lived (15 min), so a request may arrive with an
 * already-expired token. Two mechanisms cover that:
 *
 *   1. Proactive — the request interceptor refreshes *before* sending when the
 *      token is within `EXPIRY_MARGIN_SECONDS` of expiring.
 *   2. Reactive — a 401 triggers one refresh and one replay of the request.
 *
 * Both paths funnel through `runRefresh()`, a single-flight promise, so N
 * concurrent failures produce exactly one call to `/auth/refresh` and the
 * others await the same result.
 *
 * `/auth/login` and `/auth/refresh` are deliberately excluded from both paths.
 * Without that exclusion an expired *refresh* token makes `/auth/refresh`
 * itself 401, which re-enters the interceptor and calls refresh again — each
 * attempt being a fresh request config, so a per-request `_retry` flag never
 * trips and the client loops forever instead of redirecting to login.
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

/** Endpoints that must never trigger (or receive) the refresh flow. */
const AUTH_ENDPOINTS = ['/auth/login', '/auth/refresh'];

/** Refresh this many seconds before the token actually expires. */
export const EXPIRY_MARGIN_SECONDS = 60;

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Will be set by AuthContext
let getAccessToken = () => null;
let onRefreshFailed = () => {};
let refreshTokenFn = null;

export function setAuthHelpers({ getToken, onLogout, refresh }) {
  getAccessToken = getToken;
  onRefreshFailed = onLogout;
  refreshTokenFn = refresh;
}

/** True when `url` is an auth endpoint that owns its own 401 semantics. */
export function isAuthEndpoint(url = '') {
  return AUTH_ENDPOINTS.some((endpoint) => url.includes(endpoint));
}

/**
 * Read the `exp` claim (seconds since epoch) from a JWT without verifying it.
 * Returns null when the token is malformed — callers treat that as "no
 * expiry information", never as "expired".
 */
export function decodeTokenExpiry(token) {
  if (!token || typeof token !== 'string') return null;
  const payload = token.split('.')[1];
  if (!payload) return null;
  try {
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    // JWT base64url usually omits padding, which `atob` rejects — restore it.
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
    const claims = JSON.parse(atob(padded));
    return typeof claims.exp === 'number' ? claims.exp : null;
  } catch {
    return null;
  }
}

/**
 * True when the token is expired or expires within `marginSeconds`.
 * A token with no readable `exp` is treated as usable — the reactive 401 path
 * still covers it.
 */
export function isTokenExpiringSoon(token, marginSeconds = EXPIRY_MARGIN_SECONDS) {
  const expiry = decodeTokenExpiry(token);
  if (expiry === null) return false;
  return expiry * 1000 - Date.now() <= marginSeconds * 1000;
}

// Single-flight refresh: concurrent callers share one in-flight request.
let refreshPromise = null;

// Latched once a refresh is rejected. A rejected refresh token cannot start
// working again on its own, so without this latch a proactive attempt followed
// by the reactive 401 path would call `/auth/refresh` twice for one dead
// session. Cleared by `resetAuthState()` when a new session begins.
let refreshRejected = false;

/**
 * Forget the "refresh already failed" latch. Call this whenever the session
 * changes — a fresh login provides a new refresh token, so a previously dead
 * session must not keep blocking refreshes.
 */
export function resetAuthState() {
  refreshRejected = false;
}

function runRefresh() {
  if (refreshRejected) {
    const error = new Error('Session refresh previously failed');
    error.code = 'REFRESH_ALREADY_FAILED';
    return Promise.reject(error);
  }

  if (!refreshPromise) {
    refreshPromise = Promise.resolve()
      .then(() => refreshTokenFn())
      .then((token) => {
        refreshRejected = false;
        return token;
      })
      .catch((error) => {
        refreshRejected = true;
        throw error;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

// Request interceptor — attach the bearer token, refreshing it first if it is
// about to expire.
client.interceptors.request.use(async (config) => {
  if (isAuthEndpoint(config.url)) return config;

  let token = getAccessToken();

  if (token && refreshTokenFn && isTokenExpiringSoon(token)) {
    try {
      token = await runRefresh();
    } catch {
      // Leave the stale token attached; the 401 path below owns the failure
      // handling (session teardown + redirect) so it happens in one place.
    }
  }

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — refresh once and replay on 401.
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    const canRefresh =
      status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isAuthEndpoint(originalRequest.url) &&
      typeof refreshTokenFn === 'function';

    if (!canRefresh) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      const newToken = await runRefresh();
      originalRequest.headers.Authorization = `Bearer ${newToken}`;
      return client(originalRequest);
    } catch (refreshError) {
      // Refresh token is gone/expired: end the session. The guard above
      // guarantees this can only happen once per request chain.
      onRefreshFailed(refreshError);
      return Promise.reject(refreshError);
    }
  },
);

export default client;
