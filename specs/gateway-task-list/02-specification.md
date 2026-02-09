---
slug: gateway-task-list
status: Draft
---

# Gateway Task List Display

**Status:** Draft
**Authors:** Claude Code
**Date:** 2026-02-08
**Branch:** preflight/obsidian-copilot-plugin
**Ideation:** [specs/gateway-task-list/01-ideation.md](./01-ideation.md)

---

## Overview

Implement a compact, read-only task list panel in the gateway copilot UI that mirrors the Claude Code CLI's task display. The panel renders between message history and chat input, showing agent tasks sorted by state (in-progress first, then pending, then completed). An activeForm spinner message indicates what the agent is currently doing. The panel auto-hides when no tasks exist and is collapsible.

## Background / Problem Statement

The Claude Code CLI displays a task list when the agent uses TaskCreate/TaskUpdate tools, giving users real-time visibility into multi-step work. The gateway copilot UI currently has no equivalent -- users see tool calls for TaskCreate/TaskUpdate but cannot see the aggregated task state at a glance. This feature brings task visibility parity with the CLI.

Task data flows through the SDK as regular `tool_use` content blocks (not dedicated task events). The tool names are `TaskCreate`, `TaskUpdate`, `TaskList`, and `TaskGet`. Their inputs contain structured task data (subject, status, activeForm, etc.) that can be intercepted and presented as a cohesive task list.

## Goals

- Real-time task list display during active agent sessions
- Historical task state reconstruction when loading past sessions
- Compact, non-intrusive UI that auto-hides when empty
- Collapsible panel to minimize screen usage when desired
- Sort order matching CLI: in-progress, pending, completed
- ActiveForm spinner showing what the agent is currently doing

## Non-Goals

- Interactive task management (create/edit/delete from UI)
- Task filtering or search
- Virtual scrolling (max 10 tasks, unnecessary)
- Server-side task state persistence beyond JSONL transcripts
- Hover tooltips or click interactions on tasks
- Task notifications or alerts

## Technical Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| `lucide-react` | latest | Status icons (Loader2, Circle, CheckCircle2, ChevronDown) |
| `motion` | ^12.33.0 | AnimatePresence for panel entry/exit |
| `@anthropic-ai/claude-agent-sdk` | existing | SDK message types, tool_use events |

No new dependencies required. All libraries are already in `gateway/package.json`.

## Detailed Design

### Architecture Overview

```
SDK stream_event (tool_use)
    │
    ▼
agent-manager.ts ──── Detects task tool names ──── Emits task_update SSE event
    │                                                        │
    ▼                                                        ▼
tool_call_start/delta/end (existing)              task_update (new event type)
    │                                                        │
    ▼                                                        ▼
use-chat-session.ts ──────────────────────── Processes task_update events
    │                                                        │
    ▼                                                        ▼
Message rendering (existing)                     TaskListPanel (new component)
```

### 1. Shared Types (`gateway/src/shared/types.ts`)

Add task-related types to the shared types file:

```typescript
// Task status values matching CLI behavior
export type TaskStatus = 'pending' | 'in_progress' | 'completed';

// Individual task item
export interface TaskItem {
  id: string;
  subject: string;
  description?: string;
  activeForm?: string;
  status: TaskStatus;
  blockedBy?: string[];
  blocks?: string[];
  owner?: string;
}

// Task update event data
export interface TaskUpdateEvent {
  action: 'create' | 'update' | 'snapshot';
  task: TaskItem;
}

// Add to StreamEventType union:
// | 'task_update'

// Add to StreamEvent union:
// | { type: 'task_update'; data: TaskUpdateEvent }
```

### 2. Server: Task Tool Detection (`gateway/src/server/services/agent-manager.ts`)

**Approach:** Accumulate `input_json_delta` chunks for task tools server-side (the client already does this for all tools, but we need parsed JSON on the server to emit structured task events). When `content_block_stop` fires for a task tool, parse the accumulated input and emit a `task_update` event.

**Key insight from codebase research:** The server currently does NOT accumulate tool input -- it forwards each `partial_json` delta directly. For task tools specifically, we need to accumulate server-side so we can emit a parsed `task_update` event when the tool call completes.

