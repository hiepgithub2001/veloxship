/**
 * DepotFormModal — Modal form for creating and editing depots.
 * Cascading select: Province → Ward (no district level).
 */
import { useEffect, useState } from 'react';
import { Modal, Form, Input, Select, message } from 'antd';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { depotFormSchema } from '../schema';
import { createDepot, updateDepot } from '../../../api/depots';
import { getProvinces, getWardsByProvince } from '../../../api/locations';
import ImageUpload from '../../../components/common/ImageUpload';

/**
 * @param {object} props
 * @param {boolean} props.open - Whether modal is visible
 * @param {function} props.onClose - Close handler
 * @param {object|null} props.depot - Null for create mode, depot object for edit mode
 * @param {function} props.onSuccess - Called after successful create/update
 */
export function DepotFormModal({ open, onClose, depot, onSuccess }) {
  const isEdit = Boolean(depot);
  const queryClient = useQueryClient();

  const [selectedProvinceCode, setSelectedProvinceCode] = useState(null);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(depotFormSchema),
    defaultValues: {
      code: '',
      name: '',
      phone: '',
      address_detail: '',
      ward_code: undefined,
      images: [],
    },
  });

  // Fetch provinces list
  const { data: provinces = [] } = useQuery({
    queryKey: ['provinces'],
    queryFn: getProvinces,
    staleTime: Infinity,
  });

  // Fetch wards for selected province
  const { data: wards = [], isFetching: wardsLoading } = useQuery({
    queryKey: ['wards', selectedProvinceCode],
    queryFn: () => getWardsByProvince(selectedProvinceCode),
    enabled: Boolean(selectedProvinceCode),
    staleTime: Infinity,
  });

  // Reset form when modal opens or depot changes
  useEffect(() => {
    if (open) {
      if (isEdit && depot) {
        reset({
          code: depot.code || '',
          name: depot.name || '',
          phone: depot.phone || '',
          address_detail: depot.address_detail || '',
          ward_code: depot.ward_code || undefined,
          images: depot.images || [],
        });
        setSelectedProvinceCode(depot.province_code || null);
      } else {
        reset({
          code: '',
          name: '',
          phone: '',
          address_detail: '',
          ward_code: undefined,
          images: [],
        });
        setSelectedProvinceCode(null);
      }
    }
  }, [open, depot, isEdit, reset]);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data) => createDepot(data),
    onSuccess: () => {
      message.success('Tạo bưu cục thành công');
      queryClient.invalidateQueries({ queryKey: ['depots'] });
      onSuccess?.();
      onClose();
    },
    onError: (err) => {
      message.error(err.response?.data?.message || 'Lỗi khi tạo bưu cục');
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data) => updateDepot(depot.id, data),
    onSuccess: () => {
      message.success('Cập nhật bưu cục thành công');
      queryClient.invalidateQueries({ queryKey: ['depots'] });
      onSuccess?.();
      onClose();
    },
    onError: (err) => {
      message.error(err.response?.data?.message || 'Lỗi khi cập nhật bưu cục');
    },
  });

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  const onSubmit = (formData) => {
    if (isEdit) {
      // Remove code from update payload (immutable)
      const { code, ...updatePayload } = formData;
      updateMutation.mutate(updatePayload);
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleProvinceChange = (provinceCode) => {
    setSelectedProvinceCode(provinceCode || null);
  };

  return (
    <Modal
      title={isEdit ? 'Sửa bưu cục' : 'Thêm bưu cục mới'}
      open={open}
      onOk={handleSubmit(onSubmit)}
      onCancel={onClose}
      okText={isEdit ? 'Cập nhật' : 'Tạo mới'}
      cancelText="Hủy"
      confirmLoading={isSubmitting}
      destroyOnClose
      maskClosable={false}
    >
      <Form layout="vertical" style={{ marginTop: 16 }}>
        {/* Mã bưu cục */}
        <Form.Item
          label="Mã bưu cục"
          validateStatus={errors.code ? 'error' : ''}
          help={errors.code?.message}
          required
        >
          <Controller
            name="code"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                placeholder="VD: HCM01"
                disabled={isEdit}
              />
            )}
          />
        </Form.Item>

        {/* Tên bưu cục */}
        <Form.Item
          label="Tên bưu cục"
          validateStatus={errors.name ? 'error' : ''}
          help={errors.name?.message}
          required
        >
          <Controller
            name="name"
            control={control}
            render={({ field }) => (
              <Input {...field} placeholder="Nhập tên bưu cục" />
            )}
          />
        </Form.Item>

        {/* Số điện thoại */}
        <Form.Item
          label="Số điện thoại"
          validateStatus={errors.phone ? 'error' : ''}
          help={errors.phone?.message}
          required
        >
          <Controller
            name="phone"
            control={control}
            render={({ field }) => (
              <Input {...field} placeholder="VD: 0901234567" />
            )}
          />
        </Form.Item>

        {/* Địa chỉ chi tiết */}
        <Form.Item
          label="Địa chỉ chi tiết"
          validateStatus={errors.address_detail ? 'error' : ''}
          help={errors.address_detail?.message}
          required
        >
          <Controller
            name="address_detail"
            control={control}
            render={({ field }) => (
              <Input.TextArea
                {...field}
                placeholder="Nhập địa chỉ chi tiết"
                rows={2}
              />
            )}
          />
        </Form.Item>

        {/* Tỉnh/TP → Phường/Xã (cascading) */}
        <Form.Item label="Tỉnh/Thành phố">
          <Select
            value={selectedProvinceCode}
            onChange={handleProvinceChange}
            placeholder="Chọn tỉnh/thành phố"
            allowClear
            showSearch
            optionFilterProp="label"
            options={provinces.map((p) => ({
              value: p.code,
              label: p.name,
            }))}
          />
        </Form.Item>

        <Form.Item
          label="Phường/Xã"
          validateStatus={errors.ward_code ? 'error' : ''}
          help={errors.ward_code?.message}
        >
          <Controller
            name="ward_code"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                placeholder="Chọn phường/xã"
                allowClear
                showSearch
                optionFilterProp="label"
                loading={wardsLoading}
                disabled={!selectedProvinceCode}
                options={wards.map((w) => ({
                  value: w.code,
                  label: w.name,
                }))}
                onChange={(val) => {
                  field.onChange(val);
                }}
              />
            )}
          />
        </Form.Item>
        <Form.Item
          label="Hình ảnh bưu cục (tối đa 5)"
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

export default DepotFormModal;
