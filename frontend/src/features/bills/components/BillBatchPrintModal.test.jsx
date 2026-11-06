/**
 * Tests for the batch print modal — the "số liên" (copy count) option.
 *
 * Pins the contract with the print API: the first render records one print
 * event with the default copy count; changing the count only refreshes the
 * preview (record=false) so print_count is not inflated.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { getBillsPrintHtml } from '../../../api/bills';
import { BillBatchPrintModal } from './BillBatchPrintModal';

vi.mock('../../../api/bills', () => ({
  getBillsPrintHtml: vi.fn(),
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

const PRINT_HTML = '<html><body><main class="print-document">bill</main></body></html>';

async function renderModal() {
  render(<BillBatchPrintModal billIds={[1, 2]} open onClose={() => {}} />);
  await waitFor(() => expect(getBillsPrintHtml).toHaveBeenCalledTimes(1));
}

describe('BillBatchPrintModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getBillsPrintHtml.mockResolvedValue(PRINT_HTML);
  });

  it('prints three liên by default and records the print event', async () => {
    await renderModal();

    expect(getBillsPrintHtml).toHaveBeenCalledWith([1, 2], { copies: 3, record: true });
    expect(screen.getByText('2 phiếu × 3 liên = 6 trang A5')).toBeTruthy();
  });

  it('re-renders the preview with the chosen copy count without recording again', async () => {
    await renderModal();

    fireEvent.mouseDown(screen.getByRole('combobox', { name: 'Số liên in:' }));
    fireEvent.click(await screen.findByText('2 liên'));

    await waitFor(() =>
      expect(getBillsPrintHtml).toHaveBeenLastCalledWith([1, 2], { copies: 2, record: false }),
    );
    expect(screen.getByText('2 phiếu × 2 liên = 4 trang A5')).toBeTruthy();
  });
});
