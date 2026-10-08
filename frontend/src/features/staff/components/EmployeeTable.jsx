/**
 * EmployeeTable — paginated staff list with lock/unlock, edit and reset actions.
 */
import { Button, Space, Table, Tag } from 'antd';
import { EditOutlined, KeyOutlined } from '@ant-design/icons';

export function EmployeeTable({
  data,
  loading,
  onEdit,
  onToggleActive,
  onResetPassword,
  pagination,
  onPaginationChange,
}) {
  const columns = [
    {
      title: 'Mã NV',
      key: 'code',
      render: (_, record) => record.employee_code || `NV${String(record.id).padStart(4, '0')}`,
    },
    { title: 'Họ và tên', dataIndex: 'full_name', key: 'full_name' },
    { title: 'Tên đăng nhập', dataIndex: 'username', key: 'username' },
    { title: 'Số điện thoại', dataIndex: 'phone', key: 'phone', render: (v) => v || '—' },
    { title: 'Phòng ban', dataIndex: 'department', key: 'department', render: (v) => v || '—' },
    { title: 'Chức vụ', dataIndex: 'position', key: 'position', render: (v) => v || '—' },
    {
      title: 'Vai trò',
      dataIndex: 'role',
      key: 'role',
      render: (role, record) => <Tag>{record.role_name || role}</Tag>,
    },
    {
      title: 'Trạng thái',
      dataIndex: 'is_active',
      key: 'status',
      render: (isActive) =>
        isActive ? <Tag color="green">Hoạt động</Tag> : <Tag color="red">Bị khóa</Tag>,
    },
    {
      title: 'Thao tác',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button type="link" icon={<EditOutlined />} onClick={() => onEdit(record)}>
            Sửa
          </Button>
          <Button type="link" danger={record.is_active} onClick={() => onToggleActive(record)}>
            {record.is_active ? 'Khóa' : 'Mở'}
          </Button>
          <Button type="link" icon={<KeyOutlined />} onClick={() => onResetPassword(record)}>
            Đặt lại MK
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
      scroll={{ x: 1100 }}
      pagination={{
        current: pagination?.current || 1,
        pageSize: pagination?.pageSize || 20,
        total: data?.total || 0,
        showSizeChanger: true,
        showTotal: (total) => `Tổng ${total} nhân viên`,
      }}
      onChange={handleTableChange}
    />
  );
}

export default EmployeeTable;
