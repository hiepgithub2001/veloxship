/**
 * Bill detail page — shows full bill info with status timeline and print action.
 */
import { useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Button, Card, Descriptions, Space, Spin, Steps, Tag, Typography,
} from 'antd';
import { ArrowLeftOutlined, PrinterOutlined, FilePdfOutlined } from '@ant-design/icons';
import { useReactToPrint } from 'react-to-print';

import { getBill, downloadBillPdf } from '../../../api/bills';
import { BillPrintView } from '../components/BillPrintView';
import { formatVND, formatWeight, formatViDateTime } from '../../../lib/format';
import { t } from '../../../i18n/vi';

const { Title, Text } = Typography;

const statusColor = {
  da_tao: 'blue',
  da_lay_hang: 'cyan',
  dang_van_chuyen: 'orange',
  da_giao: 'green',
  hoan_tra: 'purple',
  huy: 'red',
};

export function BillDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const printRef = useRef(null);

  const { data: bill, isLoading, error } = useQuery({
    queryKey: ['bill', id],
    queryFn: () => getBill(id),
  });

  const handlePrint = useReactToPrint({ contentRef: printRef });

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '40px auto' }} />;
  if (error || !bill) {
    return (
      <Card>
        <Title level={4}>{t('bills.notFound')}</Title>
        <Button onClick={() => navigate('/phieu-gui')}>{t('common.back')}</Button>
      </Card>
    );
  }

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/phieu-gui')}>
          {t('common.back')}
        </Button>
        <Button type="primary" icon={<PrinterOutlined />} onClick={handlePrint}>
          {t('bills.print')}
        </Button>
        <Button icon={<FilePdfOutlined />} onClick={() => downloadBillPdf(bill.id)}>
          {t('bills.downloadPdf')}
        </Button>
      </Space>

      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>{bill.tracking_number}</Title>
          <Tag color={statusColor[bill.status]} style={{ fontSize: 14, padding: '4px 12px' }}>
            {t(`status.${bill.status}`)}
          </Tag>
        </div>

        <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
          <Card type="inner" title={t('bills.sender')} style={{ flex: 1 }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Họ tên">{bill.sender.name}</Descriptions.Item>
              <Descriptions.Item label="Địa chỉ">{bill.sender.address}</Descriptions.Item>
              <Descriptions.Item label="Quận/Huyện">{bill.sender.district}</Descriptions.Item>
              <Descriptions.Item label="Tỉnh/TP">{bill.sender.province}</Descriptions.Item>
              <Descriptions.Item label="SĐT">{bill.sender.phone}</Descriptions.Item>
            </Descriptions>
          </Card>
          <Card type="inner" title={t('bills.receiver')} style={{ flex: 1 }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Họ tên">{bill.receiver.name}</Descriptions.Item>
              <Descriptions.Item label="Địa chỉ">{bill.receiver.address}</Descriptions.Item>
              <Descriptions.Item label="Quận/Huyện">{bill.receiver.district}</Descriptions.Item>
              <Descriptions.Item label="Tỉnh/TP">{bill.receiver.province}</Descriptions.Item>
              <Descriptions.Item label="SĐT">{bill.receiver.phone}</Descriptions.Item>
            </Descriptions>
          </Card>
        </div>

        <Card type="inner" title={t('bills.fees')} style={{ marginBottom: 16 }}>
          <Descriptions column={2} size="small">
            <Descriptions.Item label={t('bills.feeMain')}>{formatVND(bill.fee.fee_main)}</Descriptions.Item>
            <Descriptions.Item label={t('bills.feeFuel')}>{formatVND(bill.fee.fee_fuel_surcharge)}</Descriptions.Item>
            <Descriptions.Item label={t('bills.feeOther')}>{formatVND(bill.fee.fee_other_surcharge)}</Descriptions.Item>
            <Descriptions.Item label={t('bills.feeVat')}>{formatVND(bill.fee.fee_vat)}</Descriptions.Item>
          </Descriptions>
          <div style={{ textAlign: 'right', marginTop: 8 }}>
            <Text strong style={{ fontSize: 16, color: '#C41E3A' }}>
              {t('bills.feeTotal')}: {formatVND(bill.fee.fee_total)}
            </Text>
          </div>
        </Card>

        <Card type="inner" title={t('bills.auditLog')} style={{ marginBottom: 16 }}>
          <Descriptions column={2} size="small">
            <Descriptions.Item label={t('common.createdAt')}>{formatViDateTime(bill.created_at)}</Descriptions.Item>
            <Descriptions.Item label={t('common.updatedAt')}>{formatViDateTime(bill.updated_at)}</Descriptions.Item>
            <Descriptions.Item label="Số lần in">{bill.print_count}</Descriptions.Item>
          </Descriptions>
        </Card>
      </Card>

      <div ref={printRef} style={{ position: 'absolute', left: '-9999px' }}>
        <BillPrintView bill={bill} />
      </div>
    </div>
  );
}

export default BillDetailPage;
