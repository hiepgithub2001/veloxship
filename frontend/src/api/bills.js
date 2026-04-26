/**
 * Bills API functions.
 */
import client from './client';

export async function createBill(payload) {
  const { data } = await client.post('/bills', payload);
  return data;
}

export async function getBill(id) {
  const { data } = await client.get(`/bills/${id}`);
  return data;
}

export async function downloadBillPdf(id) {
  const response = await client.get(`/bills/${id}/print?as=pdf`, {
    responseType: 'blob',
  });
  // Trigger browser download
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `phieu-gui-${id}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export async function getBillPrintHtml(id) {
  const { data } = await client.get(`/bills/${id}/print?as=html`);
  return data;
}

export async function listBills(params = {}) {
  const { data } = await client.get('/bills', { params });
  return data;
}

export async function getBillByTracking(trackingNumber) {
  const { data } = await client.get(`/bills/by-tracking/${trackingNumber}`);
  return data;
}

export async function updateStatus(id, payload) {
  const { data } = await client.post(`/bills/${id}/status`, payload);
  return data;
}

export async function getBillEvents(id) {
  const { data } = await client.get(`/bills/${id}/events`);
  return data;
}
