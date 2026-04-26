/**
 * FeesStep — Cước phí (fee breakdown + payer for the mobile wizard).
 */
import { InputNumber, Radio, Typography, Space, Input } from 'antd';
import { useFormContext } from 'react-hook-form';
import { t } from '../../../../i18n/vi';
import { formatVND } from '../../../../lib/format';

const { Text } = Typography;

export const FEES_FIELDS = [
  'fee.fee_main',
  'fee.fee_fuel_surcharge',
  'fee.fee_other_surcharge',
  'fee.fee_vat',
  'fee.fee_total',
  'payer',
];

export function FeesStep() {
  const {
    watch,
    setValue,
    formState: { errors },
  } = useFormContext();

  const feeMain = watch('fee.fee_main') || 0;
  const feeFuel = watch('fee.fee_fuel_surcharge') || 0;
  const feeOther = watch('fee.fee_other_surcharge') || 0;
  const feeVat = watch('fee.fee_vat') || 0;
  const total = feeMain + feeFuel + feeOther + feeVat;

  const handleFeeChange = (field, value) => {
    setValue(`fee.${field}`, value || 0);
    const newTotal =
      (field === 'fee_main' ? value || 0 : feeMain) +
      (field === 'fee_fuel_surcharge' ? value || 0 : feeFuel) +
      (field === 'fee_other_surcharge' ? value || 0 : feeOther) +
      (field === 'fee_vat' ? value || 0 : feeVat);
    setValue('fee.fee_total', newTotal);
  };

  const feeFields = [
    { key: 'fee_main', label: t('bills.feeMain') },
    { key: 'fee_fuel_surcharge', label: t('bills.feeFuel') },
    { key: 'fee_other_surcharge', label: t('bills.feeOther') },
    { key: 'fee_vat', label: t('bills.feeVat') },
  ];

  return (
    <div>
      {feeFields.map(({ key, label }) => (
        <div key={key} style={{ marginBottom: 12 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {label}
          </Text>
          <Space.Compact style={{ width: '100%' }}>
            <InputNumber
              min={0}
              step={1000}
              inputMode="decimal"
              value={watch(`fee.${key}`)}
              onChange={(val) => handleFeeChange(key, val)}
              formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.')}
              parser={(value) => value.replace(/\./g, '')}
              style={{ width: '100%' }}
              id={`mobile-fee-${key}`}
            />
            <Input
              style={{ width: 44, textAlign: 'center', pointerEvents: 'none' }}
              defaultValue="₫"
              tabIndex={-1}
              readOnly
            />
          </Space.Compact>
        </div>
      ))}

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginTop: 8,
          padding: '12px 0',
          borderTop: '2px solid #C41E3A',
        }}
      >
        <Text strong>{t('bills.feeTotal')}:</Text>
        <Text strong style={{ fontSize: 18, color: '#C41E3A' }}>
          {formatVND(total)}
        </Text>
      </div>

      {errors?.fee?.fee_total && <Text type="danger">{errors.fee.fee_total.message}</Text>}

      <div style={{ marginTop: 16 }}>
        <Text strong style={{ display: 'block', marginBottom: 8 }}>
          {t('bills.payer')}
        </Text>
        <Radio.Group value={watch('payer')} onChange={(e) => setValue('payer', e.target.value)}>
          <Radio value="sender">{t('bills.payerSender')}</Radio>
          <Radio value="receiver">{t('bills.payerReceiver')}</Radio>
        </Radio.Group>
        {errors?.payer && (
          <div>
            <Text type="danger">{errors.payer.message}</Text>
          </div>
        )}
      </div>
    </div>
  );
}

export default FeesStep;
