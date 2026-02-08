import path from 'path';
import { fileURLToPath } from 'url';
import { query } from '@anthropic-ai/claude-agent-sdk';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
class AgentManager {
    sessions = new Map();
    SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
    /**
     * Start or resume an agent session.
     * For new sessions, sdkSessionId is assigned after the first query() init message.
     * For resumed sessions, the sessionId IS the sdkSessionId.
     */
    ensureSession(sessionId, opts) {
        if (!this.sessions.has(sessionId)) {
            this.sessions.set(sessionId, {
                sdkSessionId: sessionId,
                lastActivity: Date.now(),
                permissionMode: opts.permissionMode,
                hasStarted: false,
            });
        }
    }
    async *sendMessage(sessionId, content, opts) {
        // Auto-create session if it doesn't exist (for resuming SDK sessions)
        if (!this.sessions.has(sessionId)) {
            this.ensureSession(sessionId, {
                permissionMode: opts?.permissionMode ?? 'default',
            });
        }
        const session = this.sessions.get(sessionId);
        session.lastActivity = Date.now();
        const vaultRoot = path.resolve(__dirname, '../../../../');
        const sdkOptions = {
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
        }
        else {
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
                    setToolState: (tool, name, id) => {
                        inTool = tool;
                        currentToolName = name;
                        currentToolId = id;
                    },
                })) {
                    if (event.type === 'done')
                        emittedDone = true;
                    yield event;
                }
            }
        }
        catch (err) {
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
    async *mapSdkMessage(message, session, sessionId, toolState) {
        // Capture session ID from init (for new sessions where SDK assigns the ID)
        if (message.type === 'system' && 'subtype' in message && message.subtype === 'init') {
            session.sdkSessionId = message.session_id;
            session.hasStarted = true;
            return;
        }
        if (message.type === 'stream_event') {
            const event = message.event;
            const eventType = event.type;
            if (eventType === 'content_block_start') {
                const contentBlock = event.content_block;
                if (contentBlock?.type === 'tool_use') {
                    toolState.setToolState(true, contentBlock.name, contentBlock.id);
                    yield {
                        type: 'tool_call_start',
                        data: {
                            toolCallId: contentBlock.id,
                            toolName: contentBlock.name,
                            status: 'running',
                        },
                    };
                }
            }
            else if (eventType === 'content_block_delta') {
                const delta = event.delta;
                if (delta?.type === 'text_delta' && !toolState.inTool) {
                    yield { type: 'text_delta', data: { text: delta.text } };
                }
                else if (delta?.type === 'input_json_delta' && toolState.inTool) {
                    yield {
                        type: 'tool_call_delta',
                        data: {
                            toolCallId: toolState.currentToolId,
                            toolName: toolState.currentToolName,
                            input: delta.partial_json,
                            status: 'running',
                        },
                    };
                }
            }
            else if (eventType === 'content_block_stop') {
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
            const summary = message;
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
    approveTool(sessionId, _toolCallId, approved) {
        const session = this.sessions.get(sessionId);
        if (!session?.pendingApproval)
            return false;
        session.pendingApproval.resolve(approved);
        session.pendingApproval = undefined;
        return true;
    }
    checkSessionHealth() {
        const now = Date.now();
        for (const [id, session] of this.sessions) {
            if (now - session.lastActivity > this.SESSION_TIMEOUT_MS) {
                this.sessions.delete(id);
            }
        }
    }
    hasSession(sessionId) {
        return this.sessions.has(sessionId);
    }
    /**
     * Get the actual SDK session ID (may differ from input if SDK assigned a new one).
     */
    getSdkSessionId(sessionId) {
        return this.sessions.get(sessionId)?.sdkSessionId;
    }
}
export const agentManager = new AgentManager();
//# sourceMappingURL=agent-manager.js.map