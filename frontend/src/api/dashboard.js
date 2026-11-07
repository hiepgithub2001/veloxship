/**
 * Dashboard API functions.
 */
import client from './client';

export async function getDashboardSummary({ date_from, date_to } = {}) {
  const params = {};
  if (date_from) params.date_from = date_from;
  if (date_to) params.date_to = date_to;
  const { data } = await client.get('/dashboard/summary', { params });
  return data;
}
