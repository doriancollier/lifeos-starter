import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTransport } from '../contexts/TransportContext';
import { useSessionId } from './use-session-id';
import type { CreateSessionRequest } from '@shared/types';

export function useSessions() {
  const queryClient = useQueryClient();
  const [activeSessionId, setActiveSession] = useSessionId();
  const transport = useTransport();

  const sessionsQuery = useQuery({
    queryKey: ['sessions'],
    queryFn: () => transport.listSessions(),
    refetchInterval: 60_000,
  });

  const createSession = useMutation({
    mutationFn: (opts: CreateSessionRequest) => transport.createSession(opts),
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
