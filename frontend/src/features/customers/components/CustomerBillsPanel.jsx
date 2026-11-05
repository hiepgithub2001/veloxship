/**
 * CustomerBillsPanel — the customer's bill history.
 *
 * Uses the same column set as the bill list (`buildBillColumns`), so the table
 * reads identically to "Danh sách phiếu gửi". The filter row is deliberately
 * smaller than the list page's: creation-date range + which side of the bill
 * the customer is on (sender / receiver).
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, DatePicker, Segmented, Table } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';

import { getCustomerBills } from '../../../api/customers';
import { usePermission } from '../../../auth/permissions';
import { t } from '../../../i18n/vi';
import { BillPdfPreview } from '../../bills/components/BillPdfPreview';
import { buildBillColumns } from '../../bills/components/billColumns';

const { RangePicker } = DatePicker;

/** RangePicker day boundary → ISO timestamp the backend filters on. */
function toIso(value, edge) {
  if (!value) return undefined;
  return (edge === 'start' ? value.startOf('day') : value.endOf('day')).toISOString();
}

export function CustomerBillsPanel({ customerId }) {
  const navigate = useNavigate();
  const { can } = usePermission();
  const canViewBills = can('bill:view');

  const [role, setRole] = useState('all');
  const [dateRange, setDateRange] = useState(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });
  const [printBillId, setPrintBillId] = useState(null);

  const createdFrom = toIso(dateRange?.[0], 'start');
  const createdTo = toIso(dateRange?.[1], 'end');

  const { data, isLoading } = useQuery({
    queryKey: ['customer-bills', customerId, role, createdFrom, createdTo, pagination],
    queryFn: () =>
      getCustomerBills(customerId, {
        page: pagination.current,
        pageSize: pagination.pageSize,
        role,
        createdFrom,
        createdTo,
      }),
    enabled: Boolean(customerId),
    keepPreviousData: true,
  });

  const resetToFirstPage = () => {
    setPagination((current) => ({ ...current, current: 1 }));
  };

  const resetFilters = () => {
    setRole('all');
    setDateRange(null);
    resetToFirstPage();
  };

  const hasFilters = role !== 'all' || Boolean(dateRange);

  const columns = buildBillColumns({
    offset: (pagination.current - 1) * pagination.pageSize,
    onView: canViewBills ? (id) => navigate(`/phieu-gui/${id}`) : undefined,
    onPrint: canViewBills ? setPrintBillId : undefined,
  });

  return (
    <div>
      <div className="customer-bills-toolbar">
        <RangePicker
          className="customer-bills-date-range"
          value={dateRange}
          onChange={(dates) => {
            setDateRange(dates);
            resetToFirstPage();
          }}
          placeholder={t('bills.dateRangePlaceholder')}
          format="DD/MM/YYYY"
          allowClear
        />
        <Segmented
          value={role}
          onChange={(value) => {
            setRole(value);
            resetToFirstPage();
          }}
          options={[
            { value: 'all', label: t('customers.roleAll') },
            { value: 'sender', label: t('customers.roleSender') },
            { value: 'receiver', label: t('customers.roleReceiver') },
          ]}
        />
        {hasFilters && (
          <Button
            type="link"
            className="customer-bills-reset"
            icon={<ReloadOutlined />}
            onClick={resetFilters}
          >
            {t('bills.resetFilters')}
          </Button>
        )}
      </div>

      <Table
        columns={columns}
        dataSource={data?.items || []}
        rowKey="id"
        loading={isLoading}
        scroll={{ x: 'max-content' }}
        locale={{ emptyText: t('customers.billsEmpty') }}
        onRow={
          canViewBills
            ? (record) => ({
                onClick: () => navigate(`/phieu-gui/${record.id}`),
                style: { cursor: 'pointer' },
              })
            : undefined
        }
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

      <BillPdfPreview
        billId={printBillId}
        open={printBillId != null}
        onClose={() => setPrintBillId(null)}
      />
    </div>
  );
}

export default CustomerBillsPanel;
