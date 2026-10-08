/**
 * Vehicle filters — status and vehicle type filter dropdowns.
 */
import { Col, Row, Select } from 'antd';

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

export function VehicleFilters({ status, vehicleType, onStatusChange, onVehicleTypeChange }) {
  return (
    <Row gutter={[12, 12]}>
      <Col xs={12}>
        <Select
          value={status}
          options={STATUS_OPTIONS}
          onChange={onStatusChange}
          allowClear
          placeholder="Trạng thái"
          style={{ width: '100%' }}
        />
      </Col>
      <Col xs={12}>
        <Select
          value={vehicleType}
          options={VEHICLE_TYPE_OPTIONS}
          onChange={onVehicleTypeChange}
          allowClear
          placeholder="Loại xe"
          style={{ width: '100%' }}
        />
      </Col>
    </Row>
  );
}

export default VehicleFilters;
