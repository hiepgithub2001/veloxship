/**
 * Vehicle table — displays paginated list of vehicles with actions.
 */
import { Button, Table, Space, Popconfirm } from 'antd';
import { EditOutlined, DeleteOutlined, CameraOutlined } from '@ant-design/icons';
import VehicleStatusBadge from './VehicleStatusBadge';

const VEHICLE_TYPE_LABELS = {
  motorcycle: 'Xe máy',
  truck: 'Xe tải',
};

export function VehicleTable({ data, loading, page, pageSize, total, onPageChange, onEdit, onDelete }) {
  const columns = [
    {
      title: 'Ảnh',
      key: 'images',
      width: 100,
      render: (_, record) => {
        const urls = record.image_urls;
        if (!urls || urls.length === 0) {
          return <CameraOutlined style={{ color: '#ccc', fontSize: 20 }} />;
        }
        const display = urls.slice(0, 3);
        return (
          <Space size={4}>
            {display.map((url, idx) => (
              <div
                key={idx}
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 4,
                  overflow: 'hidden',
                  border: '1px solid #d9d9d9',
                  backgroundColor: '#f5f5f5',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <img
                  src={url.startsWith('http') ? url : url}
                  alt=""
                  style={{
                    width: 48,
                    height: 48,
                    objectFit: 'cover',
                  }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              </div>
            ))}
            {urls.length > 3 && (
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 4,
                  border: '1px solid #d9d9d9',
                  backgroundColor: '#f5f5f5',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 12,
                  fontWeight: 600,
                  color: '#666',
                }}
              >
                +{urls.length - 3}
              </div>
            )}
          </Space>
        );
      },
    },
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
