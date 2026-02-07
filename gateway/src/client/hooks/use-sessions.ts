import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useAppStore } from '../stores/app-store';
import type { CreateSessionRequest } from '@shared/types';

export function useSessions() {
  const queryClient = useQueryClient();
  const { activeSessionId, setActiveSession } = useAppStore();

  const sessionsQuery = useQuery({
    queryKey: ['sessions'],
    queryFn: api.listSessions,
    refetchInterval: 30_000,
  });

  const createSession = useMutation({
    mutationFn: (opts: CreateSessionRequest) => api.createSession(opts),
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      setActiveSession(session.id);
    },
  });

  return {
    sessions: sessionsQuery.data ?? [],
    isLoading: sessionsQuery.isLoading,
    createSession,
    activeSessionId,
    setActiveSession,
  };
}
