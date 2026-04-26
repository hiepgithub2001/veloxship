// Test setup for vitest
import '@testing-library/jest-dom/vitest';

// Mock navigator.onLine for tests that need it
Object.defineProperty(globalThis.navigator, 'onLine', {
  writable: true,
  value: true,
});

// Mock matchMedia for responsive tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
