/**
 * Bill list page — fetches and displays bills with status and date-range filters.
 * Selecting a bill navigates to the dedicated detail page (`/phieu-gui/:id`).
 */
import React, { useEffect, useState } from 'react';
import { Button, Card, Table, Typography, Space, Tag, message } from 'antd';
import { PlusOutlined, PrinterOutlined, EyeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { t } from '../../../i18n/vi';
import { listBills } from '../../../api/bills';
import { formatVND, formatViDateTime } from '../../../lib/format';
import { BillFilters } from '../components/BillFilters';
import { BillPdfPreview } from '../components/BillPdfPreview';

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

export function BillListPage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [dateRange, setDateRange] = useState(null); // [Dayjs, Dayjs] | null
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [printBillId, setPrintBillId] = useState(null);

  const createdFrom = dateRange?.[0] ? dateRange[0].startOf('day').toISOString() : undefined;
  const createdTo = dateRange?.[1] ? dateRange[1].endOf('day').toISOString() : undefined;

  const { data, isFetching, isError } = useQuery({
    queryKey: ['bills', { page, pageSize, status, createdFrom, createdTo }],
    queryFn: () =>
      listBills({
        page,
        pageSize,
        status: status || undefined,
        createdFrom,
        createdTo,
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

  const handleTableChange = (newPagination) => {
    setPage(newPagination.current);
    setPageSize(newPagination.pageSize);
  };

  const handleStatusChange = (value) => {
    setStatus(value ?? null);
    setPage(1);
  };

  const handleDateRangeChange = (dates) => {
    setDateRange(dates && dates[0] && dates[1] ? dates : null);
    setPage(1);
  };

  const openDetail = (id) => navigate(`/phieu-gui/${id}`);

  const handlePrint = (id) => setPrintBillId(id);

  const columns = [
    {
      title: 'Mã vận đơn',
      dataIndex: 'tracking_number',
      key: 'tracking_number',
      render: (text) => <Typography.Text strong>{text}</Typography.Text>,
    },
    {
      title: 'Người gửi',
      dataIndex: ['sender', 'name'],
      key: 'sender_name',
    },
    {
      title: 'Người nhận',
      dataIndex: ['receiver', 'name'],
      key: 'receiver_name',
    },
    {
      title: 'Tổng cước',
      dataIndex: ['fee', 'fee_total'],
      key: 'fee_total',
      render: (val) => formatVND(val),
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={statusColors[status] || 'default'}>{statusText[status] || status}</Tag>
      ),
    },
    {
      title: 'Ngày tạo',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => formatViDateTime(date),
    },
    {
      title: 'Thao tác',
      key: 'actions',
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
      <BillFilters
        status={status}
        dateRange={dateRange}
        onStatusChange={handleStatusChange}
        onDateRangeChange={handleDateRangeChange}
      />
      <Card>
        <Table {...tableProps} columns={columns} pagination={pagination} />
      </Card>
      <BillPdfPreview
        billId={printBillId}
        open={printBillId != null}
        onClose={() => setPrintBillId(null)}
      />
    </div>
  );
}

export default BillListPage;
