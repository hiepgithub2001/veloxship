import { useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button, Card, Space, Spin, Steps, Tag, Timeline, Typography, message } from 'antd';
import {
  ArrowLeftOutlined,
  FilePdfOutlined,
  PrinterOutlined,
  SwapOutlined,
} from '@ant-design/icons';
import { useReactToPrint } from 'react-to-print';
import {
  downloadBillPdf,
  getBill,
  getBillEvents,
  updateBill,
  updateStatus,
} from '../../../api/bills';
import { BillCommercialEditor } from '../components/BillCommercialEditor';
import { BillPartyEditor } from '../components/BillPartyEditor';
import { StatusUpdateDrawer } from '../components/StatusUpdateDrawer';
import { BillPrintView } from '../components/BillPrintView';
import { formatVND, formatViDateTime } from '../../../lib/format';
import { t } from '../../../i18n/vi';

const { Title, Text } = Typography;
const flow = ['created', 'picked_up', 'in_transit', 'delivered'];
const colors = {
  created: 'blue',
  picked_up: 'cyan',
  in_transit: 'orange',
  delivered: 'green',
  returned: 'purple',
  cancelled: 'red',
};
const terminal = new Set(['delivered', 'returned', 'cancelled']);
export function BillDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const printRef = useRef(null);
  const [statusOpen, setStatusOpen] = useState(false);
  const {
    data: bill,
    isLoading,
    error,
  } = useQuery({ queryKey: ['bill', id], queryFn: () => getBill(id) });
  const { data: events = { status_events: [], audit_events: [] } } = useQuery({
    queryKey: ['bill-events', id],
    queryFn: () => getBillEvents(id),
    enabled: Boolean(bill),
  });
  const refresh = () => {
    qc.invalidateQueries({ queryKey: ['bill', id] });
    qc.invalidateQueries({ queryKey: ['bill-events', id] });
  };
  const amendment = useMutation({
    mutationFn: (payload) => updateBill(id, { ...payload, expected_updated_at: bill.updated_at }),
    onSuccess: () => {
      message.success('Đã cập nhật thông tin phiếu gửi.');
      refresh();
    },
    onError: (e) => message.error(e.response?.data?.message || 'Không thể cập nhật phiếu gửi.'),
  });
  const status = useMutation({
    mutationFn: (payload) => updateStatus(id, payload),
    onSuccess: () => {
      message.success(t('bills.statusUpdateSuccess'));
      setStatusOpen(false);
      refresh();
    },
    onError: (e) => message.error(e.response?.data?.message || 'Không thể cập nhật trạng thái.'),
  });
  const print = useReactToPrint({ contentRef: printRef });
  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '40px auto' }} />;
  if (error || !bill)
    return (
      <Card>
        <Title level={4}>{t('bills.notFound')}</Title>
        <Button onClick={() => navigate('/phieu-gui')}>{t('common.back')}</Button>
      </Card>
    );
  const current = flow.indexOf(bill.status);
  const journeyItems =
    bill.status === 'cancelled' || bill.status === 'returned'
      ? [
          ...flow.slice(0, Math.max(current, 0) + 1).map((key) => ({ title: t(`status.${key}`) })),
          { title: t(`status.${bill.status}`), status: 'error' },
        ]
      : flow.map((key) => ({ title: t(`status.${key}`) }));
  return (
    <div className="bill-workspace">
      <Space wrap>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/phieu-gui')}>
          {t('common.back')}
        </Button>
        <Button type="primary" icon={<PrinterOutlined />} onClick={print}>
          {bill.print_count ? t('bills.reprint') : t('bills.print')}
        </Button>
        <Button icon={<FilePdfOutlined />} onClick={() => downloadBillPdf(bill.id)}>
          {t('bills.downloadPdf')}
        </Button>
        {!terminal.has(bill.status) && (
          <Button icon={<SwapOutlined />} onClick={() => setStatusOpen(true)}>
            {t('bills.updateStatus')}
          </Button>
        )}
      </Space>
      <Card className="bill-hero">
        <div className="bill-hero-meta">
          <div>
            <Title level={2} style={{ margin: 0 }}>
              {bill.tracking_number}
            </Title>
            <Text type="secondary">
              Tạo {formatViDateTime(bill.created_at)} · Cập nhật {formatViDateTime(bill.updated_at)}{' '}
              · Đã in {bill.print_count} lần
            </Text>
          </div>
          <div style={{ textAlign: 'right' }}>
            <Tag color={colors[bill.status]} style={{ fontSize: 14, padding: '4px 12px' }}>
              {t(`status.${bill.status}`)}
            </Tag>
            <div>
              <Text strong>{formatVND(bill.fee.fee_total)}</Text> · COD {formatVND(bill.cod_amount)}
            </div>
          </div>
        </div>
        <Steps
          className="bill-status-steps"
          size="small"
          current={current < 0 ? flow.length - 1 : current}
          status={terminal.has(bill.status) && bill.status !== 'delivered' ? 'error' : 'process'}
          items={journeyItems}
        />
      </Card>
      <Card>
        <div className="bill-block-heading">
          <div>
            <h3>Thông tin liên hệ</h3>
            <span>Người gửi và người nhận của phiếu này</span>
          </div>
        </div>
        <div className="bill-parties">
          <BillPartyEditor
            bill={bill}
            side="sender"
            saving={amendment.isPending}
            onSave={amendment.mutate}
          />
          <BillPartyEditor
            bill={bill}
            side="receiver"
            saving={amendment.isPending}
            onSave={amendment.mutate}
          />
        </div>
      </Card>
      <Card>
        <BillCommercialEditor bill={bill} saving={amendment.isPending} onSave={amendment.mutate} />
      </Card>
      <Card>
        <div className="bill-block-heading">
          <div>
            <h3>Cước phí & thanh toán</h3>
            <span>Trình bày theo bố cục phiếu gửi</span>
          </div>
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
          <div className="bill-fee-list">
            {[
              [t('bills.feeMain'), bill.fee.fee_main],
              [t('bills.feeInsurance'), bill.fee.fee_insurance],
              [t('bills.feeOther'), bill.fee.fee_other],
              [t('bills.feeVat'), bill.fee.fee_vat],
            ].map(([label, amount]) => (
              <div className="bill-fee-line" key={label}>
                <span>{label}</span>
                <strong>{formatVND(amount)}</strong>
              </div>
            ))}
            <div className="bill-fee-line bill-fee-total">
              <strong>{t('bills.feeTotal')}</strong>
              <strong>{formatVND(bill.fee.fee_total)}</strong>
            </div>
          </div>
        </div>
      </Card>
      <Card>
        <div className="bill-block-heading">
          <div>
            <h3>Hành trình vận đơn</h3>
            <span>Các lần thay đổi trạng thái</span>
          </div>
        </div>
        <Timeline
          items={events.status_events.map((event) => ({
            color: colors[event.to_status],
            children: (
              <>
                <Text strong>{t(`status.${event.to_status}`)}</Text>
                <br />
                <Text type="secondary">
                  {formatViDateTime(event.created_at)} ·{' '}
                  {event.actor_name || `NV #${event.changed_by}`}
                </Text>
                {event.note && <div>{event.note}</div>}
              </>
            ),
          }))}
        />
      </Card>
      <Card>
        <div className="bill-block-heading">
          <div>
            <h3>{t('bills.auditLog')}</h3>
            <span>Chỉnh sửa, in lại và thao tác hệ thống</span>
          </div>
        </div>
        <Timeline
          items={events.audit_events.map((event) => ({
            children: (
              <>
                <Text strong>{event.action}</Text>
                <br />
                <Text type="secondary">
                  {formatViDateTime(event.created_at)} · {event.actor_name || 'Hệ thống'}
                </Text>
                {event.details?.reason && <div>Lý do: {event.details.reason}</div>}
              </>
            ),
          }))}
        />
      </Card>
      <StatusUpdateDrawer
        bill={bill}
        open={statusOpen}
        onClose={() => setStatusOpen(false)}
        saving={status.isPending}
        onSubmit={status.mutate}
      />
      <div ref={printRef} style={{ position: 'absolute', left: '-9999px' }}>
        <BillPrintView bill={bill} />
      </div>
    </div>
  );
}
export default BillDetailPage;
