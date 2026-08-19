/**
 * Cargo info block — actual weight, insurance, COD, chargeable weight.
 */
import { InputNumber, Checkbox, Typography, Space } from 'antd';
import { Controller } from 'react-hook-form';
import { t } from '../../../i18n/vi';
import { formatWeight } from '../../../lib/format';

const { Text } = Typography;

function computeChargeableWeight(actualWeight, contents) {
  let dimTotal = 0;
  (contents || []).forEach((line) => {
    const { length_cm, width_cm, height_cm } = line || {};
    if (length_cm && width_cm && height_cm) {
      dimTotal += (length_cm * width_cm * height_cm) / 6000;
    }
  });
  return Math.max(actualWeight || 0, dimTotal);
}

export function CargoInfoBlock({ control, errors, watch }) {
  const actualWeight = watch('actual_weight_kg') || 0;
  const contents = watch('contents') || [];
  const chargeableWeight = computeChargeableWeight(actualWeight, contents);

  return (
    <div>
      <h4 style={{ color: '#C41E3A', marginBottom: 8 }}>{t('bills.cargoInfo')}</h4>

      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Controller
          name="actual_weight_kg"
          control={control}
          render={({ field }) => (
            <Space>
              <Text>{t('bills.actualWeight')}:</Text>
              <InputNumber
                {...field}
                min={0}
                step={0.1}
                decimalSeparator=","
                style={{ width: 140 }}
                id="actual-weight"
              />
              <Text>kg</Text>
              {errors?.actual_weight_kg && (
                <Text type="danger">{errors.actual_weight_kg.message}</Text>
              )}
            </Space>
          )}
        />

        <div>
          <Text type="secondary">
            {t('bills.chargeableWeight')}: {formatWeight(chargeableWeight)}
          </Text>
        </div>

        <Controller
          name="is_insurance_required"
          control={control}
          render={({ field }) => (
            <Checkbox
              checked={field.value}
              onChange={(e) => field.onChange(e.target.checked)}
              id="is-insurance"
            >
              {t('bills.isInsurance')}
            </Checkbox>
          )}
        />

        <Controller
          name="cod_amount"
          control={control}
          render={({ field }) => (
            <Space>
              <Text>{t('bills.codAmount')}:</Text>
              <InputNumber
                {...field}
                min={0}
                step={1000}
                formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.')}
                parser={(value) => value.replace(/\./g, '')}
                style={{ width: 200 }}
                id="cod-amount"
              />
              <Text>₫</Text>
              {errors?.cod_amount && (
                <Text type="danger">{errors.cod_amount.message}</Text>
              )}
            </Space>
          )}
        />
      </Space>
    </div>
  );
}

export default CargoInfoBlock;
