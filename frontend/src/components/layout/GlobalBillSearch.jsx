/**
 * Topbar search for finding a bill by tracking number, customer name, or phone.
 */
import { useEffect, useRef, useState } from 'react';
import { AutoComplete, Input, Spin, Typography } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { listBills } from '../../api/bills';
import { t } from '../../i18n/vi';

const { Text } = Typography;

export function GlobalBillSearch() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const requestId = useRef(0);

  useEffect(() => {
    const normalizedQuery = query.trim();
    const currentRequest = ++requestId.current;
    if (!normalizedQuery) {
      setOptions([]);
      setLoading(false);
      return undefined;
    }

    const timer = window.setTimeout(async () => {
      setLoading(true);
      try {
        const data = await listBills({ search: normalizedQuery, page: 1, page_size: 8 });
        if (currentRequest !== requestId.current) return;
        setOptions(
          data.items.map((bill) => ({
            value: bill.tracking_number,
            billId: bill.id,
            label: (
              <div className="global-bill-search-option">
                <Text strong>{bill.tracking_number}</Text>
                <Text type="secondary">
                  {bill.sender.name} ({bill.sender.phone || '—'}) → {bill.receiver.name} (
                  {bill.receiver.phone || '—'})
                </Text>
              </div>
            ),
          })),
        );
      } catch {
        if (currentRequest === requestId.current) setOptions([]);
      } finally {
        if (currentRequest === requestId.current) setLoading(false);
      }
    }, 250);

    return () => window.clearTimeout(timer);
  }, [query]);

  const selectBill = (_, option) => {
    if (!option?.billId) return;
    setQuery('');
    setOptions([]);
    navigate(`/phieu-gui/${option.billId}`);
  };

  return (
    <AutoComplete
      className="global-bill-search"
      value={query}
      options={options}
      onSearch={setQuery}
      onSelect={selectBill}
      filterOption={false}
      notFoundContent={query.trim() && !loading ? t('layout.globalSearchEmpty') : null}
      popupMatchSelectWidth={false}
    >
      <Input
        allowClear
        prefix={loading ? <Spin size="small" /> : <SearchOutlined />}
        placeholder={t('layout.globalSearchPlaceholder')}
        aria-label={t('layout.globalSearchHint')}
      />
    </AutoComplete>
  );
}

export default GlobalBillSearch;
