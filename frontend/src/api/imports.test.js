/**
 * Tests for the Excel-import API client.
 *
 * Regression guard: `POST /imports` is multipart. The shared axios instance
 * defaults to `Content-Type: application/json`, and axios then serialises the
 * FormData to JSON (axios/lib/defaults/index.js), so the browser sends
 * `{"file": {}}` with **no file part** and the API answers 400
 * `VALIDATION_ERROR`. That is exactly what happened in the browser while every
 * unit test (which mocks this module) stayed green — so the header override is
 * pinned here through the real axios transform pipeline.
 */
import { afterEach, describe, expect, it } from 'vitest';

import client from './client';
import { importErrorMessage, validateImport } from './imports';

const originalAdapter = client.defaults.adapter;

afterEach(() => {
  client.defaults.adapter = originalAdapter;
});

/** Install an adapter that records the outgoing request and answers 201. */
function captureRequest() {
  const captured = {};
  client.defaults.adapter = async (config) => {
    captured.data = config.data;
    captured.headers = config.headers;
    captured.url = config.url;
    return {
      data: { id: 1, status: 'validated', summary: {}, preview: [] },
      status: 201,
      statusText: 'Created',
      headers: {},
      config,
    };
  };
  return captured;
}

function xlsxFile() {
  return new File(['fake-bytes'], '5.11 Mr Hải Logex.xlsx', {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  });
}

describe('validateImport', () => {
  it('sends the file as multipart FormData, never as JSON', async () => {
    const captured = captureRequest();
    await validateImport(xlsxFile());

    expect(captured.url).toBe('/imports');
    expect(captured.data).toBeInstanceOf(FormData);
    // The bug produced a JSON string here.
    expect(typeof captured.data).not.toBe('string');
    expect(captured.data.get('file')).toBeInstanceOf(File);
    expect(captured.data.get('file').name).toBe('5.11 Mr Hải Logex.xlsx');
  });

  it('overrides the JSON content type of the shared client', async () => {
    const captured = captureRequest();
    await validateImport(xlsxFile());
    expect(captured.headers.get('Content-Type')).toContain('multipart/form-data');
  });

  it('forwards options as a JSON string field when provided', async () => {
    const captured = captureRequest();
    await validateImport(xlsxFile(), { catalogue_description: 'Catalogue' });
    expect(JSON.parse(captured.data.get('options'))).toEqual({
      catalogue_description: 'Catalogue',
    });
  });
});

describe('importErrorMessage', () => {
  it('falls back when the response carries no message', () => {
    expect(importErrorMessage(new Error('boom'), 'Lỗi tải lên')).toBe('Lỗi tải lên');
  });

  it('appends the offending field from a validation error', () => {
    const error = {
      response: {
        data: {
          message: 'Dữ liệu không hợp lệ.',
          details: {
            errors: [{ field: 'body → file', message: 'Field required' }],
          },
        },
      },
    };
    expect(importErrorMessage(error, 'Lỗi')).toBe(
      'Dữ liệu không hợp lệ. (file: Field required)',
    );
  });

  it('keeps the plain message when there is no field detail', () => {
    const error = { response: { data: { message: 'Chỉ chấp nhận file .xlsx.' } } };
    expect(importErrorMessage(error, 'Lỗi')).toBe('Chỉ chấp nhận file .xlsx.');
  });
});
