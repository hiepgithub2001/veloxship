import { useEffect } from 'react';
import { Button, Drawer, Form, Input } from 'antd';
import { useForm } from 'react-hook-form';
import { t } from '../../../i18n/vi';

const partyFields = ['name', 'phone', 'address_detail', 'province_name', 'ward_name'];
export function BillEditDrawer({ bill, open, onClose, onSubmit, saving }) {
  const postPickup = ['picked_up', 'in_transit'].includes(bill?.status);
  const { register, handleSubmit, reset } = useForm();
  useEffect(() => {
    if (bill) reset({ receiver: bill.receiver, note: bill.note || '', edit_reason: '' });
  }, [bill, reset]);
  if (!bill) return null;
  return (
    <Drawer
      title={t('common.edit')}
      open={open}
      onClose={onClose}
      width={520}
      footer={
        <Button type="primary" loading={saving} onClick={handleSubmit(onSubmit)}>
          {t('common.save')}
        </Button>
      }
    >
      {postPickup && (
        <p style={{ color: '#8c5a00', background: '#fff7e6', padding: 12 }}>
          Sau khi lấy hàng, chỉ được điều chỉnh thông tin người nhận và ghi chú. Mọi thay đổi cần
          nêu lý do.
        </p>
      )}
      <Form layout="vertical">
        <h4>{t('bills.receiver')}</h4>
        {partyFields.map((field) => (
          <Form.Item
            key={field}
            label={t(
              `bills.${field === 'address_detail' ? 'addressDetail' : field === 'province_name' ? 'province' : field === 'ward_name' ? 'ward' : field}`,
            )}
          >
            <Input {...register(`receiver.${field}`)} />
          </Form.Item>
        ))}
        <Form.Item label={t('bills.note')}>
          <Input.TextArea {...register('note')} />
        </Form.Item>
        {postPickup && (
          <Form.Item label="Lý do thay đổi" required>
            <Input.TextArea {...register('edit_reason', { required: true })} />
          </Form.Item>
        )}
      </Form>
    </Drawer>
  );
}
