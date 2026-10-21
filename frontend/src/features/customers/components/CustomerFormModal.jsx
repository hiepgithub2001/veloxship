/**
 * CustomerFormModal — create and edit a customer profile.
 *
 * Address is a province → ward cascade (no district level). The form sends both
 * codes and names because the backend stores the whole address inside the
 * `metadata` JSONB column.
 *
 * A duplicated phone number does not block saving: the bill flow resolves
 * customers by phone, so blocking here would break bill entry. The form asks for
 * confirmation instead.
 */
import { useEffect, useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Form, Input, Modal, Select, Switch, message } from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  createCustomer,
  getCustomers,
  updateCustomer,
} from '../../../api/customers';
import { getProvinces, getWardsByProvince } from '../../../api/locations';
import { t } from '../../../i18n/vi';
import { customerFormSchema } from '../schema';

const CUSTOMER_TYPE_OPTIONS = [
  { value: 'retail', label: t('customers.typeRetail') },
  { value: 'shop', label: t('customers.typeShop') },
  { value: 'enterprise', label: t('customers.typeEnterprise') },
];

const EMPTY_VALUES = {
  name: '',
  phone: '',
  customer_type: 'retail',
  address_detail: '',
  province_code: undefined,
  ward_code: undefined,
  is_active: true,
};

