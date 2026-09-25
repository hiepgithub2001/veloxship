/**
 * CustomerDetailPage — customer profile with tabs for edit, bill history, metrics.
 */
import { useNavigate, useParams } from 'react-router-dom';
import { Button, Card, Space, Spin, Tabs, Tag, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';

import { getCustomer } from '../../../api/customers';
import { CustomerEditForm } from '../components/CustomerEditForm';
import { CustomerBillsTab } from '../components/CustomerBillsTab';
import { CustomerMetricsTab } from '../components/CustomerMetricsTab';
import { t } from '../../../i18n/vi';

const { Title, Text } = Typography;

const typeLabels = {
  retail: 'Khách lẻ',
  shop: 'Shop',
  enterprise: 'Doanh nghiệp',
};

export function CustomerDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const customerId = Number(id);

  const { data: customer, isLoading, error } = useQuery({
    queryKey: ['customer', customerId],
    queryFn: () => getCustomer(customerId),
  });

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 48 }}>
        <Spin />
      </div>
    );
  }

  if (error || !customer) {
    return (
      <Card>
        <Text type="secondary">{t('customers.notFound')}</Text>
      </Card>
    );
  }

  return (
    <div>
      <Space style={{ marginBottom: 16 }} align="center">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/khach-hang')} />
        <div>
          <Title level={4} style={{ margin: 0 }}>
            {customer.name}
          </Title>
          <Space size="small">
            <Text type="secondary">{customer.code || '—'}</Text>
            <Tag color="blue">{typeLabels[customer.customer_type] || customer.customer_type}</Tag>
          </Space>
        </div>
      </Space>

      <Tabs
        defaultActiveKey="profile"
        items={[
          {
            key: 'profile',
            label: t('customers.tabProfile'),
            children: <CustomerEditForm customer={customer} />,
          },
          {
            key: 'bills',
            label: t('customers.tabBills'),
            children: <CustomerBillsTab customerId={customerId} />,
          },
          {
            key: 'metrics',
            label: t('customers.tabMetrics'),
            children: <CustomerMetricsTab customerId={customerId} />,
          },
        ]}
      />
    </div>
  );
}

export default CustomerDetailPage;
