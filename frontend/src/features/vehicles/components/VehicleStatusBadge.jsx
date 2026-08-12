import { Tag } from 'antd';

const STATUS_CONFIG = {
  active: { color: 'green', label: 'Hoạt động' },
  inactive: { color: 'default', label: 'Ngừng hoạt động' },
  maintenance: { color: 'orange', label: 'Bảo trì' },
};

export default function VehicleStatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.inactive;
  return <Tag color={config.color}>{config.label}</Tag>;
}
