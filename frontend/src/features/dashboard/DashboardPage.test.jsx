import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getDashboardSummary } from '../../api/dashboard';
import { DashboardPage } from './pages/DashboardPage';

vi.mock('../../api/dashboard', () => ({
  getDashboardSummary: vi.fn(),
}));

vi.mock('@ant-design/plots', () => ({
  Line: () => <div data-testid="line-chart" />,
  Column: () => <div data-testid="column-chart" />,
  Pie: () => <div data-testid="pie-chart" />,
  Bar: () => <div data-testid="bar-chart" />,
}));

vi.mock('react-simple-maps', () => ({
  ComposableMap: ({ children }) => <div data-testid="rsm">{children}</div>,
  Geographies: ({ children }) => children({ geographies: [] }),
  Geography: () => null,
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

const summary = {
  generated_at: '2026-11-06T08:05:00Z',
  range: { date_from: '2026-10-08', date_to: '2026-11-06' },
  kpis: {
    total_bills: 128,
    bills_today: 6,
    in_progress_bills: 34,
    delivered_bills: 80,
    cancelled_bills: 5,
    returned_bills: 9,
    delivery_rate: 62.5,
    revenue_total: '125000000.00',
    revenue_today: '4500000.00',
    cod_total: '32000000.00',
  },
  daily: [{ date: '2026-11-06', bills: 6, revenue: '4500000.00' }],
  status_counts: [{ status: 'delivered', count: 80 }],
  destinations: [{ province_code: '1', province_name: 'Hà Nội', count: 42 }],
};

function renderPage(initialEntry = '/') {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <DashboardPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders KPI cards and all chart components', async () => {
    getDashboardSummary.mockResolvedValue(summary);

    renderPage();

    expect(await screen.findByText('Tổng vận đơn')).toBeTruthy();
    expect(screen.getByText('Đang xử lý')).toBeTruthy();
    expect(screen.getByText('Doanh thu')).toBeTruthy();
    expect(screen.getByText('COD theo phiếu')).toBeTruthy();
    expect(await screen.findByTestId('line-chart')).toBeTruthy();
    expect(screen.getByTestId('column-chart')).toBeTruthy();
    expect(screen.getByTestId('pie-chart')).toBeTruthy();
    expect(screen.getByTestId('bar-chart')).toBeTruthy();

    await waitFor(() => expect(getDashboardSummary).toHaveBeenCalled());
    expect(getDashboardSummary).toHaveBeenCalledWith({
      date_from: expect.any(String),
      date_to: expect.any(String),
    });
  });

  it('shows an error alert with a retry action', async () => {
    getDashboardSummary.mockRejectedValue(new Error('boom'));

    renderPage();

    expect(await screen.findByText('Không tải được số liệu tổng quan.')).toBeTruthy();
    const retry = screen.getByText('Thử lại');
    fireEvent.click(retry);
    await waitFor(() => expect(getDashboardSummary).toHaveBeenCalledTimes(2));
  });

  it('uses the date range from the URL', async () => {
    getDashboardSummary.mockResolvedValue(summary);

    renderPage('/?from=2026-11-01&to=2026-11-06');
    await screen.findByText('Tổng vận đơn');

    expect(getDashboardSummary).toHaveBeenCalledWith({
      date_from: '2026-11-01',
      date_to: '2026-11-06',
    });
  });

  it('shows the empty state when there is no data', async () => {
    getDashboardSummary.mockResolvedValue({
      ...summary,
      kpis: { ...summary.kpis, total_bills: 0 },
      daily: [],
      status_counts: [],
      destinations: [],
    });

    renderPage();

    expect(await screen.findAllByText('Chưa có dữ liệu trong khoảng thời gian này.')).toBeTruthy();
  });
});
