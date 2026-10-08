/**
 * Users (staff) admin API functions + department/position lookup.
 */
import client from './client';

/**
 * Compact user list for picker selects — available to any authenticated user.
 */
export async function getUserOptions({ search, role } = {}) {
  const params = {};
  if (search) params.search = search;
  if (role) params.role = role;
  const { data } = await client.get('/users/options', { params });
  return data;
}

export async function getUsers({
  page,
  pageSize,
  search,
  role,
  depotId,
  department,
  position,
  isActive,
} = {}) {
  const params = {};
  if (page != null) params.page = page;
  if (pageSize != null) params.page_size = pageSize;
  if (search) params.search = search;
  if (role) params.role = role;
  if (depotId != null) params.depot_id = depotId;
  if (department) params.department = department;
  if (position) params.position = position;
  if (isActive != null) params.is_active = isActive;

  const { data } = await client.get('/users', { params });
  return data;
}

export async function createUser(payload) {
  const { data } = await client.post('/users', payload);
  return data;
}

export async function updateUser(id, payload) {
  const { data } = await client.patch(`/users/${id}`, payload);
  return data;
}

export async function resetUserPassword(id, payload = {}) {
  const { data } = await client.post(`/users/${id}/reset-password`, payload);
  return data;
}

export async function deleteUser(id) {
  const { data } = await client.delete(`/users/${id}`);
  return data;
}

// --- Departments lookup ---

export async function getDepartments() {
  const { data } = await client.get('/departments');
  return data;
}

export async function renameDepartment(name, newName) {
  const { data } = await client.patch(`/departments/${encodeURIComponent(name)}`, {
    name: newName,
  });
  return data;
}

export async function deleteDepartment(name) {
  const { data } = await client.delete(`/departments/${encodeURIComponent(name)}`);
  return data;
}

// --- Positions lookup ---

export async function getPositions() {
  const { data } = await client.get('/positions');
  return data;
}

export async function renamePosition(name, newName) {
  const { data } = await client.patch(`/positions/${encodeURIComponent(name)}`, {
    name: newName,
  });
  return data;
}

export async function deletePosition(name) {
  const { data } = await client.delete(`/positions/${encodeURIComponent(name)}`);
  return data;
}
