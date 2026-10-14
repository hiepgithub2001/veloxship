/**
 * Unit tests for the frontend permission manager.
 *
 * The backend is the source of truth for the permission list; these tests pin
 * down the client-side mirroring rules (admin bypass, single/any/all checks).
 */
import { describe, expect, it } from 'vitest';

import { HOME_ROUTES, PermissionManager, can, homePathFor } from './permissions';

const operator = {
  role: 'operator',
  permissions: ['bill:view', 'bill:create', 'customer:view'],
};

const admin = { role: 'admin', permissions: [] };

describe('PermissionManager', () => {
  it('grants a held action and denies a missing one', () => {
    const manager = new PermissionManager(operator);
    expect(manager.has('bill:create')).toBe(true);
    expect(manager.has('bill:delete')).toBe(false);
  });

  it('bypasses every check for the admin role', () => {
    const manager = new PermissionManager(admin);
    expect(manager.isAdmin).toBe(true);
    expect(manager.has('iam:manage_permissions')).toBe(true);
    expect(manager.any(['nothing:here'])).toBe(true);
    expect(manager.all(['nothing:here', 'nor:this'])).toBe(true);
  });

  it('treats a missing user / permissions list as no access', () => {
    expect(new PermissionManager(null).permissions).toEqual([]);
    expect(new PermissionManager(null).has('bill:view')).toBe(false);
    expect(new PermissionManager({ role: 'operator' }).permissions).toEqual([]);
    expect(new PermissionManager({ role: 'operator' }).has('bill:view')).toBe(false);
  });

  it('requires at least one action for any()', () => {
    const manager = new PermissionManager(operator);
    expect(manager.any(['bill:delete', 'bill:view'])).toBe(true);
    expect(manager.any(['bill:delete', 'bill:cancel'])).toBe(false);
  });

  it('requires every action for all()', () => {
    const manager = new PermissionManager(operator);
    expect(manager.all(['bill:view', 'bill:create'])).toBe(true);
    expect(manager.all(['bill:view', 'bill:delete'])).toBe(false);
  });

  it('accepts a single action string in any()/all()', () => {
    const manager = new PermissionManager(operator);
    expect(manager.any('bill:view')).toBe(true);
    expect(manager.all('bill:delete')).toBe(false);
  });

  it('treats an empty request as allowed (no gate requested)', () => {
    const manager = new PermissionManager(operator);
    expect(manager.any([])).toBe(true);
    expect(manager.all([])).toBe(true);
    expect(manager.has('')).toBe(true);
  });
});

describe('can()', () => {
  it('mirrors PermissionManager.has for non-React call sites', () => {
    expect(can(operator, 'bill:create')).toBe(true);
    expect(can(operator, 'bill:delete')).toBe(false);
    expect(can(admin, 'anything:at:all')).toBe(true);
  });
});

describe('homePathFor()', () => {
  it('picks the first route the user may open', () => {
    const clerk = new PermissionManager({ role: 'clerk', permissions: ['depot:view'] });
    expect(homePathFor((action) => clerk.has(action))).toBe('/buu-cuc');
  });

  it('prefers the most-used route when several are allowed', () => {
    const manager = new PermissionManager({
      role: 'operator',
      permissions: ['bill:view', 'customer:view'],
    });
    expect(homePathFor((action) => manager.has(action))).toBe('/phieu-gui');
  });

  it('sends the admin to the first candidate', () => {
    expect(homePathFor((action) => new PermissionManager(admin).has(action))).toBe(
      HOME_ROUTES[0].path,
    );
  });

  it('falls back to the self-service account page when nothing else is allowed', () => {
    const manager = new PermissionManager({ role: 'locked', permissions: [] });
    expect(homePathFor((action) => manager.has(action))).toBe('/tai-khoan');
  });
});
