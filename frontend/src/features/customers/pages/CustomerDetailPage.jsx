/**
 * CustomerDetailPage — one customer's profile, bill history, and metrics.
 *
 * Read-only by default (matching the permissions page pattern): editing happens
 * in `CustomerFormModal`, opened from here or from the directory.
 */
import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeftOutlined, EditOutlined } from '@ant-design/icons';
import {
  Button,
  Descriptions,
  Result,
  Space,
  Spin,
  Tabs,
  Tag,
  Typography,
} from 'antd';
import { useQuery } from '@tanstack/react-query';

import { getCustomer } from '../../../api/customers';
import { Can } from '../../../auth/RequirePermission';
import { formatViDateTime } from '../../../lib/format';
import { t } from '../../../i18n/vi';
import CustomerBillsTab from '../components/CustomerBillsTab';
import CustomerFormModal from '../components/CustomerFormModal';
import CustomerMetricsTab from '../components/CustomerMetricsTab';

const { Title } = Typography;

const TYPE_LABELS = {
  retail: t('customers.typeRetail'),
  shop: t('customers.typeShop'),
  enterprise: t('customers.typeEnterprise'),
};

export function CustomerDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [editOpen, setEditOpen] = useState(false);

  const {
    data: customer,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['customer', id],
    queryFn: () => getCustomer(id),
    enabled: Boolean(id),
  });

  if (isLoading) {
    return <Spin />;
  }

  if (isError || !customer) {
    return (
      <Result
        status="404"
        title={t('customers.notFound')}
        extra={
          <Button type="primary" onClick={() => navigate('/khach-hang')}>
            {t('common.back')}
          </Button>
        }
      />
    );
  }

  const area = [customer.ward_name, customer.province_name].filter(Boolean).join(', ');

  return (
    <div>
      <Space style={{ marginBottom: 12 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/khach-hang')}>
          {t('common.back')}
        </Button>
      </Space>

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          gap: 16,
          flexWrap: 'wrap',
          marginBottom: 16,
        }}
      >
        <div>
          <Title level={3} style={{ marginBottom: 4 }}>
            {customer.name}
          </Title>
          <Space size={8} wrap>
            {customer.code && (
              <Tag>{`${t('customers.customerCode')}: ${customer.code}`}</Tag>
            )}
            <Tag color="blue">
              {TYPE_LABELS[customer.customer_type] || customer.customer_type}
            </Tag>
            <Tag color={customer.is_active ? 'green' : 'default'}>
              {customer.is_active ? t('customers.active') : t('customers.inactive')}
            </Tag>
          </Space>
        </div>

        <Can permission="customer:update">
          <Button type="primary" icon={<EditOutlined />} onClick={() => setEditOpen(true)}>
            {t('common.edit')}
          </Button>
        </Can>
      </div>

      <Tabs
        defaultActiveKey="info"
        items={[
          {
            key: 'info',
            label: t('customers.tabInfo'),
            children: (
              <Descriptions bordered size="small" column={{ xs: 1, sm: 1, md: 2 }}>
                <Descriptions.Item label={t('customers.phone')}>
                  {customer.phone || '—'}
                </Descriptions.Item>
                <Descriptions.Item label={t('customers.customerType')}>
                  {TYPE_LABELS[customer.customer_type] || customer.customer_type}
                </Descriptions.Item>
                <Descriptions.Item label={t('customers.address')} span={2}>
                  {customer.address_detail || '—'}
                </Descriptions.Item>
                <Descriptions.Item label={t('customers.area')} span={2}>
                  {area || '—'}
                </Descriptions.Item>
                <Descriptions.Item label={t('common.createdAt')}>
                  {formatViDateTime(customer.created_at)}
                </Descriptions.Item>
                <Descriptions.Item label={t('common.updatedAt')}>
                  {formatViDateTime(customer.updated_at)}
                </Descriptions.Item>
              </Descriptions>
            ),
          },
          {
            key: 'bills',
            label: t('customers.tabBills'),
            children: <CustomerBillsTab customerId={customer.id} />,
          },
          {
            key: 'metrics',
            label: t('customers.tabMetrics'),
            children: <CustomerMetricsTab customerId={customer.id} />,
          },
        ]}
      />

      <CustomerFormModal
        open={editOpen}
        onClose={() => setEditOpen(false)}
        customer={customer}
      />
    </div>
  );
}

export default CustomerDetailPage;
