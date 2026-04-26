/**
 * ConfirmStep — Xác nhận (read-only summary with "Sửa" links).
 */
import { Card, Descriptions, Typography, Button, Divider } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { useFormContext } from 'react-hook-form';
import { t } from '../../../../i18n/vi';
import { formatVND } from '../../../../lib/format';

const { Text, Title } = Typography;

export const CONFIRM_FIELDS = [];

/**
 * @param {{ goToStep: (step: number) => void }} props
 */
export function ConfirmStep({ goToStep }) {
  const { getValues } = useFormContext();
  const values = getValues();

  const sectionHeader = (title, stepIndex) => (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
      }}
    >
      <Text strong style={{ fontSize: 15, color: '#C41E3A' }}>
        {title}
      </Text>
      <Button type="link" size="small" icon={<EditOutlined />} onClick={() => goToStep(stepIndex)}>
        Sửa
      </Button>
    </div>
  );

  return (
    <div>
      <Title level={5} style={{ textAlign: 'center', marginBottom: 16 }}>
        Kiểm tra thông tin trước khi lưu
      </Title>

      {/* Sender */}
      <Card size="small" style={{ marginBottom: 12 }}>
        {sectionHeader(t('bills.sender'), 0)}
        <Descriptions column={1} size="small">
          <Descriptions.Item label="Họ tên">{values.sender.name}</Descriptions.Item>
          <Descriptions.Item label="Địa chỉ">{values.sender.address}</Descriptions.Item>
          <Descriptions.Item label="Quận/Huyện">{values.sender.district}</Descriptions.Item>
          <Descriptions.Item label="Tỉnh/TP">{values.sender.province}</Descriptions.Item>
          <Descriptions.Item label="SĐT">{values.sender.phone}</Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Receiver */}
      <Card size="small" style={{ marginBottom: 12 }}>
        {sectionHeader(t('bills.receiver'), 1)}
        <Descriptions column={1} size="small">
          <Descriptions.Item label="Họ tên">{values.receiver.name}</Descriptions.Item>
          <Descriptions.Item label="Địa chỉ">{values.receiver.address}</Descriptions.Item>
          <Descriptions.Item label="Quận/Huyện">{values.receiver.district}</Descriptions.Item>
          <Descriptions.Item label="Tỉnh/TP">{values.receiver.province}</Descriptions.Item>
          <Descriptions.Item label="SĐT">{values.receiver.phone}</Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Contents */}
      <Card size="small" style={{ marginBottom: 12 }}>
        {sectionHeader(t('bills.contents'), 2)}
        {values.contents.map((item, idx) => (
          <div
            key={idx}
            style={{
              marginBottom: 8,
              padding: '4px 0',
              borderBottom: idx < values.contents.length - 1 ? '1px solid #f0f0f0' : 'none',
            }}
          >
            <Text strong>{item.description || `Gói ${idx + 1}`}</Text>
            <div style={{ fontSize: 13, color: '#666' }}>
              SL: {item.quantity} — {item.weight_kg} kg
              {item.length_cm && ` — ${item.length_cm}×${item.width_cm}×${item.height_cm} cm`}
            </div>
          </div>
        ))}
      </Card>

      {/* Service */}
      <Card size="small" style={{ marginBottom: 12 }}>
        {sectionHeader(`${t('bills.cargoType')} & ${t('bills.serviceTier')}`, 3)}
        <Descriptions column={1} size="small">
          <Descriptions.Item label={t('bills.cargoType')}>
            {values.cargo_type === 'document' ? t('bills.document') : t('bills.goods')}
          </Descriptions.Item>
          <Descriptions.Item label={t('bills.serviceTier')}>
            {values.service_tier_code || '—'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Fees */}
      <Card size="small" style={{ marginBottom: 12 }}>
        {sectionHeader(t('bills.fees'), 4)}
        <Descriptions column={1} size="small">
          <Descriptions.Item label={t('bills.feeMain')}>
            {formatVND(values.fee.fee_main)}
          </Descriptions.Item>
          <Descriptions.Item label={t('bills.feeFuel')}>
            {formatVND(values.fee.fee_fuel_surcharge)}
          </Descriptions.Item>
          <Descriptions.Item label={t('bills.feeOther')}>
            {formatVND(values.fee.fee_other_surcharge)}
          </Descriptions.Item>
          <Descriptions.Item label={t('bills.feeVat')}>
            {formatVND(values.fee.fee_vat)}
          </Descriptions.Item>
        </Descriptions>
        <Divider style={{ margin: '8px 0' }} />
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Text strong>{t('bills.feeTotal')}:</Text>
          <Text strong style={{ fontSize: 16, color: '#C41E3A' }}>
            {formatVND(values.fee.fee_total)}
          </Text>
        </div>
        <div style={{ marginTop: 8 }}>
          <Text type="secondary">{t('bills.payer')}: </Text>
          <Text>
            {values.payer === 'sender' ? t('bills.payerSender') : t('bills.payerReceiver')}
          </Text>
        </div>
      </Card>
    </div>
  );
}

export default ConfirmStep;
