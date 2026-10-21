/**
 * CustomerMetricsTab — headline activity figures for one customer.
 *
 * `total_revenue` arrives as a STRING because the backend serializes Decimal
 * that way to preserve precision, so it is parsed before formatting.
 */
import { Card, Col, Descriptions, Row, Spin, Statistic } from 'antd';
import { useQuery } from '@tanstack/react-query';

import { getCustomerMetrics } from '../../../api/customers';
import { formatViDateTime, formatVND } from '../../../lib/format';
import { t } from '../../../i18n/vi';

export function CustomerMetricsTab({ customerId }) {
  const { data, isLoading } = useQuery({
    queryKey: ['customer-metrics', customerId],
    queryFn: () => getCustomerMetrics(customerId),
    enabled: Boolean(customerId),
  });

  if (isLoading) {
    return <Spin />;
  }

  const revenue = Number(data?.total_revenue ?? 0);

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title={t('customers.metricsTotalBills')} value={data?.total_bills ?? 0} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('customers.metricsDelivered')}
              value={data?.delivered_bills ?? 0}
              valueStyle={{ color: '#389e0d' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('customers.metricsCancelled')}
              value={data?.cancelled_bills ?? 0}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('customers.metricsRevenue')}
              value={revenue}
              formatter={(value) => formatVND(value)}
            />
          </Card>
        </Col>
      </Row>

      <Descriptions size="small" column={1} style={{ marginTop: 24 }}>
        <Descriptions.Item label={t('customers.metricsFirstBill')}>
          {data?.first_bill_at ? formatViDateTime(data.first_bill_at) : '—'}
        </Descriptions.Item>
        <Descriptions.Item label={t('customers.metricsLastBill')}>
          {data?.last_bill_at ? formatViDateTime(data.last_bill_at) : '—'}
        </Descriptions.Item>
      </Descriptions>
    </div>
  );
}

export default CustomerMetricsTab;
