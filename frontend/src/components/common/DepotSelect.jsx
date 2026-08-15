/**
 * DepotSelect — Searchable depot select using Ant Design Select.
 * Fetches depots from the API with debounced search.
 */
import { useState, useMemo, useRef, useCallback } from 'react';
import { Select, Spin } from 'antd';
import { useQuery } from '@tanstack/react-query';

import { getDepots } from '../../api/depots';

/**
 * @param {object} props
 * @param {number|null} props.value - Selected depot ID
 * @param {function} props.onChange - Change handler (receives depot ID or null)
 * @param {string} [props.placeholder]
 * @param {boolean} [props.disabled]
 * @param {boolean} [props.allowClear]
 * @param {object} [props.style]
 */
export default function DepotSelect({
  value,
  onChange,
  placeholder = 'Chọn bưu cục',
  disabled = false,
  allowClear = true,
  style,
  ...rest
}) {
  const [search, setSearch] = useState('');
  const timerRef = useRef(null);

  const { data, isLoading } = useQuery({
    queryKey: ['depots-select', search],
    queryFn: () => getDepots({ search: search || undefined, isActive: true }),
    staleTime: 30_000,
  });

  const options = useMemo(() => {
    if (!data?.items) return [];
    return data.items.map((depot) => ({
      value: depot.id,
      label: `${depot.name} (${depot.code})`,
    }));
  }, [data]);

  const handleSearch = useCallback((val) => {
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setSearch(val), 300);
  }, []);

  return (
    <Select
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      allowClear={allowClear}
      style={style}
      showSearch
      filterOption={false}
      onSearch={handleSearch}
      notFoundContent={isLoading ? <Spin size="small" /> : 'Không tìm thấy'}
      options={options}
      {...rest}
    />
  );
}
