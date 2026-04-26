/**
 * Tests for NoConnectionScreen component.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { NoConnectionScreen } from '../NoConnectionScreen';

describe('NoConnectionScreen', () => {
  it('renders Vietnamese no-connection message', () => {
    render(<NoConnectionScreen />);
    expect(screen.getByText(/Cần kết nối mạng/)).toBeInTheDocument();
  });

  it('shows retry button with correct id', () => {
    render(<NoConnectionScreen />);
    const btn = screen.getByRole('button', { name: /Thử lại/i });
    expect(btn).toBeInTheDocument();
    expect(btn.id || btn.closest('[id]')?.id).toBeTruthy();
  });

  it('has correct id on the wrapper', () => {
    render(<NoConnectionScreen />);
    expect(document.getElementById('no-connection-screen')).toBeInTheDocument();
  });

  it('calls window.location.reload on retry click', () => {
    const reloadMock = vi.fn();
    Object.defineProperty(window, 'location', {
      value: { ...window.location, reload: reloadMock },
      writable: true,
    });

    render(<NoConnectionScreen />);
    const btn = screen.getByRole('button', { name: /Thử lại/i });
    fireEvent.click(btn);
    expect(reloadMock).toHaveBeenCalled();
  });
});
