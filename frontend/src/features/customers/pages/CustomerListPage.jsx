import { useState } from 'react';
import { Input, Select, Space, Typography } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { getCustomers } from '../../../api/customers';
import { t } from '../../../i18n/vi';
import CustomerDetailDrawer from '../components/CustomerDetailDrawer';
import CustomerTable from '../components/CustomerTable';

const { Title, Text } = Typography;

export function CustomerListPage() {
  const [search, setSearch] = useState('');
  const [isActive, setIsActive] = useState(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  const { data, isLoading } = useQuery({
    queryKey: ['customers', { search, isActive, ...pagination }],
    queryFn: () =>
      getCustomers({
        page: pagination.current,
        pageSize: pagination.pageSize,
        search: search || undefined,
        isActive,
      }),
  });

  const resetToFirstPage = (updater) => {
    updater();
    setPagination((current) => ({ ...current, current: 1 }));
  };

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <Title level={3} style={{ marginBottom: 4 }}>
          {t('customers.title')}
        </Title>
        <Text type="secondary">{t('customers.createdFromBillsHint')}</Text>
      </div>

      <Space wrap style={{ width: '100%', marginBottom: 16 }}>
        <Input.Search
          allowClear
          enterButton={<SearchOutlined />}
          placeholder={t('customers.searchPlaceholder')}
          style={{ width: 340 }}
          onSearch={(value) => resetToFirstPage(() => setSearch(value.trim()))}
        />
        <Select
          allowClear
          placeholder={t('customers.statusFilter')}
          style={{ width: 180 }}
          value={isActive}
          options={[
            { value: true, label: t('customers.active') },
            { value: false, label: t('customers.inactive') },
          ]}
          onChange={(value) => resetToFirstPage(() => setIsActive(value ?? null))}
        />
      </Space>

      <CustomerTable
        data={data}
        loading={isLoading}
        pagination={pagination}
        onPaginationChange={(next) =>
          setPagination({ current: next.current, pageSize: next.pageSize })
        }
        onView={setSelectedCustomer}
      />

      <CustomerDetailDrawer
        customer={selectedCustomer}
        open={selectedCustomer !== null}
        onClose={() => setSelectedCustomer(null)}
      />
    </div>
  );
}

export default CustomerListPage;
