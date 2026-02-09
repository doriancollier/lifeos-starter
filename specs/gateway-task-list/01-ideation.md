---
slug: gateway-task-list
---

# Gateway Task List Display

**Slug:** gateway-task-list
**Author:** Claude Code
**Date:** 2026-02-08
**Branch:** preflight/obsidian-copilot-plugin

---

## 1) Intent & Assumptions

- **Task brief:** Implement a compact task list panel in the gateway copilot UI that mirrors the Claude Code CLI's task display. The list appears between message history and chat input, showing tasks sorted by state (in-progress first, then pending, then completed). Each task has a status icon, and the currently active task's `activeForm` message is shown at the top as a spinner. Max 10 tasks visible.
- **Assumptions:**
  - Task data is available via the same `stream_event` / `tool_use` events the SDK already emits (TaskCreate, TaskUpdate, TaskList, TaskGet tool calls)
  - We already intercept `tool_use` content blocks in `agent-manager.ts` for tool_call_start/end -- we can additionally detect task tool names and emit structured task events
  - Historical task state for loaded sessions can be reconstructed from JSONL transcript files
  - The task list is read-only (no creating/editing tasks from the UI)
- **Out of scope:**
  - Interactive task management (creating, editing, deleting tasks from UI)
  - Task filtering/search
  - Virtual scrolling (max 10 tasks, no need)
  - Persisting task state server-side beyond what exists in JSONL

## 2) Pre-reading Log

- `gateway/src/server/services/agent-manager.ts`: Handles SDK message mapping. `mapSdkMessage` processes `stream_event` (tool_use content blocks), `tool_use_summary`, `result`, and `system` messages. Tool calls are tracked via `toolState`. Task tool calls (TaskCreate, TaskUpdate) flow through as regular `tool_use` blocks -- their `input` JSON is available in `input_json_delta` events.
- `gateway/src/shared/types.ts`: Defines `StreamEvent`, `StreamEventType`, `ToolCallEvent`, etc. Would need new `task_update` event type.
- `gateway/src/client/hooks/use-chat-session.ts`: Client-side SSE parsing. Handles `tool_call_start`, `tool_call_delta`, `tool_call_end`, `tool_result` events. Accumulates tool input from deltas.
- `gateway/src/client/components/chat/ChatPanel.tsx`: Layout is `flex flex-col h-full` with MessageList (flex-1), error bar, then input area (`relative border-t p-4`). Task list would slot between MessageList and the input area.
- `gateway/src/client/components/chat/ChatInput.tsx`: Text input with send/stop buttons.
- `gateway/src/server/services/transcript-reader.ts`: Reads JSONL transcripts. `readTranscript()` parses all lines and returns `HistoryMessage[]`. Could be extended to also extract task state.
- `gateway/node_modules/@anthropic-ai/claude-agent-sdk/sdk.d.ts`: `SDKMessage` union type includes `SDKTaskNotificationMessage` (for subagent completion, NOT task list). Task list data is in regular `tool_use` blocks with names `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`.
- Real JSONL file analysis (`b3f06b94-da2b-4b21-be13-83ce494bcdaa.jsonl`):
  - TaskCreate inputs: `{subject, description, activeForm, metadata?}`
  - TaskUpdate inputs: `{taskId, status?, addBlockedBy?, addBlocks?, subject?, description?, activeForm?, owner?}`
  - TaskList returns formatted text: `#32 [completed] subject text [blocked by #31]`
  - TaskGet returns full task details as JSON string

## 3) Codebase Map

**Primary Components/Modules:**
- `gateway/src/server/services/agent-manager.ts` -- SDK message processing, needs to detect task tool calls and emit task events
- `gateway/src/shared/types.ts` -- Shared types, needs TaskState/TaskEvent types
- `gateway/src/client/hooks/use-chat-session.ts` -- Client SSE handler, needs to process task events
- `gateway/src/client/components/chat/ChatPanel.tsx` -- Layout, needs to render task list between messages and input
- `gateway/src/server/services/transcript-reader.ts` -- JSONL parsing, needs to extract historical task state

**New Components:**
- `gateway/src/client/components/chat/TaskListPanel.tsx` -- Compact task list display
- `gateway/src/client/hooks/use-task-state.ts` -- (optional) Task state management hook

