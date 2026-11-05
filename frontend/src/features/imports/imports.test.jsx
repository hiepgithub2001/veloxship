/**
 * Tests for the Excel import wizard components.
 *
 * These pin the rendering contract (province remapping, row status tags, result
 * counters) and the wizard's upload → preview → result state machine, with the
 * API module mocked out.
 */
import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { commitImport, validateImport } from '../../api/imports';
import { ImportPreviewTable } from './components/ImportPreviewTable';
import { ImportResultPanel } from './components/ImportResultPanel';
import { ImportWizard } from './components/ImportWizard';

vi.mock('../../api/imports', () => ({
  validateImport: vi.fn(),
  commitImport: vi.fn(),
  downloadImportResult: vi.fn(),
  importErrorMessage: (error, fallback) => fallback,
}));

// jsdom does not implement matchMedia, which antd's responsive observer needs.
if (!window.matchMedia) {
  window.matchMedia = (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  });
}

const previewBatch = {
  id: 12,
  status: 'validated',
  entity_type: 'bill',
  source_layout: 'legacy_logex',
  file_name: '5.11 Mr Hai Logex.xlsx',
  created_at: '2026-11-05T10:00:00Z',
  committed_at: null,
  summary: { total_rows: 2, ok_rows: 1, warning_rows: 1, error_rows: 0, imported_rows: 0 },
  preview: [
    {
      id: 1,
      row_number: 3,
      status: 'ok',
      warnings: [],
      error_code: null,
      error_message: null,
      raw_data: {},
      normalized_data: {
        tracking_number: 'HNLG5',
        destination_raw: 'Hà Nội',
        province_name: 'Hà Nội',
        sender_name: 'Mr Hải',
        sender_phone: '0392492229',
        receiver_name: 'HẰNG HÒA',
        contact_phone: '0949988999',
        packages: 3,
        weight_kg: '43.500',
      },
    },
    {
      id: 2,
      row_number: 21,
      status: 'warning',
      warnings: ["'Hải Dương' → quy đổi 'Hải Phòng'"],
      error_code: null,
      error_message: null,
      raw_data: {},
      normalized_data: {
        tracking_number: 'HNLG21',
        destination_raw: 'Hải Dương',
        province_name: 'Hải Phòng',
        receiver_name: 'ĐẠI LÝ ABC',
        contact_phone: '0901234567',
        packages: 1,
        weight_kg: '12.000',
      },
    },
  ],
};

const committedBatch = {
  ...previewBatch,
  status: 'completed',
  summary: { total_rows: 2, ok_rows: 1, warning_rows: 1, error_rows: 0, imported_rows: 2 },
};

const renderWithProviders = (ui) =>
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );

describe('ImportPreviewTable', () => {
  it('renders the province mapping and row statuses', () => {
    const { container } = renderWithProviders(<ImportPreviewTable batch={previewBatch} />);

    expect(container.textContent).toContain('HNLG5');
    expect(container.textContent).toContain('Hải Dương');
    expect(container.textContent).toContain('Hải Phòng');
    // Same province on both sides → rendered only once.
    expect(container.textContent).toContain('Hà Nội');
    expect(container.textContent).toContain('Hợp lệ');
    expect(container.textContent).toContain('Cảnh báo');
    expect(container.textContent).toContain('43,50 kg');
    // Sender column: the row that carries one shows name + phone, the row
    // without one falls back to the "Mặc định" hint.
    expect(container.textContent).toContain('Mr Hải');
    expect(container.textContent).toContain('0392492229');
    expect(container.textContent).toContain('Mặc định');
  });
});

describe('ImportResultPanel', () => {
  it('shows the created bill count and the result actions', () => {
    const { container } = renderWithProviders(
      <ImportResultPanel batch={committedBatch} onClose={() => {}} />
    );

    expect(container.textContent).toContain('Đã nhập thành công 2 phiếu gửi.');
    expect(container.textContent).toContain('Tải file kết quả');
    expect(container.textContent).toContain('Xem danh sách phiếu');
  });
});

