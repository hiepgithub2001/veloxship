/**
 * Tests for ResponsiveShell component.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

// Mock Ant Design Grid.useBreakpoint
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd');
  return {
    ...actual,
    Grid: {
      ...actual.Grid,
      useBreakpoint: vi.fn(() => ({ xs: false, sm: false, md: true, lg: true })),
    },
  };
});

import { ResponsiveShell, useIsMobile } from '../../components/ResponsiveShell';
import { renderHook } from '@testing-library/react';
import { Grid } from 'antd';

describe('useIsMobile', () => {
  it('returns false when md+ breakpoint is active', () => {
    Grid.useBreakpoint.mockReturnValue({ xs: false, sm: false, md: true, lg: true });
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);
  });

  it('returns true when only xs/sm is active', () => {
    Grid.useBreakpoint.mockReturnValue({ xs: true, sm: true, md: false, lg: false });
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(true);
  });
});

describe('ResponsiveShell', () => {
  it('renders desktop content on md+ screens', () => {
    Grid.useBreakpoint.mockReturnValue({ xs: false, sm: false, md: true, lg: true });
    render(
      <ResponsiveShell
        desktop={<div data-testid="desktop">Desktop</div>}
        mobile={<div data-testid="mobile">Mobile</div>}
      />,
    );
    expect(screen.getByTestId('desktop')).toBeInTheDocument();
    expect(screen.queryByTestId('mobile')).not.toBeInTheDocument();
  });

  it('renders mobile content on xs/sm screens', () => {
    Grid.useBreakpoint.mockReturnValue({ xs: true, sm: true, md: false, lg: false });
    render(
      <ResponsiveShell
        desktop={<div data-testid="desktop">Desktop</div>}
        mobile={<div data-testid="mobile">Mobile</div>}
      />,
    );
    expect(screen.getByTestId('mobile')).toBeInTheDocument();
    expect(screen.queryByTestId('desktop')).not.toBeInTheDocument();
  });
});
