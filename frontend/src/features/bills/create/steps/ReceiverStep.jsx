/**
 * ReceiverStep — Người nhận (receiver fields for the mobile wizard).
 */
import { Form, Input } from 'antd';
import { Controller, useFormContext } from 'react-hook-form';
import { t } from '../../../../i18n/vi';

export const RECEIVER_FIELDS = [
  'receiver.name',
  'receiver.address',
  'receiver.district',
  'receiver.province',
  'receiver.phone',
];

export function ReceiverStep() {
  const {
    control,
    formState: { errors },
  } = useFormContext();

  return (
    <div>
      <Form.Item
        label={t('bills.receiverName')}
        validateStatus={errors?.receiver?.name ? 'error' : ''}
        help={errors?.receiver?.name?.message}
        required
      >
        <Controller
          name="receiver.name"
          control={control}
          render={({ field }) => (
            <Input {...field} placeholder={t('bills.receiverName')} id="mobile-receiver-name" />
          )}
        />
      </Form.Item>
      <Form.Item
        label={t('bills.receiverAddress')}
        validateStatus={errors?.receiver?.address ? 'error' : ''}
        help={errors?.receiver?.address?.message}
        required
      >
        <Controller
          name="receiver.address"
          control={control}
          render={({ field }) => (
            <Input
              {...field}
              placeholder={t('bills.receiverAddress')}
              id="mobile-receiver-address"
            />
          )}
        />
      </Form.Item>
      <div style={{ display: 'flex', gap: 12 }}>
        <Form.Item
          label={t('bills.receiverDistrict')}
          style={{ flex: 1 }}
          validateStatus={errors?.receiver?.district ? 'error' : ''}
          help={errors?.receiver?.district?.message}
          required
        >
          <Controller
            name="receiver.district"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                placeholder={t('bills.receiverDistrict')}
                id="mobile-receiver-district"
              />
            )}
          />
        </Form.Item>
        <Form.Item
          label={t('bills.receiverProvince')}
          style={{ flex: 1 }}
          validateStatus={errors?.receiver?.province ? 'error' : ''}
          help={errors?.receiver?.province?.message}
          required
        >
          <Controller
            name="receiver.province"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                placeholder={t('bills.receiverProvince')}
                id="mobile-receiver-province"
              />
            )}
          />
        </Form.Item>
      </div>
      <Form.Item
        label={t('bills.receiverPhone')}
        validateStatus={errors?.receiver?.phone ? 'error' : ''}
        help={errors?.receiver?.phone?.message}
        required
      >
        <Controller
          name="receiver.phone"
          control={control}
          render={({ field }) => (
            <Input
              {...field}
              placeholder={t('bills.receiverPhone')}
              inputMode="tel"
              id="mobile-receiver-phone"
            />
          )}
        />
      </Form.Item>
    </div>
  );
}

export default ReceiverStep;
