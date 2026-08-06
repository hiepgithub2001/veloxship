/**
 * Locations API — provinces and wards.
 */
import client from './client';

export async function getProvinces() {
  const { data } = await client.get('/locations/provinces');
  return data;
}

export async function getWardsByProvince(provinceCode) {
  const { data } = await client.get(`/locations/provinces/${provinceCode}/wards`);
  return data;
}
