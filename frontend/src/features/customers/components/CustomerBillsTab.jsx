/**
 * CustomerBillsTab — paginated bill history with sender/receiver role filter.
 */
import { useState } from 'react';
import { Segmented, Table, Tag } from 'antd';
import { useQuery } from '@tanstack/react-query';

import { getCustomerBills } from '../../../api/customers';
import { formatVND, formatViDateTime } from '../../../lib/format';
import { t } from '../../../i18n/vi';

const statusColors = {
  created: 'blue',
  picked_up: 'cyan',
  in_transit: 'orange',
  delivered: 'green',
  returned: 'purple',
  cancelled: 'red',
};

export function CustomerBillsTab({ customerId }) {
  const [role, setRole] = useState('all');
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });

  const { data, isLoading } = useQuery({
    queryKey: ['customer-bills', customerId, { role, ...pagination }],
    queryFn: () =>
      getCustomerBills(customerId, {
        page: pagination.current,
        pageSize: pagination.pageSize,
        role,
      }),
    keepPreviousData: true,
  });

  const columns = [
    {
      title: t('bills.trackingNumber'),
      dataIndex: 'tracking_number',
      key: 'tracking_number',
      width: 160,
    },
    {
      title: t('bills.sender'),
      key: 'sender',
      ellipsis: true,
      render: (_, bill) => bill.sender?.name || '—',
    },
    {
      title: t('bills.receiver'),
      key: 'receiver',
      ellipsis: true,
      render: (_, bill) => bill.receiver?.name || '—',
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      width: 150,
      render: (status) => (
        <Tag color={statusColors[status] || 'default'}>{t(`status.${status}`)}</Tag>
      ),
    },
    {
      title: t('bills.feeTotal'),
      dataIndex: 'fee',
      key: 'fee_total',
      width: 150,
      align: 'right',
      render: (fee) => formatVND(fee?.fee_total),
    },
    {
      title: t('common.createdAt'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (value) => formatViDateTime(value),
    },
  ];

  return (
    <div>
      <Segmented
        style={{ marginBottom: 16 }}
        value={role}
        onChange={(value) => {
          setRole(value);
          setPagination((p) => ({ ...p, current: 1 }));
        }}
        options={[
          { value: 'all', label: t('customers.roleAll') },
          { value: 'sender', label: t('customers.roleSender') },
          { value: 'receiver', label: t('customers.roleReceiver') },
        ]}
      />

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data?.items || []}
        loading={isLoading}
        scroll={{ x: 900 }}
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
