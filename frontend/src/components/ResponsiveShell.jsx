/**
 * ResponsiveShell — picks mobile vs desktop layout based on Ant Design breakpoints.
 */
import { Grid } from 'antd';

const { useBreakpoint } = Grid;

/**
 * Hook to determine if the current viewport is mobile-sized.
 * Mobile = xs or sm, and NOT md or larger.
 */
export function useIsMobile() {
  const screens = useBreakpoint();
  // Mobile: only xs or sm is true, md+ is false
  const isMobile = (screens.xs || screens.sm) && !screens.md;
  return isMobile;
}

/**
 * Wrapper component that renders either `mobile` or `desktop` content
 * based on the current breakpoint.
 *
 * @param {{ desktop: React.ReactNode, mobile: React.ReactNode }} props
 */
export function ResponsiveShell({ desktop, mobile }) {
  const isMobile = useIsMobile();
  return isMobile ? mobile : desktop;
}

export default ResponsiveShell;
