import { Descriptions, Drawer, Tag } from 'antd';
import { t } from '../../../i18n/vi';

const typeLabels = {
  retail: 'Khách lẻ',
  shop: 'Shop',
  enterprise: 'Doanh nghiệp',
};

export function CustomerDetailDrawer({ customer, open, onClose }) {
  const metadata = customer?.metadata || {};
  const area = [metadata.ward_name, metadata.province_name].filter(Boolean).join(', ');

  return (
    <Drawer title={t('customers.detail')} open={open} onClose={onClose} width={480} destroyOnClose>
      {customer && (
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label={t('customers.displayName')}>{customer.name}</Descriptions.Item>
          <Descriptions.Item label={t('customers.customerCode')}>
            {customer.code || '—'}
          </Descriptions.Item>
          <Descriptions.Item label={t('customers.phone')}>
            {customer.phone || '—'}
          </Descriptions.Item>
          <Descriptions.Item label={t('customers.customerType')}>
            <Tag color="blue">{typeLabels[customer.customer_type] || customer.customer_type}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label={t('customers.address')}>
            {metadata.address_detail || '—'}
          </Descriptions.Item>
          <Descriptions.Item label={t('customers.area')}>{area || '—'}</Descriptions.Item>
          <Descriptions.Item label={t('customers.isActive')}>
            <Tag color={customer.is_active ? 'green' : 'default'}>
              {customer.is_active ? t('customers.active') : t('customers.inactive')}
            </Tag>
          </Descriptions.Item>
        </Descriptions>
      )}
    </Drawer>
  );
}

export default CustomerDetailDrawer;
