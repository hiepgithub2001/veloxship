/**
 * Depot status badge — displays active/inactive status.
 */
import { Tag } from 'antd';

export function DepotStatusBadge({ isActive }) {
  return (
    <Tag color={isActive ? 'green' : 'red'}>
      {isActive ? 'Hoạt động' : 'Ngưng hoạt động'}
    </Tag>
  );
}

export default DepotStatusBadge;
