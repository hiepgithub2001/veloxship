/**
 * StaffPage — Quản lý nhân viên (UC-WEB-01/02/03).
 */
import { useCallback, useState } from 'react';
import { Button, Modal, Typography, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { getUsers, updateUser, resetUserPassword } from '../../../api/users';
import EmployeeSearchBar from '../components/EmployeeSearchBar';
import EmployeeTable from '../components/EmployeeTable';
import EmployeeFormModal from '../components/EmployeeFormModal';

const { Text } = Typography;

export function StaffPage() {
  const queryClient = useQueryClient();

  // Filters
  const [search, setSearch] = useState('');
  const [role, setRole] = useState(undefined);
  const [isActive, setIsActive] = useState(undefined);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);

  // Reset-password state
  const [resetTemp, setResetTemp] = useState(null);

  const { data, isLoading } = useQuery({
    queryKey: [
      'users',
      { page: pagination.current, pageSize: pagination.pageSize, search, role, isActive },
    ],
    queryFn: () =>
      getUsers({
        page: pagination.current,
        pageSize: pagination.pageSize,
        search: search || undefined,
        role,
        isActive,
      }),
  });

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, is_active }) => updateUser(id, { is_active }),
    onSuccess: () => {
      message.success('Cập nhật trạng thái thành công');
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi cập nhật trạng thái'),
  });

  const resetPasswordMutation = useMutation({
    mutationFn: (id) => resetUserPassword(id),
    onSuccess: (res) => {
      setResetTemp(res?.temporary_password || '');
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi đặt lại mật khẩu'),
  });

  const handleSearchChange = useCallback((value) => {
    setSearch(value);
    setPagination((p) => ({ ...p, current: 1 }));
  }, []);
  const handleRoleChange = useCallback((value) => {
    setRole(value);
    setPagination((p) => ({ ...p, current: 1 }));
  }, []);
  const handleIsActiveChange = useCallback((value) => {
    setIsActive(value);
    setPagination((p) => ({ ...p, current: 1 }));
  }, []);
  const handlePaginationChange = useCallback(({ current, pageSize }) => {
    setPagination({ current, pageSize });
  }, []);

  const handleCreate = useCallback(() => {
    setEditingEmployee(null);
    setModalOpen(true);
  }, []);
  const handleEdit = useCallback((employee) => {
    setEditingEmployee(employee);
    setModalOpen(true);
  }, []);
  const handleModalClose = useCallback(() => {
    setModalOpen(false);
    setEditingEmployee(null);
  }, []);
  const handleToggleActive = useCallback(
    (employee) => toggleActiveMutation.mutate({ id: employee.id, is_active: !employee.is_active }),
    [toggleActiveMutation],
  );
  const handleResetPassword = useCallback(
    (employee) => resetPasswordMutation.mutate(employee.id),
    [resetPasswordMutation],
  );

  return (
    <div>
      <div className="page-header">
        <h2>Quản lý nhân viên</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Thêm nhân viên mới
        </Button>
      </div>

      <EmployeeSearchBar
        search={search}
        onSearchChange={handleSearchChange}
        role={role}
        onRoleChange={handleRoleChange}
        isActive={isActive}
        onIsActiveChange={handleIsActiveChange}
      />
      <EmployeeTable
        data={data}
        loading={isLoading}
        onEdit={handleEdit}
        onToggleActive={handleToggleActive}
        onResetPassword={handleResetPassword}
        pagination={pagination}
        onPaginationChange={handlePaginationChange}
      />

      <EmployeeFormModal open={modalOpen} onClose={handleModalClose} employee={editingEmployee} />

      <Modal
        title="Đặt lại mật khẩu"
        open={Boolean(resetTemp)}
        onCancel={() => setResetTemp(null)}
        footer={null}
      >
        <p>Mật khẩu tạm mới của tài khoản:</p>
        <Text code copyable style={{ fontSize: 18, fontWeight: 600 }}>
          {resetTemp}
        </Text>
      </Modal>
    </div>
  );
}

export default StaffPage;
