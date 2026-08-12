/**
 * Vehicle search bar — search input with 300ms debounce for filtering by license plate.
 */
import { useCallback, useRef } from 'react';
import { Input } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

const DEBOUNCE_MS = 300;

export function VehicleSearchBar({ onSearch, defaultValue }) {
  const timerRef = useRef(null);

  const handleSearchInput = useCallback(
    (e) => {
      const value = e.target.value;
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      timerRef.current = setTimeout(() => {
        onSearch(value);
      }, DEBOUNCE_MS);
    },
    [onSearch],
  );

  return (
    <Input
      placeholder="Tìm theo biển số xe..."
      prefix={<SearchOutlined />}
      allowClear
      defaultValue={defaultValue}
      onChange={handleSearchInput}
      style={{ width: 300 }}
    />
  );
}

export default VehicleSearchBar;
