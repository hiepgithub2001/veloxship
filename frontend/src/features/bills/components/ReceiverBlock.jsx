/**
 * Receiver block — form fields for the receiver party.
 */
import { Form, Input } from 'antd';
import { Controller } from 'react-hook-form';
import { t } from '../../../i18n/vi';

export function ReceiverBlock({ control, errors, prefix = 'receiver' }) {
  return (
    <div>
      <h4 style={{ color: '#C41E3A', marginBottom: 8 }}>{t('bills.receiver')}</h4>
      <Form.Item
        label={t('bills.receiverName')}
        validateStatus={errors?.[prefix]?.name ? 'error' : ''}
        help={errors?.[prefix]?.name?.message}
      >
        <Controller
          name={`${prefix}.name`}
          control={control}
          render={({ field }) => (
            <Input {...field} placeholder={t('bills.receiverName')} id={`${prefix}-name`} />
          )}
        />
      </Form.Item>
      <Form.Item
        label={t('bills.receiverAddress')}
        validateStatus={errors?.[prefix]?.address ? 'error' : ''}
        help={errors?.[prefix]?.address?.message}
      >
        <Controller
          name={`${prefix}.address`}
          control={control}
          render={({ field }) => (
            <Input {...field} placeholder={t('bills.receiverAddress')} id={`${prefix}-address`} />
          )}
        />
      </Form.Item>
      <div style={{ display: 'flex', gap: 12 }}>
        <Form.Item
          label={t('bills.receiverDistrict')}
          style={{ flex: 1 }}
          validateStatus={errors?.[prefix]?.district ? 'error' : ''}
          help={errors?.[prefix]?.district?.message}
        >
          <Controller
            name={`${prefix}.district`}
            control={control}
            render={({ field }) => (
              <Input {...field} placeholder={t('bills.receiverDistrict')} id={`${prefix}-district`} />
            )}
          />
        </Form.Item>
        <Form.Item
          label={t('bills.receiverProvince')}
          style={{ flex: 1 }}
          validateStatus={errors?.[prefix]?.province ? 'error' : ''}
          help={errors?.[prefix]?.province?.message}
        >
          <Controller
            name={`${prefix}.province`}
            control={control}
            render={({ field }) => (
              <Input {...field} placeholder={t('bills.receiverProvince')} id={`${prefix}-province`} />
            )}
          />
        </Form.Item>
      </div>
      <Form.Item
        label={t('bills.receiverPhone')}
        validateStatus={errors?.[prefix]?.phone ? 'error' : ''}
        help={errors?.[prefix]?.phone?.message}
      >
        <Controller
          name={`${prefix}.phone`}
          control={control}
          render={({ field }) => (
            <Input {...field} placeholder={t('bills.receiverPhone')} id={`${prefix}-phone`} />
          )}
        />
      </Form.Item>
    </div>
  );
}

export default ReceiverBlock;
