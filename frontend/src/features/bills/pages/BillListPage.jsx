/**
 * Bill list page — fetches and displays bills.
 */
import React, { useState, useEffect } from 'react';
import { Button, Card, Table, Typography, Space, Tag, message } from 'antd';
import { PlusOutlined, PrinterOutlined, EyeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { t } from '../../../i18n/vi';
import { listBills, downloadBillPdf } from '../../../api/bills';
import { formatVND, formatViDateTime } from '../../../lib/format';

const { Title } = Typography;

const statusColors = {
  da_tao: 'blue',
  da_lay_hang: 'cyan',
  dang_van_chuyen: 'orange',
  da_giao: 'green',
  hoan_tra: 'purple',
  huy: 'red',
};

const statusText = {
  da_tao: 'Đã tạo',
  da_lay_hang: 'Đã lấy hàng',
  dang_van_chuyen: 'Đang vận chuyển',
  da_giao: 'Đã giao',
  hoan_tra: 'Hoàn trả',
  huy: 'Hủy',
};

export function BillListPage() {
  const navigate = useNavigate();
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });

  const fetchBills = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const data = await listBills({ page, page_size: pageSize });
      setBills(data.items);
      setPagination({
        current: data.page,
        pageSize: data.page_size,
        total: data.total,
      });
    } catch (error) {
      message.error(t('bills.fetchError') || 'Không thể tải danh sách phiếu gửi');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBills();
  }, []);

  const handleTableChange = (newPagination) => {
    fetchBills(newPagination.current, newPagination.pageSize);
  };

  const handlePrint = async (id) => {
    try {
      await downloadBillPdf(id);
    } catch (error) {
      message.error('Lỗi khi tải phiếu in');
    }
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
        <Tag color={statusColors[status] || 'default'}>
          {statusText[status] || status}
        </Tag>
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
            onClick={() => navigate(`/phieu-gui/${record.id}`)}
          />
          <Button 
            type="text" 
            icon={<PrinterOutlined />} 
            onClick={() => handlePrint(record.id)}
          />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>{t('bills.title')}</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/phieu-gui/tao-moi')}
          id="create-bill-btn"
        >
          {t('bills.create')}
        </Button>
      </div>
      <Card styles={{ body: { padding: 0, overflow: 'auto' } }}>
        <Table
          columns={columns}
          dataSource={bills}
          rowKey="id"
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 800 }}
          size="small"
        />
      </Card>
    </div>
  );
}

export default BillListPage;
