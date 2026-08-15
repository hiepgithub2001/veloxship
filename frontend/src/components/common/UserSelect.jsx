/**
 * UserSelect — Searchable user select using Ant Design Select.
 * Fetches users from the API with debounced search.
 */
import { useState, useMemo, useRef, useCallback } from 'react';
import { Select, Spin } from 'antd';
import { useQuery } from '@tanstack/react-query';

import { getUsers } from '../../api/users';

/**
 * @param {object} props
 * @param {number|null} props.value - Selected user ID
 * @param {function} props.onChange - Change handler (receives user ID or null)
 * @param {string} [props.role] - Optional role filter (e.g. 'shipper')
 * @param {string} [props.placeholder]
 * @param {boolean} [props.disabled]
 * @param {boolean} [props.allowClear]
 * @param {object} [props.style]
 */
export default function UserSelect({
  value,
  onChange,
  role,
  placeholder = 'Chọn nhân viên',
  disabled = false,
  allowClear = true,
  style,
  ...rest
}) {
  const [search, setSearch] = useState('');
  const timerRef = useRef(null);

  const { data, isLoading } = useQuery({
    queryKey: ['users-select', search, role],
    queryFn: () => getUsers({ search: search || undefined, role }),
    staleTime: 30_000,
  });

  const options = useMemo(() => {
    if (!data?.items) return [];
    return data.items.map((user) => ({
      value: user.id,
      label: `${user.full_name} (${user.username})`,
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
