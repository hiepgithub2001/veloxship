/**
 * Depot search bar — search input with debounce and is_active filter.
 */
import { useCallback, useRef } from 'react';
import { Input, Select, Space } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

const STATUS_OPTIONS = [
  { value: null, label: 'Tất cả' },
  { value: true, label: 'Hoạt động' },
  { value: false, label: 'Ngưng hoạt động' },
];

const DEBOUNCE_MS = 300;

export function DepotSearchBar({ onSearchChange, onFilterChange }) {
  const timerRef = useRef(null);

  const handleSearchInput = useCallback(
    (e) => {
      const value = e.target.value;
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      timerRef.current = setTimeout(() => {
        onSearchChange(value);
      }, DEBOUNCE_MS);
    },
    [onSearchChange],
  );

  const handleFilterChange = useCallback(
    (value) => {
      onFilterChange(value);
    },
    [onFilterChange],
  );

  return (
    <Space style={{ marginBottom: 16 }} wrap>
      <Input
        placeholder="Tìm kiếm theo tên hoặc mã bưu cục"
        prefix={<SearchOutlined />}
        allowClear
        onChange={handleSearchInput}
        style={{ width: 300 }}
      />
      <Select
        defaultValue={null}
        options={STATUS_OPTIONS}
        onChange={handleFilterChange}
        style={{ width: 180 }}
        placeholder="Trạng thái"
      />
    </Space>
  );
}

export default DepotSearchBar;
