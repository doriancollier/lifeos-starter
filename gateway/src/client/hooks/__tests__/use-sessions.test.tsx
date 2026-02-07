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

// Mock useSessionId (nuqs-backed)
let mockSessionId: string | null = null;
const mockSetSessionId = vi.fn((id: string | null) => {
  mockSessionId = id;
});
vi.mock('../use-session-id', () => ({
  useSessionId: () => [mockSessionId, mockSetSessionId] as const,
}));

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
    mockSessionId = null;
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
      expect(mockSetSessionId).toHaveBeenCalledWith('new-1');
    });
  });

  it('exposes setActiveSession', async () => {
    vi.mocked(api.listSessions).mockResolvedValue([]);

    const { useSessions } = await import('../use-sessions');
    const { result } = renderHook(() => useSessions(), { wrapper: createWrapper() });

    act(() => {
      result.current.setActiveSession('test-id');
    });

    expect(mockSetSessionId).toHaveBeenCalledWith('test-id');
  });
});
