import { z } from 'zod';
import { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi';
extendZodWithOpenApi(z);
// === Enums ===
export const PermissionModeSchema = z
    .enum(['default', 'plan', 'acceptEdits', 'bypassPermissions'])
    .openapi('PermissionMode');
export const TaskStatusSchema = z
    .enum(['pending', 'in_progress', 'completed'])
    .openapi('TaskStatus');
export const StreamEventTypeSchema = z
    .enum([
    'text_delta',
    'tool_call_start',
    'tool_call_delta',
    'tool_call_end',
    'tool_result',
    'approval_required',
    'question_prompt',
    'error',
    'done',
    'session_status',
    'task_update',
])
    .openapi('StreamEventType');
// === Question / Option Types ===
export const QuestionOptionSchema = z
    .object({
    label: z.string(),
    description: z.string().optional(),
})
    .openapi('QuestionOption');
export const QuestionItemSchema = z
    .object({
    header: z.string(),
    question: z.string(),
    options: z.array(QuestionOptionSchema),
    multiSelect: z.boolean(),
})
    .openapi('QuestionItem');
// === Session Types ===
export const SessionSchema = z
    .object({
    id: z.string().uuid(),
    title: z.string(),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
    lastMessagePreview: z.string().optional(),
    permissionMode: PermissionModeSchema,
    model: z.string().optional(),
    contextTokens: z.number().int().optional(),
    cwd: z.string().optional(),
})
    .openapi('Session');
export const CreateSessionRequestSchema = z
    .object({
    permissionMode: PermissionModeSchema.optional(),
    cwd: z.string().optional(),
})
    .openapi('CreateSessionRequest');
export const UpdateSessionRequestSchema = z
    .object({
    permissionMode: PermissionModeSchema.optional(),
    model: z.string().optional(),
})
    .openapi('UpdateSessionRequest');
export const SendMessageRequestSchema = z
    .object({
    content: z.string().min(1, 'content is required'),
})
    .openapi('SendMessageRequest');
export const ApprovalRequestSchema = z
    .object({
    toolCallId: z.string(),
})
    .openapi('ApprovalRequest');
export const SubmitAnswersRequestSchema = z
    .object({
    toolCallId: z.string(),
    answers: z.record(z.string(), z.string()),
})
    .openapi('SubmitAnswersRequest');
export const ListSessionsQuerySchema = z
    .object({
    limit: z.coerce.number().int().min(1).max(500).optional().default(200),
    cwd: z.string().optional(),
})
    .openapi('ListSessionsQuery');
export const CommandsQuerySchema = z
    .object({
    refresh: z.enum(['true', 'false']).optional(),
})
    .openapi('CommandsQuery');
// === SSE Event Types ===
export const TextDeltaSchema = z
    .object({
    text: z.string(),
})
    .openapi('TextDelta');
const ToolCallStatusSchema = z.enum(['pending', 'running', 'complete', 'error']);
export const ToolCallEventSchema = z
    .object({
    toolCallId: z.string(),
    toolName: z.string(),
    input: z.string().optional(),
    result: z.string().optional(),
    status: ToolCallStatusSchema,
})
    .openapi('ToolCallEvent');
export const ApprovalEventSchema = z
    .object({
    toolCallId: z.string(),
    toolName: z.string(),
    input: z.string(),
})
    .openapi('ApprovalEvent');
export const QuestionPromptEventSchema = z
    .object({
    toolCallId: z.string(),
    questions: z.array(QuestionItemSchema),
})
    .openapi('QuestionPromptEvent');
export const ErrorEventSchema = z
    .object({
    message: z.string(),
    code: z.string().optional(),
})
    .openapi('ErrorEvent');
export const DoneEventSchema = z
    .object({
    sessionId: z.string(),
})
    .openapi('DoneEvent');
export const SessionStatusEventSchema = z
    .object({
    sessionId: z.string(),
    model: z.string().optional(),
    costUsd: z.number().optional(),
    contextTokens: z.number().int().optional(),
    contextMaxTokens: z.number().int().optional(),
})
    .openapi('SessionStatusEvent');
export const TaskItemSchema = z
    .object({
    id: z.string(),
    subject: z.string(),
    description: z.string().optional(),
    activeForm: z.string().optional(),
    status: TaskStatusSchema,
    blockedBy: z.array(z.string()).optional(),
    blocks: z.array(z.string()).optional(),
    owner: z.string().optional(),
})
    .openapi('TaskItem');
export const TaskUpdateEventSchema = z
    .object({
    action: z.enum(['create', 'update', 'snapshot']),
    task: TaskItemSchema,
})
    .openapi('TaskUpdateEvent');
export const StreamEventSchema = z
    .object({
    type: StreamEventTypeSchema,
    data: z.union([
        TextDeltaSchema,
        ToolCallEventSchema,
        ApprovalEventSchema,
        QuestionPromptEventSchema,
        ErrorEventSchema,
        DoneEventSchema,
        SessionStatusEventSchema,
        TaskUpdateEventSchema,
    ]),
})
    .openapi('StreamEvent');
// === Message Part Types ===
export const TextPartSchema = z
    .object({
    type: z.literal('text'),
    text: z.string(),
})
    .openapi('TextPart');
export const ToolCallPartSchema = z
    .object({
    type: z.literal('tool_call'),
    toolCallId: z.string(),
    toolName: z.string(),
    input: z.string().optional(),
    result: z.string().optional(),
    status: ToolCallStatusSchema,
    interactiveType: z.enum(['approval', 'question']).optional(),
    questions: z.array(QuestionItemSchema).optional(),
    answers: z.record(z.string(), z.string()).optional(),
})
    .openapi('ToolCallPart');
export const MessagePartSchema = z.discriminatedUnion('type', [
    TextPartSchema,
    ToolCallPartSchema,
]);
// === Chat History Types ===
export const HistoryToolCallSchema = z
    .object({
    toolCallId: z.string(),
    toolName: z.string(),
    input: z.string().optional(),
    result: z.string().optional(),
    status: z.literal('complete'),
    questions: z.array(QuestionItemSchema).optional(),
    answers: z.record(z.string(), z.string()).optional(),
})
    .openapi('HistoryToolCall');
export const HistoryMessageSchema = z
    .object({
    id: z.string(),
    role: z.enum(['user', 'assistant']),
    content: z.string(),
    toolCalls: z.array(HistoryToolCallSchema).optional(),
    parts: z.array(MessagePartSchema).optional(),
    timestamp: z.string().optional(),
})
    .openapi('HistoryMessage');
// === Command Types ===
export const CommandEntrySchema = z
    .object({
    namespace: z.string(),
    command: z.string(),
    fullCommand: z.string(),
    description: z.string(),
    argumentHint: z.string().optional(),
    allowedTools: z.array(z.string()).optional(),
    filePath: z.string(),
})
    .openapi('CommandEntry');
export const CommandRegistrySchema = z
    .object({
    commands: z.array(CommandEntrySchema),
    lastScanned: z.string(),
})
    .openapi('CommandRegistry');
// === Directory Browsing Types ===
export const BrowseDirectoryQuerySchema = z
    .object({
    path: z.string().min(1).optional(),
    showHidden: z.coerce.boolean().optional().default(false),
})
    .openapi('BrowseDirectoryQuery');
export const DirectoryEntrySchema = z
    .object({
    name: z.string(),
    path: z.string(),
    isDirectory: z.boolean(),
})
    .openapi('DirectoryEntry');
export const BrowseDirectoryResponseSchema = z
    .object({
    path: z.string(),
    entries: z.array(DirectoryEntrySchema),
    parent: z.string().nullable(),
})
    .openapi('BrowseDirectoryResponse');
// === Health Response ===
export const HealthResponseSchema = z
    .object({
    status: z.string(),
    version: z.string(),
    uptime: z.number(),
})
    .openapi('HealthResponse');
// === Error Response ===
export const ErrorResponseSchema = z
    .object({
    error: z.string(),
    details: z.any().optional(),
})
    .openapi('ErrorResponse');
//# sourceMappingURL=schemas.js.map