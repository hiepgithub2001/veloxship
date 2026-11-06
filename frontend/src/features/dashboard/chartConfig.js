/**
 * Pure chart-configuration builders for the dashboard.
 *
 * Everything here is a plain function returning the config object expected by
 * `@ant-design/plots` v2 (G2 5). Keeping them pure means the unit tests can
 * assert the shape, colours and formatting without rendering a canvas.
 */
import dayjs from 'dayjs';

import { BILL_STATUS_HEX } from '../../lib/billStatus';
import { formatVND, formatVNDCompact } from '../../lib/format';
import { t } from '../../i18n/vi';
import { brandColors } from '../../styles/theme';

/** Coerce an API value (money strings included) to a finite number, else 0. */
export function toNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function dayLabel(value) {
  return dayjs(value).format('DD/MM');
}

function dayTitle(value) {
  return dayjs(value).format('DD/MM/YYYY');
}

function truncate(text, max = 18) {
  const s = String(text ?? '');
  return s.length > max ? `${s.slice(0, max - 1)}…` : s;
}

/** Build the "bills created per day" line chart config. */
export function buildBillsTrendConfig(daily) {
  const data = (daily || []).map((d) => ({ date: d.date, value: d.bills }));
  return {
    data,
    xField: 'date',
    yField: 'value',
    shapeField: 'smooth',
    style: { lineWidth: 2, stroke: brandColors.primary },
    point:
      data.length <= 30
        ? { shapeField: 'circle', sizeField: 3, style: { fill: brandColors.primary } }
        : false,
    scale: { y: { domainMin: 0, nice: true } },
    axis: {
      x: { labelFormatter: dayLabel },
      y: { labelFormatter: (v) => `${v}` },
    },
    tooltip: {
      title: (d) => dayTitle(d.date),
      items: [
        {
          channel: 'y',
          name: t('dashboard.seriesBills'),
          valueFormatter: (v) => `${v} ${t('dashboard.unitBills')}`,
        },
      ],
    },
  };
}

/** Build the "revenue per day" column chart config. */
export function buildRevenueTrendConfig(daily) {
  const data = (daily || []).map((d) => ({ date: d.date, value: toNumber(d.revenue) }));
  return {
    data,
    xField: 'date',
    yField: 'value',
    style: { fill: brandColors.primary, radiusTopLeft: 4, radiusTopRight: 4 },
    scale: { y: { nice: true } },
    axis: {
      x: { labelFormatter: dayLabel },
      y: { labelFormatter: (v) => formatVNDCompact(v) },
    },
    tooltip: {
      title: (d) => dayTitle(d.date),
      items: [
        {
          channel: 'y',
          name: t('dashboard.kpiRevenue'),
          valueFormatter: (v) => formatVND(v),
        },
      ],
    },
  };
}

/** Build the status-distribution doughnut chart config (zero counts hidden). */
export function buildStatusPieConfig(statusCounts) {
  const data = (statusCounts || [])
    .filter((s) => s.count > 0)
    .map((s) => ({ label: t(`status.${s.status}`), value: s.count, status: s.status }));
  return {
    data,
    angleField: 'value',
    colorField: 'label',
    innerRadius: 0.6,
    scale: {
      color: {
        domain: data.map((d) => d.label),
        range: data.map((d) => BILL_STATUS_HEX[d.status] || brandColors.primary),
      },
    },
    legend: { color: { position: 'right', title: false } },
  };
}

/** Map destination rows into `{province_code: count}` for the choropleth. */
export function provinceCountById(destinations) {
  return Object.fromEntries((destinations || []).map((d) => [d.province_code, d.count]));
}

function hexToRgb(hex) {
  const h = hex.replace('#', '');
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
}

function interpolateHex(from, to, t) {
  const a = hexToRgb(from);
  const b = hexToRgb(to);
  const rgb = a.map((v, i) => Math.round(v + (b[i] - v) * t));
  return `#${rgb.map((v) => v.toString(16).padStart(2, '0')).join('')}`;
}

/** Map a province count onto a light→brand ramp (0 → neutral grey). */
export function scaleProvinceColor(count, max) {
  const value = toNumber(count);
  if (value <= 0) return '#EEF0F2';
  const t = Math.min(1, value / Math.max(1, toNumber(max)));
  return interpolateHex('#FCE8EC', brandColors.primary, t);
}

/** Build the top-destination horizontal bar chart config. */
export function buildTopDestinationsBarConfig(destinations, { selectedCode } = {}) {
  const data = (destinations || [])
    .filter((d) => d.count > 0)
    .sort((a, b) => b.count - a.count || a.province_name.localeCompare(b.province_name))
    .slice(0, 10)
    .map((d) => ({
      province_name: truncate(d.province_name),
      count: d.count,
      province_code: d.province_code,
    }));
  return {
    data,
    xField: 'province_name',
    yField: 'count',
    sort: { reverse: true },
    style: {
      radiusTopRight: 4,
      radiusBottomRight: 4,
      fill: (d) => (d.province_code === selectedCode ? brandColors.primaryActive : brandColors.primary),
    },
    axis: {
      y: { labelFormatter: (v) => `${v}` },
    },
    tooltip: {
      items: [
        {
          channel: 'y',
          name: t('dashboard.seriesBills'),
          valueFormatter: (v) => `${v} ${t('dashboard.unitBills')}`,
        },
      ],
    },
  };
}
