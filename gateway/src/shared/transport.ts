import type {
  Session,
  CreateSessionRequest,
  CommandRegistry,
  HistoryMessage,
  StreamEvent,
} from './types';

export interface Transport {
  createSession(opts: CreateSessionRequest): Promise<Session>;
  listSessions(): Promise<Session[]>;
  getSession(id: string): Promise<Session>;
  getMessages(sessionId: string): Promise<{ messages: HistoryMessage[] }>;
  sendMessage(
    sessionId: string,
    content: string,
    onEvent: (event: StreamEvent) => void,
    signal?: AbortSignal,
  ): Promise<void>;
  approveTool(
    sessionId: string,
    toolCallId: string,
  ): Promise<{ ok: boolean }>;
  denyTool(
    sessionId: string,
    toolCallId: string,
  ): Promise<{ ok: boolean }>;
  getCommands(refresh?: boolean): Promise<CommandRegistry>;
  health(): Promise<{ status: string; version: string; uptime: number }>;
}
