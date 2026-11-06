import { Card, Empty, Typography } from 'antd';

import { t } from '../../../i18n/vi';

/**
 * Shared chart card — title, optional extra, loading skeleton, and an empty
 * state. The chart itself renders inside `.dashboard-chart` (fixed height).
 */
export function DashboardChartCard({ title, extra, loading, empty, children, ariaLabel }) {
  return (
    <Card
      className="dashboard-chart-card"
      title={<Typography.Text strong>{title}</Typography.Text>}
      extra={extra}
      loading={loading}
    >
      {empty ? (
        <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={t('dashboard.empty')} />
      ) : (
        <div className="dashboard-chart" role="img" aria-label={ariaLabel || title}>
          {children}
        </div>
      )}
    </Card>
  );
}
