import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../lib/api';
import { useAppStore } from '../../stores/app-store';
import { SessionItem } from './SessionItem';
import { Plus } from 'lucide-react';
import type { Session } from '@shared/types';

export function SessionSidebar() {
  const queryClient = useQueryClient();
  const { activeSessionId, setActiveSession } = useAppStore();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [permissionMode, setPermissionMode] = useState<'default' | 'dangerously-skip'>('default');

  const { data: sessions = [] } = useQuery({
    queryKey: ['sessions'],
    queryFn: api.listSessions,
  });

  const createMutation = useMutation({
    mutationFn: api.createSession,
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      setActiveSession(session.id);
      setShowCreateForm(false);
      setPermissionMode('default');
    },
  });

  return (
    <div className="flex flex-col h-full p-2">
      {showCreateForm ? (
        <div className="rounded-lg border p-2 mb-2 space-y-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={permissionMode === 'dangerously-skip'}
              onChange={(e) =>
                setPermissionMode(e.target.checked ? 'dangerously-skip' : 'default')
              }
            />
            <span className="text-red-500 font-medium">Skip permissions</span>
          </label>
          {permissionMode === 'dangerously-skip' && (
            <p className="text-xs text-red-500">
              All tool calls will be auto-approved. Cannot be changed after session creation.
            </p>
          )}
          <div className="flex gap-1">
            <button
              onClick={() => createMutation.mutate({ permissionMode })}
              className="flex-1 rounded bg-primary px-2 py-1 text-xs text-primary-foreground hover:bg-primary/90"
            >
              Create
            </button>
            <button
              onClick={() => { setShowCreateForm(false); setPermissionMode('default'); }}
              className="rounded px-2 py-1 text-xs hover:bg-accent"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center gap-2 w-full rounded-lg border border-dashed p-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground mb-2"
        >
          <Plus className="h-4 w-4" />
          New Session
        </button>
      )}

      <div className="flex-1 overflow-y-auto space-y-1">
        {sessions.map((session: Session) => (
          <SessionItem
            key={session.id}
            session={session}
            isActive={session.id === activeSessionId}
            onClick={() => setActiveSession(session.id)}
          />
        ))}
      </div>
    </div>
  );
}
