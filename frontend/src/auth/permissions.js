/**
 * Frontend access-control helper (RBAC).
 *
 * The backend is the source of truth: `GET /auth/me` returns the effective
 * permission actions granted to the signed-in user's role. This module mirrors
 * that list so the UI can hide menus, routes and buttons the user may not use.
 *
 * This is a UX layer only — every action is still enforced server-side by the
 * `require_permission` dependency, so hiding a button never substitutes for the
 * real authorization check.
 */
import { useMemo } from 'react';
import { useAuth } from './AuthContext';

/** Reserved role code that bypasses every permission check (mirrors backend). */
export const ADMIN_ROLE = 'admin';

/**
 * Landing-route candidates, most-used first. Used to send a user to the first
 * page their role can actually open instead of a guaranteed 403.
 */
export const HOME_ROUTES = [
  { permission: 'bill:view', path: '/phieu-gui' },
  { permission: 'customer:view', path: '/khach-hang' },
  { permission: 'depot:view', path: '/buu-cuc' },
  { permission: 'fleet:view', path: '/doi-xe' },
  { permission: 'iam:view_users', path: '/nhan-vien' },
  { permission: 'iam:manage_permissions', path: '/phan-quyen' },
];

/**
 * First route the user may open, falling back to the self-service account page
 * (`/tai-khoan` needs no permission, so a landing route always exists).
 *
 * @param {(action: string) => boolean} can - permission predicate
 */
export function homePathFor(can) {
  const match = HOME_ROUTES.find((route) => can(route.permission));
  return match ? match.path : '/tai-khoan';
}

export class PermissionManager {
  constructor(user) {
    this.user = user;
  }

  get role() {
    return this.user?.role ?? null;
  }

  get permissions() {
    return Array.isArray(this.user?.permissions) ? this.user.permissions : [];
  }

  get isAdmin() {
    return this.role === ADMIN_ROLE;
  }

  /** True when the user holds `action` (the admin role bypasses every check). */
  has(action) {
    if (!action) return true;
    return this.isAdmin || this.permissions.includes(action);
  }

  /** True when the user holds at least one of `actions`. */
  any(actions = []) {
    const list = Array.isArray(actions) ? actions : [actions];
    if (list.length === 0) return true;
    return this.isAdmin || list.some((action) => this.permissions.includes(action));
  }

  /** True when the user holds every one of `actions`. */
  all(actions = []) {
    const list = Array.isArray(actions) ? actions : [actions];
    if (list.length === 0) return true;
    return this.isAdmin || list.every((action) => this.permissions.includes(action));
  }
}

/** Convenience helper for non-React call sites. */
export function can(user, action) {
  return new PermissionManager(user).has(action);
}

/**
 * React hook returning memoised permission checks for the current user.
 *
 * @returns {{isAdmin: boolean, role: string|null, permissions: string[],
 *   can: (action: string) => boolean,
 *   canAny: (actions: string[]) => boolean,
 *   canAll: (actions: string[]) => boolean}}
 */
export function usePermission() {
  const { currentUser } = useAuth();

  return useMemo(() => {
    const manager = new PermissionManager(currentUser);
    return {
      isAdmin: manager.isAdmin,
      role: manager.role,
      permissions: manager.permissions,
      can: (action) => manager.has(action),
      canAny: (actions) => manager.any(actions),
      canAll: (actions) => manager.all(actions),
    };
  }, [currentUser]);
}

export default PermissionManager;
