/**
 * CustomerBillsTab — the customer's bill history.
 *
 * The backend can filter by the customer's side of the bill (sender/receiver),
 * which is the distinction operators care about: "phiếu tôi gửi" vs "phiếu gửi
 * đến tôi".
 */
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Segmented, Table, Tag } from 'antd';
import { useQuery } from '@tanstack/react-query';

import { getCustomerBills } from '../../../api/customers';
import { formatViDate, formatVND } from '../../../lib/format';
import { t } from '../../../i18n/vi';

const STATUS_COLORS = {
  created: 'default',
  picked_up: 'blue',
  in_transit: 'geekblue',
  delivered: 'green',
  returned: 'orange',
  cancelled: 'red',
};

export function CustomerBillsTab({ customerId }) {
  const [role, setRole] = useState('all');
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });

  const { data, isLoading } = useQuery({
    queryKey: ['customer-bills', customerId, role, pagination],
    queryFn: () =>
      getCustomerBills(customerId, {
        page: pagination.current,
        pageSize: pagination.pageSize,
        role,
      }),
    enabled: Boolean(customerId),
  });

  const columns = [
    {
      title: t('bills.trackingNumber'),
      dataIndex: 'tracking_number',
      key: 'tracking_number',
      width: 160,
      render: (value, record) => <Link to={`/phieu-gui/${record.id}`}>{value}</Link>,
    },
    {
      title: t('bills.sender'),
      key: 'sender',
      ellipsis: true,
      render: (_, record) => record.sender?.name || '—',
    },
    {
      title: t('bills.receiver'),
      key: 'receiver',
      ellipsis: true,
      render: (_, record) => record.receiver?.name || '—',
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      width: 150,
      render: (status) => (
        <Tag color={STATUS_COLORS[status] || 'default'}>{t(`status.${status}`)}</Tag>
      ),
    },
    {
      title: t('bills.feeTotal'),
      dataIndex: 'fee_total',
      key: 'fee_total',
      width: 140,
      align: 'right',
      render: (value) => formatVND(value),
    },
    {
      title: t('common.createdAt'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 130,
      render: (value) => formatViDate(value),
    },
  ];

  return (
    <div>
      <Segmented
        style={{ marginBottom: 16 }}
        value={role}
        onChange={(value) => {
          setRole(value);
          setPagination((current) => ({ ...current, current: 1 }));
        }}
        options={[
          { value: 'all', label: t('customers.roleAll') },
          { value: 'sender', label: t('customers.roleSender') },
          { value: 'receiver', label: t('customers.roleReceiver') },
        ]}
      />

      <Table
        columns={columns}
        dataSource={data?.items || []}
        rowKey="id"
        loading={isLoading}
        scroll={{ x: 900 }}
        locale={{ emptyText: t('customers.billsEmpty') }}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: data?.total || 0,
          showSizeChanger: true,
        }}
        onChange={(next) =>
          setPagination({ current: next.current, pageSize: next.pageSize })
        }
      />
    </div>
  );
}

export default CustomerBillsTab;
