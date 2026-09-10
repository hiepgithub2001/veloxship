import { Button, Table, Tag } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { t } from '../../../i18n/vi';

const typeLabels = {
  retail: 'Khách lẻ',
  shop: 'Shop',
  enterprise: 'Doanh nghiệp',
};

export function CustomerTable({ data, loading, pagination, onPaginationChange, onView }) {
  const columns = [
    {
      title: t('customers.displayName'),
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
      render: (name, customer) => (
        <Button
          type="link"
          style={{ padding: 0, fontWeight: 600 }}
          onClick={() => onView(customer)}
        >
          {name}
        </Button>
      ),
    },
    {
      title: t('customers.customerCode'),
      dataIndex: 'code',
      key: 'code',
      width: 130,
      render: (code) => code || '—',
    },
    {
      title: t('customers.phone'),
      dataIndex: 'phone',
      key: 'phone',
      width: 140,
      render: (phone) => phone || '—',
    },
    {
      title: t('customers.customerType'),
      dataIndex: 'customer_type',
      key: 'customer_type',
      width: 130,
      render: (type) => <Tag color="blue">{typeLabels[type] || type}</Tag>,
    },
    {
      title: t('customers.address'),
      key: 'address',
      ellipsis: true,
      render: (_, customer) => customer.metadata?.address_detail || '—',
    },
    {
      title: t('customers.isActive'),
      dataIndex: 'is_active',
      key: 'is_active',
      width: 145,
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'default'}>
          {isActive ? t('customers.active') : t('customers.inactive')}
        </Tag>
      ),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 100,
      render: (_, customer) => (
        <Button type="link" icon={<EyeOutlined />} onClick={() => onView(customer)}>
          Xem
        </Button>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data?.items || []}
      rowKey="id"
      loading={loading}
      scroll={{ x: 900 }}
      pagination={{
        current: pagination.current,
        pageSize: pagination.pageSize,
        total: data?.total || 0,
        showSizeChanger: true,
        showTotal: (total) => `Tổng ${total} khách hàng`,
      }}
      onChange={(nextPagination) => onPaginationChange(nextPagination)}
    />
  );
}

export default CustomerTable;
