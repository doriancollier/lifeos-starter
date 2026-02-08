import type { StreamEvent } from '../../shared/types';
export declare class AgentManager {
    private sessions;
    private readonly SESSION_TIMEOUT_MS;
    private readonly cwd;
    constructor(cwd?: string);
    /**
     * Start or resume an agent session.
     * For new sessions, sdkSessionId is assigned after the first query() init message.
     * For resumed sessions, the sessionId IS the sdkSessionId.
     */
    ensureSession(sessionId: string, opts: {
        permissionMode: 'default' | 'dangerously-skip';
    }): void;
    sendMessage(sessionId: string, content: string, opts?: {
        permissionMode?: 'default' | 'dangerously-skip';
    }): AsyncGenerator<StreamEvent>;
    private mapSdkMessage;
    approveTool(sessionId: string, _toolCallId: string, approved: boolean): boolean;
    checkSessionHealth(): void;
    hasSession(sessionId: string): boolean;
    /**
     * Get the actual SDK session ID (may differ from input if SDK assigned a new one).
     */
    getSdkSessionId(sessionId: string): string | undefined;
}
export declare const agentManager: AgentManager;
//# sourceMappingURL=agent-manager.d.ts.map