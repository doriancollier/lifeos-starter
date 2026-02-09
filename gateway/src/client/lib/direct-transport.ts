import type { Transport } from '@shared/transport';
import type {
  StreamEvent,
  Session,
  CreateSessionRequest,
  UpdateSessionRequest,
  PermissionMode,
  HistoryMessage,
  CommandRegistry,
  TaskItem,
} from '@shared/types';

export interface DirectTransportServices {
  agentManager: {
    ensureSession(
      id: string,
      opts: { permissionMode: PermissionMode },
    ): void;
    sendMessage(
      id: string,
      content: string,
      opts?: { permissionMode?: PermissionMode },
    ): AsyncGenerator<StreamEvent>;
    approveTool(
      sessionId: string,
      toolCallId: string,
      approved: boolean,
    ): boolean;
    submitAnswers(
      sessionId: string,
      toolCallId: string,
      answers: Record<string, string>,
    ): boolean;
    updateSession(
      sessionId: string,
      opts: { permissionMode?: PermissionMode; model?: string },
    ): boolean;
  };
  transcriptReader: {
    listSessions(vaultRoot: string): Promise<Session[]>;
    getSession(vaultRoot: string, id: string): Promise<Session | null>;
    readTranscript(vaultRoot: string, id: string): Promise<HistoryMessage[]>;
    readTasks(vaultRoot: string, id: string): Promise<TaskItem[]>;
  };
  commandRegistry: {
    getCommands(forceRefresh?: boolean): Promise<CommandRegistry>;
  };
  vaultRoot: string;
}

export class DirectTransport implements Transport {
  constructor(private services: DirectTransportServices) {}

  async createSession(opts: CreateSessionRequest): Promise<Session> {
    const id = crypto.randomUUID();
    const permissionMode = opts.permissionMode ?? 'default';
    this.services.agentManager.ensureSession(id, { permissionMode });
    const now = new Date().toISOString();
    return {
      id,
      title: `Session ${id.slice(0, 8)}`,
      createdAt: now,
      updatedAt: now,
      permissionMode,
    };
  }

  async listSessions(): Promise<Session[]> {
    return this.services.transcriptReader.listSessions(
      this.services.vaultRoot,
    );
  }

  async getSession(id: string): Promise<Session> {
    const session = await this.services.transcriptReader.getSession(
      this.services.vaultRoot,
      id,
    );
    if (!session) {
      throw new Error(`Session not found: ${id}`);
    }
    return session;
  }

  async updateSession(id: string, opts: UpdateSessionRequest): Promise<Session> {
    const updated = this.services.agentManager.updateSession(id, opts);
    if (!updated) throw new Error(`Session not found: ${id}`);
    return this.getSession(id);
  }

  async getMessages(
    sessionId: string,
  ): Promise<{ messages: HistoryMessage[] }> {
    const messages = await this.services.transcriptReader.readTranscript(
      this.services.vaultRoot,
      sessionId,
    );
    return { messages };
  }

  async sendMessage(
    sessionId: string,
    content: string,
    onEvent: (event: StreamEvent) => void,
    signal?: AbortSignal,
  ): Promise<void> {
    const generator = this.services.agentManager.sendMessage(
      sessionId,
      content,
    );
    for await (const event of generator) {
      if (signal?.aborted) break;
      onEvent(event);
    }
  }

  async approveTool(
    sessionId: string,
    toolCallId: string,
  ): Promise<{ ok: boolean }> {
    const result = this.services.agentManager.approveTool(
      sessionId,
      toolCallId,
      true,
    );
    return { ok: result };
  }

  async denyTool(
    sessionId: string,
    toolCallId: string,
  ): Promise<{ ok: boolean }> {
    const result = this.services.agentManager.approveTool(
      sessionId,
      toolCallId,
      false,
    );
    return { ok: result };
  }

  async submitAnswers(
    sessionId: string,
    toolCallId: string,
    answers: Record<string, string>,
  ): Promise<{ ok: boolean }> {
    const ok = this.services.agentManager.submitAnswers(
      sessionId,
      toolCallId,
      answers,
    );
    return { ok };
  }

  async getTasks(sessionId: string): Promise<{ tasks: TaskItem[] }> {
    const tasks = await this.services.transcriptReader.readTasks(
      this.services.vaultRoot,
      sessionId,
    );
    return { tasks };
  }

  async getCommands(refresh?: boolean): Promise<CommandRegistry> {
    return this.services.commandRegistry.getCommands(refresh);
  }

  async health(): Promise<{ status: string; version: string; uptime: number }> {
    return { status: 'ok', version: '0.1.0', uptime: 0 };
  }
}
