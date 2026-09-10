import { useEffect, useState } from 'react';
import { Button, Descriptions, Form, Input, Space } from 'antd';
import { EditOutlined, SaveOutlined } from '@ant-design/icons';
import { t } from '../../../i18n/vi';

const fields = [
  ['name', 'Họ tên'],
  ['phone', 'Số điện thoại'],
  ['address_detail', 'Địa chỉ'],
  ['ward_name', 'Phường/Xã'],
  ['province_name', 'Tỉnh/TP'],
];

export function BillPartyEditor({ bill, side, saving, onSave }) {
  const party = bill[side];
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(party);
  const postPickup = ['picked_up', 'in_transit'].includes(bill.status);
  useEffect(() => {
    setDraft(party);
    setEditing(false);
  }, [party]);
  const editable = bill.status === 'created' || (side === 'receiver' && postPickup);
  const set = (field, value) => setDraft((current) => ({ ...current, [field]: value }));
  const save = () => {
    onSave({
      [side]: draft,
      ...(postPickup ? { edit_reason: 'Cập nhật thông tin liên hệ người nhận' } : {}),
    });
    setEditing(false);
  };
  return (
    <CardShell
      title={t(`bills.${side}`)}
      action={
        editable &&
        !editing && (
          <Button type="text" icon={<EditOutlined />} onClick={() => setEditing(true)}>
            Sửa
          </Button>
        )
      }
    >
      {editing ? (
        <Form layout="vertical">
          {fields.map(([key, label]) => (
            <Form.Item key={key} label={label}>
              <Input
                value={draft?.[key] || ''}
                onChange={(event) => set(key, event.target.value)}
              />
            </Form.Item>
          ))}
          <Space>
            <Button type="primary" icon={<SaveOutlined />} loading={saving} onClick={save}>
              {t('common.save')}
            </Button>
            <Button
              onClick={() => {
                setDraft(party);
                setEditing(false);
              }}
            >
              {t('common.cancel')}
            </Button>
          </Space>
        </Form>
      ) : (
        <Descriptions size="small" column={1}>
          {fields.map(([key, label]) => (
            <Descriptions.Item key={key} label={label}>
              {party?.[key] || '—'}
            </Descriptions.Item>
          ))}
        </Descriptions>
      )}
    </CardShell>
  );
}

function CardShell({ title, action, children }) {
  return (
    <div className="bill-party-card">
      <div className="bill-party-card-header">
        <strong>{title}</strong>
        {action}
      </div>
      {children}
    </div>
  );
}
