/**
 * Storage / Files API functions.
 */
import client from './client';

/**
 * Upload a single file to /files/upload.
 * @param {File} file - Raw File object to upload
 * @param {object} [options] - Optional config (onUploadProgress, etc.)
 * @returns {Promise<{key: string, mime_type: string, size_bytes: number, ext: string}>}
 */
export async function uploadFile(file, options = {}) {
  const formData = new FormData();
  formData.append('file', file);

  const { data } = await client.post('/files/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: options.onUploadProgress,
  });
  return data;
}
