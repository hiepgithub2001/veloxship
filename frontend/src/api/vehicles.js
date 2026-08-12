/**
 * Vehicles API functions.
 */
import client from './client';

export async function getVehicles({ page, pageSize, search, status, vehicleType, latestDepotId } = {}) {
  const params = {};
  if (page != null) params.page = page;
  if (pageSize != null) params.page_size = pageSize;
  if (search) params.search = search;
  if (status) params.status = status;
  if (vehicleType) params.vehicle_type = vehicleType;
  if (latestDepotId != null) params.latest_depot_id = latestDepotId;

  const { data } = await client.get('/vehicles', { params });
  return data;
}

export async function createVehicle(payload) {
  const { data } = await client.post('/vehicles', payload);
  return data;
}

export async function updateVehicle(id, payload) {
  const { data } = await client.patch(`/vehicles/${id}`, payload);
  return data;
}
