/**
 * Sender block — form fields for the sender party.
 */
import { Form, Input } from 'antd';
import { t } from '../../../i18n/vi';

export function SenderBlock({ control, errors, prefix = 'sender' }) {
  return (
    <div>
      <h4 style={{ color: '#C41E3A', marginBottom: 8 }}>{t('bills.sender')}</h4>
      <Form.Item
        label={t('bills.senderName')}
        validateStatus={errors?.[prefix]?.name ? 'error' : ''}
        help={errors?.[prefix]?.name?.message}
      >
        <Input {...control.register(`${prefix}.name`)} placeholder={t('bills.senderName')} id={`${prefix}-name`} />
      </Form.Item>
      <Form.Item
        label={t('bills.senderAddress')}
        validateStatus={errors?.[prefix]?.address ? 'error' : ''}
        help={errors?.[prefix]?.address?.message}
      >
        <Input {...control.register(`${prefix}.address`)} placeholder={t('bills.senderAddress')} id={`${prefix}-address`} />
      </Form.Item>
      <div style={{ display: 'flex', gap: 12 }}>
        <Form.Item
          label={t('bills.senderDistrict')}
          style={{ flex: 1 }}
          validateStatus={errors?.[prefix]?.district ? 'error' : ''}
          help={errors?.[prefix]?.district?.message}
        >
          <Input {...control.register(`${prefix}.district`)} placeholder={t('bills.senderDistrict')} id={`${prefix}-district`} />
        </Form.Item>
        <Form.Item
          label={t('bills.senderProvince')}
          style={{ flex: 1 }}
          validateStatus={errors?.[prefix]?.province ? 'error' : ''}
          help={errors?.[prefix]?.province?.message}
        >
          <Input {...control.register(`${prefix}.province`)} placeholder={t('bills.senderProvince')} id={`${prefix}-province`} />
        </Form.Item>
      </div>
      <Form.Item
        label={t('bills.senderPhone')}
        validateStatus={errors?.[prefix]?.phone ? 'error' : ''}
        help={errors?.[prefix]?.phone?.message}
      >
        <Input {...control.register(`${prefix}.phone`)} placeholder={t('bills.senderPhone')} id={`${prefix}-phone`} />
      </Form.Item>
    </div>
  );
}

export default SenderBlock;
