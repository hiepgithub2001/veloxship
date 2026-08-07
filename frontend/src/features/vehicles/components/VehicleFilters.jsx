/**
 * Vehicle filters — status and vehicle type filter dropdowns.
 */
import { Select, Space } from 'antd';

const STATUS_OPTIONS = [
  { value: null, label: 'Tất cả' },
  { value: 'active', label: 'Hoạt động' },
  { value: 'inactive', label: 'Ngừng hoạt động' },
  { value: 'maintenance', label: 'Bảo trì' },
];

const VEHICLE_TYPE_OPTIONS = [
  { value: null, label: 'Tất cả' },
  { value: 'motorcycle', label: 'Xe máy' },
  { value: 'truck', label: 'Xe tải' },
];

export function VehicleFilters({
  status,
  vehicleType,
  onStatusChange,
  onVehicleTypeChange,
}) {
  return (
    <Space style={{ marginBottom: 16 }} wrap>
      <Select
        value={status}
        options={STATUS_OPTIONS}
        onChange={onStatusChange}
        allowClear
        placeholder="Trạng thái"
        style={{ width: 180 }}
      />
      <Select
        value={vehicleType}
        options={VEHICLE_TYPE_OPTIONS}
        onChange={onVehicleTypeChange}
        allowClear
        placeholder="Loại xe"
        style={{ width: 180 }}
      />
    </Space>
  );
}

export default VehicleFilters;
