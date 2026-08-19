/**
 * Customers API — lookup by phone and create.
 */
import client from './client';

export async function getCustomerByPhone(phone) {
  const { data } = await client.get('/customers', { params: { phone } });
  return Array.isArray(data) && data.length > 0 ? data[0] : null;
}

export async function createCustomer(payload) {
  const { data } = await client.post('/customers', payload);
  return data;
}
