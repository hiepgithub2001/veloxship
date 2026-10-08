/**
 * StaffPage — Quản lý nhân viên (UC-WEB-01/02/03).
 * Tabs: Nhân viên / Phòng ban / Chức vụ.
 */
import { useCallback, useState } from 'react';
import { Button, Modal, Tabs, Typography, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  getUsers,
  updateUser,
  resetUserPassword,
  getDepartments,
  renameDepartment,
  deleteDepartment,
  getPositions,
  renamePosition,
  deletePosition,
} from '../../../api/users';
import EmployeeSearchBar from '../components/EmployeeSearchBar';
import EmployeeTable from '../components/EmployeeTable';
import EmployeeFormModal from '../components/EmployeeFormModal';
import LookupManager from '../components/LookupManager';

const { Text } = Typography;

export function StaffPage() {
  const queryClient = useQueryClient();

  // Filters
  const [search, setSearch] = useState('');
  const [role, setRole] = useState(undefined);
  const [department, setDepartment] = useState(undefined);
  const [position, setPosition] = useState(undefined);
  const [isActive, setIsActive] = useState(undefined);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);

  // Reset-password state
  const [resetTemp, setResetTemp] = useState(null);

  const [activeTab, setActiveTab] = useState('employees');

  const { data, isLoading } = useQuery({
    queryKey: [
      'users',
      { page: pagination.current, pageSize: pagination.pageSize, search, role, department, position, isActive },
    ],
    queryFn: () =>
      getUsers({
        page: pagination.current,
        pageSize: pagination.pageSize,
        search: search || undefined,
        role,
        department,
        position,
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

  const departmentsQuery = useQuery({ queryKey: ['departments-lookup'], queryFn: getDepartments });
  const positionsQuery = useQuery({ queryKey: ['positions-lookup'], queryFn: getPositions });

  const handleSearchChange = useCallback((value) => {
    setSearch(value);
    setPagination((p) => ({ ...p, current: 1 }));
  }, []);
  const handleRoleChange = useCallback((value) => {
    setRole(value);
    setPagination((p) => ({ ...p, current: 1 }));
  }, []);
  const handleDepartmentChange = useCallback((value) => {
    setDepartment(value);
    setPagination((p) => ({ ...p, current: 1 }));
  }, []);
  const handlePositionChange = useCallback((value) => {
    setPosition(value);
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

  const renameDepartmentMutation = useMutation({
    mutationFn: ({ name, newName }) => renameDepartment(name, newName),
    onSuccess: () => {
      message.success('Đổi tên phòng ban thành công');
      queryClient.invalidateQueries({ queryKey: ['departments-lookup'] });
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi đổi tên'),
  });
  const deleteDepartmentMutation = useMutation({
    mutationFn: (name) => deleteDepartment(name),
    onSuccess: () => {
      message.success('Xóa phòng ban thành công');
      queryClient.invalidateQueries({ queryKey: ['departments-lookup'] });
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi xóa'),
  });
  const renamePositionMutation = useMutation({
    mutationFn: ({ name, newName }) => renamePosition(name, newName),
    onSuccess: () => {
      message.success('Đổi tên chức vụ thành công');
      queryClient.invalidateQueries({ queryKey: ['positions-lookup'] });
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi đổi tên'),
  });
  const deletePositionMutation = useMutation({
    mutationFn: (name) => deletePosition(name),
    onSuccess: () => {
      message.success('Xóa chức vụ thành công');
      queryClient.invalidateQueries({ queryKey: ['positions-lookup'] });
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi xóa'),
  });

  return (
    <div>
      <div className="page-header">
        <h2>Quản lý nhân viên</h2>
        {activeTab === 'employees' && (
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            Thêm nhân viên mới
          </Button>
        )}
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: 'employees',
            label: 'Nhân viên',
            children: (
              <>
                <EmployeeSearchBar
                  search={search}
                  onSearchChange={handleSearchChange}
                  role={role}
                  onRoleChange={handleRoleChange}
                  department={department}
                  onDepartmentChange={handleDepartmentChange}
                  position={position}
                  onPositionChange={handlePositionChange}
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
              </>
            ),
          },
          {
            key: 'departments',
            label: 'Phòng ban',
            children: (
              <LookupManager
                singular="phòng ban"
                items={departmentsQuery.data?.items || []}
                loading={departmentsQuery.isLoading}
                onRename={(name, newName) => renameDepartmentMutation.mutateAsync({ name, newName })}
                onDelete={(name) => deleteDepartmentMutation.mutate(name)}
              />
            ),
          },
          {
            key: 'positions',
            label: 'Chức vụ',
            children: (
              <LookupManager
                singular="chức vụ"
                items={positionsQuery.data?.items || []}
                loading={positionsQuery.isLoading}
                onRename={(name, newName) => renamePositionMutation.mutateAsync({ name, newName })}
                onDelete={(name) => deletePositionMutation.mutate(name)}
              />
            ),
          },
        ]}
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
