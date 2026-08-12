/**
 * Depot table — displays paginated list of depots with actions.
 */
import { Button, Table, Space } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { Image } from 'antd';
import DepotStatusBadge from './DepotStatusBadge';

export function DepotTable({ data, loading, onEdit, onToggleActive, pagination, onPaginationChange }) {
  const columns = [
    {
      title: 'Ảnh',
      key: 'images',
      width: 100,
      render: (_, record) => {
        const urls = record.image_urls;
        if (!urls || urls.length === 0) {
          return <span style={{ color: '#ccc' }}>—</span>;
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
                {url.startsWith('http') ? (
                  <Image
                    src={url}
                    width={48}
                    height={48}
                    style={{ objectFit: 'cover' }}
                    preview={{ maskStyle: { display: 'none' } }}
                    fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMIAAADDCAYAAADQvc6UAAABRWlDQ1BJQ0MgUHJvZmlsZQAAKJFjYGASSSwoyGFhYGDIzSspCnJ3UoiIjFJgf8LAwSDCIMogwMCcmFxc4BgQ4ANUwgCjUcG3awyMIPqyLsis7PPOq3QdDFcvjV3jOD1bo/TP7gHgL+TWgTRSzwBE7QAmpDId6OA2gWB0xT6dQtaNl5S9bqSDHjE9bF9HvX82buEEHeUOCZPsMG4hqIV4xZX4EAa/4QAr3hCP/ZsHwFyxAn8zPiHtAP8ACdRHodTEAAlvF6YAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAG3SURBVHja7Ns9boMwEAXQV6u3Sl1A3IF3EHYXcAdhdxBxD+5C3ITdgVuQW4gbcTfgJuQW4kZchVx8N/Pum52kJDFjJ5OZk313ZhYiwuFwOBwOh8PhcDgcDofD4XA4HA6Hw+FwOBwOh8PhcDgcDofD4XA4HA6Hw+FwOBwOh8P5H8z3ABv7MfMC8wXzA+E5wm6CcJXgmITnCXN+gvCV4JyEmxCeJ8xnCH8JwmmC4RkizxQ4h+RbhG8JwluEAwnOI9knCF9J8lvCfJLnCH8pwkmC8ZnknCFxJslTgnmEfxLhXITxKxIuRLhQ4ReSbhE+IvEngifEL+RNCb4r8mvBrwmWq4jXhVsV3FXxXcW/FfxPxb8H/FfDfw39N/6fWfw39F9g81t+j/W/2v6x9V+rfV/u39X/s/U/7f1f/79H/M5b/o8z/I8z/8crfYeX/E8z/Ucr3Ucr3Ucr3Ucr3Ucr3Ucr3Ucr3Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qc//Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qc//48ZAAAAAElFTkSuQmCC"
                    }}
                  />
                ) : (
                  <Image
                    src={url}
                    width={48}
                    height={48}
                    style={{ objectFit: 'cover' }}
                    preview={{ maskStyle: { display: 'none' } }}
                    fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMIAAADDCAYAAADQvc6UAAABRWlDQ1BJQ0MgUHJvZmlsZQAAKJFjYGASSSwoyGFhYGDIzSspCnJ3UoiIjFJgf8LAwSDCIMogwMCcmFxc4BgQ4ANUwgCjUcG3awyMIPqyLsis7PPOq3QdDFcvjV3jOD1bo/TP7gHgL+TWgTRSzwBE7QAmpDId6OA2gWB0xT6dQtaNl5S9bqSDHjE9bF9HvX82buEEHeUOCZPsMG4hqIV4xZX4EAa/4QAr3hCP/ZsHwFyxAn8zPiHtAP8ACdRHodTEAAlvF6YAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAG3SURBVHja7Ns9boMwEAXQV6u3Sl1A3IF3EHYXcAdhdxBxD+5C3ITdgVuQW4gbcTfgJuQW4kZchVx8N/Pum52kJDFjJ5OZk313ZhYiwuFwOBwOh8PhcDgcDofD4XA4HA6Hw+FwOBwOh8PhcDgcDofD4XA4HA6Hw+FwOBwOh8P5H8z3ABv7MfMC8wXzA+E5wm6CcJXgmITnCXN+gvCV4JyEmxCeJ8xnCH8JwmmC4RkizxQ4h+RbhG8JwluEAwnOI9knCF9J8lvCfJLnCH8pwkmC8ZnknCFxJslTgnmEfxLhXITxKxIuRLhQ4ReSbhE+IvEngifEL+RNCb4r8mvBrwmWq4jXhVsV3FXxXcW/FfxPxb8H/FfDfw39N/6fWfw39F9g81t+j/W/2v6x9V+rfV/u39X/s/U/7f1f/79H/M5b/o8z/I8z/8crfYeX/E8z/Ucr3Ucr3Ucr3Ucr3Ucr3Ucr3Ucr3Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qc//Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qcz/Qc//48ZAAAAAElFTkSuQmCC"
                  />
                )}
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
