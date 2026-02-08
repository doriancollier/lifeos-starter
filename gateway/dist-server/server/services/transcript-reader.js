import fs from 'fs/promises';
import path from 'path';
import os from 'os';
class TranscriptReader {
    projectSlug = null;
    metaCache = new Map();
    getProjectSlug(vaultRoot) {
        if (this.projectSlug)
            return this.projectSlug;
        this.projectSlug = vaultRoot.replace(/\//g, '-');
        return this.projectSlug;
    }
    getTranscriptsDir(vaultRoot) {
        const slug = this.getProjectSlug(vaultRoot);
        return path.join(os.homedir(), '.claude', 'projects', slug);
    }
    /**
     * List all sessions by scanning SDK JSONL transcript files.
     * Extracts metadata (title, timestamps, preview) from file content and stats.
     */
    async listSessions(vaultRoot) {
        const transcriptsDir = this.getTranscriptsDir(vaultRoot);
        let files;
        try {
            files = (await fs.readdir(transcriptsDir)).filter(f => f.endsWith('.jsonl'));
        }
        catch {
            return [];
        }
        const sessions = [];
        for (const file of files) {
            const sessionId = file.replace('.jsonl', '');
            const filePath = path.join(transcriptsDir, file);
            try {
                const fileStat = await fs.stat(filePath);
                const cached = this.metaCache.get(sessionId);
                if (cached && cached.mtimeMs === fileStat.mtimeMs) {
                    sessions.push(cached.session);
                    continue;
                }
                const meta = await this.extractSessionMeta(filePath, sessionId, fileStat);
                this.metaCache.set(sessionId, { session: meta, mtimeMs: fileStat.mtimeMs });
                sessions.push(meta);
            }
            catch {
                // Skip unreadable files
            }
        }
        // Sort by updatedAt descending (most recent first)
        sessions.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
        return sessions;
    }
    /**
     * Get metadata for a single session.
     */
    async getSession(vaultRoot, sessionId) {
        const filePath = path.join(this.getTranscriptsDir(vaultRoot), `${sessionId}.jsonl`);
        try {
            return await this.extractSessionMeta(filePath, sessionId);
        }
        catch {
            return null;
        }
    }
    /**
     * Extract session metadata from a JSONL file.
     * Reads only the first ~8KB for title/permissionMode, and uses file stat for timestamps.
     */
    async extractSessionMeta(filePath, sessionId, fileStat) {
        const stat = fileStat ?? await fs.stat(filePath);
        // Read only the head of the file (8KB) — metadata is always in the first few lines
        const fileHandle = await fs.open(filePath, 'r');
        let chunk;
        try {
            const buffer = Buffer.alloc(8192);
            const { bytesRead } = await fileHandle.read(buffer, 0, 8192, 0);
            chunk = buffer.toString('utf-8', 0, bytesRead);
        }
        finally {
            await fileHandle.close();
        }
        const lines = chunk.split('\n').filter(l => l.trim());
        let firstUserMessage = '';
        let permissionMode = 'default';
        let firstTimestamp = '';
        for (const line of lines) {
            let parsed;
            try {
                parsed = JSON.parse(line);
            }
            catch {
                continue;
            }
            // Extract permission mode from init message
            if (parsed.type === 'system' && parsed.subtype === 'init' && parsed.permissionMode) {
                if (parsed.permissionMode === 'bypassPermissions') {
                    permissionMode = 'dangerously-skip';
                }
            }
            // Extract timestamps
            if (parsed.timestamp && !firstTimestamp) {
                firstTimestamp = parsed.timestamp;
            }
            // Extract first user message for title
            if (!firstUserMessage && parsed.type === 'user' && parsed.message) {
                const text = this.extractTextContent(parsed.message.content);
                if (text.startsWith('<local-command') || text.startsWith('<command-name>')) {
                    continue;
                }
                const cleanText = this.stripSystemTags(text);
                if (!cleanText.trim())
                    continue;
                firstUserMessage = cleanText.trim();
            }
            // Once we have all metadata, stop early
            if (firstUserMessage && firstTimestamp)
                break;
        }
        const title = firstUserMessage
            ? firstUserMessage.slice(0, 80) + (firstUserMessage.length > 80 ? '...' : '')
            : `Session ${sessionId.slice(0, 8)}`;
        return {
            id: sessionId,
            title,
            createdAt: firstTimestamp || stat.birthtime.toISOString(),
            updatedAt: stat.mtime.toISOString(),
            lastMessagePreview: undefined,
            permissionMode,
        };
    }
    /**
     * Read messages from an SDK session transcript.
     */
    async readTranscript(vaultRoot, sessionId) {
        const transcriptsDir = this.getTranscriptsDir(vaultRoot);
        const filePath = path.join(transcriptsDir, `${sessionId}.jsonl`);
        let content;
        try {
            content = await fs.readFile(filePath, 'utf-8');
        }
        catch {
            return [];
        }
        const messages = [];
        const lines = content.split('\n').filter(l => l.trim());
        for (const line of lines) {
            let parsed;
            try {
                parsed = JSON.parse(line);
            }
            catch {
                continue;
            }
            if (parsed.type === 'user' && parsed.message) {
                const text = this.extractTextContent(parsed.message.content);
                if (text.startsWith('<local-command') || text.startsWith('<command-name>')) {
                    continue;
                }
                const cleanText = this.stripSystemTags(text);
                if (!cleanText.trim())
                    continue;
                messages.push({
                    id: parsed.uuid || crypto.randomUUID(),
                    role: 'user',
                    content: cleanText,
                });
            }
            else if (parsed.type === 'assistant' && parsed.message) {
                const contentBlocks = parsed.message.content;
                if (!Array.isArray(contentBlocks))
                    continue;
                const textParts = [];
                const toolCalls = [];
                for (const block of contentBlocks) {
                    if (block.type === 'text' && block.text) {
                        textParts.push(block.text);
                    }
                    else if (block.type === 'tool_use' && block.name && block.id) {
                        toolCalls.push({
                            toolCallId: block.id,
                            toolName: block.name,
                            status: 'complete',
                        });
                    }
                }
                const text = textParts.join('\n').trim();
                if (!text && toolCalls.length === 0)
                    continue;
                messages.push({
                    id: parsed.uuid || crypto.randomUUID(),
                    role: 'assistant',
                    content: text,
                    toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
                });
            }
        }
        return messages;
    }
    /**
     * List available SDK session transcript IDs.
     */
    async listTranscripts(vaultRoot) {
        const transcriptsDir = this.getTranscriptsDir(vaultRoot);
        try {
            const files = await fs.readdir(transcriptsDir);
            return files
                .filter(f => f.endsWith('.jsonl'))
                .map(f => f.replace('.jsonl', ''));
        }
        catch {
            return [];
        }
    }
    extractTextContent(content) {
        if (typeof content === 'string')
            return content;
        if (!Array.isArray(content))
            return '';
        return content
            .filter(b => b.type === 'text' && b.text)
            .map(b => b.text)
            .join('\n');
    }
    stripSystemTags(text) {
        return text.replace(/<system-reminder>[\s\S]*?<\/system-reminder>/g, '').trim();
    }
}
export const transcriptReader = new TranscriptReader();
//# sourceMappingURL=transcript-reader.js.map