/**
 * SenderStep — Người gửi (sender fields for the mobile wizard).
 */
import { Form, Input } from 'antd';
import { Controller, useFormContext } from 'react-hook-form';
import { t } from '../../../../i18n/vi';

export const SENDER_FIELDS = [
  'sender.name',
  'sender.address',
  'sender.district',
  'sender.province',
  'sender.phone',
];

export function SenderStep() {
  const {
    control,
    formState: { errors },
  } = useFormContext();

  return (
    <div>
      <Form.Item
        label={t('bills.senderName')}
        validateStatus={errors?.sender?.name ? 'error' : ''}
        help={errors?.sender?.name?.message}
        required
      >
        <Controller
          name="sender.name"
          control={control}
          render={({ field }) => (
            <Input {...field} placeholder={t('bills.senderName')} id="mobile-sender-name" />
          )}
        />
      </Form.Item>
      <Form.Item
        label={t('bills.senderAddress')}
        validateStatus={errors?.sender?.address ? 'error' : ''}
        help={errors?.sender?.address?.message}
        required
      >
        <Controller
          name="sender.address"
          control={control}
          render={({ field }) => (
            <Input {...field} placeholder={t('bills.senderAddress')} id="mobile-sender-address" />
          )}
        />
      </Form.Item>
      <div style={{ display: 'flex', gap: 12 }}>
        <Form.Item
          label={t('bills.senderDistrict')}
          style={{ flex: 1 }}
          validateStatus={errors?.sender?.district ? 'error' : ''}
          help={errors?.sender?.district?.message}
          required
        >
          <Controller
            name="sender.district"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                placeholder={t('bills.senderDistrict')}
                id="mobile-sender-district"
              />
            )}
          />
        </Form.Item>
        <Form.Item
          label={t('bills.senderProvince')}
          style={{ flex: 1 }}
          validateStatus={errors?.sender?.province ? 'error' : ''}
          help={errors?.sender?.province?.message}
          required
        >
          <Controller
            name="sender.province"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                placeholder={t('bills.senderProvince')}
                id="mobile-sender-province"
              />
            )}
          />
        </Form.Item>
      </div>
      <Form.Item
        label={t('bills.senderPhone')}
        validateStatus={errors?.sender?.phone ? 'error' : ''}
        help={errors?.sender?.phone?.message}
        required
      >
        <Controller
          name="sender.phone"
          control={control}
          render={({ field }) => (
            <Input
              {...field}
              placeholder={t('bills.senderPhone')}
              inputMode="tel"
              id="mobile-sender-phone"
            />
          )}
        />
      </Form.Item>
    </div>
  );
}

export default SenderStep;
