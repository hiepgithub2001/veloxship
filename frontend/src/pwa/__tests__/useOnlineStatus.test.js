/**
 * Tests for useOnlineStatus hook.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useOnlineStatus } from '../useOnlineStatus';

describe('useOnlineStatus', () => {
  let originalOnLine;

  beforeEach(() => {
    originalOnLine = navigator.onLine;
  });

  afterEach(() => {
    Object.defineProperty(navigator, 'onLine', { value: originalOnLine, writable: true });
  });

  it('returns { online: true } when navigator.onLine is true', () => {
    Object.defineProperty(navigator, 'onLine', { value: true, writable: true });
    const { result } = renderHook(() => useOnlineStatus());
    expect(result.current.online).toBe(true);
  });

  it('returns { online: false } when navigator.onLine is false', () => {
    Object.defineProperty(navigator, 'onLine', { value: false, writable: true });
    const { result } = renderHook(() => useOnlineStatus());
    expect(result.current.online).toBe(false);
  });

  it('transitions to false on "offline" event', () => {
    Object.defineProperty(navigator, 'onLine', { value: true, writable: true });
    const { result } = renderHook(() => useOnlineStatus());
    expect(result.current.online).toBe(true);

    act(() => {
      window.dispatchEvent(new Event('offline'));
    });
    expect(result.current.online).toBe(false);
  });

  it('transitions to true on "online" event', () => {
    Object.defineProperty(navigator, 'onLine', { value: false, writable: true });
    const { result } = renderHook(() => useOnlineStatus());
    expect(result.current.online).toBe(false);

    act(() => {
      window.dispatchEvent(new Event('online'));
    });
    expect(result.current.online).toBe(true);
  });

  it('cleans up event listeners on unmount', () => {
    const addSpy = vi.spyOn(window, 'addEventListener');
    const removeSpy = vi.spyOn(window, 'removeEventListener');

    const { unmount } = renderHook(() => useOnlineStatus());
    expect(addSpy).toHaveBeenCalledWith('online', expect.any(Function));
    expect(addSpy).toHaveBeenCalledWith('offline', expect.any(Function));

    unmount();
    expect(removeSpy).toHaveBeenCalledWith('online', expect.any(Function));
    expect(removeSpy).toHaveBeenCalledWith('offline', expect.any(Function));

    addSpy.mockRestore();
    removeSpy.mockRestore();
  });
});
