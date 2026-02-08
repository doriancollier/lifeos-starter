import type {
  Session,
  CreateSessionRequest,
  CommandRegistry,
  HistoryMessage,
  StreamEvent,
} from '@shared/types';
import type { Transport } from '@shared/transport';

async function fetchJSON<T>(baseUrl: string, url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${baseUrl}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(error.error || `HTTP ${res.status}`);
  }
  return res.json();
}

export class HttpTransport implements Transport {
  constructor(private baseUrl: string) {}

  createSession(opts: CreateSessionRequest): Promise<Session> {
    return fetchJSON<Session>(this.baseUrl, '/sessions', {
      method: 'POST',
      body: JSON.stringify(opts),
    });
  }

  listSessions(): Promise<Session[]> {
    return fetchJSON<Session[]>(this.baseUrl, '/sessions');
  }

  getSession(id: string): Promise<Session> {
    return fetchJSON<Session>(this.baseUrl, `/sessions/${id}`);
  }

  getMessages(sessionId: string): Promise<{ messages: HistoryMessage[] }> {
    return fetchJSON<{ messages: HistoryMessage[] }>(this.baseUrl, `/sessions/${sessionId}/messages`);
  }

  async sendMessage(
    sessionId: string,
    content: string,
    onEvent: (event: StreamEvent) => void,
    signal?: AbortSignal,
  ): Promise<void> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
      signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      let eventType = '';
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith('data: ') && eventType) {
          const data = JSON.parse(line.slice(6));
          onEvent({ type: eventType, data } as StreamEvent);
          eventType = '';
        }
      }
    }
  }

  approveTool(sessionId: string, toolCallId: string): Promise<{ ok: boolean }> {
    return fetchJSON<{ ok: boolean }>(this.baseUrl, `/sessions/${sessionId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ toolCallId }),
    });
  }

  denyTool(sessionId: string, toolCallId: string): Promise<{ ok: boolean }> {
    return fetchJSON<{ ok: boolean }>(this.baseUrl, `/sessions/${sessionId}/deny`, {
      method: 'POST',
      body: JSON.stringify({ toolCallId }),
    });
  }

  getCommands(refresh = false): Promise<CommandRegistry> {
    return fetchJSON<CommandRegistry>(this.baseUrl, `/commands${refresh ? '?refresh=true' : ''}`);
  }

  health(): Promise<{ status: string; version: string; uptime: number }> {
    return fetchJSON<{ status: string; version: string; uptime: number }>(this.baseUrl, '/health');
  }
}
