import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the api module
vi.mock('../../lib/api', () => ({
  api: {
    listSessions: vi.fn(),
    createSession: vi.fn(),
  },
}));

// Mock localStorage for app-store
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

import { api } from '../../lib/api';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('useSessions', () => {
  beforeEach(async () => {
    vi.resetModules();
    vi.clearAllMocks();
    localStorageMock.clear();
  });

  it('lists sessions via React Query', async () => {
    const sessions = [
      { id: 's1', title: 'Session 1', createdAt: '2024-01-01', updatedAt: '2024-01-01', permissionMode: 'default' },
    ];
    vi.mocked(api.listSessions).mockResolvedValue(sessions);

    const { useSessions } = await import('../use-sessions');
    const { result } = renderHook(() => useSessions(), { wrapper: createWrapper() });

    await waitFor(() => {
      expect(result.current.sessions).toHaveLength(1);
    });

    expect(result.current.sessions[0].title).toBe('Session 1');
  });

  it('returns empty array while loading', async () => {
    vi.mocked(api.listSessions).mockResolvedValue([]);

    const { useSessions } = await import('../use-sessions');
    const { result } = renderHook(() => useSessions(), { wrapper: createWrapper() });

    // Initially returns empty array
    expect(result.current.sessions).toEqual([]);
    expect(result.current.isLoading).toBe(true);
  });

  it('createSession mutation sets active session on success', async () => {
    const newSession = { id: 'new-1', title: 'New Session', createdAt: '2024-01-01', updatedAt: '2024-01-01', permissionMode: 'default' as const };
    vi.mocked(api.createSession).mockResolvedValue(newSession);
    vi.mocked(api.listSessions).mockResolvedValue([newSession]);

    const { useSessions } = await import('../use-sessions');
    const { result } = renderHook(() => useSessions(), { wrapper: createWrapper() });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    result.current.createSession.mutate({ permissionMode: 'default' });

    await waitFor(() => {
      expect(result.current.activeSessionId).toBe('new-1');
    });
  });

  it('exposes setActiveSession from app store', async () => {
    vi.mocked(api.listSessions).mockResolvedValue([]);

    const { useSessions } = await import('../use-sessions');
    const { result } = renderHook(() => useSessions(), { wrapper: createWrapper() });

    act(() => {
      result.current.setActiveSession('test-id');
    });

    await waitFor(() => {
      expect(result.current.activeSessionId).toBe('test-id');
    });
  });
});
