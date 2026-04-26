/**
 * Auth API functions.
 */
import client from './client';

export async function login(username, password) {
  const { data } = await client.post('/auth/login', { username, password });
  return data;
}

export async function refresh(refreshToken) {
  const { data } = await client.post('/auth/refresh', { refresh_token: refreshToken });
  return data;
}

export async function me() {
  const { data } = await client.get('/auth/me');
  return data;
}
