/**
 * Users API functions.
 * Currently mocked — returns empty state until backend endpoint is implemented.
 */

/**
 * @param {object} [params]
 * @param {string} [params.search]
 * @param {string} [params.role]
 * @param {boolean} [params.isActive]
 * @returns {Promise<{items: Array, total: number, page: number, page_size: number}>}
 */
export async function getUsers(/* { search, role, isActive } = {} */) {
  // TODO: Replace with real API call once GET /api/v1/users is implemented
  // const params = {};
  // if (search) params.search = search;
  // if (role) params.role = role;
  // if (isActive != null) params.is_active = isActive;
  // const { data } = await client.get('/users', { params });
  // return data;

  return { items: [], total: 0, page: 1, page_size: 20 };
}
