/**
 * Tests for UpdatePrompt component.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Mock the registerSW module
const listeners = [];
vi.mock('../registerSW', () => ({
  onNeedRefresh: vi.fn((cb) => {
    listeners.push(cb);
    return () => {
      const idx = listeners.indexOf(cb);
      if (idx >= 0) listeners.splice(idx, 1);
    };
  }),
  updateSW: vi.fn(),
}));

import { UpdatePrompt } from '../UpdatePrompt';
import { updateSW } from '../registerSW';

function triggerNeedRefresh() {
  act(() => {
    listeners.forEach((fn) => fn());
  });
}

function renderWithRouter(ui, { route = '/' } = {}) {
  return render(<MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>);
}

describe('UpdatePrompt', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listeners.length = 0;
  });

  it('renders nothing initially (no update available)', () => {
    const { container } = renderWithRouter(<UpdatePrompt />);
    expect(container.querySelector('#update-prompt')).toBeNull();
  });

  it('shows Vietnamese update prompt when needRefresh fires', () => {
    renderWithRouter(<UpdatePrompt />);
    triggerNeedRefresh();
    expect(screen.getByText('Có phiên bản mới')).toBeInTheDocument();
    expect(screen.getByText('Tải lại để cập nhật ứng dụng')).toBeInTheDocument();
  });

  it('calls updateSW when "Cập nhật" is clicked', () => {
    renderWithRouter(<UpdatePrompt />);
    triggerNeedRefresh();
    const btn = screen.getByText('Cập nhật');
    fireEvent.click(btn);
    expect(updateSW).toHaveBeenCalledWith(true);
  });

  it('is suppressed when on wizard route /phieu-gui/tao-moi', () => {
    renderWithRouter(<UpdatePrompt />, { route: '/phieu-gui/tao-moi' });
    triggerNeedRefresh();
    expect(screen.queryByText('Có phiên bản mới')).not.toBeInTheDocument();
  });

  it('is NOT suppressed on preview route /phieu-gui/tao-moi/preview/123', () => {
    renderWithRouter(<UpdatePrompt />, { route: '/phieu-gui/tao-moi/preview/123' });
    triggerNeedRefresh();
    expect(screen.getByText('Có phiên bản mới')).toBeInTheDocument();
  });

  it('can be dismissed', () => {
    renderWithRouter(<UpdatePrompt />);
    triggerNeedRefresh();

    // Find the close button (small X icon button, not the "Cập nhật" button)
    const allButtons = screen.getAllByRole('button');
    const closeBtn = allButtons.find((btn) => btn.textContent !== 'Cập nhật');
    if (closeBtn) {
      fireEvent.click(closeBtn);
      expect(screen.queryByText('Có phiên bản mới')).not.toBeInTheDocument();
    }
  });
});
