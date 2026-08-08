/**
 * ServiceStep — Dịch vụ (service category + tier selection for the mobile wizard).
 */
import { Radio, Checkbox, Spin, Typography } from 'antd';
import { useFormContext } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import client from '../../../../api/client';
import { t } from '../../../../i18n/vi';

const { Text } = Typography;

export const SERVICE_FIELDS = ['cargo_type', 'service_tier_code'];

export function ServiceStep() {
  const {
    watch,
    setValue,
    formState: { errors },
  } = useFormContext();
  const cargoType = watch('cargo_type');
  const tierCode = watch('service_tier_code');

  const { data: tiers = [], isLoading } = useQuery({
    queryKey: ['service-tiers'],
    queryFn: async () => {
      const { data } = await client.get('/service-tiers');
      return data;
    },
  });

  const domesticTiers = tiers.filter((tier) => tier.scope === 'domestic');
  const internationalTiers = tiers.filter((tier) => tier.scope === 'international');

  const selectedTier = tiers.find((tier) => tier.code === tierCode);
  const activeScope = selectedTier?.scope || null;

  if (isLoading) return <Spin />;

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Text strong style={{ display: 'block', marginBottom: 8 }}>
          {t('bills.cargoType')}
        </Text>
        <Radio.Group
          value={cargoType}
          onChange={(e) => {
            setValue('cargo_type', e.target.value);
            setValue('service_tier_code', '');
          }}
        >
          <Radio value="document">{t('bills.document')}</Radio>
          <Radio value="goods">{t('bills.goods')}</Radio>
        </Radio.Group>
        {errors?.cargo_type && (
          <div>
            <Text type="danger">{errors.cargo_type.message}</Text>
          </div>
        )}
      </div>

      <div>
        <Text strong style={{ display: 'block', marginBottom: 8 }}>
          {t('bills.serviceTier')}
        </Text>
        <div style={{ marginBottom: 12 }}>
          <Text type={activeScope === 'international' ? 'secondary' : undefined}>
            {t('bills.domestic')}
          </Text>
          <div style={{ marginTop: 4 }}>
            {domesticTiers.map((tier) => (
              <div key={tier.code} style={{ marginBottom: 8 }}>
                <Checkbox
                  checked={tierCode === tier.code}
                  disabled={activeScope === 'international'}
                  onChange={() => setValue('service_tier_code', tier.code)}
                >
                  {tier.display_name}
                </Checkbox>
              </div>
            ))}
          </div>
        </div>

        <div>
          <Text type={activeScope === 'domestic' ? 'secondary' : undefined}>
            {t('bills.international')}
          </Text>
          <div style={{ marginTop: 4 }}>
            {internationalTiers.map((tier) => (
              <div key={tier.code} style={{ marginBottom: 8 }}>
                <Checkbox
                  checked={tierCode === tier.code}
                  disabled={activeScope === 'domestic'}
                  onChange={() => setValue('service_tier_code', tier.code)}
                >
                  {tier.display_name}
                </Checkbox>
              </div>
            ))}
          </div>
        </div>

        {errors?.service_tier_code && <Text type="danger">{errors.service_tier_code.message}</Text>}
      </div>
    </div>
  );
}

export default ServiceStep;
