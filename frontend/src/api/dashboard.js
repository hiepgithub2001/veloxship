/**
 * Dashboard API functions.
 */
import client from './client';

export async function getDashboardSummary({ days } = {}) {
  const params = {};
  if (days != null) params.days = days;
  const { data } = await client.get('/dashboard/summary', { params });
  return data;
}
