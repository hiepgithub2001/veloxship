/**
 * LookupManager — reusable manager for departments / positions.
 * These values are stored in `users.metadata`, so the list is derived and
 * "adding" happens through the employee form (a hint is shown).
 */
import { useState } from 'react';
import { Alert, Button, Input, Modal, Popconfirm, Space, Table } from 'antd';
import { DeleteOutlined, EditOutlined } from '@ant-design/icons';

export function LookupManager({ singular, items, loading, onRename, onDelete }) {
  const [renaming, setRenaming] = useState(null);
  const [newName, setNewName] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const columns = [
    { title: 'Tên', dataIndex: 'name', key: 'name' },
    { title: 'Số nhân viên', dataIndex: 'user_count', key: 'user_count', width: 140 },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 180,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => {
              setRenaming(record.name);
              setNewName(record.name);
            }}
          >
            Đổi tên
          </Button>
          <Popconfirm
            title={`Xóa ${singular} "${record.name}"?`}
            description="Thao tác sẽ gỡ giá trị này khỏi tất cả nhân viên."
            okText="Xóa"
            cancelText="Hủy"
            okButtonProps={{ danger: true }}
            onConfirm={() => onDelete(record.name)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Xóa
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleRenameOk = async () => {
    if (!newName.trim() || newName.trim() === renaming) {
      setRenaming(null);
      return;
    }
    setSubmitting(true);
    try {
      await onRename(renaming, newName.trim());
    } finally {
      setSubmitting(false);
      setRenaming(null);
    }
  };

  return (
    <div>
      <Alert
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
        message={`Thêm ${singular} mới bằng cách nhập tên trong form "Thêm/Sửa nhân viên".`}
      />
      <Table
        columns={columns}
        dataSource={items}
        rowKey="name"
        loading={loading}
        pagination={false}
        size="middle"
      />
      <Modal
        title={`Đổi tên ${singular}`}
        open={Boolean(renaming)}
        onOk={handleRenameOk}
        onCancel={() => setRenaming(null)}
        okText="Lưu"
        cancelText="Hủy"
        confirmLoading={submitting}
      >
        <Input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Nhập tên mới"
          onPressEnter={handleRenameOk}
        />
      </Modal>
    </div>
  );
}

export default LookupManager;
