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

/**
 * Update the current user's own profile (full_name, phone, avatar).
 */
export async function updateMe(payload) {
  const { data } = await client.patch('/auth/me', payload);
  return data;
}

/**
 * Change the current user's own password.
 */
export async function changePassword(payload) {
  const { data } = await client.post('/auth/change-password', payload);
  return data;
}
