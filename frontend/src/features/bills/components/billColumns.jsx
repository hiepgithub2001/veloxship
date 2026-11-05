/**
 * Bill table columns — ONE definition shared by the bill list and the customer
 * detail's bill history, so both tables read as the same table (same columns,
 * widths, formats and row behaviour).
 */
import { Button, Space, Tag, Typography } from 'antd';
import { EyeOutlined, PrinterOutlined } from '@ant-design/icons';

import { ImagePreviewGroup } from '../../../components/common/ImagePreviewGroup';
import { formatVND, formatViDate } from '../../../lib/format';
import { t } from '../../../i18n/vi';

export const BILL_STATUS_COLORS = {
  created: 'blue',
  picked_up: 'cyan',
  in_transit: 'orange',
  delivered: 'green',
  returned: 'purple',
  cancelled: 'red',
};

/** Column keys the user may show/hide from the list. `index` and `actions` stay fixed. */
export const TOGGLEABLE_BILL_COLUMN_KEYS = [
  'created_at',
  'tracking_number',
  'sender_name',
  'sender_province',
  'cod_amount',
  'fee_total',
  'status',
  'receiver_name',
  'images',
  'receiver_phone',
  'receiver_address',
  'note',
];

export const formatBillAddress = (party) =>
  [party?.address_detail, party?.ward_name, party?.province_name].filter(Boolean).join(', ');

/**
 * Build the shared bill table columns.
 *
 * @param {object} options
 * @param {number} [options.offset] - rows already displayed before this page (for STT).
 * @param {(id: number) => void} [options.onView] - adds the view action + row click target.
 * @param {(id: number) => void} [options.onPrint] - adds the print action.
 */
export function buildBillColumns({ offset = 0, onView, onPrint } = {}) {
  const columns = [
    {
      title: t('bills.stt'),
      key: 'index',
      width: 60,
      render: (_, __, index) => offset + index + 1,
    },
    {
      title: t('bills.date'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 110,
      render: (date) => formatViDate(date),
    },
    {
      title: t('bills.trackingNumber'),
      dataIndex: 'tracking_number',
      key: 'tracking_number',
      width: 170,
      render: (text) => <Typography.Text strong>{text}</Typography.Text>,
    },
    {
      title: t('bills.sender'),
      dataIndex: ['sender', 'name'],
      key: 'sender_name',
      width: 160,
      ellipsis: true,
    },
    {
      title: t('bills.senderProvinceColumn'),
      dataIndex: ['sender', 'province_name'],
      key: 'sender_province',
      width: 130,
    },
    {
      title: t('bills.cod'),
      dataIndex: 'cod_amount',
      key: 'cod_amount',
      width: 120,
      render: (val) => (val ? formatVND(val) : '—'),
    },
    {
      title: t('bills.feeTotal'),
      dataIndex: 'fee_total',
      key: 'fee_total',
      width: 140,
      align: 'right',
      render: (value) => formatVND(value),
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      width: 150,
      render: (status) => (
        <Tag color={BILL_STATUS_COLORS[status] || 'default'}>{t(`status.${status}`)}</Tag>
      ),
    },
    {
      title: t('bills.receiver'),
      dataIndex: ['receiver', 'name'],
      key: 'receiver_name',
      width: 160,
    },
    {
      title: t('bills.imagesColumn'),
      key: 'images',
      width: 90,
      render: (_, record) => {
        const images = (record.contents || []).flatMap((c) => c.images || []).filter(Boolean);
        return <ImagePreviewGroup images={images} />;
      },
    },
    {
      title: t('bills.receiverPhone'),
      dataIndex: ['receiver', 'phone'],
      key: 'receiver_phone',
      width: 140,
    },
    {
      title: t('bills.receiverAddress'),
      key: 'receiver_address',
      width: 220,
      ellipsis: true,
      render: (_, record) => formatBillAddress(record.receiver),
    },
    {
      title: t('bills.note'),
      dataIndex: 'note',
      key: 'note',
      width: 160,
      ellipsis: true,
      render: (text) => text || '—',
    },
  ];

  if (onView) {
    columns.push({
      title: t('common.actions'),
      key: 'actions',
      fixed: 'right',
      width: 100,
      render: (_, record) => (
        <Space size="middle">
          <Button type="text" icon={<EyeOutlined />} onClick={() => onView(record.id)} />
          {onPrint && (
            <Button
              type="text"
              icon={<PrinterOutlined />}
              onClick={(event) => {
                event.stopPropagation();
                onPrint(record.id);
              }}
            />
          )}
        </Space>
      ),
    });
  }

  return columns;
}