export function CustomerFormModal({ open, onClose, customer, onSuccess }) {
  const isEdit = Boolean(customer);
  const queryClient = useQueryClient();

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(customerFormSchema),
    defaultValues: EMPTY_VALUES,
  });

  const provinceCode = watch('province_code');

  const { data: provinces = [] } = useQuery({
    queryKey: ['provinces'],
    queryFn: getProvinces,
    staleTime: Infinity,
  });

  const { data: wards = [] } = useQuery({
    queryKey: ['wards', provinceCode],
    queryFn: () => getWardsByProvince(provinceCode),
    enabled: Boolean(provinceCode),
    staleTime: Infinity,
  });

  // Prefill on open; the flattened address fields come straight from the API.
  useEffect(() => {
    if (!open) return;
    if (isEdit && customer) {
      reset({
        name: customer.name || '',
        phone: customer.phone || '',
        customer_type: customer.customer_type || 'retail',
        address_detail: customer.address_detail || '',
        province_code: customer.province_code || undefined,
        ward_code: customer.ward_code || undefined,
        is_active: customer.is_active ?? true,
      });
    } else {
      reset(EMPTY_VALUES);
    }
  }, [open, isEdit, customer, reset]);

  const createMutation = useMutation({
    mutationFn: (payload) => createCustomer(payload),
    onSuccess: (created) => {
      message.success(t('customers.createSuccess'));
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      onSuccess?.(created);
      onClose();
    },
    onError: (err) => {
      message.error(err.response?.data?.message || t('customers.createError'));
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload) => updateCustomer(customer.id, payload),
    onSuccess: (updated) => {
      message.success(t('customers.updateSuccess'));
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      queryClient.invalidateQueries({ queryKey: ['customer', String(customer.id)] });
      onSuccess?.(updated);
      onClose();
    },
    onError: (err) => {
      message.error(err.response?.data?.message || t('customers.updateError'));
    },
  });

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  /** Resolve the selected province/ward names alongside their codes. */
  const buildPayload = (formData) => {
    const province = (provinces || []).find((item) => item.code === formData.province_code);
    const ward = (wards || []).find((item) => item.code === formData.ward_code);

    const payload = {
      name: formData.name.trim(),
      phone: formData.phone?.trim() || null,
      customer_type: formData.customer_type,
      address_detail: formData.address_detail?.trim() || null,
      province_code: formData.province_code || null,
      province_name: province?.name ?? null,
      ward_code: formData.ward_code || null,
      ward_name: ward?.name ?? null,
    };
    if (isEdit) payload.is_active = formData.is_active ?? true;
    return payload;
  };

  const submit = (payload) => {
    if (isEdit) updateMutation.mutate(payload);
    else createMutation.mutate(payload);
  };

  const onSubmit = async (formData) => {
    const payload = buildPayload(formData);

    if (payload.phone) {
      try {
        const found = await getCustomers({ search: payload.phone, pageSize: 5 });
        const isDuplicate = (found.items || []).some(
          (item) => item.phone === payload.phone && item.id !== customer?.id,
        );
        if (isDuplicate) {
          Modal.confirm({
            title: t('customers.duplicatePhoneTitle'),
            content: t('customers.duplicatePhoneContent'),
            okText: t('customers.duplicatePhoneOk'),
            cancelText: t('common.cancel'),
            onOk: () => submit(payload),
          });
          return;
        }
      } catch {
        // A failed lookup must never block saving.
      }
    }

    submit(payload);
  };

  return (
    <Modal
      title={isEdit ? t('customers.editTitle') : t('customers.createTitle')}
      open={open}
      onOk={handleSubmit(onSubmit)}
      onCancel={onClose}
      okText={isEdit ? t('common.save') : t('common.create')}
      cancelText={t('common.cancel')}
      confirmLoading={isSubmitting}
      destroyOnClose
      maskClosable={false}
    >
      <Form layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          label={t('customers.displayName')}
          validateStatus={errors.name ? 'error' : ''}
          help={errors.name?.message}
          required
        >
          <Controller
            name="name"
            control={control}
            render={({ field }) => (
              <Input {...field} placeholder={t('customers.namePlaceholder')} />
            )}
          />
        </Form.Item>

        <Form.Item
          label={t('customers.phone')}
          validateStatus={errors.phone ? 'error' : ''}
          help={errors.phone?.message}
        >
          <Controller
            name="phone"
            control={control}
            render={({ field }) => (
              <Input {...field} placeholder={t('customers.phonePlaceholder')} />
            )}
          />
        </Form.Item>

        <Form.Item
          label={t('customers.customerType')}
          validateStatus={errors.customer_type ? 'error' : ''}
          help={errors.customer_type?.message}
          required
        >
          <Controller
            name="customer_type"
            control={control}
            render={({ field }) => (
              <Select
                value={field.value}
                onChange={field.onChange}
                options={CUSTOMER_TYPE_OPTIONS}
              />
            )}
          />
        </Form.Item>

        <Form.Item label={t('customers.address')}>
          <Controller
            name="address_detail"
            control={control}
            render={({ field }) => (
              <Input.TextArea
                {...field}
                rows={2}
                placeholder={t('customers.addressPlaceholder')}
              />
            )}
          />
        </Form.Item>

        <Form.Item label={t('customers.province')}>
          <Controller
            name="province_code"
            control={control}
            render={({ field }) => (
              <Select
                value={field.value}
                onChange={(value) => {
                  field.onChange(value);
                  // Ward belongs to the previous province — clear it.
                  setValue('ward_code', undefined);
                }}
                placeholder={t('customers.provincePlaceholder')}
                options={(provinces || []).map((item) => ({
                  value: item.code,
                  label: item.name,
                }))}
                allowClear
                showSearch
                optionFilterProp="label"
              />
            )}
          />
        </Form.Item>

        <Form.Item label={t('customers.ward')}>
          <Controller
            name="ward_code"
            control={control}
            render={({ field }) => (
              <Select
                value={field.value}
                onChange={field.onChange}
                placeholder={t('customers.wardPlaceholder')}
                options={(wards || []).map((item) => ({
                  value: item.code,
                  label: item.name,
                }))}
                disabled={!provinceCode}
                allowClear
                showSearch
                optionFilterProp="label"
              />
            )}
          />
        </Form.Item>

        {isEdit && (
          <Form.Item label={t('customers.isActive')} style={{ marginBottom: 0 }}>
            <Controller
              name="is_active"
              control={control}
              render={({ field }) => (
                <Switch checked={field.value} onChange={field.onChange} />
              )}
            />
          </Form.Item>
        )}
      </Form>
    </Modal>
  );
}

export default CustomerFormModal;
