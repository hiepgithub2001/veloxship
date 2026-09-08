import { useEffect } from 'react';
import { Button, Drawer, Form, Input, Select } from 'antd';
import { useForm } from 'react-hook-form';
import { t } from '../../../i18n/vi';

const transitions = {
  created: ['picked_up', 'cancelled'],
  picked_up: ['in_transit', 'returned', 'cancelled'],
  in_transit: ['delivered', 'returned'],
};

export function StatusUpdateDrawer({ bill, open, onClose, onSubmit, saving }) {
  const { register, handleSubmit, watch, setValue, reset } = useForm({
    defaultValues: { to_status: '' },
  });
  const target = watch('to_status');
  useEffect(() => reset({ to_status: transitions[bill?.status]?.[0] || '' }), [bill, reset]);
  if (!bill) return null;
  return (
    <Drawer
      title={t('bills.updateStatus')}
      open={open}
      onClose={onClose}
      width={420}
      footer={
        <Button type="primary" loading={saving} onClick={handleSubmit(onSubmit)}>
          {t('common.confirm')}
        </Button>
      }
    >
      <Form layout="vertical">
        <Form.Item label="Trạng thái mới">
          <Select
            value={target}
            onChange={(value) => setValue('to_status', value)}
            options={(transitions[bill.status] || []).map((value) => ({
              value,
              label: t(`status.${value}`),
            }))}
          />
        </Form.Item>
        {target === 'delivered' && (
          <Form.Item label={t('bills.deliveredToName')} required>
            <Input {...register('delivered_to_name', { required: true })} />
          </Form.Item>
        )}
        {target === 'cancelled' && (
          <Form.Item label={t('bills.cancellationReason')} required>
            <Input.TextArea {...register('cancellation_reason', { required: true })} />
          </Form.Item>
        )}
        {target === 'returned' && (
          <Form.Item label="Lý do hoàn trả" required>
            <Input.TextArea {...register('note', { required: true })} />
          </Form.Item>
        )}
        {!['returned'].includes(target) && (
          <Form.Item label={t('bills.note')}>
            <Input.TextArea {...register('note')} />
          </Form.Item>
        )}
      </Form>
    </Drawer>
  );
}
