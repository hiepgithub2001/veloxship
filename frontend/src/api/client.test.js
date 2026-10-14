/**
 * Unit tests for the Axios auth interceptor.
 *
 * The behaviour under test is the expiry path: a dead refresh token must end
 * the session exactly once instead of re-entering the interceptor forever.
 * `/auth/refresh` is called through this same client, so a 401 there is the
 * precise input that used to cause the loop.
 */
import { AxiosError } from 'axios';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import client, {
  decodeTokenExpiry,
  isAuthEndpoint,
  isTokenExpiringSoon,
  resetAuthState,
  setAuthHelpers,
} from './client';

/** Build an unsigned JWT with the given claims (base64url, padding stripped). */
function makeJwt(claims) {
  const encode = (obj) =>
    btoa(JSON.stringify(obj)).replace(/=+$/, '').replace(/\+/g, '-').replace(/\//g, '_');
  return `${encode({ alg: 'HS256', typ: 'JWT' })}.${encode(claims)}.signature`;
}

const nowSeconds = () => Math.floor(Date.now() / 1000);
const VALID_TOKEN = makeJwt({ sub: '1', exp: nowSeconds() + 3600 });
const EXPIRED_TOKEN = makeJwt({ sub: '1', exp: nowSeconds() - 60 });

const originalAdapter = client.defaults.adapter;
let requests = [];
let respond;

function installAdapter() {
  client.defaults.adapter = async (config) => {
    requests.push({
      url: config.url,
      authorization: config.headers?.Authorization,
      retried: config._retry === true,
    });

    const status = respond(config);
    if (status >= 400) {
      throw new AxiosError(
        `Request failed with status ${status}`,
        'ERR_BAD_REQUEST',
        config,
        null,
        { status, statusText: '', data: {}, headers: {}, config },
      );
    }
    return { status, statusText: 'OK', data: {}, headers: {}, config };
  };
}

beforeEach(() => {
  requests = [];
  respond = () => 200;
  resetAuthState();
  installAdapter();
});

afterEach(() => {
  client.defaults.adapter = originalAdapter;
  setAuthHelpers({ getToken: () => null, onLogout: () => {}, refresh: null });
});

describe('isAuthEndpoint', () => {
  it('matches only the endpoints that own their 401 semantics', () => {
    expect(isAuthEndpoint('/auth/login')).toBe(true);
    expect(isAuthEndpoint('/auth/refresh')).toBe(true);
    expect(isAuthEndpoint('/bills')).toBe(false);
    expect(isAuthEndpoint(undefined)).toBe(false);
  });
});

describe('token expiry helpers', () => {
  it('reads the exp claim', () => {
    expect(decodeTokenExpiry(VALID_TOKEN)).toBe(nowSeconds() + 3600);
  });

  it('returns null for a malformed token instead of throwing', () => {
    expect(decodeTokenExpiry('not-a-jwt')).toBeNull();
    expect(decodeTokenExpiry('')).toBeNull();
    expect(decodeTokenExpiry(null)).toBeNull();
  });

  it('flags expired and nearly-expired tokens only', () => {
    expect(isTokenExpiringSoon(EXPIRED_TOKEN)).toBe(true);
    expect(isTokenExpiringSoon(VALID_TOKEN)).toBe(false);

    const soon = makeJwt({ sub: '1', exp: nowSeconds() + 10 });
    expect(isTokenExpiringSoon(soon, 60)).toBe(true);
    expect(isTokenExpiringSoon(soon, 5)).toBe(false);
  });

  it('treats an unreadable token as usable (401 path still covers it)', () => {
    expect(isTokenExpiringSoon('garbage')).toBe(false);
  });
});

describe('refresh recursion guard', () => {
  it('does not attempt a refresh when /auth/refresh itself returns 401', async () => {
    const refresh = vi.fn(async () => {
      throw new Error('must not be called');
    });
    const onLogout = vi.fn();
    setAuthHelpers({ getToken: () => EXPIRED_TOKEN, onLogout, refresh });
    respond = () => 401;

    await expect(client.post('/auth/refresh', { refresh_token: 'dead' })).rejects.toBeTruthy();

    expect(refresh).not.toHaveBeenCalled();
    expect(onLogout).not.toHaveBeenCalled();
  });

  it('does not attempt a refresh when /auth/login returns 401', async () => {
    const refresh = vi.fn(async () => {
      throw new Error('must not be called');
    });
    setAuthHelpers({ getToken: () => null, onLogout: vi.fn(), refresh });
    respond = () => 401;

    await expect(client.post('/auth/login', { username: 'a', password: 'b' })).rejects.toBeTruthy();

    expect(refresh).not.toHaveBeenCalled();
  });

  it('ends the session after exactly one refresh attempt when the refresh token is dead', async () => {
    const refresh = vi.fn(async () => {
      throw new Error('refresh token expired');
    });
    const onLogout = vi.fn();
    setAuthHelpers({ getToken: () => EXPIRED_TOKEN, onLogout, refresh });
    respond = () => 401;

    await expect(client.get('/bills')).rejects.toBeTruthy();

    // The latch is what keeps this at 1: proactive refresh fails, then the
    // reactive 401 path must not try again.
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(onLogout).toHaveBeenCalledTimes(1);
    expect(requests.filter((r) => r.url === '/bills')).toHaveLength(1);
  });

  it('allows a refresh again after resetAuthState (a new session)', async () => {
    const refresh = vi.fn(async () => {
      throw new Error('dead');
    });
    setAuthHelpers({ getToken: () => EXPIRED_TOKEN, onLogout: vi.fn(), refresh });
    respond = () => 401;

    await expect(client.get('/bills')).rejects.toBeTruthy();
    expect(refresh).toHaveBeenCalledTimes(1);

    resetAuthState();

    await expect(client.get('/phieu-gui')).rejects.toBeTruthy();
    expect(refresh).toHaveBeenCalledTimes(2);
  });
});

describe('refresh happy paths', () => {
  it('refreshes once for concurrent 401s and replays every request', async () => {
    const refresh = vi.fn(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10));
      return VALID_TOKEN;
    });
    setAuthHelpers({ getToken: () => VALID_TOKEN, onLogout: vi.fn(), refresh });

    const attempts = new Map();
    respond = (config) => {
      const seen = (attempts.get(config.url) || 0) + 1;
      attempts.set(config.url, seen);
      return seen === 1 ? 401 : 200;
    };

    const responses = await Promise.all([
      client.get('/a'),
      client.get('/b'),
      client.get('/c'),
    ]);

    expect(responses.every((response) => response.status === 200)).toBe(true);
    expect(refresh).toHaveBeenCalledTimes(1);
    // Each request was replayed with the refreshed bearer token.
    for (const url of ['/a', '/b', '/c']) {
      const replays = requests.filter((r) => r.url === url && r.retried);
      expect(replays).toHaveLength(1);
      expect(replays[0].authorization).toBe(`Bearer ${VALID_TOKEN}`);
    }
  });

  it('refreshes proactively before sending when the token is about to expire', async () => {
    const refresh = vi.fn(async () => VALID_TOKEN);
    setAuthHelpers({ getToken: () => EXPIRED_TOKEN, onLogout: vi.fn(), refresh });
    respond = () => 200;

    await client.get('/bills');

    expect(refresh).toHaveBeenCalledTimes(1);
    // No 401 round-trip needed — the first attempt already carried a new token.
    expect(requests).toHaveLength(1);
    expect(requests[0].authorization).toBe(`Bearer ${VALID_TOKEN}`);
  });

  it('attaches the bearer token when it is still valid', async () => {
    const refresh = vi.fn(async () => VALID_TOKEN);
    setAuthHelpers({ getToken: () => VALID_TOKEN, onLogout: vi.fn(), refresh });
    respond = () => 200;

    await client.get('/bills');

    expect(refresh).not.toHaveBeenCalled();
    expect(requests[0].authorization).toBe(`Bearer ${VALID_TOKEN}`);
  });

  it('reports a logout once and rejects when refresh fails on the reactive path', async () => {
    const refresh = vi.fn(async () => {
      throw new Error('dead');
    });
    const onLogout = vi.fn();
    // Token looks valid so the proactive path stays out of the way, leaving
    // only the 401 -> refresh -> fail flow under test.
    setAuthHelpers({ getToken: () => VALID_TOKEN, onLogout, refresh });
    respond = () => 401;

    await expect(client.get('/bills')).rejects.toBeTruthy();

    expect(refresh).toHaveBeenCalledTimes(1);
    expect(onLogout).toHaveBeenCalledTimes(1);
  });
});
