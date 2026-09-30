/**
 * Bill list page — fetches and displays bills with status and date-range filters.
 * Filters and pagination live in the URL so returning from the detail page
 * (via the shared BackButton) restores the exact previous view.
 */
import { useEffect, useState } from 'react';
import { Button, Card, Table, Typography, Space, Tag, message } from 'antd';
import {
  PlusOutlined,
  PrinterOutlined,
  EyeOutlined,
  FileExcelOutlined,
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { t } from '../../../i18n/vi';
import { listBills, exportBills } from '../../../api/bills';
import { formatVND, formatViDate } from '../../../lib/format';
import { ImagePreviewGroup } from '../../../components/common/ImagePreviewGroup';
import { BillFilters } from '../components/BillFilters';
import { BillPdfPreview } from '../components/BillPdfPreview';
import { BillBatchPrintModal } from '../components/BillBatchPrintModal';

const { Title } = Typography;

const statusColors = {
  created: 'blue',
  picked_up: 'cyan',
  in_transit: 'orange',
  delivered: 'green',
  returned: 'purple',
  cancelled: 'red',
};

const statusText = {
  created: 'Đã tạo',
  picked_up: 'Đã lấy hàng',
  in_transit: 'Đang vận chuyển',
  delivered: 'Đã giao',
  returned: 'Hoàn trả',
  cancelled: 'Đã hủy',
};

const formatAddress = (party) =>
  [party?.address_detail, party?.ward_name, party?.province_name].filter(Boolean).join(', ');

export function BillListPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [printBillId, setPrintBillId] = useState(null);
  const [batchPrintIds, setBatchPrintIds] = useState(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);

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

  const columns = [
    {
      title: 'STT',
      key: 'index',
      width: 60,
      render: (_, __, index) => (page - 1) * pageSize + index + 1,
    },
    {
      title: 'Ngày',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 110,
      render: (date) => formatViDate(date),
    },
    {
      title: 'Mã vận đơn',
      dataIndex: 'tracking_number',
      key: 'tracking_number',
      width: 170,
      render: (text) => <Typography.Text strong>{text}</Typography.Text>,
    },
    {
      title: 'Tỉnh phát',
      dataIndex: ['sender', 'province_name'],
      key: 'sender_province',
      width: 130,
    },
    {
      title: 'COD',
      dataIndex: 'cod_amount',
      key: 'cod_amount',
      width: 120,
      render: (val) => (val ? formatVND(val) : '—'),
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      width: 150,
      render: (status) => (
        <Tag color={statusColors[status] || 'default'}>{statusText[status] || status}</Tag>
      ),
    },
    {
      title: 'Người nhận',
      dataIndex: ['receiver', 'name'],
      key: 'receiver_name',
      width: 160,
    },
    {
      title: 'Hình ảnh',
      key: 'images',
      width: 90,
      render: (_, record) => {
        const images = (record.contents || []).flatMap((c) => c.images || []).filter(Boolean);
        return <ImagePreviewGroup images={images} />;
      },
    },
    {
      title: 'SĐT người nhận',
      dataIndex: ['receiver', 'phone'],
      key: 'receiver_phone',
      width: 140,
    },
    {
      title: 'Địa chỉ người nhận',
      key: 'receiver_address',
      width: 220,
      ellipsis: true,
      render: (_, record) => formatAddress(record.receiver),
    },
    {
      title: 'Ghi chú',
      dataIndex: 'note',
      key: 'note',
      width: 160,
      ellipsis: true,
      render: (text) => text || '—',
    },
    {
      title: 'Thao tác',
      key: 'actions',
      fixed: 'right',
      width: 100,
      render: (_, record) => (
        <Space size="middle">
          <Button type="text" icon={<EyeOutlined />} onClick={() => openDetail(record.id)} />
          <Button
            type="text"
            icon={<PrinterOutlined />}
            onClick={(event) => {
              event.stopPropagation();
              handlePrint(record.id);
            }}
          />
        </Space>
      ),
    },
  ];

  const tableProps = {
    dataSource: bills,
    rowKey: 'id',
    loading: isFetching,
    onChange: handleTableChange,
    scroll: { x: 'max-content' },
    rowSelection: {
      selectedRowKeys,
      onChange: handleSelectChange,
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
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/phieu-gui/tao-moi')}
          id="create-bill-btn"
        >
          {t('bills.create')}
        </Button>
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
        {selectedRowKeys.length > 0 && (
          <Space size="middle" wrap style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <Typography.Text>
              {t('bills.selectedCount').replace('{count}', selectedRowKeys.length)}
            </Typography.Text>
            <Button icon={<FileExcelOutlined />} onClick={handleExportExcel}>
              {t('bills.exportExcel')}
            </Button>
            <Button icon={<PrinterOutlined />} onClick={handlePrintSelected}>
              {t('bills.print')}
            </Button>
          </Space>
        )}
        <Table {...tableProps} columns={columns} pagination={pagination} />
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
    </div>
  );
}

export default BillListPage;
