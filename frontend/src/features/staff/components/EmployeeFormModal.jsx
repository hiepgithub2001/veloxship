/**
 * EmployeeFormModal — create/edit staff account.
 * Shows the one-time temporary password after creation.
 */
import { useEffect, useState } from 'react';
import { AutoComplete, Col, Form, Input, Modal, Row, Select, Typography, message } from 'antd';
import { Controller, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { employeeFormSchema } from '../schema';
import { createUser, updateUser, getDepartments, getPositions } from '../../../api/users';
import { getRoles } from '../../../api/permissions';
import DepotSelect from '../../../components/common/DepotSelect';

const { Text } = Typography;

export function EmployeeFormModal({ open, onClose, employee, onSuccess }) {
  const isEdit = Boolean(employee);
  const queryClient = useQueryClient();
  const [tempPassword, setTempPassword] = useState(null);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(employeeFormSchema),
    defaultValues: {
      username: '',
      full_name: '',
      phone: '',
      password: '',
      role: 'operator',
      department: '',
      position: '',
      employee_code: '',
      depot_id: null,
    },
  });

  const { data: departments = { items: [] } } = useQuery({
    queryKey: ['departments-lookup'],
    queryFn: getDepartments,
  });

  const { data: positions = { items: [] } } = useQuery({
    queryKey: ['positions-lookup'],
    queryFn: getPositions,
  });

  const { data: roles = [] } = useQuery({
    queryKey: ['roles'],
    queryFn: getRoles,
  });

  const roleOptions = (roles || [])
    .filter((r) => r.is_active)
    .map((r) => ({ value: r.code, label: r.name }));

  useEffect(() => {
    if (open) {
      setTempPassword(null);
      if (isEdit && employee) {
        reset({
          username: employee.username || '',
          full_name: employee.full_name || '',
          phone: employee.phone || '',
          password: '',
          role: employee.role || 'operator',
          department: employee.department || '',
          position: employee.position || '',
          employee_code: employee.employee_code || '',
          depot_id: employee.depot_id ?? null,
        });
      } else {
        reset({
          username: '',
          full_name: '',
          phone: '',
          password: '',
          role: 'operator',
          department: '',
          position: '',
          employee_code: '',
          depot_id: null,
        });
      }
    }
  }, [open, employee, isEdit, reset]);

  const createMutation = useMutation({
    mutationFn: (data) => createUser(data),
    onSuccess: (res) => {
      message.success('Tạo nhân viên thành công');
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['departments-lookup'] });
      queryClient.invalidateQueries({ queryKey: ['positions-lookup'] });
      if (res?.temporary_password) {
        setTempPassword(res.temporary_password);
      } else {
        onSuccess?.();
        onClose();
      }
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi tạo nhân viên'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updateUser(id, data),
    onSuccess: () => {
      message.success('Cập nhật nhân viên thành công');
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['departments-lookup'] });
      queryClient.invalidateQueries({ queryKey: ['positions-lookup'] });
      onSuccess?.();
      onClose();
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi cập nhật nhân viên'),
  });

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  const onSubmit = (formData) => {
    if (isEdit) {
      const { username, password, ...payload } = formData;
      updateMutation.mutate({ id: employee.id, data: payload });
    } else {
      createMutation.mutate(formData);
    }
  };

  return (
    <>
      <Modal
        title={isEdit ? 'Sửa nhân viên' : 'Thêm nhân viên mới'}
        open={open}
        onOk={handleSubmit(onSubmit)}
        onCancel={onClose}
        okText={isEdit ? 'Cập nhật' : 'Tạo tài khoản'}
        cancelText="Hủy"
        confirmLoading={isSubmitting}
        destroyOnClose
        maskClosable={false}
      >
        <Form layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            label="Họ và tên"
            validateStatus={errors.full_name ? 'error' : ''}
            help={errors.full_name?.message}
            required
          >
            <Controller
              name="full_name"
              control={control}
              render={({ field }) => <Input {...field} placeholder="Nhập họ tên" />}
            />
          </Form.Item>

          <Form.Item
            label="Tên đăng nhập"
            validateStatus={errors.username ? 'error' : ''}
            help={errors.username?.message}
            required
          >
            <Controller
              name="username"
              control={control}
              render={({ field }) => (
                <Input {...field} placeholder="VD: nvquay01" disabled={isEdit} />
              )}
            />
          </Form.Item>

          <Form.Item
            label="Số điện thoại"
            validateStatus={errors.phone ? 'error' : ''}
            help={errors.phone?.message}
          >
            <Controller
              name="phone"
              control={control}
              render={({ field }) => <Input {...field} placeholder="VD: 0901234567" />}
            />
          </Form.Item>

          {!isEdit && (
            <Form.Item
              label="Mật khẩu (bỏ trống để tự sinh)"
              validateStatus={errors.password ? 'error' : ''}
              help={errors.password?.message}
            >
              <Controller
                name="password"
                control={control}
                render={({ field }) => <Input.Password {...field} placeholder="Tự sinh nếu bỏ trống" />}
              />
            </Form.Item>
          )}

          <Form.Item label="Bưu cục / Kho làm việc">
            <Controller
              name="depot_id"
              control={control}
              render={({ field }) => (
                <DepotSelect value={field.value} onChange={field.onChange} />
              )}
            />
          </Form.Item>

          <Row gutter={12}>
            <Col xs={24} sm={12}>
              <Form.Item label="Phòng ban">
                <Controller
                  name="department"
                  control={control}
                  render={({ field }) => (
                    <AutoComplete
                      {...field}
                      placeholder="Nhập hoặc chọn phòng ban"
                      options={(departments.items || []).map((d) => ({ value: d.name }))}
                    />
                  )}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item label="Chức vụ">
                <Controller
                  name="position"
                  control={control}
                  render={({ field }) => (
                    <AutoComplete
                      {...field}
                      placeholder="Nhập hoặc chọn chức vụ"
                      options={(positions.items || []).map((p) => ({ value: p.name }))}
                    />
                  )}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="Mã nhân viên">
            <Controller
              name="employee_code"
              control={control}
              render={({ field }) => <Input {...field} placeholder="VD: NV0123" />}
            />
          </Form.Item>

          <Form.Item
            label="Vai trò"
            validateStatus={errors.role ? 'error' : ''}
            help={errors.role?.message}
            required
          >
            <Controller
              name="role"
              control={control}
              render={({ field }) => <Select {...field} options={roleOptions} />}
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Tài khoản đã được tạo"
        open={Boolean(tempPassword)}
        onCancel={() => {
          setTempPassword(null);
          onSuccess?.();
          onClose();
        }}
        footer={null}
      >
        <p>Mật khẩu tạm của tài khoản (chỉ hiển thị một lần):</p>
        <Text code copyable style={{ fontSize: 18, fontWeight: 600 }}>
          {tempPassword}
        </Text>
        <p style={{ marginTop: 12, color: '#888' }}>
          Vui lòng gửi mật khẩu này cho nhân viên và yêu cầu đổi mật khẩu sau lần đăng nhập đầu tiên.
        </p>
      </Modal>
    </>
  );
}

export default EmployeeFormModal;