describe('ImportWizard', () => {
  it('renders the three steps with the upload hint', () => {
    renderWithProviders(<ImportWizard open onClose={() => {}} />);

    // The Modal renders into a portal on document.body, outside the container.
    const text = document.body.textContent;
    expect(text).toContain('Chọn và tải file');
    expect(text).toContain('Xem trước và xác nhận');
    expect(text).toContain('Kết quả');
    expect(text).toContain('Chỉ nhận file .xlsx, dung lượng tối đa 5 MB.');
  });

  it('walks from upload to preview to result', async () => {
    validateImport.mockResolvedValue(previewBatch);
    commitImport.mockResolvedValue(committedBatch);
    const onCompleted = vi.fn();

    renderWithProviders(<ImportWizard open onClose={() => {}} onCompleted={onCompleted} />);

    const fileInput = document.querySelector('input[type="file"]');
    const file = new File(['data'], '5.11 Mr Hai Logex.xlsx');
    fireEvent.change(fileInput, { target: { files: [file] } });

    const validateButton = await screen.findByRole('button', { name: /Kiểm tra dữ liệu/ });
    await waitFor(() => expect(validateButton.disabled).toBe(false));
    fireEvent.click(validateButton);

    await waitFor(() => expect(validateImport).toHaveBeenCalledTimes(1));
    expect(validateImport.mock.calls[0][0]).toMatchObject({ name: '5.11 Mr Hai Logex.xlsx' });

    // Preview step: the validated batch is rendered.
    await screen.findByText('HNLG5');

    fireEvent.click(screen.getByRole('button', { name: /Xác nhận nhập/ }));

    await waitFor(() =>
      expect(commitImport).toHaveBeenCalledWith(12, { skipErrorRows: true })
    );
    await screen.findByText('Đã nhập thành công 2 phiếu gửi.');
    expect(onCompleted).toHaveBeenCalledWith(committedBatch);
  });

  it('forwards the optional sender to the API when the file has no sender column', async () => {
    validateImport.mockResolvedValue(previewBatch);
    validateImport.mockClear();

    renderWithProviders(<ImportWizard open onClose={() => {}} />);

    fireEvent.change(screen.getByPlaceholderText('VD: Mr Hải'), {
      target: { value: 'Mr Hải' },
    });
    fireEvent.change(screen.getByPlaceholderText('VD: 0392492229'), {
      target: { value: '0392492229' },
    });

    const fileInput = document.querySelector('input[type="file"]');
    fireEvent.change(fileInput, {
      target: { files: [new File(['data'], 'x.xlsx')] },
    });

    const validateButton = await screen.findByRole('button', { name: /Kiểm tra dữ liệu/ });
    await waitFor(() => expect(validateButton.disabled).toBe(false));
    fireEvent.click(validateButton);

    await waitFor(() => expect(validateImport).toHaveBeenCalledTimes(1));
    expect(validateImport.mock.calls[0][1]).toEqual({
      sender_name: 'Mr Hải',
      sender_phone: '0392492229',
    });
  });

  it('sends no options when the sender fields are left empty', async () => {
    validateImport.mockResolvedValue(previewBatch);
    validateImport.mockClear();

    renderWithProviders(<ImportWizard open onClose={() => {}} />);
    const fileInput = document.querySelector('input[type="file"]');
    fireEvent.change(fileInput, {
      target: { files: [new File(['data'], 'x.xlsx')] },
    });

    const validateButton = await screen.findByRole('button', { name: /Kiểm tra dữ liệu/ });
    await waitFor(() => expect(validateButton.disabled).toBe(false));
    fireEvent.click(validateButton);

    await waitFor(() => expect(validateImport).toHaveBeenCalledTimes(1));
    expect(validateImport.mock.calls[0][1]).toBeUndefined();
  });
});