#### Changes to `mapSdkMessage`:

Add a `taskToolInput` accumulator alongside the existing `toolState`:

```typescript
// In sendMessage(), alongside toolState:
let taskToolInput = '';

// Set of task tool names
const TASK_TOOL_NAMES = new Set(['TaskCreate', 'TaskUpdate', 'TaskList', 'TaskGet']);
```

In `content_block_delta` handling, when the current tool is a task tool, also accumulate the input:

```typescript
} else if (delta?.type === 'input_json_delta' && toolState.inTool) {
  // Accumulate input for task tools
  if (TASK_TOOL_NAMES.has(toolState.currentToolName)) {
    taskToolInput += delta.partial_json as string;
  }
  yield { type: 'tool_call_delta', data: { ... } };
}
```

In `content_block_stop` handling, when the completed tool is a task tool, parse and emit:

```typescript
if (toolState.inTool) {
  const wasTaskTool = TASK_TOOL_NAMES.has(toolState.currentToolName);
  const taskToolName = toolState.currentToolName;

  yield { type: 'tool_call_end', data: { ... } };
  toolState.setToolState(false, '', '');

  // Emit task_update for completed task tools
  if (wasTaskTool && taskToolInput) {
    try {
      const input = JSON.parse(taskToolInput);
      const taskEvent = buildTaskEvent(taskToolName, input);
      if (taskEvent) {
        yield { type: 'task_update', data: taskEvent };
      }
    } catch { /* malformed JSON, skip */ }
    taskToolInput = '';
  }
}
```

#### `buildTaskEvent` helper:

```typescript
function buildTaskEvent(
  toolName: string,
  input: Record<string, unknown>
): TaskUpdateEvent | null {
  switch (toolName) {
    case 'TaskCreate':
      return {
        action: 'create',
        task: {
          id: '', // ID assigned by tool result, filled client-side from sequential ordering
          subject: input.subject as string,
          description: input.description as string | undefined,
          activeForm: input.activeForm as string | undefined,
          status: 'pending',
        },
      };
    case 'TaskUpdate':
      return {
        action: 'update',
        task: {
          id: input.taskId as string,
          subject: input.subject as string | undefined ?? '',
          ...(input.status && { status: input.status as TaskStatus }),
          ...(input.activeForm && { activeForm: input.activeForm as string }),
          ...(input.description && { description: input.description as string }),
          ...(input.addBlockedBy && { blockedBy: input.addBlockedBy as string[] }),
          ...(input.addBlocks && { blocks: input.addBlocks as string[] }),
          ...(input.owner && { owner: input.owner as string }),
        },
      };
    default:
      return null; // TaskList and TaskGet don't modify state
  }
}
```

**Task ID assignment problem:** `TaskCreate` doesn't include the task ID in its input -- the ID is assigned by the tool and returned in the result. Two approaches:

1. **Client assigns temporary IDs**: Use an incrementing counter. When a `tool_result` for TaskCreate arrives, the result text contains the assigned ID. The client can correlate by order.
2. **Server emits after tool_result**: Wait for the `tool_use_summary` that follows TaskCreate to extract the ID.

**Chosen approach:** Use auto-incrementing client-side IDs for TaskCreate events. TaskUpdate events already include `taskId` in their input. The exact numeric ID doesn't matter for display purposes -- tasks are identified by subject/position. If a TaskUpdate references an ID not yet seen, it's a no-op (unlikely in practice since TaskUpdate always follows TaskCreate).

### 3. Server: Historical Task Extraction (`gateway/src/server/services/transcript-reader.ts`)

Add a `readTasks()` method that extracts task state from JSONL transcripts:

```typescript
async readTasks(sessionId: string, vaultRoot: string): Promise<TaskItem[]> {
  const filePath = this.getTranscriptPath(sessionId, vaultRoot);
  const content = await fs.readFile(filePath, 'utf-8');
  const lines = content.split('\n').filter(l => l.trim());

  const tasks = new Map<string, TaskItem>();
  let nextId = 1;

  for (const line of lines) {
    const parsed = JSON.parse(line);
    if (parsed.type !== 'assistant') continue;

    const message = parsed.message;
    if (!message?.content) continue;

    for (const block of message.content) {
      if (block.type !== 'tool_use') continue;
      if (!['TaskCreate', 'TaskUpdate'].includes(block.name)) continue;

      const input = block.input;
      if (block.name === 'TaskCreate') {
        const id = String(nextId++);
        tasks.set(id, {
          id,
          subject: input.subject ?? '',
          description: input.description,
          activeForm: input.activeForm,
          status: 'pending',
        });
      } else if (block.name === 'TaskUpdate' && input.taskId) {
        const existing = tasks.get(input.taskId);
        if (existing) {
          if (input.status) existing.status = input.status;
          if (input.subject) existing.subject = input.subject;
          if (input.activeForm) existing.activeForm = input.activeForm;
          if (input.description) existing.description = input.description;
          if (input.addBlockedBy) existing.blockedBy = [
            ...(existing.blockedBy ?? []),
            ...input.addBlockedBy,
          ];
          if (input.addBlocks) existing.blocks = [
            ...(existing.blocks ?? []),
            ...input.addBlocks,
          ];
          if (input.owner) existing.owner = input.owner;
        }
      }
    }
  }

  return Array.from(tasks.values());
}
```

**Note:** This reads the full file (same as `readTranscript()`). For very large sessions, this is acceptable since task extraction only happens once on session load, not on every poll. The data is cached client-side after initial fetch.

### 4. Server: API Endpoint (`gateway/src/server/routes/sessions.ts`)

Add a tasks endpoint:

```typescript
// GET /api/sessions/:id/tasks
router.get('/:id/tasks', async (req, res) => {
  try {
    const tasks = await transcriptReader.readTasks(req.params.id, vaultRoot);
    res.json({ tasks });
  } catch (err) {
    res.status(404).json({ error: 'Session not found' });
  }
});
```

Also add a `getTasks` method to the `Transport` interface:

```typescript
// In Transport interface
getTasks(sessionId: string): Promise<{ tasks: TaskItem[] }>;
```

Implement in `HttpTransport`:

```typescript
async getTasks(sessionId: string): Promise<{ tasks: TaskItem[] }> {
  const res = await fetch(`${this.baseUrl}/api/sessions/${sessionId}/tasks`);
  if (!res.ok) return { tasks: [] };
  return res.json();
}
```

Implement in `DirectTransport`:

```typescript
async getTasks(sessionId: string): Promise<{ tasks: TaskItem[] }> {
  const tasks = await this.transcriptReader.readTasks(sessionId, this.vaultRoot);
  return { tasks };
}
```

### 5. Client: Task State Management (`gateway/src/client/hooks/use-task-state.ts`)

New hook that manages task state from both streaming events and historical data:

```typescript
import { useState, useCallback, useEffect, useRef } from 'react';
import { useTransport } from './use-transport';
import type { TaskItem, TaskUpdateEvent, TaskStatus } from '@shared/types';

interface UseTaskStateOptions {
  sessionId: string;
}

interface TaskState {
  tasks: TaskItem[];
  activeForm: string | null;
  isCollapsed: boolean;
  toggleCollapse: () => void;
  handleTaskEvent: (event: TaskUpdateEvent) => void;
  clearTasks: () => void;
}

// Sort priority: in_progress (0) > pending (1) > completed (2)
const STATUS_ORDER: Record<TaskStatus, number> = {
  in_progress: 0,
  pending: 1,
  completed: 2,
};

function sortTasks(tasks: TaskItem[]): TaskItem[] {
  return [...tasks].sort((a, b) => STATUS_ORDER[a.status] - STATUS_ORDER[b.status]);
}

export function useTaskState({ sessionId }: UseTaskStateOptions): TaskState {
  const transport = useTransport();
  const [taskMap, setTaskMap] = useState<Map<string, TaskItem>>(new Map());
  const [isCollapsed, setIsCollapsed] = useState(false);
  const nextIdRef = useRef(1);

  // Load historical tasks on session change
  useEffect(() => {
    setTaskMap(new Map());
    nextIdRef.current = 1;

    transport.getTasks(sessionId).then(({ tasks }) => {
      if (tasks.length > 0) {
        const map = new Map<string, TaskItem>();
        for (const task of tasks) {
          map.set(task.id, task);
        }
        setTaskMap(map);
        nextIdRef.current = tasks.length + 1;
      }
    }).catch(() => { /* session may not exist yet */ });
  }, [sessionId, transport]);

  const handleTaskEvent = useCallback((event: TaskUpdateEvent) => {
    setTaskMap(prev => {
      const next = new Map(prev);
      if (event.action === 'create') {
        const id = String(nextIdRef.current++);
        next.set(id, { ...event.task, id });
      } else if (event.action === 'update') {
        const existing = next.get(event.task.id);
        if (existing) {
          next.set(event.task.id, { ...existing, ...stripUndefined(event.task) });
        }
      }
      return next;
    });
  }, []);

  const clearTasks = useCallback(() => {
    setTaskMap(new Map());
    nextIdRef.current = 1;
  }, []);

  const toggleCollapse = useCallback(() => {
    setIsCollapsed(prev => !prev);
  }, []);

  // Derive sorted list and activeForm
  const allTasks = Array.from(taskMap.values());
  const sorted = sortTasks(allTasks);
  const visible = sorted.slice(0, 10);
  const inProgressTask = allTasks.find(t => t.status === 'in_progress');
  const activeForm = inProgressTask?.activeForm ?? null;

  return {
    tasks: visible,
    activeForm,
    isCollapsed,
    toggleCollapse,
    handleTaskEvent,
    clearTasks,
  };
}

function stripUndefined(obj: Record<string, unknown>): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    if (value !== undefined && value !== '') result[key] = value;
  }
  return result;
}
```

### 6. Client: SSE Event Integration (`gateway/src/client/hooks/use-chat-session.ts`)

Add `task_update` handling to the `handleStreamEvent` function:

```typescript
// In handleStreamEvent, add case:
case 'task_update': {
  const taskEvent = event.data as TaskUpdateEvent;
  onTaskEvent?.(taskEvent);
  break;
}
```

The `onTaskEvent` callback is passed from `ChatPanel` to `useChatSession` via options, connecting the SSE stream to the task state hook.

Alternatively, `useChatSession` can accept and return task state directly. The simpler approach: `useChatSession` returns a `taskEvents` array that `ChatPanel` feeds to `useTaskState`.

**Chosen approach:** Add an `onTaskEvent` callback option to `useChatSession`. `ChatPanel` passes `taskState.handleTaskEvent` as this callback.

```typescript
// In useChatSession options:
interface UseChatSessionOptions {
  transformContent?: (content: string) => string | Promise<string>;
  onTaskEvent?: (event: TaskUpdateEvent) => void;
}
```

### 7. Client: TaskListPanel Component (`gateway/src/client/components/chat/TaskListPanel.tsx`)

