/**
 * Tests for version module.
 */
import { describe, it, expect } from 'vitest';
import { APP_VERSION, APP_GIT_SHA, formatVersion } from '../version';

describe('version module', () => {
  it('exports APP_VERSION as a string', () => {
    expect(typeof APP_VERSION).toBe('string');
    expect(APP_VERSION.length).toBeGreaterThan(0);
  });

  it('exports APP_GIT_SHA as a string', () => {
    expect(typeof APP_GIT_SHA).toBe('string');
    expect(APP_GIT_SHA.length).toBeGreaterThan(0);
  });

  it('formatVersion() returns Vietnamese format', () => {
    const result = formatVersion();
    expect(result).toMatch(/^Phiên bản: v/);
    expect(result).toContain(APP_VERSION);
    expect(result).toContain(APP_GIT_SHA);
  });
});
