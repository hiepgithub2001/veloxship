/**
 * PermissionPage — Quản lý Vai trò & Phân quyền.
 * Left: dynamic role list (add/edit/delete). Right: grant actions per role.
 */
import { useEffect, useMemo, useState } from 'react';
import {
  Button,
  Card,
  Checkbox,
  Col,
  Divider,
  Empty,
  List,
  Popconfirm,
  Row,
  Space,
  Tag,
  Typography,
  message,
} from 'antd';
import {
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  deleteRole,
  getPermissionCatalog,
  getRoles,
  updateRolePermissions,
} from '../../../api/permissions';
import { RoleFormModal } from '../components/RoleFormModal';

const { Text, Title } = Typography;

export function PermissionPage() {
  const queryClient = useQueryClient();

  const [selectedRoleCode, setSelectedRoleCode] = useState(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingRole, setEditingRole] = useState(null);
  const [checkedActions, setCheckedActions] = useState([]);

  const rolesQuery = useQuery({ queryKey: ['roles'], queryFn: getRoles });
  const catalogQuery = useQuery({
    queryKey: ['permission-catalog'],
    queryFn: getPermissionCatalog,
  });

  const roles = useMemo(() => rolesQuery.data || [], [rolesQuery.data]);
  const modules = useMemo(() => catalogQuery.data?.modules || [], [catalogQuery.data]);

  const selectedRole = useMemo(
    () => roles.find((r) => r.code === selectedRoleCode) || null,
    [roles, selectedRoleCode],
  );

  // Auto-select the first role on load.
  useEffect(() => {
    if (!selectedRoleCode && roles.length > 0) {
      setSelectedRoleCode(roles[0].code);
    }
  }, [roles, selectedRoleCode]);

  // Sync checkbox state when the selected role changes.
  useEffect(() => {
    setCheckedActions(selectedRole?.actions || []);
  }, [selectedRoleCode, selectedRole]);

  const deleteMutation = useMutation({
    mutationFn: (code) => deleteRole(code),
    onSuccess: () => {
      message.success('Xóa vai trò thành công');
      setSelectedRoleCode(null);
      queryClient.invalidateQueries({ queryKey: ['roles'] });
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi xóa vai trò'),
  });

  const savePermissionsMutation = useMutation({
    mutationFn: ({ code, actions }) => updateRolePermissions(code, actions),
    onSuccess: () => {
      message.success('Đã lưu quyền cho vai trò');
      queryClient.invalidateQueries({ queryKey: ['roles'] });
    },
    onError: (err) => message.error(err.response?.data?.message || 'Lỗi khi lưu quyền'),
  });

  const toggleAction = (code) => {
    setCheckedActions((prev) =>
      prev.includes(code) ? prev.filter((a) => a !== code) : [...prev, code],
    );
  };

  const handleCreate = () => {
    setEditingRole(null);
    setFormOpen(true);
  };

  const handleEdit = () => {
    setEditingRole(selectedRole);
    setFormOpen(true);
  };

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <h2 style={{ margin: 0 }}>Vai trò & Phân quyền</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Thêm vai trò
        </Button>
      </div>

      <Row gutter={16}>
        <Col xs={24} md={8}>
          <Card title="Danh sách vai trò" size="small" style={{ height: '100%' }}>
            <List
              loading={rolesQuery.isLoading}
              dataSource={roles}
              locale={{ emptyText: <Empty description="Chưa có vai trò" /> }}
              renderItem={(role) => (
                <List.Item
                  onClick={() => setSelectedRoleCode(role.code)}
                  style={{
                    cursor: 'pointer',
                    padding: '8px 12px',
                    borderRadius: 6,
                    background:
                      role.code === selectedRoleCode ? 'var(--color-primary-bg, #e6f4ff)' : undefined,
                  }}
                >
                  <List.Item.Meta
                    title={
                      <Space>
                        <Text strong>{role.name}</Text>
                        {!role.is_active && <Tag color="red">Tắt</Tag>}
                      </Space>
                    }
                    description={`${role.code} · ${role.user_count ?? 0} người dùng`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        <Col xs={24} md={16}>
          <Card
            title="Quyền của vai trò"
            size="small"
            style={{ height: '100%' }}
            extra={
              selectedRole ? (
                <Space>
                  <Button icon={<EditOutlined />} onClick={handleEdit}>
                    Sửa
                  </Button>
                  <Popconfirm
                    title="Xóa vai trò này?"
                    description="Chỉ xóa được vai trò không còn người dùng nào."
                    okText="Xóa"
                    cancelText="Hủy"
                    okButtonProps={{ danger: true }}
                    onConfirm={() => deleteMutation.mutate(selectedRole.code)}
                  >
                    <Button danger icon={<DeleteOutlined />} disabled={selectedRole.code === 'admin'}>
                      Xóa
                    </Button>
                  </Popconfirm>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    loading={savePermissionsMutation.isPending}
                    onClick={() =>
                      savePermissionsMutation.mutate({
                        code: selectedRole.code,
                        actions: checkedActions,
                      })
                    }
                  >
                    Lưu quyền
                  </Button>
                </Space>
              ) : null
            }
          >
            {!selectedRole ? (
              <Empty description="Chọn một vai trò để cấu hình quyền." style={{ marginTop: 40 }} />
            ) : (
              <div>
                <Title level={4} style={{ marginTop: 0 }}>
                  {selectedRole.name}{' '}
                  <Text type="secondary" style={{ fontSize: 14 }}>
                    ({selectedRole.code})
                  </Text>
                </Title>
                {selectedRole.description && (
                  <Text type="secondary">{selectedRole.description}</Text>
                )}

                <Divider style={{ margin: '16px 0' }} />

                <div style={{ maxHeight: 420, overflowY: 'auto' }}>
                  {modules.map((mod) => (
                    <div key={mod.code} style={{ marginBottom: 12 }}>
                      <Text strong>{mod.label}</Text>
                      <div style={{ marginTop: 4 }}>
                        {mod.actions.map((action) => (
                          <Checkbox
                            key={action.code}
                            checked={checkedActions.includes(action.code)}
                            onChange={() => toggleAction(action.code)}
                            style={{ marginRight: 16, marginBottom: 4 }}
                          >
                            {action.label}
                          </Checkbox>
                        ))}
                      </div>
                      <Divider style={{ margin: '8px 0' }} />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      <RoleFormModal
        open={formOpen}
        onClose={() => setFormOpen(false)}
        role={editingRole}
        onSuccess={() => {
          if (editingRole) setSelectedRoleCode(editingRole.code);
          setEditingRole(null);
        }}
      />
    </div>
  );
}

export default PermissionPage;
