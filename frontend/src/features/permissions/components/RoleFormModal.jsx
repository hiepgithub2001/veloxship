/**
 * RoleFormModal — create or edit a role (name + description; code immutable on edit).
 */
import { useEffect, useState } from 'react';
import { Form, Input, Modal, message } from 'antd';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { createRole, updateRole } from '../../../api/permissions';

export function RoleFormModal({ open, onClose, role, onSuccess }) {
  const isEdit = Boolean(role);
  const queryClient = useQueryClient();

  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  useEffect(() => {
    if (open) {
      if (isEdit && role) {
        setCode(role.code || '');
        setName(role.name || '');
        setDescription(role.description || '');
      } else {
        setCode('');
        setName('');
        setDescription('');
      }
    }
  }, [open, role, isEdit]);

  const mutation = useMutation({
    mutationFn: (payload) =>
      isEdit ? updateRole(role.code, payload) : createRole(payload),
    onSuccess: () => {
      message.success(isEdit ? 'Cập nhật vai trò thành công' : 'Tạo vai trò thành công');
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      onSuccess?.();
      onClose();
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi lưu vai trò'),
  });

  const handleOk = () => {
    if (!name.trim()) {
      message.warning('Tên vai trò là bắt buộc.');
      return;
    }
    if (!isEdit && !code.trim()) {
      message.warning('Mã vai trò là bắt buộc.');
      return;
    }
    const payload = { name: name.trim(), description: description.trim() || null };
    if (!isEdit) payload.code = code.trim().toLowerCase();
    mutation.mutate(payload);
  };

  return (
    <Modal
      title={isEdit ? 'Sửa vai trò' : 'Thêm vai trò mới'}
      open={open}
      onOk={handleOk}
      onCancel={onClose}
      okText={isEdit ? 'Lưu' : 'Tạo vai trò'}
      cancelText="Hủy"
      confirmLoading={mutation.isPending}
      destroyOnClose
      maskClosable={false}
    >
      <Form layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          label="Mã vai trò"
          required={!isEdit}
          extra={isEdit ? 'Mã vai trò không thể thay đổi.' : 'Chữ thường, số hoặc _ (VD: supervisor)'}
        >
          <Input
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="VD: supervisor"
            disabled={isEdit}
          />
        </Form.Item>

        <Form.Item label="Tên vai trò" required>
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="VD: Giám sát"
          />
        </Form.Item>

        <Form.Item label="Mô tả">
          <Input.TextArea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
            placeholder="Mô tả ngắn (tùy chọn)"
          />
        </Form.Item>
      </Form>
    </Modal>
  );
}

export default RoleFormModal;
