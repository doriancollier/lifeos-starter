import type { Session, HistoryMessage, HistoryToolCall, TaskItem } from '../../shared/types.js';
export type { HistoryMessage, HistoryToolCall };
export declare class TranscriptReader {
    private metaCache;
    getProjectSlug(cwd: string): string;
    getTranscriptsDir(vaultRoot: string): string;
    /**
     * List all sessions by scanning SDK JSONL transcript files.
     * Extracts metadata (title, timestamps, preview) from file content and stats.
     */
    listSessions(vaultRoot: string): Promise<Session[]>;
    /**
     * Get metadata for a single session.
     * Reads both head (for title/timestamps) and tail (for latest model/context).
     */
    getSession(vaultRoot: string, sessionId: string): Promise<Session | null>;
    /**
     * Read the tail of a JSONL file to get the most recent model, permissionMode, and context tokens.
     * Reads the last ~16KB which typically contains the final assistant messages.
     */
    private readTailStatus;
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
    /**
     * Read task state from an SDK session transcript.
     * Parses TaskCreate/TaskUpdate tool_use blocks and reconstructs final state.
     */
    readTasks(vaultRoot: string, sessionId: string): Promise<TaskItem[]>;
    private extractToolResultContent;
    private extractTextContent;
    private stripSystemTags;
}
export declare const transcriptReader: TranscriptReader;
//# sourceMappingURL=transcript-reader.d.ts.map