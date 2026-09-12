/**
 * Bill list page — fetches and displays bills with status and date-range filters.
 */
import React, { useEffect, useState } from 'react';
import { Button, Card, Drawer, Grid, Table, Typography, Space, Tag, message } from 'antd';
import { PlusOutlined, PrinterOutlined, EyeOutlined, CloseOutlined, ExpandOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { t } from '../../../i18n/vi';
import { listBills, downloadBillPdf } from '../../../api/bills';
import { formatVND, formatViDateTime } from '../../../lib/format';
import { BillDetailView } from '../components/BillDetailView';
import { BillFilters } from '../components/BillFilters';

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
  const [selectedId, setSelectedId] = useState(null);
  const [status, setStatus] = useState(null);
  const [dateRange, setDateRange] = useState(null); // [Dayjs, Dayjs] | null
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const screens = Grid.useBreakpoint();
  const isMobile = !screens.md;
  const isSelecting = selectedId != null;

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

  const handlePrint = async (id) => {
    try {
      await downloadBillPdf(id);
    } catch (error) {
      message.error('Lỗi khi tải phiếu in');
    }
  };

  const closeDetail = () => {
    setSelectedId(null);
  };

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
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => setSelectedId(record.id)}
          />
          <Button type="text" icon={<PrinterOutlined />} onClick={() => handlePrint(record.id)} />
        </Space>
      ),
    },
  ];

  // Narrow column set shown while the detail drawer is open (Outlook-style reading pane).
  const compactColumns = [
    {
      title: 'Mã vận đơn',
      dataIndex: 'tracking_number',
      key: 'tracking_number',
      render: (text) => <Typography.Text strong>{text}</Typography.Text>,
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
      title: 'Tổng cước',
      dataIndex: ['fee', 'fee_total'],
      key: 'fee_total',
      render: (val) => formatVND(val),
    },
  ];

  const tableProps = {
    dataSource: bills,
    rowKey: 'id',
    loading: isFetching,
    onChange: handleTableChange,
    onRow: (record) => ({
      onClick: () => setSelectedId(record.id),
      style: { cursor: 'pointer' },
    }),
    rowClassName: (record) => (record.id === selectedId ? 'bill-row-selected' : ''),
  };

  return (
    <div>
      {!isMobile && isSelecting ? (
        // Desktop: the whole list column (header + table) compacts beside the detail.
        <div className="bill-master-detail">
          <div className="bill-master-list">
            <div className="bill-list-header bill-list-header-compact">
              <Title level={4} style={{ margin: 0 }}>
                {t('bills.title')}
              </Title>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/phieu-gui/tao-moi')}
                id="create-bill-btn"
                block
              >
                {t('bills.create')}
              </Button>
            </div>
            <Card>
              <Table
                {...tableProps}
                columns={compactColumns}
                size="small"
                pagination={{ ...pagination, simple: true }}
              />
            </Card>
          </div>
          <div className="bill-master-detail-pane" key={selectedId}>
            <div className="bill-master-detail-pane-header">
              <Button type="text" icon={<CloseOutlined />} onClick={closeDetail}>
                {t('common.close')}
              </Button>
              <Button
                type="text"
                icon={<ExpandOutlined />}
                onClick={() => navigate(`/phieu-gui/${selectedId}`)}
              >
                {t('bills.viewFull')}
              </Button>
            </div>
            <BillDetailView id={selectedId} embedded key={selectedId} />
          </div>
        </div>
      ) : (
        <>
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
            <Table
              {...tableProps}
              columns={isSelecting ? compactColumns : columns}
              pagination={pagination}
            />
          </Card>
        </>
      )}
      {isMobile && (
        <Drawer
          className="bill-list-drawer"
          title={t('bills.detail')}
          placement="right"
          width="100%"
          mask={false}
          open={isSelecting}
          onClose={closeDetail}
          extra={
            selectedId && (
              <Button
                type="text"
                icon={<ExpandOutlined />}
                onClick={() => navigate(`/phieu-gui/${selectedId}`)}
              >
                {t('bills.viewFull')}
              </Button>
            )
          }
        >
          {selectedId && <BillDetailView id={selectedId} embedded key={selectedId} />}
        </Drawer>
      )}
    </div>
  );
}

export default BillListPage;
