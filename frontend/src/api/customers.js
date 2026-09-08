/**
 * Customers API — read-only directory. Customers are created from bills.
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

export async function getCustomerByPhone(phone) {
  if (!phone) return null;
  const page = await getCustomers({ search: phone, isActive: true, pageSize: 20 });
  return page.items?.find((customer) => customer.phone === phone) || null;
}
