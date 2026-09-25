/**
 * CustomerEditForm — edit a customer profile with province → ward cascade.
 */
import { useEffect } from 'react';
import { Button, Form, Input, Select, Space, Switch, message } from 'antd';
import { Controller, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { customerFormSchema } from '../schema';
import { updateCustomer } from '../../../api/customers';
import { getProvinces, getWardsByProvince } from '../../../api/locations';
import { t } from '../../../i18n/vi';

const typeOptions = [
  { value: 'retail', label: 'Khách lẻ' },
  { value: 'shop', label: 'Shop' },
  { value: 'enterprise', label: 'Doanh nghiệp' },
];

function toDefaultValues(customer) {
  const metadata = customer?.metadata || {};
  return {
    name: customer?.name || '',
    phone: customer?.phone || '',
    customer_type: customer?.customer_type || 'retail',
    address_detail: metadata.address_detail || '',
    province_code: metadata.province_code || '',
    ward_code: metadata.ward_code || '',
    is_active: customer?.is_active ?? true,
  };
}

export function CustomerEditForm({ customer, onSuccess }) {
  const queryClient = useQueryClient();

  const { control, handleSubmit, reset, watch, setValue } = useForm({
    resolver: zodResolver(customerFormSchema),
    defaultValues: toDefaultValues(customer),
  });

  const provinceCode = watch('province_code');

  const { data: provinces = [] } = useQuery({
    queryKey: ['provinces'],
    queryFn: getProvinces,
    staleTime: Infinity,
  });

  const { data: wards = [], isFetching: wardsLoading } = useQuery({
    queryKey: ['wards', provinceCode],
    queryFn: () => getWardsByProvince(provinceCode),
    enabled: Boolean(provinceCode),
    staleTime: Infinity,
  });

  useEffect(() => {
    if (customer) reset(toDefaultValues(customer));
  }, [customer, reset]);

  const mutation = useMutation({
    mutationFn: (payload) => updateCustomer(customer.id, payload),
    onSuccess: () => {
      message.success(t('customers.updateSuccess'));
      queryClient.invalidateQueries({ queryKey: ['customer', customer.id] });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      onSuccess?.();
    },
    onError: (err) => {
      message.error(err.response?.data?.message || t('customers.updateError'));
    },
  });

  const onSubmit = (values) => {
    const provinceName = provinces.find((p) => p.code === values.province_code)?.name || null;
    const wardName = wards.find((w) => w.code === values.ward_code)?.name || null;
    mutation.mutate({
      name: values.name,
      phone: values.phone || null,
      customer_type: values.customer_type,
      address_detail: values.address_detail || null,
      province_code: values.province_code || null,
      province_name: provinceName,
      ward_code: values.ward_code || null,
      ward_name: wardName,
      is_active: values.is_active,
    });
  };

  return (
    <Form layout="vertical" onFinish={handleSubmit(onSubmit)} style={{ maxWidth: 560 }}>
      <Form.Item label={t('customers.displayName')} required>
        <Controller
          name="name"
          control={control}
          render={({ field, fieldState }) => (
            <>
              <Input {...field} placeholder={t('customers.namePlaceholder')} status={fieldState.error ? 'error' : undefined} />
              {fieldState.error && (
                <div style={{ color: '#ff4d4f', fontSize: 12, marginTop: 4 }}>{fieldState.error.message}</div>
              )}
            </>
          )}
        />
      </Form.Item>

      <Form.Item label={t('customers.phone')}>
        <Controller
          name="phone"
          control={control}
          render={({ field, fieldState }) => (
            <>
              <Input {...field} placeholder={t('customers.phonePlaceholder')} status={fieldState.error ? 'error' : undefined} />
              {fieldState.error && (
                <div style={{ color: '#ff4d4f', fontSize: 12, marginTop: 4 }}>{fieldState.error.message}</div>
              )}
            </>
          )}
        />
      </Form.Item>

      <Form.Item label={t('customers.customerType')}>
        <Controller
          name="customer_type"
          control={control}
          render={({ field }) => <Select {...field} options={typeOptions} />}
        />
      </Form.Item>

      <Form.Item label={t('customers.address')}>
        <Controller
          name="address_detail"
          control={control}
          render={({ field }) => (
            <Input.TextArea {...field} placeholder={t('customers.addressPlaceholder')} rows={2} />
          )}
        />
      </Form.Item>

      <Form.Item label={t('customers.province')}>
        <Controller
          name="province_code"
          control={control}
          render={({ field }) => (
            <Select
              {...field}
              placeholder={t('customers.provincePlaceholder')}
              allowClear
              showSearch
              optionFilterProp="label"
              options={provinces.map((p) => ({ value: p.code, label: p.name }))}
              onChange={(value) => {
                field.onChange(value || '');
                setValue('ward_code', '');
              }}
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
              {...field}
              placeholder={t('customers.wardPlaceholder')}
              allowClear
              showSearch
              optionFilterProp="label"
              loading={wardsLoading}
              disabled={!provinceCode}
              options={wards.map((w) => ({ value: w.code, label: w.name }))}
              onChange={(value) => field.onChange(value || '')}
            />
          )}
        />
      </Form.Item>

      <Form.Item label={t('customers.isActive')}>
        <Controller
          name="is_active"
          control={control}
          render={({ field }) => <Switch checked={field.value} onChange={field.onChange} />}
        />
      </Form.Item>

      <Space>
        <Button type="primary" htmlType="submit" loading={mutation.isPending}>
          {t('common.save')}
        </Button>
      </Space>
    </Form>
  );
}

export default CustomerEditForm;