```typescript
import { Loader2, Circle, CheckCircle2, ChevronDown, ChevronRight, ListTodo } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import type { TaskItem, TaskStatus } from '@shared/types';

interface TaskListPanelProps {
  tasks: TaskItem[];
  activeForm: string | null;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const STATUS_ICON: Record<TaskStatus, React.ReactNode> = {
  in_progress: <Loader2 className="h-3 w-3 animate-spin text-blue-400" />,
  pending: <Circle className="h-3 w-3 text-muted-foreground" />,
  completed: <CheckCircle2 className="h-3 w-3 text-green-500" />,
};

export function TaskListPanel({ tasks, activeForm, isCollapsed, onToggleCollapse }: TaskListPanelProps) {
  if (tasks.length === 0) return null;

  const done = tasks.filter(t => t.status === 'completed').length;
  const inProgress = tasks.filter(t => t.status === 'in_progress').length;
  const open = tasks.filter(t => t.status === 'pending').length;

  return (
    <div className="border-t px-4 py-2">
      {/* ActiveForm spinner */}
      <AnimatePresence>
        {activeForm && !isCollapsed && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="flex items-center gap-2 text-xs text-blue-400 mb-1"
          >
            <Loader2 className="h-3 w-3 animate-spin" />
            <span className="truncate">{activeForm}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header with toggle */}
      <button
        onClick={onToggleCollapse}
        className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground w-full"
      >
        {isCollapsed ? (
          <ChevronRight className="h-3 w-3" />
        ) : (
          <ChevronDown className="h-3 w-3" />
        )}
        <ListTodo className="h-3 w-3" />
        <span>
          {tasks.length} task{tasks.length !== 1 ? 's' : ''}
          {' '}({done} done{inProgress > 0 ? `, ${inProgress} in progress` : ''}, {open} open)
        </span>
      </button>

      {/* Task list */}
      <AnimatePresence>
        {!isCollapsed && (
          <motion.ul
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-1 space-y-0.5"
          >
            {tasks.map(task => (
              <li
                key={task.id}
                className={`flex items-center gap-2 text-xs py-0.5 ${
                  task.status === 'completed'
                    ? 'text-muted-foreground/50 line-through'
                    : task.status === 'in_progress'
                    ? 'text-foreground font-medium'
                    : 'text-muted-foreground'
                }`}
              >
                {STATUS_ICON[task.status]}
                <span className="truncate">{task.subject}</span>
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
}
```

### 8. Client: ChatPanel Integration (`gateway/src/client/components/chat/ChatPanel.tsx`)

Add TaskListPanel between MessageList and the input area:

