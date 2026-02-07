import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value; }),
    removeItem: vi.fn((key: string) => { delete store[key]; }),
    clear: vi.fn(() => { store = {}; }),
  };
})();
Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock });

describe('AppStore', () => {
  beforeEach(async () => {
    vi.resetModules();
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  it('initializes activeSessionId from localStorage', async () => {
    localStorageMock.getItem.mockReturnValueOnce('saved-id');
    const { useAppStore } = await import('../../stores/app-store');
    expect(useAppStore.getState().activeSessionId).toBe('saved-id');
  });

  it('setActiveSession persists to localStorage', async () => {
    const { useAppStore } = await import('../../stores/app-store');
    useAppStore.getState().setActiveSession('new-id');

    expect(localStorageMock.setItem).toHaveBeenCalledWith('activeSessionId', 'new-id');
    expect(useAppStore.getState().activeSessionId).toBe('new-id');
  });

  it('setActiveSession(null) removes from localStorage', async () => {
    const { useAppStore } = await import('../../stores/app-store');
    useAppStore.getState().setActiveSession(null);

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('activeSessionId');
    expect(useAppStore.getState().activeSessionId).toBeNull();
  });

  it('toggleSidebar flips state', async () => {
    const { useAppStore } = await import('../../stores/app-store');
    expect(useAppStore.getState().sidebarOpen).toBe(true);

    useAppStore.getState().toggleSidebar();
    expect(useAppStore.getState().sidebarOpen).toBe(false);

    useAppStore.getState().toggleSidebar();
    expect(useAppStore.getState().sidebarOpen).toBe(true);
  });

  it('setSidebarOpen sets explicit value', async () => {
    const { useAppStore } = await import('../../stores/app-store');

    useAppStore.getState().setSidebarOpen(false);
    expect(useAppStore.getState().sidebarOpen).toBe(false);

    useAppStore.getState().setSidebarOpen(true);
    expect(useAppStore.getState().sidebarOpen).toBe(true);
  });
});
