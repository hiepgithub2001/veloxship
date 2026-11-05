/**
 * CustomerMetricsCards — the headline activity figures for one customer.
 *
 * Laid out as a flat row above the profile (Ant Design "Basic Detail" template)
 * rather than hidden behind a tab, so counter staff read them at a glance.
 *
 * `total_revenue` arrives as a STRING because the backend serializes Decimal
 * that way to preserve precision, so it is parsed before formatting.
 */
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  FileTextOutlined,
  WalletOutlined,
} from '@ant-design/icons';
import { Card, Col, Row, Statistic } from 'antd';

import { formatVND } from '../../../lib/format';
import { t } from '../../../i18n/vi';

export function CustomerMetricsCards({ metrics, loading = false }) {
  const revenue = Number(metrics?.total_revenue ?? 0);

  return (
    <Row gutter={[16, 16]}>
      <Col xs={12} sm={12} lg={6}>
        <Card size="small" className="customer-metric-card customer-metric-total" loading={loading}>
          <Statistic
            title={t('customers.metricsTotalBills')}
            value={metrics?.total_bills ?? 0}
            prefix={<FileTextOutlined />}
          />
        </Card>
      </Col>
      <Col xs={12} sm={12} lg={6}>
        <Card
          size="small"
          className="customer-metric-card customer-metric-delivered"
          loading={loading}
        >
          <Statistic
            title={t('customers.metricsDelivered')}
            value={metrics?.delivered_bills ?? 0}
            valueStyle={{ color: 'var(--color-success)' }}
            prefix={<CheckCircleOutlined />}
          />
        </Card>
      </Col>
      <Col xs={12} sm={12} lg={6}>
        <Card
          size="small"
          className="customer-metric-card customer-metric-cancelled"
          loading={loading}
        >
          <Statistic
            title={t('customers.metricsCancelled')}
            value={metrics?.cancelled_bills ?? 0}
            valueStyle={{ color: 'var(--color-error)' }}
            prefix={<CloseCircleOutlined />}
          />
        </Card>
      </Col>
      <Col xs={12} sm={12} lg={6}>
        <Card size="small" className="customer-metric-card customer-metric-revenue" loading={loading}>
          <Statistic
            title={t('customers.metricsRevenue')}
            value={revenue}
            formatter={(value) => formatVND(value)}
            prefix={<WalletOutlined />}
          />
        </Card>
      </Col>
    </Row>
  );
}

export default CustomerMetricsCards;
