/**
 * PartyBlock — sender/receiver form with phone autofill + province/ward cascade.
 */
import { Form, Input, Select, message } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { Controller } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { getProvinces, getWardsByProvince } from '../../../api/locations';
import { getCustomerByPhone } from '../../../api/customers';
import { t } from '../../../i18n/vi';

export function PartyBlock({ control, errors, setValue, watch, prefix = 'sender' }) {
  const name = (field) => `${prefix}.${field}`;
  const err = (field) => errors?.[prefix]?.[field];

  const { data: provinces = [] } = useQuery({
    queryKey: ['provinces'],
    queryFn: getProvinces,
  });

  const provinceCode = watch(name('province_code'));

  const { data: wards = [] } = useQuery({
    queryKey: ['wards', provinceCode],
    queryFn: () => getWardsByProvince(provinceCode),
    enabled: !!provinceCode,
  });

  const handlePhoneSearch = async (phone) => {
    if (!phone) return;
    try {
      const customer = await getCustomerByPhone(phone);
      if (customer) {
        setValue(name('customer_id'), customer.id);
        setValue(name('name'), customer.name || '');
        setValue(name('phone'), customer.phone || phone);
        setValue(name('address_detail'), customer.metadata?.address_detail || '');
        setValue(name('province_code'), customer.metadata?.province_code || '');
        setValue(name('province_name'), customer.metadata?.province_name || '');
        setValue(name('ward_code'), customer.metadata?.ward_code || '');
        setValue(name('ward_name'), customer.metadata?.ward_name || '');
        message.info(t('bills.customerAutofilled'));
      } else {
        setValue(name('customer_id'), null);
        message.info(t('bills.newPhoneHint'));
      }
    } catch {
      message.error(t('common.loading'));
    }
  };

  return (
    <div>
      <h4 style={{ color: '#C41E3A', marginBottom: 8 }}>{t(prefix === 'sender' ? 'bills.sender' : 'bills.receiver')}</h4>

      <Form.Item
        label={t('bills.phone')}
        validateStatus={err('phone') ? 'error' : ''}
        help={err('phone')?.message}
      >
        <Controller
          name={name('phone')}
          control={control}
          render={({ field }) => (
            <Input.Search
              {...field}
              placeholder={t('bills.phonePlaceholder')}
              enterButton={<SearchOutlined />}
              onSearch={handlePhoneSearch}
              id={`${prefix}-phone`}
            />
          )}
        />
      </Form.Item>

      <Form.Item
        label={t('bills.name')}
        validateStatus={err('name') ? 'error' : ''}
        help={err('name')?.message}
      >
        <Controller
          name={name('name')}
          control={control}
          render={({ field }) => (
            <Input {...field} placeholder={t('bills.name')} id={`${prefix}-name`} />
          )}
        />
      </Form.Item>

      <Form.Item
        label={t('bills.addressDetail')}
        validateStatus={err('address_detail') ? 'error' : ''}
        help={err('address_detail')?.message}
      >
        <Controller
          name={name('address_detail')}
          control={control}
          render={({ field }) => (
            <Input {...field} placeholder={t('bills.addressDetail')} id={`${prefix}-address`} />
          )}
        />
      </Form.Item>

      <div style={{ display: 'flex', gap: 12 }}>
        <Form.Item
          label={t('bills.province')}
          style={{ flex: 1 }}
          validateStatus={err('province_code') ? 'error' : ''}
          help={err('province_code')?.message}
        >
          <Controller
            name={name('province_code')}
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                showSearch
                optionFilterProp="label"
                placeholder={t('bills.provincePlaceholder')}
                options={provinces.map((p) => ({ value: p.code, label: p.name }))}
                onChange={(code) => {
                  field.onChange(code);
                  const prov = provinces.find((p) => p.code === code);
                  setValue(name('province_name'), prov?.name || '');
                  setValue(name('ward_code'), '');
                  setValue(name('ward_name'), '');
                }}
                id={`${prefix}-province`}
              />
            )}
          />
        </Form.Item>
        <Form.Item
          label={t('bills.ward')}
          style={{ flex: 1 }}
          validateStatus={err('ward_code') ? 'error' : ''}
          help={err('ward_code')?.message}
        >
          <Controller
            name={name('ward_code')}
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                showSearch
                optionFilterProp="label"
                placeholder={t('bills.wardPlaceholder')}
                disabled={!provinceCode}
                options={wards.map((w) => ({ value: w.code, label: w.name }))}
                onChange={(code) => {
                  field.onChange(code);
                  const w = wards.find((x) => x.code === code);
                  setValue(name('ward_name'), w?.name || '');
                }}
                id={`${prefix}-ward`}
              />
            )}
          />
        </Form.Item>
      </div>
    </div>
  );
}

export default PartyBlock;
