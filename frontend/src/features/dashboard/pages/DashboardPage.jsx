import { ReloadOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Col, DatePicker, Row, Space, Typography } from 'antd';
import dayjs from 'dayjs';
import { useSearchParams } from 'react-router-dom';

import { getDashboardSummary } from '../../../api/dashboard';
import { formatViDateTime } from '../../../lib/format';
import { t } from '../../../i18n/vi';
import { DashboardChartCard } from '../components/DashboardChartCard';
import { DashboardKpiCards } from '../components/DashboardKpiCards';
import { BillsTrendChart } from '../components/BillsTrendChart';
import { RevenueTrendChart } from '../components/RevenueTrendChart';
import { StatusPieChart } from '../components/StatusPieChart';
import { TopDestinationsPanel } from '../components/TopDestinationsPanel';

const { RangePicker } = DatePicker;
const DEFAULT_RANGE_DAYS = 30;

/** Resolve the date filter from the URL, defaulting to the last 30 VN days. */
function resolveRange(searchParams) {
  const fromDay = dayjs(searchParams.get('from'));
  const toDay = dayjs(searchParams.get('to'));
  if (fromDay.isValid() && toDay.isValid() && !fromDay.isAfter(toDay)) {
    return { from: fromDay.format('YYYY-MM-DD'), to: toDay.format('YYYY-MM-DD') };
  }
  const today = dayjs();
  return {
    from: today.subtract(DEFAULT_RANGE_DAYS - 1, 'day').format('YYYY-MM-DD'),
    to: today.format('YYYY-MM-DD'),
  };
}

export function DashboardPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const range = resolveRange(searchParams);

  const now = dayjs();
  const rangePresets = [
    { label: t('dashboard.today'), value: [now, now] },
    { label: t('dashboard.preset7'), value: [now.subtract(6, 'day'), now] },
    { label: t('dashboard.preset30'), value: [now.subtract(29, 'day'), now] },
    { label: t('dashboard.preset90'), value: [now.subtract(89, 'day'), now] },
  ];

  const { data, isLoading, isFetching, isError, refetch } = useQuery({
    queryKey: ['dashboard', 'summary', range.from, range.to],
    queryFn: () => getDashboardSummary({ date_from: range.from, date_to: range.to }),
    refetchInterval: 60_000,
  });

  const daily = data?.daily ?? [];
  const statusCounts = data?.status_counts ?? [];
  const destinations = data?.destinations ?? [];

  const dailyEmpty = daily.every((d) => d.bills === 0 && Number(d.revenue) === 0);
  const statusEmpty = statusCounts.every((s) => s.count === 0);

  const handleRangeChange = (dates) => {
    if (!dates || dates.length !== 2) {
      // Cleared → fall back to the default 30-day window.
      setSearchParams({}, { replace: true });
      return;
    }
    setSearchParams(
      {
        from: dates[0].format('YYYY-MM-DD'),
        to: dates[1].format('YYYY-MM-DD'),
      },
      { replace: true },
    );
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <Typography.Title level={3} style={{ marginBottom: 4 }}>
            {t('dashboard.title')}
          </Typography.Title>
          <Typography.Text type="secondary" className="dashboard-subtitle">
            {t('dashboard.subtitle')}
          </Typography.Text>
        </div>
        <Space wrap>
          <RangePicker
            value={[dayjs(range.from), dayjs(range.to)]}
            onChange={handleRangeChange}
            presets={rangePresets}
            placeholder={[t('dashboard.dateFrom'), t('dashboard.dateTo')]}
            style={{ width: 260 }}
          />
          <Button
            icon={<ReloadOutlined />}
            onClick={() => refetch()}
            loading={isFetching && !isLoading}
            aria-label={t('dashboard.refresh')}
          />
        </Space>
      </div>

      {isError ? (
        <Alert
          type="error"
          showIcon
          message={t('dashboard.loadError')}
          action={
            <Button size="small" onClick={() => refetch()}>
              {t('dashboard.retry')}
            </Button>
          }
        />
      ) : (
        <>
          <DashboardKpiCards kpis={data?.kpis} loading={isLoading} />

          <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
            <Col xs={24} lg={16}>
              <DashboardChartCard
                title={t('dashboard.chartBills')}
                loading={isLoading}
                empty={dailyEmpty}
              >
                <BillsTrendChart daily={daily} />
              </DashboardChartCard>
            </Col>
            <Col xs={24} lg={8}>
              <DashboardChartCard
                title={t('dashboard.chartStatus')}
                loading={isLoading}
                empty={statusEmpty}
              >
                <StatusPieChart statusCounts={statusCounts} />
              </DashboardChartCard>
            </Col>
          </Row>

          <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
            <Col xs={24} lg={24}>
              <DashboardChartCard
                title={t('dashboard.chartRevenue')}
                loading={isLoading}
                empty={dailyEmpty}
              >
                <RevenueTrendChart daily={daily} />
              </DashboardChartCard>
            </Col>
          </Row>

          <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
            <Col xs={24} lg={24}>
              <TopDestinationsPanel destinations={destinations} />
            </Col>
          </Row>

          {data?.generated_at && (
            <Typography.Text type="secondary" className="dashboard-updated">
              {t('dashboard.updatedAt')} {formatViDateTime(data.generated_at)}
            </Typography.Text>
          )}
        </>
      )}
    </div>
  );
}
