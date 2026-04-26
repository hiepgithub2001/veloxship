/**
 * Axios instance with JWT bearer interceptor and auto-refresh on 401.
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

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

// Request interceptor — add Bearer token
client.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Custom error class for network failures (device offline or request unreachable).
 */
export class NetworkError extends Error {
  constructor(originalError) {
    super('Mất kết nối — vui lòng kiểm tra mạng và thử lại');
    this.name = 'NetworkError';
    this.originalError = originalError;
  }
}

// Response interceptor — retry once on 401
let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token);
  });
  failedQueue = [];
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Detect network errors — no response means the request never reached the server
    if (
      error.code === 'ERR_NETWORK' ||
      (!error.response && typeof navigator !== 'undefined' && navigator.onLine === false)
    ) {
      return Promise.reject(new NetworkError(error));
    }

    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry && refreshTokenFn) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return client(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await refreshTokenFn();
        processQueue(null, newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return client(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        onRefreshFailed();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

export default client;
