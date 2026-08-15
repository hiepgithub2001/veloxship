/**
 * VehicleFormModal — Modal form for creating and editing vehicles.
 * Uses react-hook-form + zod + Ant Design Modal.
 */
import { useEffect } from 'react';
import { Modal, Form, Input, InputNumber, Select, message } from 'antd';
import UserSelect from '../../../components/common/UserSelect';
import DepotSelect from '../../../components/common/DepotSelect';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { vehicleFormSchema } from '../schema';
import { createVehicle, updateVehicle } from '../../../api/vehicles';
import ImageUpload from '../../../components/common/ImageUpload';

/**
 * @param {object} props
 * @param {boolean} props.open - Whether modal is visible
 * @param {function} props.onClose - Close handler
 * @param {object|null} props.vehicle - Null for create mode, vehicle object for edit mode
 * @param {function} props.onSuccess - Called after successful create/update
 */
export function VehicleFormModal({ open, onClose, vehicle, onSuccess }) {
  const isEdit = Boolean(vehicle);
  const queryClient = useQueryClient();

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(vehicleFormSchema),
    defaultValues: {
      license_plate: '',
      vehicle_type: undefined,
      max_weight_kg: undefined,
      max_volume_m3: undefined,
      status: 'active',
      driver_id: null,
      latest_depot_id: null,
      images: [],
    },
  });

  // Reset form when modal opens or vehicle changes
  useEffect(() => {
    if (open) {
      if (isEdit && vehicle) {
        reset({
          license_plate: vehicle.license_plate || '',
          vehicle_type: vehicle.vehicle_type || undefined,
          max_weight_kg: vehicle.max_weight_kg || undefined,
          max_volume_m3: vehicle.max_volume_m3 || undefined,
          status: vehicle.status || 'active',
          driver_id: vehicle.driver_id ?? null,
          latest_depot_id: vehicle.latest_depot_id ?? null,
          images: vehicle.images || [],
        });
      } else {
        reset({
          license_plate: '',
          vehicle_type: undefined,
          max_weight_kg: undefined,
          max_volume_m3: undefined,
          status: 'active',
          driver_id: null,
          latest_depot_id: null,
          images: [],
        });
      }
    }
  }, [open, vehicle, isEdit, reset]);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data) => createVehicle(data),
    onSuccess: () => {
      message.success('Đăng ký xe thành công');
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
      onSuccess?.();
      onClose();
    },
    onError: (err) => {
      message.error(err.response?.data?.message || 'Lỗi kết nối, vui lòng thử lại');
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data) => updateVehicle(vehicle.id, data),
    onSuccess: () => {
      message.success('Cập nhật xe thành công');
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
      onSuccess?.();
      onClose();
    },
    onError: (err) => {
      message.error(err.response?.data?.message || 'Lỗi kết nối, vui lòng thử lại');
    },
  });

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  const onSubmit = (formData) => {
    if (isEdit) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData);
    }
  };

  return (
    <Modal
      title={isEdit ? 'Sửa thông tin xe' : 'Đăng ký xe mới'}
      open={open}
      onOk={handleSubmit(onSubmit)}
      onCancel={onClose}
      okText={isEdit ? 'Cập nhật' : 'Đăng ký'}
      cancelText="Hủy"
      confirmLoading={isSubmitting}
      destroyOnClose
      maskClosable={false}
    >
      <Form layout="vertical" style={{ marginTop: 16 }}>
        {/* Biển số xe */}
        <Form.Item
          label="Biển số xe"
          validateStatus={errors.license_plate ? 'error' : ''}
          help={errors.license_plate?.message}
          required
        >
          <Controller
            name="license_plate"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                placeholder="VD: 51F-123.45"
                disabled={isEdit}
              />
            )}
          />
        </Form.Item>

        {/* Loại xe */}
        <Form.Item
          label="Loại xe"
          validateStatus={errors.vehicle_type ? 'error' : ''}
          help={errors.vehicle_type?.message}
          required
        >
          <Controller
            name="vehicle_type"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                placeholder="Chọn loại xe"
                options={[
                  { value: 'motorcycle', label: 'Xe máy' },
                  { value: 'truck', label: 'Xe tải' },
                ]}
              />
            )}
          />
        </Form.Item>

        {/* Tải trọng */}
        <Form.Item
          label="Tải trọng (kg)"
          validateStatus={errors.max_weight_kg ? 'error' : ''}
          help={errors.max_weight_kg?.message}
          required
        >
          <Controller
            name="max_weight_kg"
            control={control}
            render={({ field }) => (
              <InputNumber
                {...field}
                placeholder="VD: 500"
                min={0}
                style={{ width: '100%' }}
              />
            )}
          />
        </Form.Item>

        {/* Thể tích */}
        <Form.Item
          label="Thể tích (m³)"
          validateStatus={errors.max_volume_m3 ? 'error' : ''}
          help={errors.max_volume_m3?.message}
          required
        >
          <Controller
            name="max_volume_m3"
            control={control}
            render={({ field }) => (
              <InputNumber
                {...field}
                placeholder="VD: 2.5"
                min={0}
                step={0.1}
                style={{ width: '100%' }}
              />
            )}
          />
        </Form.Item>

        {/* Trạng thái */}
        <Form.Item
          label="Trạng thái"
          validateStatus={errors.status ? 'error' : ''}
          help={errors.status?.message}
        >
          <Controller
            name="status"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                placeholder="Chọn trạng thái"
                options={[
                  { value: 'active', label: 'Hoạt động' },
                  { value: 'inactive', label: 'Ngừng hoạt động' },
                  { value: 'maintenance', label: 'Bảo trì' },
                ]}
              />
            )}
          />
        </Form.Item>

        {/* Tài xế phụ trách */}
        <Form.Item
          label="Tài xế phụ trách"
          validateStatus={errors.driver_id ? 'error' : ''}
          help={errors.driver_id?.message}
        >
          <Controller
            name="driver_id"
            control={control}
            render={({ field }) => (
              <UserSelect
                value={field.value}
                onChange={field.onChange}
                role="shipper"
                placeholder="Chọn tài xế (tùy chọn)"
                style={{ width: '100%' }}
              />
            )}
          />
        </Form.Item>

        {/* Bưu cục hiện tại */}
        <Form.Item
          label="Bưu cục hiện tại"
          validateStatus={errors.latest_depot_id ? 'error' : ''}
          help={errors.latest_depot_id?.message}
        >
          <Controller
            name="latest_depot_id"
            control={control}
            render={({ field }) => (
              <DepotSelect
                value={field.value}
                onChange={field.onChange}
                placeholder="Chọn bưu cục (tùy chọn)"
                style={{ width: '100%' }}
              />
            )}
          />
        </Form.Item>
        <Form.Item
          label="Hình ảnh xe (tối đa 5)"
          validateStatus={errors.images ? 'error' : ''}
          help={errors.images?.message}
        >
          <Controller
            name="images"
            control={control}
            render={({ field }) => (
              <ImageUpload
                value={field.value}
                onChange={field.onChange}
                maxCount={5}
              />
            )}
          />
        </Form.Item>
      </Form>
    </Modal>
  );
}

export default VehicleFormModal;
