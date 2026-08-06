/**
 * Depot table — displays paginated list of depots with actions.
 */
import { Button, Table, Space } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import DepotStatusBadge from './DepotStatusBadge';

export function DepotTable({ data, loading, onEdit, onToggleActive, pagination, onPaginationChange }) {
  const columns = [
    {
      title: 'Mã',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: 'Tên',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Điện thoại',
      dataIndex: 'phone',
      key: 'phone',
    },
    {
      title: 'Địa chỉ',
      dataIndex: 'address_detail',
      key: 'address_detail',
    },
    {
      title: 'Khu vực',
      key: 'area',
      render: (_, record) => {
        const parts = [record.ward_name, record.province_name].filter(Boolean);
        return parts.join(', ') || '—';
      },
    },
    {
      title: 'Trạng thái',
      dataIndex: 'is_active',
      key: 'status',
      render: (isActive) => <DepotStatusBadge isActive={isActive} />,
    },
    {
      title: 'Thao tác',
      key: 'actions',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => onEdit(record)}
          >
            Sửa
          </Button>
          <Button
            type="link"
            danger={record.is_active}
            onClick={() => onToggleActive(record)}
          >
            {record.is_active ? 'Vô hiệu hóa' : 'Kích hoạt'}
          </Button>
        </Space>
      ),
    },
  ];

  const handleTableChange = (paginationInfo) => {
    onPaginationChange({
      current: paginationInfo.current,
      pageSize: paginationInfo.pageSize,
    });
  };

  return (
    <Table
      columns={columns}
      dataSource={data?.items || []}
      rowKey="id"
      loading={loading}
      pagination={{
        current: pagination?.current || 1,
        pageSize: pagination?.pageSize || 20,
        total: data?.total || 0,
        showSizeChanger: true,
        showTotal: (total) => `Tổng ${total} bưu cục`,
      }}
      onChange={handleTableChange}
    />
  );
}

export default DepotTable;
