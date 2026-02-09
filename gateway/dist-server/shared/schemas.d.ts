import { z } from 'zod';
export declare const PermissionModeSchema: z.ZodEnum<{
    default: "default";
    plan: "plan";
    acceptEdits: "acceptEdits";
    bypassPermissions: "bypassPermissions";
}>;
export type PermissionMode = z.infer<typeof PermissionModeSchema>;
export declare const TaskStatusSchema: z.ZodEnum<{
    pending: "pending";
    in_progress: "in_progress";
    completed: "completed";
}>;
export type TaskStatus = z.infer<typeof TaskStatusSchema>;
export declare const StreamEventTypeSchema: z.ZodEnum<{
    text_delta: "text_delta";
    tool_call_start: "tool_call_start";
    tool_call_delta: "tool_call_delta";
    tool_call_end: "tool_call_end";
    tool_result: "tool_result";
    approval_required: "approval_required";
    question_prompt: "question_prompt";
    error: "error";
    done: "done";
    session_status: "session_status";
    task_update: "task_update";
}>;
export type StreamEventType = z.infer<typeof StreamEventTypeSchema>;
export declare const QuestionOptionSchema: z.ZodObject<{
    label: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
}, z.core.$strip>;
export type QuestionOption = z.infer<typeof QuestionOptionSchema>;
export declare const QuestionItemSchema: z.ZodObject<{
    header: z.ZodString;
    question: z.ZodString;
    options: z.ZodArray<z.ZodObject<{
        label: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
    }, z.core.$strip>>;
    multiSelect: z.ZodBoolean;
}, z.core.$strip>;
export type QuestionItem = z.infer<typeof QuestionItemSchema>;
export declare const SessionSchema: z.ZodObject<{
    id: z.ZodString;
    title: z.ZodString;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    lastMessagePreview: z.ZodOptional<z.ZodString>;
    permissionMode: z.ZodEnum<{
        default: "default";
        plan: "plan";
        acceptEdits: "acceptEdits";
        bypassPermissions: "bypassPermissions";
    }>;
    model: z.ZodOptional<z.ZodString>;
    contextTokens: z.ZodOptional<z.ZodNumber>;
    cwd: z.ZodOptional<z.ZodString>;
}, z.core.$strip>;
export type Session = z.infer<typeof SessionSchema>;
export declare const CreateSessionRequestSchema: z.ZodObject<{
    permissionMode: z.ZodOptional<z.ZodEnum<{
        default: "default";
        plan: "plan";
        acceptEdits: "acceptEdits";
        bypassPermissions: "bypassPermissions";
    }>>;
}, z.core.$strip>;
export type CreateSessionRequest = z.infer<typeof CreateSessionRequestSchema>;
export declare const UpdateSessionRequestSchema: z.ZodObject<{
    permissionMode: z.ZodOptional<z.ZodEnum<{
        default: "default";
        plan: "plan";
        acceptEdits: "acceptEdits";
        bypassPermissions: "bypassPermissions";
    }>>;
    model: z.ZodOptional<z.ZodString>;
}, z.core.$strip>;
export type UpdateSessionRequest = z.infer<typeof UpdateSessionRequestSchema>;
export declare const SendMessageRequestSchema: z.ZodObject<{
    content: z.ZodString;
}, z.core.$strip>;
export type SendMessageRequest = z.infer<typeof SendMessageRequestSchema>;
export declare const ApprovalRequestSchema: z.ZodObject<{
    toolCallId: z.ZodString;
}, z.core.$strip>;
export type ApprovalRequest = z.infer<typeof ApprovalRequestSchema>;
export declare const SubmitAnswersRequestSchema: z.ZodObject<{
    toolCallId: z.ZodString;
    answers: z.ZodRecord<z.ZodString, z.ZodString>;
}, z.core.$strip>;
export type SubmitAnswersRequest = z.infer<typeof SubmitAnswersRequestSchema>;
export declare const ListSessionsQuerySchema: z.ZodObject<{
    limit: z.ZodDefault<z.ZodOptional<z.ZodCoercedNumber<unknown>>>;
}, z.core.$strip>;
export type ListSessionsQuery = z.infer<typeof ListSessionsQuerySchema>;
export declare const CommandsQuerySchema: z.ZodObject<{
    refresh: z.ZodOptional<z.ZodEnum<{
        true: "true";
        false: "false";
    }>>;
}, z.core.$strip>;
export type CommandsQuery = z.infer<typeof CommandsQuerySchema>;
export declare const TextDeltaSchema: z.ZodObject<{
    text: z.ZodString;
}, z.core.$strip>;
export type TextDelta = z.infer<typeof TextDeltaSchema>;
export declare const ToolCallEventSchema: z.ZodObject<{
    toolCallId: z.ZodString;
    toolName: z.ZodString;
    input: z.ZodOptional<z.ZodString>;
    result: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<{
        pending: "pending";
        error: "error";
        running: "running";
        complete: "complete";
    }>;
}, z.core.$strip>;
export type ToolCallEvent = z.infer<typeof ToolCallEventSchema>;
export declare const ApprovalEventSchema: z.ZodObject<{
    toolCallId: z.ZodString;
    toolName: z.ZodString;
    input: z.ZodString;
}, z.core.$strip>;
export type ApprovalEvent = z.infer<typeof ApprovalEventSchema>;
export declare const QuestionPromptEventSchema: z.ZodObject<{
    toolCallId: z.ZodString;
    questions: z.ZodArray<z.ZodObject<{
        header: z.ZodString;
        question: z.ZodString;
        options: z.ZodArray<z.ZodObject<{
            label: z.ZodString;
            description: z.ZodOptional<z.ZodString>;
        }, z.core.$strip>>;
        multiSelect: z.ZodBoolean;
    }, z.core.$strip>>;
}, z.core.$strip>;
export type QuestionPromptEvent = z.infer<typeof QuestionPromptEventSchema>;
export declare const ErrorEventSchema: z.ZodObject<{
    message: z.ZodString;
    code: z.ZodOptional<z.ZodString>;
}, z.core.$strip>;
export type ErrorEvent = z.infer<typeof ErrorEventSchema>;
export declare const DoneEventSchema: z.ZodObject<{
    sessionId: z.ZodString;
}, z.core.$strip>;
export type DoneEvent = z.infer<typeof DoneEventSchema>;
export declare const SessionStatusEventSchema: z.ZodObject<{
    sessionId: z.ZodString;
    model: z.ZodOptional<z.ZodString>;
    costUsd: z.ZodOptional<z.ZodNumber>;
    contextTokens: z.ZodOptional<z.ZodNumber>;
    contextMaxTokens: z.ZodOptional<z.ZodNumber>;
}, z.core.$strip>;
export type SessionStatusEvent = z.infer<typeof SessionStatusEventSchema>;
export declare const TaskItemSchema: z.ZodObject<{
    id: z.ZodString;
    subject: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    activeForm: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<{
        pending: "pending";
        in_progress: "in_progress";
        completed: "completed";
    }>;
    blockedBy: z.ZodOptional<z.ZodArray<z.ZodString>>;
    blocks: z.ZodOptional<z.ZodArray<z.ZodString>>;
    owner: z.ZodOptional<z.ZodString>;
}, z.core.$strip>;
export type TaskItem = z.infer<typeof TaskItemSchema>;
export declare const TaskUpdateEventSchema: z.ZodObject<{
    action: z.ZodEnum<{
        create: "create";
        update: "update";
        snapshot: "snapshot";
    }>;
    task: z.ZodObject<{
        id: z.ZodString;
        subject: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
        activeForm: z.ZodOptional<z.ZodString>;
        status: z.ZodEnum<{
            pending: "pending";
            in_progress: "in_progress";
            completed: "completed";
        }>;
        blockedBy: z.ZodOptional<z.ZodArray<z.ZodString>>;
        blocks: z.ZodOptional<z.ZodArray<z.ZodString>>;
        owner: z.ZodOptional<z.ZodString>;
    }, z.core.$strip>;
}, z.core.$strip>;
export type TaskUpdateEvent = z.infer<typeof TaskUpdateEventSchema>;
export declare const StreamEventSchema: z.ZodObject<{
    type: z.ZodEnum<{
        text_delta: "text_delta";
        tool_call_start: "tool_call_start";
        tool_call_delta: "tool_call_delta";
        tool_call_end: "tool_call_end";
        tool_result: "tool_result";
        approval_required: "approval_required";
        question_prompt: "question_prompt";
        error: "error";
        done: "done";
        session_status: "session_status";
        task_update: "task_update";
    }>;
    data: z.ZodUnion<readonly [z.ZodObject<{
        text: z.ZodString;
    }, z.core.$strip>, z.ZodObject<{
        toolCallId: z.ZodString;
        toolName: z.ZodString;
        input: z.ZodOptional<z.ZodString>;
        result: z.ZodOptional<z.ZodString>;
        status: z.ZodEnum<{
            pending: "pending";
            error: "error";
            running: "running";
            complete: "complete";
        }>;
    }, z.core.$strip>, z.ZodObject<{
        toolCallId: z.ZodString;
        toolName: z.ZodString;
        input: z.ZodString;
    }, z.core.$strip>, z.ZodObject<{
        toolCallId: z.ZodString;
        questions: z.ZodArray<z.ZodObject<{
            header: z.ZodString;
            question: z.ZodString;
            options: z.ZodArray<z.ZodObject<{
                label: z.ZodString;
                description: z.ZodOptional<z.ZodString>;
            }, z.core.$strip>>;
            multiSelect: z.ZodBoolean;
        }, z.core.$strip>>;
    }, z.core.$strip>, z.ZodObject<{
        message: z.ZodString;
        code: z.ZodOptional<z.ZodString>;
    }, z.core.$strip>, z.ZodObject<{
        sessionId: z.ZodString;
    }, z.core.$strip>, z.ZodObject<{
        sessionId: z.ZodString;
        model: z.ZodOptional<z.ZodString>;
        costUsd: z.ZodOptional<z.ZodNumber>;
        contextTokens: z.ZodOptional<z.ZodNumber>;
        contextMaxTokens: z.ZodOptional<z.ZodNumber>;
    }, z.core.$strip>, z.ZodObject<{
        action: z.ZodEnum<{
            create: "create";
            update: "update";
            snapshot: "snapshot";
        }>;
        task: z.ZodObject<{
            id: z.ZodString;
            subject: z.ZodString;
            description: z.ZodOptional<z.ZodString>;
            activeForm: z.ZodOptional<z.ZodString>;
            status: z.ZodEnum<{
                pending: "pending";
                in_progress: "in_progress";
                completed: "completed";
            }>;
            blockedBy: z.ZodOptional<z.ZodArray<z.ZodString>>;
            blocks: z.ZodOptional<z.ZodArray<z.ZodString>>;
            owner: z.ZodOptional<z.ZodString>;
        }, z.core.$strip>;
    }, z.core.$strip>]>;
}, z.core.$strip>;
export type StreamEvent = z.infer<typeof StreamEventSchema>;
export declare const TextPartSchema: z.ZodObject<{
    type: z.ZodLiteral<"text">;
    text: z.ZodString;
}, z.core.$strip>;
export type TextPart = z.infer<typeof TextPartSchema>;
export declare const ToolCallPartSchema: z.ZodObject<{
    type: z.ZodLiteral<"tool_call">;
    toolCallId: z.ZodString;
    toolName: z.ZodString;
    input: z.ZodOptional<z.ZodString>;
    result: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<{
        pending: "pending";
        error: "error";
        running: "running";
        complete: "complete";
    }>;
    interactiveType: z.ZodOptional<z.ZodEnum<{
        question: "question";
        approval: "approval";
    }>>;
    questions: z.ZodOptional<z.ZodArray<z.ZodObject<{
        header: z.ZodString;
        question: z.ZodString;
        options: z.ZodArray<z.ZodObject<{
            label: z.ZodString;
            description: z.ZodOptional<z.ZodString>;
        }, z.core.$strip>>;
        multiSelect: z.ZodBoolean;
    }, z.core.$strip>>>;
    answers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
}, z.core.$strip>;
export type ToolCallPart = z.infer<typeof ToolCallPartSchema>;
export declare const MessagePartSchema: z.ZodDiscriminatedUnion<[z.ZodObject<{
    type: z.ZodLiteral<"text">;
    text: z.ZodString;
}, z.core.$strip>, z.ZodObject<{
    type: z.ZodLiteral<"tool_call">;
    toolCallId: z.ZodString;
    toolName: z.ZodString;
    input: z.ZodOptional<z.ZodString>;
    result: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<{
        pending: "pending";
        error: "error";
        running: "running";
        complete: "complete";
    }>;
    interactiveType: z.ZodOptional<z.ZodEnum<{
        question: "question";
        approval: "approval";
    }>>;
    questions: z.ZodOptional<z.ZodArray<z.ZodObject<{
        header: z.ZodString;
        question: z.ZodString;
        options: z.ZodArray<z.ZodObject<{
            label: z.ZodString;
            description: z.ZodOptional<z.ZodString>;
        }, z.core.$strip>>;
        multiSelect: z.ZodBoolean;
    }, z.core.$strip>>>;
    answers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
}, z.core.$strip>], "type">;
export type MessagePart = z.infer<typeof MessagePartSchema>;
export declare const HistoryToolCallSchema: z.ZodObject<{
    toolCallId: z.ZodString;
    toolName: z.ZodString;
    input: z.ZodOptional<z.ZodString>;
    result: z.ZodOptional<z.ZodString>;
    status: z.ZodLiteral<"complete">;
    questions: z.ZodOptional<z.ZodArray<z.ZodObject<{
        header: z.ZodString;
        question: z.ZodString;
        options: z.ZodArray<z.ZodObject<{
            label: z.ZodString;
            description: z.ZodOptional<z.ZodString>;
        }, z.core.$strip>>;
        multiSelect: z.ZodBoolean;
    }, z.core.$strip>>>;
    answers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
}, z.core.$strip>;
export type HistoryToolCall = z.infer<typeof HistoryToolCallSchema>;
export declare const HistoryMessageSchema: z.ZodObject<{
    id: z.ZodString;
    role: z.ZodEnum<{
        user: "user";
        assistant: "assistant";
    }>;
    content: z.ZodString;
    toolCalls: z.ZodOptional<z.ZodArray<z.ZodObject<{
        toolCallId: z.ZodString;
        toolName: z.ZodString;
        input: z.ZodOptional<z.ZodString>;
        result: z.ZodOptional<z.ZodString>;
        status: z.ZodLiteral<"complete">;
        questions: z.ZodOptional<z.ZodArray<z.ZodObject<{
            header: z.ZodString;
            question: z.ZodString;
            options: z.ZodArray<z.ZodObject<{
                label: z.ZodString;
                description: z.ZodOptional<z.ZodString>;
            }, z.core.$strip>>;
            multiSelect: z.ZodBoolean;
        }, z.core.$strip>>>;
        answers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
    }, z.core.$strip>>>;
    parts: z.ZodOptional<z.ZodArray<z.ZodDiscriminatedUnion<[z.ZodObject<{
        type: z.ZodLiteral<"text">;
        text: z.ZodString;
    }, z.core.$strip>, z.ZodObject<{
        type: z.ZodLiteral<"tool_call">;
        toolCallId: z.ZodString;
        toolName: z.ZodString;
        input: z.ZodOptional<z.ZodString>;
        result: z.ZodOptional<z.ZodString>;
        status: z.ZodEnum<{
            pending: "pending";
            error: "error";
            running: "running";
            complete: "complete";
        }>;
        interactiveType: z.ZodOptional<z.ZodEnum<{
            question: "question";
            approval: "approval";
        }>>;
        questions: z.ZodOptional<z.ZodArray<z.ZodObject<{
            header: z.ZodString;
            question: z.ZodString;
            options: z.ZodArray<z.ZodObject<{
                label: z.ZodString;
                description: z.ZodOptional<z.ZodString>;
            }, z.core.$strip>>;
            multiSelect: z.ZodBoolean;
        }, z.core.$strip>>>;
        answers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
    }, z.core.$strip>], "type">>>;
    timestamp: z.ZodOptional<z.ZodString>;
}, z.core.$strip>;
export type HistoryMessage = z.infer<typeof HistoryMessageSchema>;
export declare const CommandEntrySchema: z.ZodObject<{
    namespace: z.ZodString;
    command: z.ZodString;
    fullCommand: z.ZodString;
    description: z.ZodString;
    argumentHint: z.ZodOptional<z.ZodString>;
    allowedTools: z.ZodOptional<z.ZodArray<z.ZodString>>;
    filePath: z.ZodString;
}, z.core.$strip>;
export type CommandEntry = z.infer<typeof CommandEntrySchema>;
export declare const CommandRegistrySchema: z.ZodObject<{
    commands: z.ZodArray<z.ZodObject<{
        namespace: z.ZodString;
        command: z.ZodString;
        fullCommand: z.ZodString;
        description: z.ZodString;
        argumentHint: z.ZodOptional<z.ZodString>;
        allowedTools: z.ZodOptional<z.ZodArray<z.ZodString>>;
        filePath: z.ZodString;
    }, z.core.$strip>>;
    lastScanned: z.ZodString;
}, z.core.$strip>;
export type CommandRegistry = z.infer<typeof CommandRegistrySchema>;
export declare const HealthResponseSchema: z.ZodObject<{
    status: z.ZodString;
    version: z.ZodString;
    uptime: z.ZodNumber;
}, z.core.$strip>;
export type HealthResponse = z.infer<typeof HealthResponseSchema>;
export declare const ErrorResponseSchema: z.ZodObject<{
    error: z.ZodString;
    details: z.ZodOptional<z.ZodAny>;
}, z.core.$strip>;
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;
//# sourceMappingURL=schemas.d.ts.map