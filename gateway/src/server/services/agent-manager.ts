import path from 'path';
import { fileURLToPath } from 'url';
import { query, type Options, type SDKMessage } from '@anthropic-ai/claude-agent-sdk';
import type { StreamEvent } from '../../shared/types';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

interface AgentSession {
  sdkSessionId: string;
  lastActivity: number;
  permissionMode: 'default' | 'dangerously-skip';
  /** True once the first SDK query has been sent (JSONL file exists) */
  hasStarted: boolean;
  pendingApproval?: {
    toolCallId: string;
    resolve: (approved: boolean) => void;
  };
}

class AgentManager {
  private sessions = new Map<string, AgentSession>();
  private readonly SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

  /**
   * Start or resume an agent session.
   * For new sessions, sdkSessionId is assigned after the first query() init message.
   * For resumed sessions, the sessionId IS the sdkSessionId.
   */
  ensureSession(sessionId: string, opts: {
    permissionMode: 'default' | 'dangerously-skip';
  }): void {
    if (!this.sessions.has(sessionId)) {
      this.sessions.set(sessionId, {
        sdkSessionId: sessionId,
        lastActivity: Date.now(),
        permissionMode: opts.permissionMode,
        hasStarted: false,
      });
    }
  }

  async *sendMessage(
    sessionId: string,
    content: string,
    opts?: { permissionMode?: 'default' | 'dangerously-skip' }
  ): AsyncGenerator<StreamEvent> {
    // Auto-create session if it doesn't exist (for resuming SDK sessions)
    if (!this.sessions.has(sessionId)) {
      this.ensureSession(sessionId, {
        permissionMode: opts?.permissionMode ?? 'default',
      });
    }

    const session = this.sessions.get(sessionId)!;
    session.lastActivity = Date.now();

    const vaultRoot = path.resolve(__dirname, '../../../../');

    const sdkOptions: Options = {
      cwd: vaultRoot,
      includePartialMessages: true,
      settingSources: ['project', 'user'],
    };

    // Only resume if the session has been started (JSONL exists)
    if (session.hasStarted) {
      sdkOptions.resume = session.sdkSessionId;
    }

    if (session.permissionMode === 'dangerously-skip') {
      sdkOptions.permissionMode = 'bypassPermissions';
      sdkOptions.allowDangerouslySkipPermissions = true;
    } else {
      sdkOptions.permissionMode = 'acceptEdits';
    }

    const agentQuery = query({ prompt: content, options: sdkOptions });

    let inTool = false;
    let currentToolName = '';
    let currentToolId = '';
    let emittedDone = false;

    try {
      for await (const message of agentQuery) {
        for await (const event of this.mapSdkMessage(message, session, sessionId, {
          inTool,
          currentToolName,
          currentToolId,
          setToolState: (tool: boolean, name: string, id: string) => {
            inTool = tool;
            currentToolName = name;
            currentToolId = id;
          },
        })) {
          if (event.type === 'done') emittedDone = true;
          yield event;
        }
      }
    } catch (err) {
      yield {
        type: 'error',
        data: {
          message: err instanceof Error ? err.message : 'SDK error',
        },
      };
    }

    if (!emittedDone) {
      yield {
        type: 'done',
        data: { sessionId },
      };
    }
  }

  private async *mapSdkMessage(
    message: SDKMessage,
    session: AgentSession,
    sessionId: string,
    toolState: {
      inTool: boolean;
      currentToolName: string;
      currentToolId: string;
      setToolState: (tool: boolean, name: string, id: string) => void;
    }
  ): AsyncGenerator<StreamEvent> {
    // Capture session ID from init (for new sessions where SDK assigns the ID)
    if (message.type === 'system' && 'subtype' in message && message.subtype === 'init') {
      session.sdkSessionId = message.session_id;
      session.hasStarted = true;
      return;
    }

    if (message.type === 'stream_event') {
      const event = (message as { event: Record<string, unknown> }).event;
      const eventType = event.type as string;

      if (eventType === 'content_block_start') {
        const contentBlock = event.content_block as Record<string, unknown> | undefined;
        if (contentBlock?.type === 'tool_use') {
          toolState.setToolState(true, contentBlock.name as string, contentBlock.id as string);
          yield {
            type: 'tool_call_start',
            data: {
              toolCallId: contentBlock.id as string,
              toolName: contentBlock.name as string,
              status: 'running',
            },
          };
        }
      } else if (eventType === 'content_block_delta') {
        const delta = event.delta as Record<string, unknown> | undefined;
        if (delta?.type === 'text_delta' && !toolState.inTool) {
          yield { type: 'text_delta', data: { text: delta.text as string } };
        } else if (delta?.type === 'input_json_delta' && toolState.inTool) {
          yield {
            type: 'tool_call_delta',
            data: {
              toolCallId: toolState.currentToolId,
              toolName: toolState.currentToolName,
              input: delta.partial_json as string,
              status: 'running',
            },
          };
        }
      } else if (eventType === 'content_block_stop') {
        if (toolState.inTool) {
          yield {
            type: 'tool_call_end',
            data: {
              toolCallId: toolState.currentToolId,
              toolName: toolState.currentToolName,
              status: 'complete',
            },
          };
          toolState.setToolState(false, '', '');
        }
      }
      return;
    }

    if (message.type === 'tool_use_summary') {
      const summary = message as { summary: string; preceding_tool_use_ids: string[] };
      for (const toolUseId of summary.preceding_tool_use_ids) {
        yield {
          type: 'tool_result',
          data: {
            toolCallId: toolUseId,
            toolName: '',
            result: summary.summary,
            status: 'complete',
          },
        };
      }
      return;
    }

    if (message.type === 'result') {
      yield {
        type: 'done',
        data: { sessionId },
      };
    }
  }

  approveTool(sessionId: string, _toolCallId: string, approved: boolean): boolean {
    const session = this.sessions.get(sessionId);
    if (!session?.pendingApproval) return false;
    session.pendingApproval.resolve(approved);
    session.pendingApproval = undefined;
    return true;
  }

  checkSessionHealth(): void {
    const now = Date.now();
    for (const [id, session] of this.sessions) {
      if (now - session.lastActivity > this.SESSION_TIMEOUT_MS) {
        this.sessions.delete(id);
      }
    }
  }

  hasSession(sessionId: string): boolean {
    return this.sessions.has(sessionId);
  }

  /**
   * Get the actual SDK session ID (may differ from input if SDK assigned a new one).
   */
  getSdkSessionId(sessionId: string): string | undefined {
    return this.sessions.get(sessionId)?.sdkSessionId;
  }
}

export const agentManager = new AgentManager();
