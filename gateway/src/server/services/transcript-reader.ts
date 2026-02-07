import fs from 'fs/promises';
import path from 'path';
import os from 'os';
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

interface TranscriptLine {
  type: string;
  uuid?: string;
  message?: {
    role: string;
    content: string | ContentBlock[];
  };
  timestamp?: string;
  sessionId?: string;
  permissionMode?: string;
  subtype?: string;
}

interface ContentBlock {
  type: string;
  text?: string;
  name?: string;
  id?: string;
  input?: Record<string, unknown>;
}

class TranscriptReader {
  private projectSlug: string | null = null;

  getProjectSlug(vaultRoot: string): string {
    if (this.projectSlug) return this.projectSlug;
    this.projectSlug = vaultRoot.replace(/\//g, '-');
    return this.projectSlug;
  }

  getTranscriptsDir(vaultRoot: string): string {
    const slug = this.getProjectSlug(vaultRoot);
    return path.join(os.homedir(), '.claude', 'projects', slug);
  }

  /**
   * List all sessions by scanning SDK JSONL transcript files.
   * Extracts metadata (title, timestamps, preview) from file content and stats.
   */
  async listSessions(vaultRoot: string): Promise<Session[]> {
    const transcriptsDir = this.getTranscriptsDir(vaultRoot);

    let files: string[];
    try {
      files = (await fs.readdir(transcriptsDir)).filter(f => f.endsWith('.jsonl'));
    } catch {
      return [];
    }

    const sessions: Session[] = [];

    for (const file of files) {
      const sessionId = file.replace('.jsonl', '');
      const filePath = path.join(transcriptsDir, file);

      try {
        const meta = await this.extractSessionMeta(filePath, sessionId);
        sessions.push(meta);
      } catch {
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
  async getSession(vaultRoot: string, sessionId: string): Promise<Session | null> {
    const filePath = path.join(this.getTranscriptsDir(vaultRoot), `${sessionId}.jsonl`);
    try {
      return await this.extractSessionMeta(filePath, sessionId);
    } catch {
      return null;
    }
  }

  /**
   * Extract session metadata from a JSONL file.
   * Reads first ~20 lines for title/permissionMode, and uses file stat for timestamps.
   */
  private async extractSessionMeta(filePath: string, sessionId: string): Promise<Session> {
    const stat = await fs.stat(filePath);
    const content = await fs.readFile(filePath, 'utf-8');
    const lines = content.split('\n').filter(l => l.trim());

    let firstUserMessage = '';
    let lastUserMessage = '';
    let permissionMode: 'default' | 'dangerously-skip' = 'default';
    let firstTimestamp = '';

    for (const line of lines) {
      let parsed: TranscriptLine;
      try {
        parsed = JSON.parse(line);
      } catch {
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

      // Extract user messages for title and preview
      if (parsed.type === 'user' && parsed.message) {
        const text = this.extractTextContent(parsed.message.content);
        if (text.startsWith('<local-command') || text.startsWith('<command-name>')) {
          continue;
        }
        const cleanText = this.stripSystemTags(text);
        if (!cleanText.trim()) continue;

        if (!firstUserMessage) {
          firstUserMessage = cleanText.trim();
        }
        lastUserMessage = cleanText.trim();
      }
    }

    const title = firstUserMessage
      ? firstUserMessage.slice(0, 80) + (firstUserMessage.length > 80 ? '...' : '')
      : `Session ${sessionId.slice(0, 8)}`;

    const preview = lastUserMessage
      ? lastUserMessage.slice(0, 100) + (lastUserMessage.length > 100 ? '...' : '')
      : undefined;

    return {
      id: sessionId,
      title,
      createdAt: firstTimestamp || stat.birthtime.toISOString(),
      updatedAt: stat.mtime.toISOString(),
      lastMessagePreview: preview,
      permissionMode,
    };
  }

  /**
   * Read messages from an SDK session transcript.
   */
  async readTranscript(
    vaultRoot: string,
    sessionId: string
  ): Promise<HistoryMessage[]> {
    const transcriptsDir = this.getTranscriptsDir(vaultRoot);
    const filePath = path.join(transcriptsDir, `${sessionId}.jsonl`);

    let content: string;
    try {
      content = await fs.readFile(filePath, 'utf-8');
    } catch {
      return [];
    }

    const messages: HistoryMessage[] = [];
    const lines = content.split('\n').filter(l => l.trim());

    for (const line of lines) {
      let parsed: TranscriptLine;
      try {
        parsed = JSON.parse(line);
      } catch {
        continue;
      }

      if (parsed.type === 'user' && parsed.message) {
        const text = this.extractTextContent(parsed.message.content);
        if (text.startsWith('<local-command') || text.startsWith('<command-name>')) {
          continue;
        }
        const cleanText = this.stripSystemTags(text);
        if (!cleanText.trim()) continue;

        messages.push({
          id: parsed.uuid || crypto.randomUUID(),
          role: 'user',
          content: cleanText,
        });
      } else if (parsed.type === 'assistant' && parsed.message) {
        const contentBlocks = parsed.message.content;
        if (!Array.isArray(contentBlocks)) continue;

        const textParts: string[] = [];
        const toolCalls: HistoryToolCall[] = [];

        for (const block of contentBlocks) {
          if (block.type === 'text' && block.text) {
            textParts.push(block.text);
          } else if (block.type === 'tool_use' && block.name && block.id) {
            toolCalls.push({
              toolCallId: block.id,
              toolName: block.name,
              status: 'complete',
            });
          }
        }

        const text = textParts.join('\n').trim();
        if (!text && toolCalls.length === 0) continue;

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
  async listTranscripts(vaultRoot: string): Promise<string[]> {
    const transcriptsDir = this.getTranscriptsDir(vaultRoot);
    try {
      const files = await fs.readdir(transcriptsDir);
      return files
        .filter(f => f.endsWith('.jsonl'))
        .map(f => f.replace('.jsonl', ''));
    } catch {
      return [];
    }
  }

  private extractTextContent(content: string | ContentBlock[]): string {
    if (typeof content === 'string') return content;
    if (!Array.isArray(content)) return '';
    return content
      .filter(b => b.type === 'text' && b.text)
      .map(b => b.text!)
      .join('\n');
  }

  private stripSystemTags(text: string): string {
    return text.replace(/<system-reminder>[\s\S]*?<\/system-reminder>/g, '').trim();
  }
}

export const transcriptReader = new TranscriptReader();
