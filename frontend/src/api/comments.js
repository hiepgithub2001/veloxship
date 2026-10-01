/**
 * Comments API functions.
 */
import client from './client';

export async function listComments({ entityType, entityId }) {
  const { data } = await client.get('/comments', {
    params: { entity_type: entityType, entity_id: entityId },
  });
  return data;
}

export async function createComment({ entityType, entityId, body, parent_id, parentId }) {
  const { data } = await client.post('/comments', {
    entity_type: entityType,
    entity_id: entityId,
    body,
    parent_id: parent_id ?? parentId,
  });
  return data;
}

export async function updateComment(id, payload) {
  const { data } = await client.patch(`/comments/${id}`, payload);
  return data;
}

export async function deleteComment(id) {
  await client.delete(`/comments/${id}`);
}