```typescript
import { TaskListPanel } from './TaskListPanel';
import { useTaskState } from '../../hooks/use-task-state';

// In ChatPanel:
const taskState = useTaskState({ sessionId });

const { messages, input, setInput, handleSubmit, status, error, stop, isLoadingHistory, sessionStatus } =
  useChatSession(sessionId, {
    transformContent,
    onTaskEvent: taskState.handleTaskEvent,
  });

// In JSX, between MessageList and the input div:
<TaskListPanel
  tasks={taskState.tasks}
  activeForm={taskState.activeForm}
  isCollapsed={taskState.isCollapsed}
  onToggleCollapse={taskState.toggleCollapse}
/>
```

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Live Streaming                        │
│                                                         │
│  SDK → agent-manager.ts                                 │
│         ├─ content_block_start → tool_call_start        │
│         ├─ content_block_delta → tool_call_delta        │
│         │   (+ accumulate if task tool)                 │
│         └─ content_block_stop → tool_call_end           │
│              └─ if task tool → task_update event         │
│                                    │                    │
│  SSE stream ◄──────────────────────┘                    │
│       │                                                 │
│  use-chat-session.ts → onTaskEvent callback             │
│       │                                                 │
│  useTaskState.handleTaskEvent() → update Map            │
│       │                                                 │
│  TaskListPanel renders sorted tasks                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                Historical (Session Load)                 │
│                                                         │
│  useTaskState mount effect                              │
│       │                                                 │
│  transport.getTasks(sessionId)                          │
│       │                                                 │
│  ┌─ HttpTransport: GET /api/sessions/:id/tasks          │
│  │   └─ transcript-reader.readTasks() → parse JSONL     │
│  └─ DirectTransport: transcriptReader.readTasks()       │
│       │                                                 │
│  Initialize taskMap from response                       │
│       │                                                 │
│  TaskListPanel renders sorted tasks                     │
└─────────────────────────────────────────────────────────┘
```

## User Experience

1. **No tasks:** Panel is completely hidden. No UI change.
2. **Agent creates tasks:** Panel appears between messages and input with smooth animation. Header shows task count summary. ActiveForm spinner shows what the agent is doing.
3. **Tasks update:** Status icons change in real-time (pending -> in-progress -> completed). Sort order updates automatically.
4. **Collapse:** User clicks header to collapse/expand. Collapsed state shows only the header line (and activeForm if present).
5. **Session load:** Loading a past session displays its final task state.
6. **Max 10 tasks:** Only 10 tasks are rendered. The header count reflects total tasks.

## Testing Strategy

### Unit Tests

**`use-task-state.test.ts`:**
- Task creation adds to map with auto-incrementing IDs
- Task update modifies existing task properties
- Task update for non-existent ID is a no-op
- Sort order: in_progress first, pending second, completed last
- Max 10 tasks visible (11th task not in returned array)
- ActiveForm returns the in_progress task's activeForm
- ActiveForm is null when no in_progress task
- clearTasks resets state
- toggleCollapse flips boolean
- Historical tasks load on sessionId change

**`TaskListPanel.test.tsx`:**
- Renders nothing when tasks array is empty
- Renders header with correct counts
- Renders task items with correct status icons
- Completed tasks have line-through styling
- In-progress tasks have bold styling
- Collapsed state hides task list but shows header
- ActiveForm spinner shown when provided and not collapsed
- Truncates long task subjects

**`buildTaskEvent.test.ts`:**
- TaskCreate produces create action with pending status
- TaskUpdate produces update action with provided fields
- TaskUpdate with only taskId and status works
- TaskList returns null (no state change)
- TaskGet returns null (no state change)
- Malformed input doesn't throw

**`transcript-reader.readTasks.test.ts`:**
- Empty JSONL returns empty array
- TaskCreate entries create tasks with pending status
- TaskUpdate entries modify existing tasks
- Multiple creates produce sequential IDs
- Status transitions are applied correctly
- blockedBy arrays accumulate (addBlockedBy)
- Non-task tool_use blocks are ignored
- Non-assistant messages are ignored

### Integration Tests

**`use-chat-session` + task events:**
- task_update events trigger onTaskEvent callback
- Historical task load on mount populates state
- Session change resets task state and reloads

### Mocking Strategy

- Mock `transport.getTasks()` for historical load tests
- Mock SSE events for streaming tests
- Use `renderHook` from `@testing-library/react` for hook tests
- Use `render` from `@testing-library/react` for component tests

## Performance Considerations

- **Task map operations are O(1):** Map get/set for each event
- **Sort is O(n log n)** but n <= ~50 tasks max in practice
- **Historical parse is O(n)** where n = JSONL lines, runs once on session load
- **No re-renders on non-task events:** Task state is separate from message state
- **AnimatePresence:** Lightweight CSS-driven animations, no layout thrashing

## Security Considerations

- Task data is read-only in the UI (no mutations sent to server)
- No user input is reflected in task display (XSS-safe)
- JSONL parsing uses `JSON.parse` (safe, no eval)
- Task endpoint uses same auth context as other session endpoints

## Documentation

No external documentation changes needed. This is an internal UI feature that mirrors existing CLI behavior.

## Implementation Phases

### Phase 1: Core Pipeline

1. Add `TaskItem`, `TaskUpdateEvent`, and `task_update` StreamEvent types to `types.ts`
2. Add task tool detection and `task_update` emission in `agent-manager.ts`
3. Add `readTasks()` to `transcript-reader.ts`
4. Add `/api/sessions/:id/tasks` endpoint and `getTasks` to Transport interface
5. Write server-side tests

### Phase 2: Client State & UI

1. Create `use-task-state.ts` hook
2. Add `task_update` handling to `use-chat-session.ts`
3. Create `TaskListPanel.tsx` component
4. Integrate into `ChatPanel.tsx`
5. Write client-side tests

### Phase 3: Polish

1. Verify animation smoothness
2. Test with large task counts (10+ tasks)
3. Test Obsidian plugin (DirectTransport path)
4. Verify no regressions to existing streaming/message display

## Open Questions

None -- all clarifications resolved during ideation.

## References

- [Ideation Document](./01-ideation.md) -- Research, approach analysis, codebase map
- Claude Code CLI task list -- Reference implementation (visual parity target)
- `gateway/src/server/services/agent-manager.ts` -- SDK message processing
- `gateway/src/shared/types.ts` -- StreamEvent type system
- `gateway/src/client/hooks/use-chat-session.ts` -- Client SSE handling
- `gateway/src/server/services/transcript-reader.ts` -- JSONL parsing
