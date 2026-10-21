/**
 * Customers API — directory, manual create/edit, bill history, metrics.
 *
 * Customers are still auto-created when a bill is recorded; these calls cover
 * managing a profile directly and inspecting its activity.
 */
import client from './client';

export async function getCustomers({ page, pageSize, search, isActive } = {}) {
  const params = {};
  if (page != null) params.page = page;
  if (pageSize != null) params.page_size = pageSize;
  if (search) params.search = search;
  if (isActive != null) params.is_active = isActive;

  const { data } = await client.get('/customers', { params });
  return data;
}

export async function getCustomer(id) {
  const { data } = await client.get(`/customers/${id}`);
  return data;
}

export async function createCustomer(payload) {
  const { data } = await client.post('/customers', payload);
  return data;
}

export async function updateCustomer(id, payload) {
  const { data } = await client.patch(`/customers/${id}`, payload);
  return data;
}

export async function getCustomerBills(id, { page, pageSize, role } = {}) {
  const params = {};
  if (page != null) params.page = page;
  if (pageSize != null) params.page_size = pageSize;
  if (role) params.role = role;

  const { data } = await client.get(`/customers/${id}/bills`, { params });
  return data;
}

export async function getCustomerMetrics(id) {
  const { data } = await client.get(`/customers/${id}/metrics`);
  return data;
}
