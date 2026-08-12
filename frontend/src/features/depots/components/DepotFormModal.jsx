/**
 * DepotFormModal — Modal form for creating and editing depots.
 * Cascading select: Province → Ward (no district level).
 */
import { useEffect, useMemo, useState } from 'react';
import { Modal, Form, Input, Select, message, Upload, Avatar } from 'antd';
import { CameraOutlined } from '@ant-design/icons';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../../auth/AuthContext';

import { depotFormSchema } from '../schema';
import { createDepot, updateDepot } from '../../../api/depots';
import { getProvinces, getWardsByProvince } from '../../../api/locations';

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
  const { accessToken } = useAuth();

  const [selectedProvinceCode, setSelectedProvinceCode] = useState(null);
  const [fileList, setFileList] = useState([]);
  const [uploading, setUploading] = useState(false);

  const API_BASE = useMemo(() => import.meta.env.VITE_API_BASE_URL || '/api/v1', []);

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

  // Cleanup object URLs on unmount
  useEffect(() => {
    return () => {
      fileList.forEach((f) => {
        if (f.url && f.url.startsWith('blob:')) URL.revokeObjectURL(f.url);
      });
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Build initial file list from existing depot images
  useEffect(() => {
    if (isEdit && depot?.image_urls?.length) {
      const existingFiles = depot.image_urls.map((key, idx) => ({
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
  }, [isEdit, depot]); // eslint-disable-line react-hooks/exhaustive-deps

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
        });
        setSelectedProvinceCode(depot.province_code || null);
      } else {
        reset({
          code: '',
          name: '',
          phone: '',
          address_detail: '',
          ward_code: undefined,
        });
        setSelectedProvinceCode(null);
      }
    }
  }, [open, depot, isEdit, reset]);

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
      fd.append('code', formData.code || '');
      fd.append('name', formData.name || '');
      fd.append('phone', formData.phone || '');
      fd.append('address_detail', formData.address_detail || '');
      if (formData.ward_code) fd.append('ward_code', formData.ward_code);

      fileList.forEach((f) => {
        const raw = f.originFileObj || f;
        if (raw instanceof File) {
          fd.append('images', raw);
        }
      });

      const url = `${API_BASE}/depots${isEdit ? '/' + depot.id : ''}`;
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
      message.success(isEdit ? 'Cập nhật bưu cục thành công' : 'Tạo bưu cục thành công');
      queryClient.invalidateQueries({ queryKey: ['depots'] });
      onSuccess?.();
      onClose();
    } catch (err) {
      message.error(err.message || 'Lỗi khi lưu bưu cục');
    } finally {
      setUploading(false);
    }
  };

  const handleProvinceChange = (provinceCode) => {
    setSelectedProvinceCode(provinceCode || null);
  };

  return (
    <Modal
      title={isEdit ? 'Sửa bưu cục' : 'Thêm bưu cục mới'}
      open={open}
      onOk={handleSubmit(submitWithImages)}
      onCancel={onClose}
      okText={isEdit ? 'Cập nhật' : 'Tạo mới'}
      cancelText="Hủy"
      confirmLoading={uploading}
      destroyOnClose
      maskClosable={false}
      width={720}
    >
      <Form layout="vertical" style={{ marginTop: 16 }}>
        {/* Ảnh bưu cục */}
        <Form.Item label="Ảnh bưu cục">
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
      </Form>
    </Modal>
  );
}

export default DepotFormModal;
