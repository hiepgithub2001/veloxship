import { describe, expect, it } from 'vitest';

import { formatVNDCompact } from '../../lib/format';
import {
  buildBillsTrendConfig,
  buildRevenueTrendConfig,
  buildStatusPieConfig,
  buildTopDestinationsBarConfig,
  provinceCountById,
  scaleProvinceColor,
  toNumber,
} from './chartConfig';

describe('buildBillsTrendConfig', () => {
  it('maps daily rows into date/value points', () => {
    const config = buildBillsTrendConfig([
      { date: '2026-11-05', bills: 3, revenue: '0.00' },
      { date: '2026-11-06', bills: 5, revenue: '0.00' },
    ]);
    expect(config.data).toEqual([
      { date: '2026-11-05', value: 3 },
      { date: '2026-11-06', value: 5 },
    ]);
    expect(config.xField).toBe('date');
    expect(config.yField).toBe('value');
  });
});

describe('buildRevenueTrendConfig', () => {
  it('parses money strings to numbers', () => {
    const config = buildRevenueTrendConfig([
      { date: '2026-11-06', bills: 0, revenue: '2500000.00' },
    ]);
    expect(config.data[0].value).toBe(2500000);
  });
});

describe('buildStatusPieConfig', () => {
  it('filters zero counts and maps status colours', () => {
    const config = buildStatusPieConfig([
      { status: 'delivered', count: 5 },
      { status: 'cancelled', count: 0 },
    ]);
    expect(config.data).toEqual([{ label: 'Đã giao', value: 5, status: 'delivered' }]);
    expect(config.scale.color.range[0]).toBe('#52C41A');
  });
});

describe('buildTopDestinationsBarConfig', () => {
  it('sorts descending and drops zero-count rows', () => {
    const config = buildTopDestinationsBarConfig([
      { province_code: '1', province_name: 'Hà Nội', count: 10 },
      { province_code: '79', province_name: 'Hồ Chí Minh', count: 20 },
      { province_code: '82', province_name: 'Đồng Tháp', count: 0 },
    ]);
    expect(config.data[0].province_code).toBe('79');
    expect(config.data[1].province_code).toBe('1');
    expect(config.data.some((d) => d.province_code === '82')).toBe(false);
  });
});

describe('provinceCountById + scaleProvinceColor', () => {
  it('builds the code→count map and colours zero as neutral', () => {
    const counts = provinceCountById([{ province_code: '1', count: 4 }]);
    expect(counts['1']).toBe(4);
    expect(counts['99']).toBeUndefined();
    expect(scaleProvinceColor(0, 10)).toBe('#EEF0F2');
    expect(scaleProvinceColor(10, 10)).toBe('#c41e3a');
    expect(scaleProvinceColor(5, 10)).not.toBe('#EEF0F2');
  });
});

describe('toNumber', () => {
  it('coerces values and falls back to 0', () => {
    expect(toNumber('2500000.00')).toBe(2500000);
    expect(toNumber(undefined)).toBe(0);
    expect(toNumber('abc')).toBe(0);
  });
});

describe('formatVNDCompact', () => {
  it('formats VND magnitudes', () => {
    expect(formatVNDCompact(1_500_000)).toBe('1,5 tr');
    expect(formatVNDCompact(2_300_000_000)).toBe('2,3 tỷ');
    expect(formatVNDCompact(500)).toBe('500 ₫');
  });
});
