import type { StreamEvent, PermissionMode, TaskUpdateEvent } from '../../shared/types';
export declare function buildTaskEvent(toolName: string, input: Record<string, unknown>): TaskUpdateEvent | null;
export declare class AgentManager {
    private sessions;
    private readonly SESSION_TIMEOUT_MS;
    private readonly cwd;
    private readonly claudeCliPath;
    constructor(cwd?: string);
    /**
     * Start or resume an agent session.
     * For new sessions, sdkSessionId is assigned after the first query() init message.
     * For resumed sessions, the sessionId IS the sdkSessionId.
     */
    ensureSession(sessionId: string, opts: {
        permissionMode: PermissionMode;
    }): void;
    sendMessage(sessionId: string, content: string, opts?: {
        permissionMode?: PermissionMode;
    }): AsyncGenerator<StreamEvent>;
    private mapSdkMessage;
    updateSession(sessionId: string, opts: {
        permissionMode?: PermissionMode;
        model?: string;
    }): boolean;
    approveTool(sessionId: string, toolCallId: string, approved: boolean): boolean;
    submitAnswers(sessionId: string, toolCallId: string, answers: Record<string, string>): boolean;
    checkSessionHealth(): void;
    hasSession(sessionId: string): boolean;
    /**
     * Get the actual SDK session ID (may differ from input if SDK assigned a new one).
     */
    getSdkSessionId(sessionId: string): string | undefined;
}
export declare const agentManager: AgentManager;
//# sourceMappingURL=agent-manager.d.ts.map