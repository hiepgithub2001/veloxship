/**
 * Excel import (nhập phiếu gửi từ Excel) API functions.
 *
 * ⚠️ `POST /imports` is `multipart/form-data`. The request MUST override
 * `Content-Type` (see `validateImport`): the shared axios instance defaults to
 * `application/json`, and axios then **serialises the FormData to JSON**
 * (`axios/lib/defaults/index.js`: `hasJSONContentType ? JSON.stringify(formDataToJSON(data)) : data`).
 * The browser ends up sending `{"file": {}}` with no file part, and the API
 * answers 400 `VALIDATION_ERROR` ("Dữ liệu không hợp lệ"). This is the same
 * pattern as `uploadFile()` in `api/files.js`.
 */
import client from './client';

/** Spreadsheet MIME type used when saving the result workbook. */
const XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

/**
 * Upload an .xlsx file and run the server-side validation.
 *
 * Nothing is written to bills/customers at this point — the response is an
 * `ImportBatchRead` whose `preview` + `summary` drive the confirmation step.
 *
 * @param {File} file - the .xlsx file picked by the user
 * @param {object} [options] - import options (catalogue_description, default_packages, …)
 * @returns {Promise<object>} ImportBatchRead
 */
export async function validateImport(file, options) {
  const formData = new FormData();
  formData.append('file', file);
  if (options) {
    formData.append('options', JSON.stringify(options));
  }

  const { data } = await client.post('/imports', formData, {
    // Without this override axios turns the FormData into a JSON object.
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

/**
 * List past import batches (paginated).
 *
 * @param {object} [params]
 * @param {number} [params.page]
 * @param {number} [params.pageSize]
 * @returns {Promise<{items: object[], total: number, page: number, page_size: number}>}
 */
export async function listImports({ page, pageSize } = {}) {
  const params = {};
  if (page != null) params.page = page;
  if (pageSize != null) params.page_size = pageSize;

  const { data } = await client.get('/imports', { params });
  return data;
}

/**
 * Fetch one import batch (summary + up to 200 preview rows).
 *
 * @param {number} id - batch id
 * @returns {Promise<object>} ImportBatchRead
 */
export async function getImport(id) {
  const { data } = await client.get(`/imports/${id}`);
  return data;
}

/**
 * List the rows of an import batch, optionally filtered by row status.
 *
 * @param {number} id - batch id
 * @param {object} [params]
 * @param {'ok'|'warning'|'error'|'imported'|'skipped'} [params.status]
 * @param {number} [params.page]
 * @param {number} [params.pageSize]
 * @returns {Promise<{items: object[], total: number, page: number, page_size: number}>}
 */
export async function listImportRows(id, { status, page, pageSize } = {}) {
  const params = {};
  if (status) params.status = status;
  if (page != null) params.page = page;
  if (pageSize != null) params.page_size = pageSize;

  const { data } = await client.get(`/imports/${id}/rows`, { params });
  return data;
}

/**
 * Write a validated batch to bills/customers/comments.
 *
 * @param {number} id - batch id
 * @param {object} [options]
 * @param {boolean} [options.skipErrorRows] - drop error rows instead of failing the batch
 * @returns {Promise<object>} ImportBatchRead (committed batch)
 */
export async function commitImport(id, { skipErrorRows = true } = {}) {
  const { data } = await client.post(`/imports/${id}/commit`, {
    skip_error_rows: skipErrorRows,
  });
  return data;
}

async function fetchImportResult(id) {
  return client.get(`/imports/${id}/result`, {
    responseType: 'blob',
  });
}

function saveImportResult(response, id) {
  const url = window.URL.createObjectURL(new Blob([response.data], { type: XLSX_MIME }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `ket-qua-nhap-du-lieu-${id}.xlsx`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

/**
 * Download the result workbook: original rows plus status/error columns.
 *
 * @param {number} id - batch id
 */
export async function downloadImportResult(id) {
  const response = await fetchImportResult(id);
  saveImportResult(response, id);
}

/**
 * Build a user-facing message from an API error.
 *
 * The backend answers `400 VALIDATION_ERROR` with a generic Vietnamese message
 * plus `details.errors[]` naming the offending field; appending that field turns
 * an opaque "Dữ liệu không hợp lệ" into something actionable.
 *
 * @param {any} error - axios error
 * @param {string} fallback - message used when the response carries none
 * @returns {string}
 */
export function importErrorMessage(error, fallback) {
  const data = error?.response?.data;
  const base = data?.message || fallback;
  const first = data?.details?.errors?.[0];
  if (!first?.field) {
    return base;
  }
  const field = String(first.field).replace(/^body\s*→\s*/, '');
  return `${base} (${field}: ${first.message})`;
}
