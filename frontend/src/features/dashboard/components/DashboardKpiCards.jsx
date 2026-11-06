import {
  CheckCircleOutlined,
  DollarOutlined,
  FileTextOutlined,
  RiseOutlined,
  SyncOutlined,
  WalletOutlined,
} from '@ant-design/icons';
import { Card, Col, Row, Statistic } from 'antd';

import { formatVND } from '../../../lib/format';
import { t } from '../../../i18n/vi';

/**
 * Headline KPI cards. Money figures arrive as Decimal strings from the API and
 * are parsed before formatting.
 */
export function DashboardKpiCards({ kpis, loading }) {
  const k = kpis || {};
  const money = (value) => Number(value ?? 0);

  const items = [
    {
      key: 'total',
      title: t('dashboard.kpiTotalBills'),
      value: k.total_bills ?? 0,
      prefix: <FileTextOutlined />,
      hint: `${t('dashboard.today')}: ${k.bills_today ?? 0}`,
    },
    {
      key: 'inProgress',
      title: t('dashboard.kpiInProgress'),
      value: k.in_progress_bills ?? 0,
      prefix: <SyncOutlined />,
      hint: t('dashboard.inProgressHint'),
    },
    {
      key: 'delivered',
      title: t('dashboard.kpiDelivered'),
      value: k.delivered_bills ?? 0,
      prefix: <CheckCircleOutlined />,
      valueStyle: { color: 'var(--color-success)' },
      hint: `${t('dashboard.cancelled')}: ${k.cancelled_bills ?? 0} · ${t('dashboard.returned')}: ${k.returned_bills ?? 0}`,
    },
    {
      key: 'rate',
      title: t('dashboard.kpiDeliveryRate'),
      value: k.delivery_rate ?? 0,
      precision: 1,
      suffix: '%',
      prefix: <RiseOutlined />,
      hint: t('dashboard.deliveryRateHint'),
    },
    {
      key: 'revenue',
      title: t('dashboard.kpiRevenue'),
      value: money(k.revenue_total),
      formatter: (v) => formatVND(v),
      prefix: <DollarOutlined />,
      hint: t('dashboard.revenueHint'),
    },
    {
      key: 'cod',
      title: t('dashboard.kpiCod'),
      value: money(k.cod_total),
      formatter: (v) => formatVND(v),
      prefix: <WalletOutlined />,
      hint: t('dashboard.codHint'),
    },
  ];

  return (
    <Row gutter={[16, 16]}>
      {items.map((item) => (
        <Col key={item.key} xs={24} sm={12} xl={8}>
          <Card className="dashboard-kpi-card" size="small">
            <Statistic
              title={item.title}
              value={item.value}
              precision={item.precision}
              suffix={item.suffix}
              prefix={item.prefix}
              formatter={item.formatter}
              valueStyle={item.valueStyle}
              loading={loading}
            />
            {item.hint && <div className="dashboard-kpi-hint">{item.hint}</div>}
          </Card>
        </Col>
      ))}
    </Row>
  );
}
