/**
 * Service tier selector — cargo type + tier selection.
 */
import { Radio, Checkbox, Spin, Space, Typography } from 'antd';
import { useQuery } from '@tanstack/react-query';
import client from '../../../api/client';
import { t } from '../../../i18n/vi';

const { Text } = Typography;

export function ServiceTierSelector({ cargoType, tierCode, onCargoTypeChange, onTierChange }) {
  const { data: tiers = [], isLoading } = useQuery({
    queryKey: ['service-tiers'],
    queryFn: async () => {
      const { data } = await client.get('/service-tiers');
      return data;
    },
  });

  const domesticTiers = tiers.filter((tier) => tier.scope === 'domestic');
  const internationalTiers = tiers.filter((tier) => tier.scope === 'international');

  // Determine which scope is active based on current selection
  const selectedTier = tiers.find((tier) => tier.code === tierCode);
  const activeScope = selectedTier?.scope || null;

  if (isLoading) return <Spin />;

  return (
    <div>
      <h4 style={{ color: '#C41E3A', marginBottom: 8 }}>{t('bills.cargoType')} & {t('bills.serviceTier')}</h4>

      <div style={{ marginBottom: 12 }}>
        <Text strong>{t('bills.cargoType')}: </Text>
        <Radio.Group value={cargoType} onChange={(e) => onCargoTypeChange(e.target.value)}>
          <Radio value="document">{t('bills.document')}</Radio>
          <Radio value="goods">{t('bills.goods')}</Radio>
        </Radio.Group>
      </div>

      <div style={{ display: 'flex', gap: 24 }}>
        <div style={{ flex: 1 }}>
          <Text strong type={activeScope === 'international' ? 'secondary' : undefined}>
            {t('bills.domestic')}
          </Text>
          <div style={{ marginTop: 4 }}>
            {domesticTiers.map((tier) => (
              <div key={tier.code} style={{ marginBottom: 4 }}>
                <Checkbox
                  checked={tierCode === tier.code}
                  disabled={activeScope === 'international'}
                  onChange={() => onTierChange(tier.code)}
                >
                  {tier.display_name}
                </Checkbox>
              </div>
            ))}
          </div>
        </div>

        <div style={{ flex: 1 }}>
          <Text strong type={activeScope === 'domestic' ? 'secondary' : undefined}>
            {t('bills.international')}
          </Text>
          <div style={{ marginTop: 4 }}>
            {internationalTiers.map((tier) => (
              <div key={tier.code} style={{ marginBottom: 4 }}>
                <Checkbox
                  checked={tierCode === tier.code}
                  disabled={activeScope === 'domestic'}
                  onChange={() => onTierChange(tier.code)}
                >
                  {tier.display_name}
                </Checkbox>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ServiceTierSelector;
