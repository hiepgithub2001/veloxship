import { describe, expect, it } from 'vitest';

import vietnamTopology from '../../assets/geo/vietnam-provinces.json';

describe('vietnam-provinces map asset', () => {
  it('carries 34 post-merger provinces with unique backend codes', () => {
    const objectName = Object.keys(vietnamTopology.objects)[0];
    const geometries = vietnamTopology.objects[objectName].geometries;
    const codes = geometries.map((g) => g.properties?.code).filter(Boolean);
    expect(codes).toHaveLength(34);
    expect(new Set(codes).size).toBe(34);
  });
});
