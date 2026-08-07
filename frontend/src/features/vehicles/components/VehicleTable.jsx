/**
 * Vehicle table — displays paginated list of vehicles with actions.
 */
import { Button, Table, Space, Popconfirm } from 'antd';
import { EditOutlined, DeleteOutlined } from '@ant-design/icons';
import VehicleStatusBadge from './VehicleStatusBadge';

const VEHICLE_TYPE_LABELS = {
  motorcycle: 'Xe máy',
  truck: 'Xe tải',
};

export function VehicleTable({ data, loading, page, pageSize, total, onPageChange, onEdit, onDelete }) {
  const columns = [
    {
      title: 'Biển số',
      dataIndex: 'license_plate',
      key: 'license_plate',
    },
    {
      title: 'Loại xe',
      dataIndex: 'vehicle_type',
      key: 'vehicle_type',
      render: (type) => VEHICLE_TYPE_LABELS[type] || type,
    },
    {
      title: 'Tải trọng',
      dataIndex: 'max_weight_kg',
      key: 'max_weight_kg',
      render: (value) => `${value} kg`,
    },
    {
      title: 'Thể tích',
      dataIndex: 'max_volume_m3',
      key: 'max_volume_m3',
      render: (value) => `${value} m³`,
    },
    {
      title: 'Tài xế',
      dataIndex: 'driver_name',
      key: 'driver_name',
      render: (name) => name || '—',
    },
    {
      title: 'Bưu cục',
      dataIndex: 'depot_name',
      key: 'depot_name',
      render: (name) => name || '—',
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      render: (status) => <VehicleStatusBadge status={status} />,
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
          <Popconfirm
            title="Xác nhận vô hiệu hóa xe này?"
            onConfirm={() => onDelete(record)}
            okText="Đồng ý"
            cancelText="Hủy"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Xóa
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data}
      rowKey="id"
      loading={loading}
      pagination={{
        current: page,
        pageSize: pageSize,
        total: total,
        showSizeChanger: true,
        showTotal: (total) => `Tổng ${total} phương tiện`,
      }}
      onChange={(paginationInfo) => onPageChange(paginationInfo.current, paginationInfo.pageSize)}
    />
  );
}

export default VehicleTable;
