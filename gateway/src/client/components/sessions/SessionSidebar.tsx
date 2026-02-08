import { useState, useMemo, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../lib/api';
import { useSessionId } from '../../hooks/use-session-id';
import { useAppStore } from '../../stores/app-store';
import { useIsMobile } from '../../hooks/use-is-mobile';
import { SessionItem } from './SessionItem';
import { groupSessionsByTime } from '@/lib/session-utils';
import { Plus, Shield, ShieldOff, PanelLeftClose } from 'lucide-react';
import type { Session } from '@shared/types';

export function SessionSidebar() {
  const queryClient = useQueryClient();
  const [activeSessionId, setActiveSession] = useSessionId();
  const { setSidebarOpen } = useAppStore();
  const isMobile = useIsMobile();
  const [permissionMode, setPermissionMode] = useState<'default' | 'dangerously-skip'>('default');
  const [justCreatedId, setJustCreatedId] = useState<string | null>(null);

  const { data: sessions = [] } = useQuery({
    queryKey: ['sessions'],
    queryFn: api.listSessions,
  });

  const createMutation = useMutation({
    mutationFn: api.createSession,
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      setActiveSession(session.id);
      setJustCreatedId(session.id);
      setTimeout(() => setJustCreatedId(null), 300);
      if (isMobile) setTimeout(() => setSidebarOpen(false), 300);
    },
  });

  const handleSessionClick = useCallback(
    (sessionId: string) => {
      setActiveSession(sessionId);
      if (isMobile) setSidebarOpen(false);
    },
    [isMobile, setActiveSession, setSidebarOpen]
  );

  const groupedSessions = useMemo(() => groupSessionsByTime(sessions), [sessions]);

  return (
    <div className="flex flex-col h-full p-3">
      {/* Header: New Chat + Collapse */}
      <div className="mb-3 space-y-1.5">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => createMutation.mutate({ permissionMode })}
            disabled={createMutation.isPending}
            className="flex items-center justify-center gap-2 flex-1 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 active:scale-[0.98] transition-all duration-100 disabled:opacity-50"
          >
            <Plus className="h-4 w-4" />
            New chat
          </button>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-md hover:bg-accent transition-colors duration-150"
            aria-label="Close sidebar"
          >
            <PanelLeftClose className="h-4 w-4 text-muted-foreground" />
          </button>
        </div>
        <button
          onClick={() =>
            setPermissionMode((p) => (p === 'default' ? 'dangerously-skip' : 'default'))
          }
          className={`flex items-center gap-1.5 w-full rounded px-2 py-1 text-xs transition-colors duration-150 ${
            permissionMode === 'dangerously-skip'
              ? 'bg-red-500/10 text-red-500 hover:bg-red-500/15'
              : 'text-muted-foreground hover:bg-secondary/50'
          }`}
        >
          {permissionMode === 'dangerously-skip' ? (
            <>
              <ShieldOff className="h-3 w-3" />
              Skip permissions
            </>
          ) : (
            <>
              <Shield className="h-3 w-3" />
              Require approval
            </>
          )}
        </button>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto -mx-1 px-1">
        {groupedSessions.length > 0 ? (
          <div className="space-y-5">
            {groupedSessions.map((group) => {
              const hideHeader = groupedSessions.length === 1 && group.label === 'Today';
              return (
              <div key={group.label}>
                {!hideHeader && (
                  <h3 className="px-3 mb-1.5 text-2xs font-medium text-muted-foreground/70 uppercase tracking-wider">
                    {group.label}
                  </h3>
                )}
                <div className="space-y-0.5">
                  {group.sessions.map((session: Session) => (
                    <SessionItem
                      key={session.id}
                      session={session}
                      isActive={session.id === activeSessionId}
                      isNew={session.id === justCreatedId}
                      onClick={() => handleSessionClick(session.id)}
                    />
                  ))}
                </div>
              </div>
              );
            })}
          </div>
        ) : (
          <div className="flex items-center justify-center h-32">
            <p className="text-sm text-muted-foreground/60">No conversations yet</p>
          </div>
        )}
      </div>
    </div>
  );
}
