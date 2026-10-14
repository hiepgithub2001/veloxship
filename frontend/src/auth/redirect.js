/**
 * Login redirect helpers.
 *
 * Two things must hold so that an expired session and a deliberate sign-out
 * both land the user correctly:
 *
 *   1. The path they were on is captured in full — `pathname`, `search` and
 *      `hash`. Keeping only `pathname` silently drops filters, pagination and
 *      deep links (e.g. `/phieu-gui?status=cho-xu-ly&page=2`).
 *   2. The captured path is safe to navigate to. A login path would bounce the
 *      user straight back to login, and an absolute/protocol-relative URL would
 *      turn the login page into an open redirect.
 */

/** Vietnamese login route. */
export const LOGIN_PATH = '/dang-nhap';

/** Flatten a react-router location (or a plain string) into a navigable path. */
export function toPath(location) {
  if (!location) return '';
  if (typeof location === 'string') return location;
  const { pathname = '', search = '', hash = '' } = location;
  return `${pathname}${search}${hash}`;
}

/** True when `path` points at the login page itself. */
export function isLoginPath(path = '') {
  return path === LOGIN_PATH || path.startsWith(`${LOGIN_PATH}?`) || path.startsWith(`${LOGIN_PATH}#`);
}

/**
 * True when `path` is a safe same-origin absolute path.
 * Rejects external (`https://…`), protocol-relative (`//evil.com`) and relative
 * (`foo`) targets, plus anything containing a control character.
 */
export function isSafeInternalPath(path = '') {
  if (!path.startsWith('/')) return false;
  if (path.startsWith('//')) return false;
  // eslint-disable-next-line no-control-regex
  return !/[\u0000-\u001f\u007f]/.test(path);
}

/**
 * Pick where to send the user after a successful login.
 *
 * @param {object|string|null} from - `location.state.from`, or a path string
 * @param {string} fallback - landing path when `from` is unusable
 * @returns {string} a safe internal path, never the login page
 */
export function resolveReturnPath(from, fallback = LOGIN_PATH) {
  const path = toPath(from);
  if (!path || isLoginPath(path) || !isSafeInternalPath(path)) {
    return fallback;
  }
  return path;
}
