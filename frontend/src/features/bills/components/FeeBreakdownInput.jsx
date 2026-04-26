/**
 * Fee breakdown input with auto-computed total.
 */
import { InputNumber, Radio, Typography, Space, Input } from 'antd';
import { t } from '../../../i18n/vi';
import { formatVND } from '../../../lib/format';

const { Text } = Typography;

export function FeeBreakdownInput({ watch, setValue, errors }) {
  const feeMain = watch('fee.fee_main') || 0;
  const feeFuel = watch('fee.fee_fuel_surcharge') || 0;
  const feeOther = watch('fee.fee_other_surcharge') || 0;
  const feeVat = watch('fee.fee_vat') || 0;
  const total = feeMain + feeFuel + feeOther + feeVat;

  // Auto-update total when components change
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
      <h4 style={{ color: '#C41E3A', marginBottom: 8 }}>{t('bills.fees')}</h4>

      {feeFields.map(({ key, label }) => (
        <div key={key} style={{ display: 'flex', alignItems: 'center', marginBottom: 8, gap: 12 }}>
          <Text style={{ width: 160 }}>{label}:</Text>
          <Space.Compact style={{ width: 200 }}>
            <InputNumber
              min={0}
              step={1000}
              value={watch(`fee.${key}`)}
              onChange={(val) => handleFeeChange(key, val)}
              formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.')}
              parser={(value) => value.replace(/\./g, '')}
              style={{ width: '100%' }}
              id={`fee-${key}`}
            />
            <Input style={{ width: '40px', textAlign: 'center', pointerEvents: 'none' }} defaultValue="₫" tabIndex={-1} readOnly />
          </Space.Compact>
        </div>
      ))}

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          marginTop: 12,
          padding: '8px 0',
          borderTop: '2px solid #C41E3A',
        }}
      >
        <Text strong style={{ width: 160, fontSize: 14 }}>
          {t('bills.feeTotal')}:
        </Text>
        <Text strong style={{ fontSize: 16, color: '#C41E3A' }}>
          {formatVND(total)}
        </Text>
      </div>

      {errors?.fee?.fee_total && (
        <Text type="danger">{errors.fee.fee_total.message}</Text>
      )}

      <div style={{ marginTop: 16 }}>
        <h4 style={{ color: '#C41E3A', marginBottom: 8 }}>{t('bills.payer')}</h4>
        <Radio.Group
          value={watch('payer')}
          onChange={(e) => setValue('payer', e.target.value)}
        >
          <Radio value="sender">{t('bills.payerSender')}</Radio>
          <Radio value="receiver">{t('bills.payerReceiver')}</Radio>
        </Radio.Group>
        {errors?.payer && <div><Text type="danger">{errors.payer.message}</Text></div>}
      </div>
    </div>
  );
}

export default FeeBreakdownInput;
