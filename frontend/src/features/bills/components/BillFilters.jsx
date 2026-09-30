/**
 * Bill filters — status, creation-date range, tracking number, sender and
 * receiver search, wrapped in a white card. The text filters only apply when
 * the user presses "Tìm kiếm" (or Enter); status/date apply immediately.
 */
import { useEffect, useState } from 'react';
import { Button, Card, DatePicker, Input, Select, Space } from 'antd';
import { SearchOutlined, UndoOutlined } from '@ant-design/icons';
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

export function BillFilters({
  status,
  dateRange,
  tracking,
  sender,
  receiver,
  onStatusChange,
  onDateRangeChange,
  onSearch,
  onReset,
}) {
  const [draft, setDraft] = useState({
    tracking: tracking || '',
    sender: sender || '',
    receiver: receiver || '',
  });

  // Sync the draft when applied values change (back navigation, reset, ...).
  useEffect(() => {
    setDraft({
      tracking: tracking || '',
      sender: sender || '',
      receiver: receiver || '',
    });
  }, [tracking, sender, receiver]);

  const setField = (key) => (event) =>
    setDraft((prev) => ({ ...prev, [key]: event.target.value }));

  const handleSearch = () => onSearch(draft);

  const handleReset = () => {
    setDraft({ tracking: '', sender: '', receiver: '' });
    onReset();
  };

  return (
    <Card style={{ marginBottom: 16 }} styles={{ body: { padding: 16 } }}>
      <Space wrap size="middle">
        <Input
          value={draft.tracking}
          onChange={setField('tracking')}
          onPressEnter={handleSearch}
          allowClear
          placeholder={t('bills.trackingFilter')}
          style={{ width: 180 }}
        />
        <Input
          value={draft.sender}
          onChange={setField('sender')}
          onPressEnter={handleSearch}
          allowClear
          placeholder={t('bills.senderFilter')}
          style={{ width: 180 }}
        />
        <Input
          value={draft.receiver}
          onChange={setField('receiver')}
          onPressEnter={handleSearch}
          allowClear
          placeholder={t('bills.receiverFilter')}
          style={{ width: 180 }}
        />
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
        <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
          {t('common.search')}
        </Button>
        <Button icon={<UndoOutlined />} onClick={handleReset}>
          {t('bills.resetFilters')}
        </Button>
      </Space>
    </Card>
  );
}

export default BillFilters;
