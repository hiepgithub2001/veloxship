/**
 * Depots API functions.
 */
import client from './client';

export async function getDepots({ page, pageSize, search, isActive } = {}) {
  const params = {};
  if (page != null) params.page = page;
  if (pageSize != null) params.page_size = pageSize;
  if (search) params.search = search;
  if (isActive != null) params.is_active = isActive;

  const { data } = await client.get('/depots', { params });
  return data;
}

export async function createDepot(payload) {
  const { data } = await client.post('/depots', payload);
  return data;
}

export async function updateDepot(id, payload) {
  const { data } = await client.patch(`/depots/${id}`, payload);
  return data;
}
