import { useState } from 'react';
import { Col, Input, Row, Select, Typography } from 'antd';
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

      <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={14}>
          <Input.Search
            allowClear
            enterButton={<SearchOutlined />}
            placeholder={t('customers.searchPlaceholder')}
            style={{ width: '100%' }}
            onSearch={(value) => resetToFirstPage(() => setSearch(value.trim()))}
          />
        </Col>
        <Col xs={24} sm={10}>
          <Select
            allowClear
            placeholder={t('customers.statusFilter')}
            style={{ width: '100%' }}
            value={isActive}
            options={[
              { value: true, label: t('customers.active') },
              { value: false, label: t('customers.inactive') },
            ]}
            onChange={(value) => resetToFirstPage(() => setIsActive(value ?? null))}
          />
        </Col>
      </Row>

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
