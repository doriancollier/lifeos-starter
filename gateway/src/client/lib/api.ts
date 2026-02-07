import type {
  Session,
  CreateSessionRequest,
  CommandRegistry,
  HistoryMessage,
} from '@shared/types';

const BASE_URL = '/api';

async function fetchJSON<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(error.error || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Sessions
  createSession: (body: CreateSessionRequest) =>
    fetchJSON<Session>('/sessions', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  listSessions: () => fetchJSON<Session[]>('/sessions'),

  getSession: (id: string) => fetchJSON<Session>(`/sessions/${id}`),

  // Messages
  getMessages: (sessionId: string) =>
    fetchJSON<{ messages: HistoryMessage[] }>(`/sessions/${sessionId}/messages`),

  getMessageStreamUrl: (sessionId: string) =>
    `${BASE_URL}/sessions/${sessionId}/messages`,

  // Tool approval
  approveTool: (sessionId: string, toolCallId: string) =>
    fetchJSON<{ ok: boolean }>(`/sessions/${sessionId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ toolCallId }),
    }),

  denyTool: (sessionId: string, toolCallId: string) =>
    fetchJSON<{ ok: boolean }>(`/sessions/${sessionId}/deny`, {
      method: 'POST',
      body: JSON.stringify({ toolCallId }),
    }),

  // Commands
  getCommands: (refresh = false) =>
    fetchJSON<CommandRegistry>(`/commands${refresh ? '?refresh=true' : ''}`),

  // Health
  health: () => fetchJSON<{ status: string; version: string; uptime: number }>('/health'),
};
