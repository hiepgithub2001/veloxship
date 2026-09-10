/**
 * Fee breakdown input with auto-computed total (manual entry).
 * Layout: note (Ghi chú) → payer → right-aligned price rows + total.
 */
import { InputNumber, Radio, Typography, Space, Input } from 'antd';
import { t } from '../../../i18n/vi';
import { formatVND } from '../../../lib/format';

const { Text } = Typography;

export function FeeBreakdownInput({ watch, setValue, errors }) {
  const feeMain = watch('fee.fee_main') || 0;
  const feeInsurance = watch('fee.fee_insurance') || 0;
  const feeOther = watch('fee.fee_other') || 0;
  const feeVat = watch('fee.fee_vat') || 0;
  const total = feeMain + feeInsurance + feeOther + feeVat;

  // Auto-update total when components change
  const handleFeeChange = (field, value) => {
    setValue(`fee.${field}`, value || 0);
    const newTotal =
      (field === 'fee_main' ? value || 0 : feeMain) +
      (field === 'fee_insurance' ? value || 0 : feeInsurance) +
      (field === 'fee_other' ? value || 0 : feeOther) +
      (field === 'fee_vat' ? value || 0 : feeVat);
    setValue('fee.fee_total', newTotal);
  };

  const feeFields = [
    { key: 'fee_main', label: t('bills.feeMain') },
    { key: 'fee_insurance', label: t('bills.feeInsurance') },
    { key: 'fee_other', label: t('bills.feeOther') },
    { key: 'fee_vat', label: t('bills.feeVat') },
  ];

  return (
    <div>
      <h4 className="form-section-title">{t('bills.fees')}</h4>

      {/* Ghi chú (description) */}
      <div style={{ marginBottom: 16 }}>
        <Text style={{ display: 'block', fontSize: 12, color: '#8c8c8c', marginBottom: 4 }}>
          {t('bills.note')}
        </Text>
        <Input.TextArea
          rows={2}
          value={watch('note')}
          onChange={(e) => setValue('note', e.target.value)}
          placeholder={t('bills.note')}
          id="fee-note"
        />
      </div>

      {/* Payer — above the price section */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          marginBottom: 16,
        }}
      >
        <h4 className="form-section-title">{t('bills.payer')}</h4>
        <Radio.Group value={watch('payer')} onChange={(e) => setValue('payer', e.target.value)}>
          <Radio value="sender">{t('bills.payerSender')}</Radio>
          <Radio value="receiver">{t('bills.payerReceiver')}</Radio>
        </Radio.Group>
        {errors?.payer && (
          <div style={{ marginTop: 4 }}>
            <Text type="danger">{errors.payer.message}</Text>
          </div>
        )}
      </div>

      {/* Price rows — right-aligned */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
        {feeFields.map(({ key, label }) => (
          <div
            key={key}
            style={{ display: 'flex', alignItems: 'center', marginBottom: 8, gap: 12 }}
          >
            <Text style={{ width: 160, textAlign: 'right' }}>{label}:</Text>
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
              <Input
                style={{ width: '40px', textAlign: 'center', pointerEvents: 'none' }}
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
            marginTop: 12,
            padding: '8px 0',
            borderTop: '2px solid var(--color-primary)',
            gap: 12,
            width: 372,
          }}
        >
          <Text strong style={{ width: 160, fontSize: 14, textAlign: 'right' }}>
            {t('bills.feeTotal')}:
          </Text>
          <Text
            strong
            style={{
              display: 'block',
              width: 200,
              textAlign: 'right',
              fontSize: 16,
              color: 'var(--color-primary)',
            }}
          >
            {formatVND(total)}
          </Text>
        </div>

        {errors?.fee?.fee_total && (
          <div style={{ textAlign: 'right', marginTop: 4 }}>
            <Text type="danger">{errors.fee.fee_total.message}</Text>
          </div>
        )}
      </div>
    </div>
  );
}

export default FeeBreakdownInput;
