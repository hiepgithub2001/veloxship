/**
 * EmployeeSearchBar — search + filters for the staff list.
 */
import { useRef, useCallback } from 'react';
import { Col, Input, Row, Select } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';

import { getRoles } from '../../../api/permissions';

const ACTIVE_OPTIONS = [
  { value: true, label: 'Hoạt động' },
  { value: false, label: 'Bị khóa' },
];

export function EmployeeSearchBar({
  search,
  onSearchChange,
  role,
  onRoleChange,
  isActive,
  onIsActiveChange,
}) {
  const timerRef = useRef(null);

  const { data: roles = [] } = useQuery({
    queryKey: ['roles'],
    queryFn: getRoles,
  });

  const handleSearch = useCallback(
    (e) => {
      clearTimeout(timerRef.current);
      const value = e.target.value;
      timerRef.current = setTimeout(() => onSearchChange(value), 300);
    },
    [onSearchChange],
  );

  return (
    <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
      <Col xs={24} sm={12} md={8}>
        <Input
          allowClear
          prefix={<SearchOutlined />}
          placeholder="Tìm theo tên, SĐT hoặc tên đăng nhập..."
          defaultValue={search}
          onChange={handleSearch}
          style={{ width: '100%' }}
        />
      </Col>
      <Col xs={12} sm={12} md={8}>
        <Select
          allowClear
          placeholder="Vai trò"
          value={role}
          onChange={(v) => onRoleChange(v)}
          style={{ width: '100%' }}
          options={(roles || []).map((r) => ({ value: r.code, label: r.name }))}
        />
      </Col>
      <Col xs={12} sm={12} md={8}>
        <Select
          allowClear
          placeholder="Trạng thái"
          value={isActive}
          onChange={(v) => onIsActiveChange(v)}
          style={{ width: '100%' }}
          options={ACTIVE_OPTIONS}
        />
      </Col>
    </Row>
  );
}

export default EmployeeSearchBar;
