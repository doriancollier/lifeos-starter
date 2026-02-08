import type { Session } from '../../shared/types';
export interface HistoryMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    toolCalls?: HistoryToolCall[];
    timestamp?: string;
}
export interface HistoryToolCall {
    toolCallId: string;
    toolName: string;
    status: 'complete';
}
declare class TranscriptReader {
    private projectSlug;
    private metaCache;
    getProjectSlug(vaultRoot: string): string;
    getTranscriptsDir(vaultRoot: string): string;
    /**
     * List all sessions by scanning SDK JSONL transcript files.
     * Extracts metadata (title, timestamps, preview) from file content and stats.
     */
    listSessions(vaultRoot: string): Promise<Session[]>;
    /**
     * Get metadata for a single session.
     */
    getSession(vaultRoot: string, sessionId: string): Promise<Session | null>;
    /**
     * Extract session metadata from a JSONL file.
     * Reads only the first ~8KB for title/permissionMode, and uses file stat for timestamps.
     */
    private extractSessionMeta;
    /**
     * Read messages from an SDK session transcript.
     */
    readTranscript(vaultRoot: string, sessionId: string): Promise<HistoryMessage[]>;
    /**
     * List available SDK session transcript IDs.
     */
    listTranscripts(vaultRoot: string): Promise<string[]>;
    private extractTextContent;
    private stripSystemTags;
}
export declare const transcriptReader: TranscriptReader;
export {};
//# sourceMappingURL=transcript-reader.d.ts.map