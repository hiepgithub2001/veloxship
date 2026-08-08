/**
 * Tests for AboutScreen component.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AboutScreen } from '../../features/settings/AboutScreen';

describe('AboutScreen', () => {
  it('renders Vietnamese version label', () => {
    render(<AboutScreen />);
    expect(screen.getByText('Giới thiệu')).toBeInTheDocument();
    expect(screen.getByText('Phiên bản')).toBeInTheDocument();
  });

  it('shows build date label', () => {
    render(<AboutScreen />);
    expect(screen.getByText('Ngày xây dựng')).toBeInTheDocument();
  });

  it('shows Vietnamese app description', () => {
    render(<AboutScreen />);
    expect(screen.getByText(/Ứng dụng quản lý phiếu gửi/)).toBeInTheDocument();
  });

  it('displays the formatVersion() output', () => {
    render(<AboutScreen />);
    expect(screen.getByText(/Phiên bản: v/)).toBeInTheDocument();
  });
});
