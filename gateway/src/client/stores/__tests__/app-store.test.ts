import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('AppStore', () => {
  beforeEach(async () => {
    vi.resetModules();
    vi.clearAllMocks();
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
