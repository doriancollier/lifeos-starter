import type {
  Session,
  CreateSessionRequest,
  UpdateSessionRequest,
  CommandRegistry,
  HistoryMessage,
  StreamEvent,
  TaskItem,
} from './types';

export interface Transport {
  createSession(opts: CreateSessionRequest): Promise<Session>;
  listSessions(): Promise<Session[]>;
  getSession(id: string): Promise<Session>;
  updateSession(id: string, opts: UpdateSessionRequest): Promise<Session>;
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
  submitAnswers(
    sessionId: string,
    toolCallId: string,
    answers: Record<string, string>,
  ): Promise<{ ok: boolean }>;
  getTasks(sessionId: string): Promise<{ tasks: TaskItem[] }>;
  getCommands(refresh?: boolean): Promise<CommandRegistry>;
  health(): Promise<{ status: string; version: string; uptime: number }>;
}
