/**
 * Tests for InstallPrompt component.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { InstallPrompt } from '../InstallPrompt';

describe('InstallPrompt', () => {
  let originalMatchMedia;

  beforeEach(() => {
    localStorage.clear();
    originalMatchMedia = window.matchMedia;
    // Default: not standalone
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
  });

  afterEach(() => {
    window.matchMedia = originalMatchMedia;
  });

  it('renders nothing by default (no beforeinstallprompt)', () => {
    const { container } = render(<InstallPrompt />);
    // No install banner should be visible
    expect(container.querySelector('.pwa-install-banner')).toBeNull();
  });

  it('renders nothing when in standalone mode', () => {
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: query === '(display-mode: standalone)',
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));

    const { container } = render(<InstallPrompt />);
    expect(container.innerHTML).toBe('');
  });

  it('shows Android banner on beforeinstallprompt event', async () => {
    const { container } = render(<InstallPrompt />);

    const mockPrompt = vi.fn();
    const event = new Event('beforeinstallprompt');
    event.preventDefault = vi.fn();
    event.prompt = mockPrompt;
    event.userChoice = Promise.resolve({ outcome: 'dismissed' });

    act(() => {
      window.dispatchEvent(event);
    });

    // Banner should appear with "Cài đặt" button
    expect(screen.getByText(/Cài đặt ứng dụng vào màn hình chính/)).toBeInTheDocument();
    expect(screen.getByText('Cài đặt')).toBeInTheDocument();
    expect(screen.getByText('Để sau')).toBeInTheDocument();
  });

  it('dismisses banner and stores timestamp', () => {
    render(<InstallPrompt />);

    const event = new Event('beforeinstallprompt');
    event.preventDefault = vi.fn();
    event.prompt = vi.fn();

    act(() => {
      window.dispatchEvent(event);
    });

    const dismissBtn = screen.getByText('Để sau');
    fireEvent.click(dismissBtn);

    expect(localStorage.getItem('pwa-install-dismissed-at')).toBeTruthy();
  });
});
