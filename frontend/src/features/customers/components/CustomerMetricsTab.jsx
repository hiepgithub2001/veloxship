/**
 * CustomerMetricsTab — headline metrics for a customer's bill activity.
 */
import { Card, Col, Row, Statistic } from 'antd';
import { useQuery } from '@tanstack/react-query';

import { getCustomerMetrics } from '../../../api/customers';
import { formatVND } from '../../../lib/format';
import { t } from '../../../i18n/vi';

export function CustomerMetricsTab({ customerId }) {
  const { data, isLoading } = useQuery({
    queryKey: ['customer-metrics', customerId],
    queryFn: () => getCustomerMetrics(customerId),
  });

  return (
    <Row gutter={16}>
      <Col xs={24} sm={12}>
        <Card>
          <Statistic
            title={t('customers.metricsTotalBills')}
            value={data?.total_bills ?? 0}
            loading={isLoading}
          />
        </Card>
      </Col>
      <Col xs={24} sm={12}>
        <Card>
          <Statistic
            title={t('customers.metricsTotalRevenue')}
            value={formatVND(data?.total_revenue ?? 0)}
            loading={isLoading}
          />
        </Card>
      </Col>
    </Row>
  );
}

export default CustomerMetricsTab;
