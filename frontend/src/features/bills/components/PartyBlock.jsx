/**
 * PartyBlock — sender/receiver form with customer autocomplete (name/code/phone)
 * plus province/ward cascade.
 */
import { useEffect, useRef, useState } from 'react';
import { AutoComplete, Form, Input, Select, Tag, message } from 'antd';
import { Controller } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { getProvinces, getWardsByProvince } from '../../../api/locations';
import { getCustomers } from '../../../api/customers';
import { t } from '../../../i18n/vi';

export function PartyBlock({ control, errors, setValue, watch, prefix = 'sender' }) {
  const name = (field) => `${prefix}.${field}`;
  const err = (field) => errors?.[prefix]?.[field];

  const [query, setQuery] = useState('');
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCode, setSelectedCode] = useState('');
  const requestId = useRef(0);

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

  useEffect(() => {
    const normalizedQuery = query.trim();
    const currentRequest = ++requestId.current;
    if (!normalizedQuery) {
      setOptions([]);
      setLoading(false);
      return undefined;
    }

    const timer = window.setTimeout(async () => {
      setLoading(true);
      try {
        const data = await getCustomers({
          search: normalizedQuery,
          isActive: true,
          pageSize: 20,
        });
        if (currentRequest !== requestId.current) return;
        setOptions(
          data.items.map((customer) => ({
            value: String(customer.id),
            customer,
            label: (
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                <span>{customer.name}</span>
                <span style={{ color: '#8c8c8c', whiteSpace: 'nowrap' }}>
                  {[customer.code, customer.phone].filter(Boolean).join(' · ') || '—'}
                </span>
              </div>
            ),
          })),
        );
      } catch {
        if (currentRequest === requestId.current) setOptions([]);
      } finally {
        if (currentRequest === requestId.current) setLoading(false);
      }
    }, 250);

    return () => window.clearTimeout(timer);
  }, [query]);

  const selectCustomer = (_, option) => {
    const customer = option?.customer;
    if (!customer) return;
    const metadata = customer.metadata || {};
    setValue(name('customer_id'), customer.id);
    setValue(name('name'), customer.name || '');
    setValue(name('phone'), customer.phone || '');
    setValue(name('address_detail'), metadata.address_detail || '');
    setValue(name('province_code'), metadata.province_code || '');
    setValue(name('province_name'), metadata.province_name || '');
    setValue(name('ward_code'), metadata.ward_code || '');
    setValue(name('ward_name'), metadata.ward_name || '');
    setSelectedCode(customer.code || '');
    setQuery('');
    setOptions([]);
    message.info(t('bills.customerAutofilled'));
  };

  return (
    <div>
      <h4 className="form-section-title">
        {t(prefix === 'sender' ? 'bills.sender' : 'bills.receiver')}
      </h4>

      <Form.Item label={t('bills.selectCustomer')}>
        <AutoComplete
          value={query}
          options={options}
          onSearch={setQuery}
          onSelect={selectCustomer}
          filterOption={false}
          notFoundContent={query.trim() && !loading ? t('bills.customerSearchEmpty') : null}
          id={`${prefix}-customer-search`}
        >
          <Input.Search
            placeholder={t('bills.customerSearchPlaceholder')}
            enterButton
            loading={loading}
          />
        </AutoComplete>
        {selectedCode && (
          <Tag color="blue" style={{ marginTop: 6 }}>
            {t('bills.customerCode')}: {selectedCode}
          </Tag>
        )}
      </Form.Item>

      <Form.Item
        label={t('bills.phone')}
        validateStatus={err('phone') ? 'error' : ''}
        help={err('phone')?.message}
      >
        <Controller
          name={name('phone')}
          control={control}
          render={({ field }) => (
            <Input {...field} placeholder={t('bills.phonePlaceholder')} id={`${prefix}-phone`} />
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
