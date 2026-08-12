/**
 * VehicleFormModal — Modal form for creating and editing vehicles.
 * Uses react-hook-form + zod + Ant Design Modal.
 */
import { useEffect, useMemo, useState } from 'react';
import { Modal, Form, Input, InputNumber, Select, message, Upload, Avatar } from 'antd';
import { CameraOutlined } from '@ant-design/icons';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../../auth/AuthContext';

import { vehicleFormSchema } from '../schema';
import { createVehicle, updateVehicle } from '../../../api/vehicles';

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
  const { accessToken } = useAuth();

  const [fileList, setFileList] = useState([]);
  const [uploading, setUploading] = useState(false);

  const API_BASE = useMemo(() => import.meta.env.VITE_API_BASE_URL || '/api/v1', []);

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
    },
  });

  // Cleanup object URLs on unmount
  useEffect(() => {
    return () => {
      fileList.forEach((f) => {
        if (f.url && f.url.startsWith('blob:')) URL.revokeObjectURL(f.url);
      });
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Build initial file list from existing vehicle images
  useEffect(() => {
    if (isEdit && vehicle?.image_urls?.length) {
      const existingFiles = vehicle.image_urls.map((key, idx) => ({
        uid: `existing-${idx}-${key}`,
        name: key.split('/').pop() || `image-${idx + 1}`,
        status: 'done',
        url: key,
        thumbUrl: undefined,
      }));
      setFileList(existingFiles);
    } else if (!isEdit) {
      setFileList([]);
    }
  }, [isEdit, vehicle]); // eslint-disable-line react-hooks/exhaustive-deps

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
        });
      }
    }
  }, [open, vehicle, isEdit, reset]);

  const handleUploadChange = ({ fileList: newFileList }) => {
    setFileList(newFileList);
  };

  const submitWithImages = async (formData) => {
    if (uploading) return;

    const pendingFiles = fileList.filter((f) => f.status === 'uploading');
    if (pendingFiles.length > 0) {
      message.warning('Vui lòng đợi tải ảnh hoàn tất');
      return;
    }

    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('license_plate', formData.license_plate || '');
      fd.append('vehicle_type', formData.vehicle_type || '');
      if (formData.max_weight_kg != null) fd.append('max_weight_kg', String(formData.max_weight_kg));
      if (formData.max_volume_m3 != null) fd.append('max_volume_m3', String(formData.max_volume_m3));
      fd.append('status', formData.status || 'active');
      if (formData.driver_id != null) fd.append('driver_id', String(formData.driver_id));
      if (formData.latest_depot_id != null) fd.append('latest_depot_id', String(formData.latest_depot_id));

      fileList.forEach((f) => {
        const raw = f.originFileObj || f;
        if (raw instanceof File) {
          fd.append('images', raw);
        }
      });

      const vehicleId = isEdit ? '/' + vehicle.id : '';
      const url = `${API_BASE}/vehicles${vehicleId}`;
      const res = await fetch(url, {
        method: isEdit ? 'PATCH' : 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        body: fd,
      });

      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.message || `HTTP ${res.status}`);
      }

      await res.json();
      message.success(isEdit ? 'Cập nhật xe thành công' : 'Đăng ký xe thành công');
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
      onSuccess?.();
      onClose();
    } catch (err) {
      message.error(err.message || 'Lỗi khi lưu thông tin xe');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Modal
      title={isEdit ? 'Sửa thông tin xe' : 'Đăng ký xe mới'}
      open={open}
      onOk={handleSubmit(submitWithImages)}
      onCancel={onClose}
      okText={isEdit ? 'Cập nhật' : 'Đăng ký'}
      cancelText="Hủy"
      confirmLoading={uploading}
      destroyOnClose
      maskClosable={false}
      width={720}
    >
      <Form layout="vertical" style={{ marginTop: 16 }}>
        {/* Ảnh xe */}
        <Form.Item label="Ảnh xe">
          <Upload.Dragger
            accept="image/*"
            multiple
            maxCount={10}
            listType="picture-card"
            fileList={fileList}
            onChange={handleUploadChange}
            beforeUpload={() => false}
            showUploadList={{
              showRemoveIcon: true,
              showPreviewIcon: true,
            }}
          >
            {fileList.length < 10 && (
              <div>
                <p style={{ fontSize: 14, margin: 0 }}>Tải ảnh lên</p>
                <p style={{ fontSize: 12, color: '#999' }}>Click hoặc kéo thả vào đây</p>
              </div>
            )}
          </Upload.Dragger>
        </Form.Item>

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

        {/* Mã tài xế */}
        <Form.Item
          label="Mã tài xế"
          validateStatus={errors.driver_id ? 'error' : ''}
          help={errors.driver_id?.message}
        >
          <Controller
            name="driver_id"
            control={control}
            render={({ field }) => (
              <InputNumber
                {...field}
                placeholder="Nhập mã tài xế (tùy chọn)"
                min={1}
                style={{ width: '100%' }}
              />
            )}
          />
        </Form.Item>

        {/* Mã bưu cục */}
        <Form.Item
          label="Mã bưu cục"
          validateStatus={errors.latest_depot_id ? 'error' : ''}
          help={errors.latest_depot_id?.message}
        >
          <Controller
            name="latest_depot_id"
            control={control}
            render={({ field }) => (
              <InputNumber
                {...field}
                placeholder="Nhập mã bưu cục (tùy chọn)"
                min={1}
                style={{ width: '100%' }}
              />
            )}
          />
        </Form.Item>
      </Form>
    </Modal>
  );
}

export default VehicleFormModal;
