import { useEffect, useState } from 'react';
import { Button, InputNumber, Space } from 'antd';
import { SaveOutlined } from '@ant-design/icons';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { feeSchema } from '../schema';
import { formatVND } from '../../../lib/format';
import { t } from '../../../i18n/vi';

const FEE_FIELDS = [
  { key: 'fee_main', label: t('bills.feeMain') },
  { key: 'fee_insurance', label: t('bills.feeInsurance') },
  { key: 'fee_other', label: t('bills.feeOther') },
  { key: 'fee_vat', label: t('bills.feeVat') },
];
const FEE_KEYS = FEE_FIELDS.map(({ key }) => key);

const vndFormatter = (value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
const vndParser = (value) => value.replace(/\./g, '');

/** Inline fee editor for the bill detail view (fee edit only while `created`). */
export function BillFeeEditor({ bill, saving, onSave }) {
  const [editing, setEditing] = useState(false);
  const {
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(feeSchema),
    defaultValues: { fee_main: 0, fee_insurance: 0, fee_other: 0, fee_vat: 0, fee_total: 0 },
  });

  useEffect(() => {
    reset(bill.fee);
  }, [bill, reset]);

  const values = watch();
  const total = FEE_KEYS.reduce((sum, key) => sum + (Number(values[key]) || 0), 0);

  const handleFeeChange = (field, value) => {
    setValue(field, value || 0);
    const next = FEE_KEYS.reduce(
      (sum, key) => sum + (Number(key === field ? value || 0 : values[key]) || 0),
      0,
    );
    setValue('fee_total', next);
  };

  const save = (fee) => {
    onSave({ fee });
    setEditing(false);
  };

  const cancel = () => {
    reset(bill.fee);
    setEditing(false);
  };

  return (
    <div className="bill-fee-editor">
      <div className="bill-block-heading">
        <div>
          <h3>Cước phí & thanh toán</h3>
          <span>Trình bày theo bố cục phiếu gửi</span>
        </div>
        {bill.status === 'created' && !editing && (
          <Button onClick={() => setEditing(true)}>Chỉnh sửa</Button>
        )}
      </div>
      <div className="bill-fee-layout">
        <div>
          <strong>{t('bills.payer')}</strong>
          <div style={{ marginTop: 10 }}>
            {bill.payer === 'sender' ? t('bills.payerSender') : t('bills.payerReceiver')}
          </div>
          <div style={{ marginTop: 24 }}>
            <strong>{t('bills.serviceTier')}</strong>
            <div style={{ marginTop: 10 }}>
              {bill.service_tier_code || '—'} · {t(`bills.${bill.cargo_type}`)}
            </div>
          </div>
        </div>
        {editing ? (
          <div className="bill-fee-list">
            {FEE_FIELDS.map(({ key, label }) => (
              <div className="bill-fee-line" key={key}>
                <span>{label}</span>
                <InputNumber
                  min={0}
                  value={values[key]}
                  onChange={(value) => handleFeeChange(key, value)}
                  formatter={vndFormatter}
                  parser={vndParser}
                  addonAfter="₫"
                  style={{ width: 200 }}
                />
              </div>
            ))}
            <div className="bill-fee-line bill-fee-total">
              <strong>{t('bills.feeTotal')}</strong>
              <strong>{formatVND(total)}</strong>
            </div>
          </div>
        ) : (
          <div className="bill-fee-list">
            {FEE_FIELDS.map(({ key, label }) => (
              <div className="bill-fee-line" key={key}>
                <span>{label}</span>
                <strong>{formatVND(bill.fee[key])}</strong>
              </div>
            ))}
            <div className="bill-fee-line bill-fee-total">
              <strong>{t('bills.feeTotal')}</strong>
              <strong>{formatVND(bill.fee.fee_total)}</strong>
            </div>
          </div>
        )}
      </div>
      {editing && errors.fee_total && (
        <div style={{ color: '#ff4d4f', marginTop: 8, textAlign: 'right' }}>
          {errors.fee_total.message}
        </div>
      )}
      {editing && (
        <Space style={{ marginTop: 14 }}>
          <Button type="primary" icon={<SaveOutlined />} loading={saving} onClick={handleSubmit(save)}>
            {t('common.save')}
          </Button>
          <Button onClick={cancel}>{t('common.cancel')}</Button>
        </Space>
      )}
    </div>
  );
}

export default BillFeeEditor;
