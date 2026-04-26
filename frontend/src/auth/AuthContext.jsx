/**
 * Authentication context — stores tokens and provides login/logout.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import * as authApi from '../api/auth';
import { setAuthHelpers } from '../api/client';

const AuthContext = createContext(null);

const REFRESH_TOKEN_KEY = 'veloxship_refresh_token';

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    setAccessToken(null);
    setCurrentUser(null);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    // PWA: clear any user-prefixed caches on logout (FR-017, FR-020)
    if ('caches' in window) {
      caches.keys().then((keys) =>
        Promise.all(
          keys.filter((k) => k.startsWith('user-')).map((k) => caches.delete(k)),
        ),
      );
    }
  }, []);

  const doRefresh = useCallback(async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) throw new Error('No refresh token');
    const tokens = await authApi.refresh(refreshToken);
    setAccessToken(tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    return tokens.access_token;
  }, []);

  // Wire up the Axios client helpers
  useEffect(() => {
    setAuthHelpers({
      getToken: () => accessToken,
      onLogout: logout,
      refresh: doRefresh,
    });
  }, [accessToken, logout, doRefresh]);

  // On mount, try to restore session via refresh token
  useEffect(() => {
    const init = async () => {
      try {
        const token = await doRefresh();
        setAccessToken(token);
        const user = await authApi.me();
        setCurrentUser(user);
      } catch {
        logout();
      } finally {
        setLoading(false);
      }
    };
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(async (username, password) => {
    const tokens = await authApi.login(username, password);
    setAccessToken(tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    const user = await authApi.me();
    setCurrentUser(user);
    return user;
  }, []);

  const value = useMemo(
    () => ({ currentUser, loading, login, logout, isAuthenticated: !!accessToken }),
    [currentUser, loading, login, logout, accessToken],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export default AuthContext;
