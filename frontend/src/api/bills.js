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

export async function updateBill(id, payload) {
  const { data } = await client.patch(`/bills/${id}`, payload);
  return data;
}

async function fetchBillPdf(id) {
  return client.get(`/bills/${id}/print?as=pdf`, {
    responseType: 'blob',
  });
}

export async function getBillPrintHtml(id) {
  const { data } = await client.get(`/bills/${id}/print?as=html`);
  return data;
}

function saveBillPdf(response, id) {
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `phieu-gui-${id}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export async function downloadBillPdf(id) {
  const response = await fetchBillPdf(id);
  saveBillPdf(response, id);
}

export async function listBills({
  page,
  pageSize,
  search,
  status,
  createdFrom,
  createdTo,
  trackingNumber,
  senderName,
  receiverName,
} = {}) {
  const params = {};
  if (page != null) params.page = page;
  if (pageSize != null) params.page_size = pageSize;
  if (search) params.search = search;
  if (status) params.status = status;
  if (createdFrom) params.created_from = createdFrom;
  if (createdTo) params.created_to = createdTo;
  if (trackingNumber) params.tracking_number = trackingNumber;
  if (senderName) params.sender_name = senderName;
  if (receiverName) params.receiver_name = receiverName;

  const { data } = await client.get('/bills', { params });
  return data;
}

export async function exportBills(ids) {
  const response = await client.get('/bills/export', {
    params: { ids: ids.join(',') },
    responseType: 'blob',
  });
  return response;
}

export async function getBillsPrintHtml(ids) {
  const { data } = await client.get('/bills/print-batch', {
    params: { ids: ids.join(',') },
  });
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
