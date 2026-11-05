/**
 * Bill list page — fetches and displays bills with status and date-range filters.
 * Filters and pagination live in the URL so returning from the detail page
 * (via the shared BackButton) restores the exact previous view.
 */
import { useEffect, useState } from 'react';
import { Button, Card, Table, Typography, Space, Checkbox, Divider, Popover, message } from 'antd';
import {
  PlusOutlined,
  PrinterOutlined,
  FileExcelOutlined,
  ImportOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { t } from '../../../i18n/vi';
import { usePermission } from '../../../auth/permissions';
import { listBills, exportBills } from '../../../api/bills';
import { buildBillColumns, TOGGLEABLE_BILL_COLUMN_KEYS } from '../components/billColumns';
import { BillFilters } from '../components/BillFilters';
import { BillPdfPreview } from '../components/BillPdfPreview';
import { BillBatchPrintModal } from '../components/BillBatchPrintModal';
import { ImportWizard } from '../../imports/components/ImportWizard';

const { Title } = Typography;

const COLUMN_STORAGE_KEY = 'bill-list-visible-columns';

const loadVisibleColumns = () => {
  try {
    const raw = localStorage.getItem(COLUMN_STORAGE_KEY);
    if (!raw) return TOGGLEABLE_BILL_COLUMN_KEYS;
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return TOGGLEABLE_BILL_COLUMN_KEYS;
    return parsed.filter((key) => TOGGLEABLE_BILL_COLUMN_KEYS.includes(key));
  } catch {
    return TOGGLEABLE_BILL_COLUMN_KEYS;
  }
};

export function BillListPage() {
  const { can } = usePermission();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const [printBillId, setPrintBillId] = useState(null);
  const [batchPrintIds, setBatchPrintIds] = useState(null);
  const [importOpen, setImportOpen] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [visibleColumnKeys, setVisibleColumnKeys] = useState(loadVisibleColumns);

  const status = searchParams.get('status') || null;
  const page = Number(searchParams.get('page')) || 1;
  const pageSize = Number(searchParams.get('pageSize')) || 10;
  const from = searchParams.get('from');
  const to = searchParams.get('to');
  const tracking = searchParams.get('tracking') || '';
  const sender = searchParams.get('sender') || '';
  const receiver = searchParams.get('receiver') || '';
  const dateRange = from && to ? [dayjs(from), dayjs(to)] : null; // [Dayjs, Dayjs] | null

  const createdFrom = dateRange?.[0] ? dateRange[0].startOf('day').toISOString() : undefined;
  const createdTo = dateRange?.[1] ? dateRange[1].endOf('day').toISOString() : undefined;

  const { data, isFetching, isError } = useQuery({
    queryKey: [
      'bills',
      { page, pageSize, status, createdFrom, createdTo, tracking, sender, receiver },
    ],
    queryFn: () =>
      listBills({
        page,
        pageSize,
        status: status || undefined,
        createdFrom,
        createdTo,
        trackingNumber: tracking || undefined,
        senderName: sender || undefined,
        receiverName: receiver || undefined,
      }),
    keepPreviousData: true,
  });

  useEffect(() => {
    if (isError) {
      message.error(t('bills.fetchError'));
    }
  }, [isError]);

  const bills = data?.items ?? [];
  const pagination = { current: page, pageSize, total: data?.total ?? 0 };

  const updateParams = (patch) => {
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        Object.entries(patch).forEach(([key, value]) => {
          if (value == null || value === '') next.delete(key);
          else next.set(key, String(value));
        });
        return next;
      },
      { replace: true }
    );
  };

  const handleTableChange = (newPagination) => {
    updateParams({ page: newPagination.current, pageSize: newPagination.pageSize });
  };

  const handleStatusChange = (value) => {
    updateParams({ status: value ?? null, page: 1 });
  };

  const handleDateRangeChange = (dates) => {
    updateParams({
      from: dates?.[0] ? dates[0].format('YYYY-MM-DD') : null,
      to: dates?.[1] ? dates[1].format('YYYY-MM-DD') : null,
      page: 1,
    });
  };

  const openDetail = (id) => navigate(`/phieu-gui/${id}`);

  const handlePrint = (id) => setPrintBillId(id);

  const handleSearchFilters = ({ tracking: trackingValue, sender: senderValue, receiver: receiverValue }) => {
    updateParams({
      tracking: trackingValue || null,
      sender: senderValue || null,
      receiver: receiverValue || null,
      page: 1,
    });
  };

  const handleResetFilters = () => {
    updateParams({ tracking: null, sender: null, receiver: null, page: 1 });
  };

  const handleSelectChange = (keys) => setSelectedRowKeys(keys);

  const handleVisibleColumnsChange = (keys) => {
    setVisibleColumnKeys(keys);
    try {
      localStorage.setItem(COLUMN_STORAGE_KEY, JSON.stringify(keys));
    } catch {
      // Storage may be unavailable; the selection still works for this session.
    }
  };

  const handleExportExcel = async () => {
    if (selectedRowKeys.length === 0) return;
    try {
      const response = await exportBills(selectedRowKeys);
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'phieu-gui.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      message.error(t('bills.exportError'));
    }
  };

  const handlePrintSelected = () => {
    if (selectedRowKeys.length === 0) return;
    setBatchPrintIds(selectedRowKeys);
  };

  const columns = buildBillColumns({
    offset: (page - 1) * pageSize,
    onView: openDetail,
    onPrint: handlePrint,
  });

  // Only drop a column when it is toggleable and the user hid it.
  const visibleColumns = columns.filter(
    (col) => !TOGGLEABLE_BILL_COLUMN_KEYS.includes(col.key) || visibleColumnKeys.includes(col.key)
  );

  const toggleableColumns = columns.filter((col) => TOGGLEABLE_BILL_COLUMN_KEYS.includes(col.key));

  const columnChooser = (
    <Popover
      trigger="click"
      placement="bottomRight"
      content={
        <div className="bill-list-column-chooser">
          <Checkbox.Group
            value={visibleColumnKeys}
            onChange={handleVisibleColumnsChange}
            className="bill-list-column-choices"
          >
            {toggleableColumns.map((col) => (
              <Checkbox key={col.key} value={col.key}>
                {col.title}
              </Checkbox>
            ))}
          </Checkbox.Group>
          <Divider />
          <Space>
            <Button
              size="small"
              type="text"
              onClick={() => handleVisibleColumnsChange(TOGGLEABLE_BILL_COLUMN_KEYS)}
            >
              {t('bills.columnsSelectAll')}
            </Button>
            <Button size="small" type="text" onClick={() => handleVisibleColumnsChange([])}>
              {t('bills.columnsClear')}
            </Button>
          </Space>
        </div>
      }
    >
      <Button icon={<SettingOutlined />}>{t('bills.columns')}</Button>
    </Popover>
  );

  const tableProps = {
    dataSource: bills,
    rowKey: 'id',
    loading: isFetching,
    onChange: handleTableChange,
    scroll: { x: 'max-content' },
    rowSelection: {
      selectedRowKeys,
      onChange: handleSelectChange,
      fixed: true,
    },
    onRow: (record) => ({
      onClick: () => openDetail(record.id),
      style: { cursor: 'pointer' },
    }),
  };

  return (
    <div>
      <div className="bill-list-header">
        <Title level={3} style={{ margin: 0 }}>
          {t('bills.title')}
        </Title>
        {can('bill:create') && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/phieu-gui/tao-moi')}
            id="create-bill-btn"
          >
            {t('bills.create')}
          </Button>
        )}
      </div>
      <Card
      >
        <BillFilters
          status={status}
          dateRange={dateRange}
          tracking={tracking}
          sender={sender}
          receiver={receiver}
          onStatusChange={handleStatusChange}
          onDateRangeChange={handleDateRangeChange}
          onSearch={handleSearchFilters}
          onReset={handleResetFilters}
        />
        <div className="bill-list-toolbar">
          <Space size="middle" wrap>
            {selectedRowKeys.length > 0 && (
              <>
                <Typography.Text>
                  {t('bills.selectedCount').replace('{count}', selectedRowKeys.length)}
                </Typography.Text>
                <Button icon={<FileExcelOutlined />} onClick={handleExportExcel}>
                  {t('bills.exportExcel')}
                </Button>
                <Button icon={<PrinterOutlined />} onClick={handlePrintSelected}>
                  {t('bills.print')}
                </Button>
              </>
            )}
            {can('bill:import') && (
              <Button
                id="import-bill-btn"
                icon={<ImportOutlined />}
                onClick={() => setImportOpen(true)}
              >
                {t('imports.action')}
              </Button>
            )}
          </Space>
          {columnChooser}
        </div>
        <Table {...tableProps} columns={visibleColumns} pagination={pagination} />
      </Card>
      <BillPdfPreview
        billId={printBillId}
        open={printBillId != null}
        onClose={() => setPrintBillId(null)}
      />
      <BillBatchPrintModal
        billIds={batchPrintIds}
        open={batchPrintIds != null && batchPrintIds.length > 0}
        onClose={() => setBatchPrintIds(null)}
      />
      <ImportWizard
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onCompleted={() => queryClient.invalidateQueries({ queryKey: ['bills'] })}
      />
    </div>
  );
}

export default BillListPage;
