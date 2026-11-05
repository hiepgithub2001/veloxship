/**
 * CustomerDetailPage — flat, single-page profile of one customer.
 *
 * Follows Ant Design's "Basic Detail" template: identity + actions on top, the
 * headline activity figures and the full profile spread out flat on the page,
 * and the bill history as the related list below. There are no tabs — operators
 * should be able to read the whole profile without hunting through sections.
 *
 * Read-only by default (matching the permissions page pattern): editing happens
 * in `CustomerFormModal`, opened from here or from the directory.
 */
import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  EditOutlined,
  EnvironmentOutlined,
  FileTextOutlined,
  PhoneOutlined,
} from '@ant-design/icons';
import {
  Avatar,
  Button,
  Card,
  Descriptions,
  Divider,
  Result,
  Space,
  Spin,
  Tag,
  Typography,
} from 'antd';
import { useQuery } from '@tanstack/react-query';

import { getCustomer, getCustomerMetrics } from '../../../api/customers';
import { Can } from '../../../auth/RequirePermission';
import BackButton from '../../../components/common/BackButton';
import { formatViDate, formatViDateTime } from '../../../lib/format';
import { t } from '../../../i18n/vi';
import CustomerBillsPanel from '../components/CustomerBillsPanel';
import CustomerFormModal from '../components/CustomerFormModal';
import CustomerMetricsCards from '../components/CustomerMetricsCards';

const { Title, Text } = Typography;

const TYPE_LABELS = {
  retail: t('customers.typeRetail'),
  shop: t('customers.typeShop'),
  enterprise: t('customers.typeEnterprise'),
};

const TYPE_COLORS = {
  retail: 'blue',
  shop: 'geekblue',
  enterprise: 'purple',
};

/** Initials shown in the avatar, e.g. "Nguyễn Văn An" → "VA". */
function getInitials(name) {
  const words = (name || '').trim().split(/\s+/).filter(Boolean);
  if (!words.length) return '?';
  return words
    .slice(-2)
    .map((word) => word[0])
    .join('')
    .toUpperCase();
}

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

  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['customer-metrics', id],
    queryFn: () => getCustomerMetrics(id),
    enabled: Boolean(id),
  });

  if (isLoading) {
    return <Spin size="large" className="customer-detail-loading" />;
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

  const typeLabel = TYPE_LABELS[customer.customer_type] || customer.customer_type;
  const area = [customer.ward_name, customer.province_name].filter(Boolean).join(', ');
  const addressLine = [customer.address_detail, customer.ward_name, customer.province_name]
    .filter(Boolean)
    .join(', ');

  return (
    <div className="customer-detail">
      <div className="customer-detail-actions">
        <BackButton fallback="/khach-hang" />
        <Can permission="customer:update">
          <Button
            className="customer-detail-edit"
            type="primary"
            icon={<EditOutlined />}
            onClick={() => setEditOpen(true)}
          >
            {t('common.edit')}
          </Button>
        </Can>
      </div>

      <Card className="customer-hero">
        <div className="customer-hero-identity">
          <Avatar size={64} className="customer-hero-avatar">
            {getInitials(customer.name)}
          </Avatar>
          <div className="customer-hero-identity-text">
            <Title level={3} className="customer-hero-name">
              {customer.name}
            </Title>
            <Space size={[8, 8]} wrap>
              {customer.code && (
                <Tag>{`${t('customers.customerCode')}: ${customer.code}`}</Tag>
              )}
              <Tag color={TYPE_COLORS[customer.customer_type]}>{typeLabel}</Tag>
              <Tag color={customer.is_active ? 'green' : 'default'}>
                {customer.is_active ? t('customers.active') : t('customers.inactive')}
              </Tag>
            </Space>
          </div>
        </div>

        <div className="customer-hero-contact">
          <span className="customer-hero-contact-item">
            <PhoneOutlined />
            {customer.phone || '—'}
          </span>
          <span className="customer-hero-contact-item">
            <EnvironmentOutlined />
            {addressLine || '—'}
          </span>
        </div>

        <Divider className="customer-hero-divider" />

        <Descriptions
          className="customer-flat-descriptions"
          column={{ xs: 1, sm: 2, lg: 3 }}
          colon={false}
          size="middle"
        >
          <Descriptions.Item label={t('customers.customerType')}>{typeLabel}</Descriptions.Item>
          <Descriptions.Item label={t('customers.area')}>{area || '—'}</Descriptions.Item>
          <Descriptions.Item label={t('customers.isActive')}>
            {customer.is_active ? t('customers.active') : t('customers.inactive')}
          </Descriptions.Item>
          <Descriptions.Item label={t('common.createdAt')}>
            {formatViDateTime(customer.created_at)}
          </Descriptions.Item>
          <Descriptions.Item label={t('common.updatedAt')}>
            {formatViDateTime(customer.updated_at)}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <CustomerMetricsCards metrics={metrics} loading={metricsLoading} />

      <Card
        className="customer-bills-card"
        title={
          <Space size={8}>
            <FileTextOutlined />
            <span>{t('customers.sectionBills')}</span>
          </Space>
        }
        extra={
          <Text type="secondary" className="customer-bills-summary">
            {`${t('customers.metricsLastBill')}: ${
              metrics?.last_bill_at ? formatViDate(metrics.last_bill_at) : '—'
            }`}
          </Text>
        }
      >
        <CustomerBillsPanel customerId={customer.id} />
      </Card>

      <CustomerFormModal
        open={editOpen}
        onClose={() => setEditOpen(false)}
        customer={customer}
      />
    </div>
  );
}

export default CustomerDetailPage;
