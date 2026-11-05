import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Col, Input, Row, Select, Typography } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { getCustomers } from '../../../api/customers';
import { Can } from '../../../auth/RequirePermission';
import { t } from '../../../i18n/vi';
import CustomerFormModal from '../components/CustomerFormModal';
import CustomerTable from '../components/CustomerTable';

const { Title, Text } = Typography;

export function CustomerListPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [isActive, setIsActive] = useState(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });
  const [createOpen, setCreateOpen] = useState(false);

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
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          gap: 16,
          flexWrap: 'wrap',
          marginBottom: 20,
        }}
      >
        <div>
          <Title level={3} style={{ marginBottom: 4 }}>
            {t('customers.title')}
          </Title>
          <Text type="secondary">{t('customers.createdFromBillsHint')}</Text>
        </div>

        <Can permission="customer:create">
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
            {t('customers.create')}
          </Button>
        </Can>
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
        onView={(customer) => navigate(`/khach-hang/${customer.id}`)}
      />

      <CustomerFormModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSuccess={(created) => {
          if (created?.id) navigate(`/khach-hang/${created.id}`);
        }}
      />
    </div>
  );
}

export default CustomerListPage;
