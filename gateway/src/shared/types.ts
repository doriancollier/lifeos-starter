// === Session Types ===

export interface Session {
  id: string; // SDK session ID (UUID from JSONL filename)
  title: string;
  createdAt: string;
  updatedAt: string;
  lastMessagePreview?: string;
  permissionMode: 'default' | 'dangerously-skip';
}

export interface CreateSessionRequest {
  permissionMode?: 'default' | 'dangerously-skip';
}

export interface SendMessageRequest {
  content: string;
}

// === Message Types (SSE stream events) ===

export type StreamEventType =
  | 'text_delta'
  | 'tool_call_start'
  | 'tool_call_delta'
  | 'tool_call_end'
  | 'tool_result'
  | 'approval_required'
  | 'error'
  | 'done';

export interface StreamEvent {
  type: StreamEventType;
  data: TextDelta | ToolCallEvent | ApprovalEvent | ErrorEvent | DoneEvent;
}

export interface TextDelta {
  text: string;
}

export interface ToolCallEvent {
  toolCallId: string;
  toolName: string;
  input?: string;
  result?: string;
  status: 'pending' | 'running' | 'complete' | 'error';
}

export interface ApprovalEvent {
  toolCallId: string;
  toolName: string;
  input: string;
}

export interface ErrorEvent {
  message: string;
  code?: string;
}

export interface DoneEvent {
  sessionId: string;
}

// === Chat History Types ===

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

// === Command Types ===

export interface CommandEntry {
  namespace: string;
  command: string;
  fullCommand: string;
  description: string;
  argumentHint?: string;
  allowedTools?: string[];
  filePath: string;
}

export interface CommandRegistry {
  commands: CommandEntry[];
  lastScanned: string;
}
