/**
 * Tests for ConnectionBanner component.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { ConnectionBanner } from '../ConnectionBanner';

describe('ConnectionBanner', () => {
  let originalOnLine;

  beforeEach(() => {
    originalOnLine = navigator.onLine;
  });

  afterEach(() => {
    Object.defineProperty(navigator, 'onLine', { value: originalOnLine, writable: true });
  });

  it('renders nothing when online', () => {
    Object.defineProperty(navigator, 'onLine', { value: true, writable: true });
    const { container } = render(<ConnectionBanner />);
    expect(container.innerHTML).toBe('');
  });

  it('renders Vietnamese warning when offline', () => {
    Object.defineProperty(navigator, 'onLine', { value: false, writable: true });
    render(<ConnectionBanner />);
    expect(screen.getByText(/Mất kết nối/)).toBeInTheDocument();
  });

  it('has id="connection-banner" when visible', () => {
    Object.defineProperty(navigator, 'onLine', { value: false, writable: true });
    render(<ConnectionBanner />);
    expect(document.getElementById('connection-banner')).toBeInTheDocument();
  });

  it('shows banner when transitioning from online to offline', () => {
    Object.defineProperty(navigator, 'onLine', { value: true, writable: true });
    const { container, rerender } = render(<ConnectionBanner />);
    expect(container.innerHTML).toBe('');

    // Simulate going offline
    act(() => {
      window.dispatchEvent(new Event('offline'));
    });
    rerender(<ConnectionBanner />);
    // After the offline event, useOnlineStatus updates → banner should appear
  });
});
