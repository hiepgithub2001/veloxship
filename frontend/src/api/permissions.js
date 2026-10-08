/**
 * Roles & role-permissions API functions + assignable action catalogue.
 */
import client from './client';

export async function getRoles() {
  const { data } = await client.get('/roles');
  return data;
}

export async function createRole(payload) {
  const { data } = await client.post('/roles', payload);
  return data;
}

export async function updateRole(code, payload) {
  const { data } = await client.patch(`/roles/${code}`, payload);
  return data;
}

export async function deleteRole(code) {
  await client.delete(`/roles/${code}`);
}

export async function updateRolePermissions(code, actions) {
  const { data } = await client.put(`/roles/${code}/permissions`, { actions });
  return data;
}

export async function getPermissionCatalog() {
  const { data } = await client.get('/permissions/catalog');
  return data;
}
