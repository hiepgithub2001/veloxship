/**
 * Bill filters — status dropdown and creation-date range picker.
 */
import { DatePicker, Select, Space } from 'antd';
import { t } from '../../../i18n/vi';

const { RangePicker } = DatePicker;

const STATUS_OPTIONS = [
  'created',
  'picked_up',
  'in_transit',
  'delivered',
  'returned',
  'cancelled',
].map((value) => ({ value, label: t(`status.${value}`) }));

export function BillFilters({ status, dateRange, onStatusChange, onDateRangeChange }) {
  return (
    <Space wrap style={{ marginBottom: 16 }}>
      <Select
        value={status}
        options={STATUS_OPTIONS}
        onChange={onStatusChange}
        allowClear
        placeholder={t('bills.statusFilter')}
        style={{ width: 180 }}
      />
      <RangePicker
        value={dateRange}
        onChange={onDateRangeChange}
        placeholder={t('bills.dateRangePlaceholder')}
      />
    </Space>
  );
}

export default BillFilters;