**Shared Dependencies:**
- `lucide-react` -- Icons (CheckCircle2, Circle, Loader2, etc.)
- `motion/react` -- Entry/exit animations (AnimatePresence)
- `@shared/types` -- Shared interfaces

**Data Flow:**
1. **Streaming (live):** SDK emits `stream_event` with `tool_use` content blocks -> `agent-manager` detects task tool names -> emits new `task_update` SSE event -> client receives and updates task state
2. **Historical (session load):** `readTranscript()` or new `readTasks()` parses JSONL -> extracts TaskCreate/TaskUpdate tool calls -> reconstructs task state -> returned via API -> client initializes task state

**Potential Blast Radius:**
- `agent-manager.ts` -- Small change: detect task tool names in existing tool_use handling
- `use-chat-session.ts` -- Add task event handler
- `ChatPanel.tsx` -- Add TaskListPanel between messages and input area
- `types.ts` -- Add task-related types
- `transcript-reader.ts` -- Add task extraction method

## 4) Root Cause Analysis

N/A -- This is a new feature, not a bug fix.

## 5) Research

### Approach A: Intercept tool_call events client-side

**Description:** The client already receives `tool_call_start` and `tool_call_delta` events with `toolName` and accumulated `input`. When `toolName` is `TaskCreate`, `TaskUpdate`, etc., parse the input JSON and update a client-side task state map.

- **Pros:**
  - Zero server changes needed
  - Uses existing event stream
  - Real-time as tool calls happen
- **Cons:**
  - Must accumulate `input_json_delta` chunks and parse when complete
  - Complex: need to track partial JSON across deltas
  - `tool_call_end` doesn't include the full input (only start/delta do)
  - Can't distinguish task tool results from other tool results
  - Historical task state still needs JSONL parsing
- **Complexity:** Medium-High
- **Maintenance:** Medium

### Approach B: Emit dedicated `task_update` events from server (Recommended)

**Description:** In `agent-manager.ts`, when we detect a `tool_use` content block with a task tool name, accumulate the input JSON and emit a dedicated `task_update` SSE event with the parsed task data. For historical sessions, add a `readTasks()` method to `transcript-reader.ts` and expose via API.

- **Pros:**
  - Clean separation: server parses, client renders
  - Dedicated event type makes client handling simple
  - Server already has access to full tool input (from `input_json_delta` accumulation)
  - Can include the tool result (task ID assignment) in the event
  - Historical state served via clean API endpoint
- **Cons:**
  - Requires changes to agent-manager (small)
  - New SSE event type
  - Need to handle both live and historical data sources
- **Complexity:** Medium
- **Maintenance:** Low

### Approach C: Poll server for task state

**Description:** Server reconstructs task state from JSONL on each request. Client polls periodically.

- **Pros:**
  - Simple client: just fetch and render
  - No streaming changes needed
- **Cons:**
  - Polling latency (tasks appear delayed)
  - Expensive: re-parsing JSONL every poll
  - Doesn't feel real-time
- **Complexity:** Low
- **Maintenance:** Low

### Recommendation

**Approach B** is recommended. It provides real-time task updates through the existing SSE stream with clean event types, and serves historical task state via a REST endpoint. The server already processes all tool_use events, so detecting task tools is a small addition.

### UI Pattern: Compact Task List

Based on the CLI screenshot:
- **Header line:** `9 tasks (5 done, 1 in progress, 3 open) - ctrl+t to hide tasks`
- **Sort order:** in_progress (bold), then pending, then completed (dimmed, strikethrough)
- **Icons:** Filled square (in_progress), empty square (pending), checkmark (completed)
- **Max 10 visible** with overflow count in header
- **ActiveForm message** shown as spinner text above the list (the "currently doing" message)

## 6) Clarification

1. **Live-only vs Historical:** Should we show task state for loaded historical sessions too, or only for active streaming sessions? (Recommendation: Both -- reconstruct from JSONL for loaded sessions)

2. **Task list position:** The CLI shows it above the input. In our UI, should it be between the message list and input area, or as a collapsible panel at the bottom of the message list? (Recommendation: Between messages and input, matching CLI layout)

3. **Collapse/expand:** Should there be a toggle to hide the task list (like CLI's ctrl+t)? (Recommendation: Yes, with a small toggle button or keyboard shortcut)

4. **Task detail on click:** Should clicking a task do anything (e.g., scroll to the message where it was created, or show description in a tooltip)? (Recommendation: Tooltip with description on hover, no click action for v1)
