/**
 * Authentication context — stores tokens and provides login/logout.
 *
 * The access token is kept in state for rendering and mirrored into a ref so
 * the Axios interceptor always reads the current value. Reading state through a
 * closure would hand the interceptor the *previous* token for the request that
 * immediately follows a refresh, costing an extra 401 round-trip.
 *
 * Session end has two distinct flavours, and the login page reports them
 * differently:
 *   - `logout()`        — the user asked to sign out. No message.
 *   - `expireSession()` — the refresh token was rejected. Shows `sessionExpired`.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import * as authApi from '../api/auth';
import { setAuthHelpers, resetAuthState } from '../api/client';

const AuthContext = createContext(null);

export const REFRESH_TOKEN_KEY = 'veloxship_refresh_token';

/** Marker so a missing token is never mistaken for an expired session. */
export const NO_REFRESH_TOKEN = 'NO_REFRESH_TOKEN';

function noRefreshTokenError() {
  const error = new Error('No refresh token stored');
  error.code = NO_REFRESH_TOKEN;
  return error;
}

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionExpired, setSessionExpired] = useState(false);

  // Mirrors `accessToken` so the interceptor never reads a stale closure.
  const tokenRef = useRef(null);

  const applyToken = useCallback((token) => {
    tokenRef.current = token;
    setAccessToken(token);
  }, []);

  const getToken = useCallback(() => tokenRef.current, []);

  const clearSession = useCallback(() => {
    applyToken(null);
    setCurrentUser(null);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    resetAuthState();
  }, [applyToken]);

  /** Deliberate sign-out — no expiry notice. */
  const logout = useCallback(() => {
    clearSession();
    setSessionExpired(false);
  }, [clearSession]);

  /**
   * Unrecoverable refresh failure. Clears the session and flags it so the login
   * page explains why. Navigation is left to `ProtectedRoute`, which captures
   * the current location as `from` so the user returns here after signing in.
   */
  const expireSession = useCallback(
    (error) => {
      const hadSession = error?.code !== NO_REFRESH_TOKEN;
      clearSession();
      setSessionExpired(hadSession);
    },
    [clearSession],
  );

  /** Exchange the stored refresh token for a new token pair (rotating). */
  const doRefresh = useCallback(async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) throw noRefreshTokenError();

    try {
      const tokens = await authApi.refresh(refreshToken);
      applyToken(tokens.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
      return tokens.access_token;
    } catch (error) {
      // A rejected refresh token can never succeed on retry — drop it so a
      // later attempt fails fast as NO_REFRESH_TOKEN instead of re-hitting the API.
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      throw error;
    }
  }, [applyToken]);

  // Wire up the Axios client helpers. Everything here is a stable callback, so
  // this effectively runs once.
  useEffect(() => {
    setAuthHelpers({
      getToken,
      onLogout: expireSession,
      refresh: doRefresh,
    });
  }, [getToken, expireSession, doRefresh]);

  // On mount, restore the session from the stored refresh token.
  useEffect(() => {
    const init = async () => {
      if (!localStorage.getItem(REFRESH_TOKEN_KEY)) {
        // Nothing to restore — a first visit, not an expired session.
        setLoading(false);
        return;
      }
      try {
        const token = await doRefresh();
        setCurrentUser(await authApi.me());
      } catch (error) {
        expireSession(error);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [doRefresh, expireSession]);

  const login = useCallback(
    async (username, password) => {
      const tokens = await authApi.login(username, password);
      resetAuthState(); // new session — clear any latch from a dead one
      applyToken(tokens.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
      setSessionExpired(false);
      const user = await authApi.me();
      setCurrentUser(user);
      return user;
    },
    [applyToken],
  );

  // Re-fetch the current user (e.g. after editing profile/avatar) and update state.
  const refreshMe = useCallback(async () => {
    const user = await authApi.me();
    setCurrentUser(user);
    return user;
  }, []);

  /** Called by the login page once it has surfaced the expiry notice. */
  const clearSessionExpired = useCallback(() => setSessionExpired(false), []);

  const value = useMemo(
    () => ({
      currentUser,
      loading,
      login,
      logout,
      refreshMe,
      sessionExpired,
      clearSessionExpired,
      isAuthenticated: !!accessToken,
    }),
    [
      currentUser,
      loading,
      login,
      logout,
      refreshMe,
      sessionExpired,
      clearSessionExpired,
      accessToken,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export default AuthContext;
