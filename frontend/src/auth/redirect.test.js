/**
 * Unit tests for the login redirect helpers.
 *
 * These pin down the two behaviours that make "return to the page you were on"
 * work without becoming a redirect loop or an open redirect.
 */
import { describe, expect, it } from 'vitest';

import {
  LOGIN_PATH,
  isLoginPath,
  isSafeInternalPath,
  resolveReturnPath,
  toPath,
} from './redirect';

describe('toPath', () => {
  it('keeps pathname, query string and hash', () => {
    expect(toPath({ pathname: '/phieu-gui', search: '?page=2', hash: '#row-5' })).toBe(
      '/phieu-gui?page=2#row-5',
    );
  });

  it('tolerates a partial or missing location', () => {
    expect(toPath({ pathname: '/tai-khoan' })).toBe('/tai-khoan');
    expect(toPath('/plain')).toBe('/plain');
    expect(toPath(null)).toBe('');
    expect(toPath(undefined)).toBe('');
  });
});

describe('isLoginPath', () => {
  it('matches the login route with or without query/hash', () => {
    expect(isLoginPath(LOGIN_PATH)).toBe(true);
    expect(isLoginPath(`${LOGIN_PATH}?next=1`)).toBe(true);
    expect(isLoginPath(`${LOGIN_PATH}#form`)).toBe(true);
  });

  it('does not match other routes', () => {
    expect(isLoginPath('/phieu-gui')).toBe(false);
    expect(isLoginPath('/dang-nhap-khac')).toBe(false);
  });
});

describe('isSafeInternalPath', () => {
  it('accepts same-origin absolute paths', () => {
    expect(isSafeInternalPath('/phieu-gui?page=2')).toBe(true);
  });

  it('rejects external, protocol-relative and relative targets', () => {
    expect(isSafeInternalPath('https://evil.example')).toBe(false);
    expect(isSafeInternalPath('//evil.example')).toBe(false);
    expect(isSafeInternalPath('phieu-gui')).toBe(false);
    expect(isSafeInternalPath('')).toBe(false);
  });

  it('rejects control characters', () => {
    expect(isSafeInternalPath('/phieu-gui\nSet-Cookie: x=1')).toBe(false);
  });
});

describe('resolveReturnPath', () => {
  it('preserves the full target including filters and pagination', () => {
    const from = {
      pathname: '/phieu-gui',
      search: '?status=cho-xu-ly&page=2',
      hash: '#row-5',
    };
    expect(resolveReturnPath(from, '/tai-khoan')).toBe(
      '/phieu-gui?status=cho-xu-ly&page=2#row-5',
    );
  });

  it('falls back when there is no captured location', () => {
    expect(resolveReturnPath(undefined, '/tai-khoan')).toBe('/tai-khoan');
    expect(resolveReturnPath({}, '/tai-khoan')).toBe('/tai-khoan');
  });

  it('never returns the login page, so login cannot bounce to itself', () => {
    expect(resolveReturnPath({ pathname: LOGIN_PATH }, '/tai-khoan')).toBe('/tai-khoan');
    expect(resolveReturnPath({ pathname: LOGIN_PATH, search: '?x=1' }, '/tai-khoan')).toBe(
      '/tai-khoan',
    );
  });

  it('refuses external targets (open-redirect guard)', () => {
    expect(resolveReturnPath('https://evil.example', '/tai-khoan')).toBe('/tai-khoan');
    expect(resolveReturnPath({ pathname: '//evil.example' }, '/tai-khoan')).toBe('/tai-khoan');
  });

  it('defaults the fallback to the login path', () => {
    expect(resolveReturnPath(null)).toBe(LOGIN_PATH);
  });
});
