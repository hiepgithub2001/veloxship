/**
 * ContentsStep — Nội dung hàng (package contents for the mobile wizard).
 */
import { Button, InputNumber, Input, Card, Space, Typography } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useFormContext, useFieldArray } from 'react-hook-form';
import { t } from '../../../../i18n/vi';

const { Text } = Typography;

export const CONTENTS_FIELDS = ['contents'];

export function ContentsStep() {
  const {
    control,
    watch,
    setValue,
    formState: { errors },
  } = useFormContext();
  const { fields, append, remove } = useFieldArray({ control, name: 'contents' });

  return (
    <div>
      {fields.map((field, index) => (
        <Card
          key={field.id}
          size="small"
          title={`Gói hàng ${index + 1}`}
          extra={
            fields.length > 1 && (
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={() => remove(index)}
                size="small"
                id={`mobile-content-${index}-remove`}
              />
            )
          }
          style={{ marginBottom: 12 }}
        >
          <div style={{ marginBottom: 8 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {t('bills.description')}
            </Text>
            <Input
              value={watch(`contents.${index}.description`)}
              onChange={(e) => setValue(`contents.${index}.description`, e.target.value)}
              placeholder={t('bills.description')}
              id={`mobile-content-${index}-description`}
            />
          </div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
            <div style={{ flex: 1 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {t('bills.quantity')}
              </Text>
              <InputNumber
                min={1}
                inputMode="numeric"
                value={watch(`contents.${index}.quantity`)}
                onChange={(val) => setValue(`contents.${index}.quantity`, val)}
                style={{ width: '100%' }}
                id={`mobile-content-${index}-quantity`}
              />
            </div>
            <div style={{ flex: 1 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {t('bills.weight')}
              </Text>
              <InputNumber
                min={0}
                step={0.01}
                inputMode="decimal"
                decimalSeparator=","
                value={watch(`contents.${index}.weight_kg`)}
                onChange={(val) => setValue(`contents.${index}.weight_kg`, val)}
                style={{ width: '100%' }}
                id={`mobile-content-${index}-weight`}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <div style={{ flex: 1 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {t('bills.length')}
              </Text>
              <InputNumber
                min={0}
                step={0.1}
                inputMode="decimal"
                decimalSeparator=","
                value={watch(`contents.${index}.length_cm`)}
                onChange={(val) => setValue(`contents.${index}.length_cm`, val)}
                style={{ width: '100%' }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {t('bills.width')}
              </Text>
              <InputNumber
                min={0}
                step={0.1}
                inputMode="decimal"
                decimalSeparator=","
                value={watch(`contents.${index}.width_cm`)}
                onChange={(val) => setValue(`contents.${index}.width_cm`, val)}
                style={{ width: '100%' }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {t('bills.height')}
              </Text>
              <InputNumber
                min={0}
                step={0.1}
                inputMode="decimal"
                decimalSeparator=","
                value={watch(`contents.${index}.height_cm`)}
                onChange={(val) => setValue(`contents.${index}.height_cm`, val)}
                style={{ width: '100%' }}
              />
            </div>
          </div>
        </Card>
      ))}

      <Button
        type="dashed"
        icon={<PlusOutlined />}
        onClick={() =>
          append({
            description: '',
            quantity: 1,
            weight_kg: 0,
            length_cm: null,
            width_cm: null,
            height_cm: null,
          })
        }
        style={{ width: '100%' }}
        id="mobile-add-content"
      >
        {t('bills.addLine')}
      </Button>

      {errors?.contents && (
        <Text type="danger" style={{ display: 'block', marginTop: 8 }}>
          {errors.contents.message || errors.contents.root?.message}
        </Text>
      )}
    </div>
  );
}

export default ContentsStep;
