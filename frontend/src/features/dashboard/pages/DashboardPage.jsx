import { ReloadOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Col, Row, Segmented, Space, Typography } from 'antd';
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

const ALLOWED_RANGES = [7, 30, 90];

function resolveDays(raw) {
  const value = Number(raw);
  return ALLOWED_RANGES.includes(value) ? value : 30;
}

export function DashboardPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const days = resolveDays(searchParams.get('days'));

  const { data, isLoading, isFetching, isError, refetch } = useQuery({
    queryKey: ['dashboard', 'summary', days],
    queryFn: () => getDashboardSummary({ days }),
    refetchInterval: 60_000,
  });

  const daily = data?.daily ?? [];
  const statusCounts = data?.status_counts ?? [];
  const destinations = data?.destinations ?? [];

  const dailyEmpty = daily.every((d) => d.bills === 0 && Number(d.revenue) === 0);
  const statusEmpty = statusCounts.every((s) => s.count === 0);

  const handleRangeChange = (value) => {
    setSearchParams({ days: String(value) }, { replace: true });
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
          <Segmented
            options={[
              { label: t('dashboard.range7'), value: 7 },
              { label: t('dashboard.range30'), value: 30 },
              { label: t('dashboard.range90'), value: 90 },
            ]}
            value={days}
            onChange={handleRangeChange}
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
