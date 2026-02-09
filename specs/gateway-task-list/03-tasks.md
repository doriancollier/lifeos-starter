---
slug: gateway-task-list
status: Ready
decomposed: 2026-02-08
---

# Gateway Task List - Implementation Tasks

**Spec:** [02-specification.md](./02-specification.md)
**Branch:** preflight/obsidian-copilot-plugin
**Total Tasks:** 9 (Phase 1: 4, Phase 2: 4, Phase 3: 1)

---

## Dependency Graph

```
Task 1.1 (types) ─────────────────────────────────────────────┐
    │                                                          │
    ├──► Task 1.2 (agent-manager) ──► Task 2.2 (chat-session) │
    │                                                          │
    ├──► Task 1.3 (transcript-reader) ──► Task 1.4 (API+Transport)
    │                                          │               │
    ├──► Task 2.1 (use-task-state) ◄───────────┘               │
    │                                                          │
    └──► Task 2.3 (TaskListPanel) ─────────────────────────────┤
                                                               │
    Task 2.4 (ChatPanel integration) ◄── 2.1, 2.2, 2.3        │
         │                                                     │
         ▼                                                     │
    Task 3.1 (tests) ◄────────────────────────────────────────┘
```

---

## Phase 1: Core Pipeline

### Task 1.1: Add shared task types to types.ts

**File:** `gateway/src/shared/types.ts`
**Dependencies:** None
**ActiveForm:** Adding shared task types to types.ts

Add TaskItem, TaskUpdateEvent, TaskStatus types and extend StreamEvent/StreamEventType unions.

**Add after the `CommandRegistry` interface (line ~138):**

```typescript
// === Task Types ===

export type TaskStatus = 'pending' | 'in_progress' | 'completed';

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

export interface TaskUpdateEvent {
  action: 'create' | 'update' | 'snapshot';
  task: TaskItem;
}
```

**Modify `StreamEventType` union (line ~32) to add `'task_update'`:**

```typescript
export type StreamEventType =
  | 'text_delta'
  | 'tool_call_start'
  | 'tool_call_delta'
  | 'tool_call_end'
  | 'tool_result'
  | 'approval_required'
  | 'question_prompt'
  | 'error'
  | 'done'
  | 'session_status'
  | 'task_update';
```

**Modify `StreamEvent` interface (line ~52) to add `TaskUpdateEvent` to data union:**

```typescript
export interface StreamEvent {
  type: StreamEventType;
  data: TextDelta | ToolCallEvent | ApprovalEvent | QuestionPromptEvent | ErrorEvent | DoneEvent | SessionStatusEvent | TaskUpdateEvent;
}
```

**Acceptance criteria:**
- TaskStatus, TaskItem, TaskUpdateEvent types are exported
- StreamEventType includes 'task_update'
- StreamEvent data union includes TaskUpdateEvent
- No existing type signatures are broken

---

### Task 1.2: Add task tool detection and task_update emission in agent-manager.ts

**File:** `gateway/src/server/services/agent-manager.ts`
**Dependencies:** Task 1.1
**ActiveForm:** Adding task tool detection to agent-manager

Detect TaskCreate/TaskUpdate/TaskList/TaskGet tool calls server-side, accumulate their input JSON deltas, and emit `task_update` events when the tool call completes.

**Add import for new types at top of file:**

```typescript
import type { StreamEvent, PermissionMode, TaskUpdateEvent, TaskStatus } from '../../shared/types';
```

**Add `buildTaskEvent` helper function before the `AgentManager` class (after the `handleToolApproval` function, around line 133):**

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
          id: '',
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
      return null;
  }
}
```

**In `sendMessage()` method, add alongside existing `toolState` declaration (around line 240-254):**

```typescript
let taskToolInput = '';
const TASK_TOOL_NAMES = new Set(['TaskCreate', 'TaskUpdate', 'TaskList', 'TaskGet']);
```

**In `mapSdkMessage()`, modify the `content_block_delta` handler for `input_json_delta` (around line 364). Change:**

```typescript
} else if (delta?.type === 'input_json_delta' && toolState.inTool) {
  yield {
    type: 'tool_call_delta',
    data: {
      toolCallId: toolState.currentToolId,
      toolName: toolState.currentToolName,
      input: delta.partial_json as string,
      status: 'running',
    },
  };
}
```

**Problem:** `taskToolInput` is a local variable in `sendMessage()` but `mapSdkMessage()` is a separate method. Two approaches:

**Approach A (recommended):** Pass `taskToolInput` and `TASK_TOOL_NAMES` into `mapSdkMessage` via the `toolState` parameter, or add them to the toolState object.

**Approach B:** Move the accumulation into `sendMessage()` by wrapping the `mapSdkMessage` yield. The `sendMessage()` method iterates over `mapSdkMessage` results and can intercept/augment events.

**Implementation using Approach B** - modify the for-await loop in `sendMessage()` (around line 292):

```typescript
for await (const event of this.mapSdkMessage(result.value, session, sessionId, toolState)) {
  // Accumulate input for task tools
  if (event.type === 'tool_call_delta' && TASK_TOOL_NAMES.has(toolState.currentToolName)) {
    const tcData = event.data as { input?: string };
    if (tcData.input) {
      taskToolInput += tcData.input;
    }
  }

  // On tool call end, check if it was a task tool and emit task_update
  if (event.type === 'tool_call_end') {
    if (event.type === 'done') emittedDone = true;
    yield event;

    // Check the tool name from the event data
    const tcData = event.data as { toolName?: string };
    if (tcData.toolName && TASK_TOOL_NAMES.has(tcData.toolName) && taskToolInput) {
      try {
        const input = JSON.parse(taskToolInput);
        const taskEvent = buildTaskEvent(tcData.toolName, input);
        if (taskEvent) {
          yield { type: 'task_update', data: taskEvent };
        }
      } catch { /* malformed JSON, skip */ }
      taskToolInput = '';
    }
    continue;
  }

  if (event.type === 'done') emittedDone = true;
  yield event;
}
```

**Note:** The key insight is that `tool_call_delta` events arrive BEFORE `tool_call_end`, so we accumulate during deltas and emit on end. The `toolState.currentToolName` is still set during deltas but cleared after end in `mapSdkMessage`. However, since we moved accumulation to `sendMessage()`, we can capture the tool name from the `tool_call_end` event data which already includes `toolName`.

**Acceptance criteria:**
- TaskCreate tool calls emit a `task_update` event with action 'create' and status 'pending'
- TaskUpdate tool calls emit a `task_update` event with action 'update' and the provided fields
- TaskList and TaskGet do NOT emit task_update events
- Malformed JSON in tool input is silently skipped
- Existing tool_call_start/delta/end events continue to work unchanged
- `buildTaskEvent` is exported (for testing)

---

### Task 1.3: Add readTasks() to transcript-reader.ts

**File:** `gateway/src/server/services/transcript-reader.ts`
**Dependencies:** Task 1.1
**ActiveForm:** Adding readTasks method to transcript-reader

Add a `readTasks()` method to `TranscriptReader` that extracts task state from JSONL transcripts by replaying TaskCreate and TaskUpdate tool_use blocks.

**Add import for TaskItem:**

```typescript
import type { Session, PermissionMode, HistoryMessage, HistoryToolCall, QuestionItem, TaskItem } from '../../shared/types';
```

**Add the following method to the `TranscriptReader` class (after `readTranscript`, around line 371):**

```typescript
/**
 * Extract task state from an SDK session transcript.
 * Replays TaskCreate and TaskUpdate tool_use blocks to reconstruct final task state.
 */
async readTasks(vaultRoot: string, sessionId: string): Promise<TaskItem[]> {
  const transcriptsDir = this.getTranscriptsDir(vaultRoot);
  const filePath = path.join(transcriptsDir, `${sessionId}.jsonl`);

  let content: string;
  try {
    content = await fs.readFile(filePath, 'utf-8');
  } catch {
    return [];
  }

  const lines = content.split('\n').filter(l => l.trim());
  const tasks = new Map<string, TaskItem>();
  let nextId = 1;

  for (const line of lines) {
    let parsed: TranscriptLine;
    try {
      parsed = JSON.parse(line);
    } catch {
      continue;
    }

    if (parsed.type !== 'assistant') continue;

    const message = parsed.message;
    if (!message?.content) continue;
    if (!Array.isArray(message.content)) continue;

    for (const block of message.content as ContentBlock[]) {
      if (block.type !== 'tool_use') continue;
      if (!block.name || !['TaskCreate', 'TaskUpdate'].includes(block.name)) continue;

      const input = block.input as Record<string, unknown> | undefined;
      if (!input) continue;

      if (block.name === 'TaskCreate') {
        const id = String(nextId++);
        tasks.set(id, {
          id,
          subject: (input.subject as string) ?? '',
          description: input.description as string | undefined,
          activeForm: input.activeForm as string | undefined,
          status: 'pending',
        });
      } else if (block.name === 'TaskUpdate' && input.taskId) {
        const existing = tasks.get(input.taskId as string);
        if (existing) {
          if (input.status) existing.status = input.status as TaskItem['status'];
          if (input.subject) existing.subject = input.subject as string;
          if (input.activeForm) existing.activeForm = input.activeForm as string;
          if (input.description) existing.description = input.description as string;
          if (input.addBlockedBy) {
            existing.blockedBy = [
              ...(existing.blockedBy ?? []),
              ...(input.addBlockedBy as string[]),
            ];
          }
          if (input.addBlocks) {
            existing.blocks = [
              ...(existing.blocks ?? []),
              ...(input.addBlocks as string[]),
            ];
          }
          if (input.owner) existing.owner = input.owner as string;
        }
      }
    }
  }

  return Array.from(tasks.values());
}
```

**Note:** The method signature uses `(vaultRoot, sessionId)` to match the existing `readTranscript` pattern, NOT `(sessionId, vaultRoot)` as the spec originally suggested. The `getTranscriptsDir` method already derives the path from `vaultRoot`.

**Acceptance criteria:**
- Empty JSONL returns empty array
- TaskCreate entries create tasks with auto-incrementing IDs and status 'pending'
- TaskUpdate entries modify existing task properties
- TaskUpdate for non-existent taskId is a no-op
- blockedBy and blocks arrays accumulate (addBlockedBy appends)
- Non-task tool_use blocks are ignored
- Non-assistant messages are ignored
- File not found returns empty array

---

### Task 1.4: Add /api/sessions/:id/tasks endpoint and getTasks to Transport interface

**Files:** `gateway/src/server/routes/sessions.ts`, `gateway/src/shared/transport.ts`, `gateway/src/client/lib/http-transport.ts`, `gateway/src/client/lib/direct-transport.ts`
**Dependencies:** Task 1.1, Task 1.3
**ActiveForm:** Adding tasks API endpoint and Transport methods

#### 1. API Endpoint (`gateway/src/server/routes/sessions.ts`)

Add the following route after the existing `GET /:id/messages` route (after line 53):

```typescript
// GET /api/sessions/:id/tasks - Get task state from SDK transcript
router.get('/:id/tasks', async (req, res) => {
  try {
    const tasks = await transcriptReader.readTasks(vaultRoot, req.params.id);
    res.json({ tasks });
  } catch (err) {
    res.status(404).json({ error: 'Session not found' });
  }
});
```

#### 2. Transport Interface (`gateway/src/shared/transport.ts`)

Add import for TaskItem:

```typescript
import type {
  Session,
  CreateSessionRequest,
  UpdateSessionRequest,
  CommandRegistry,
  HistoryMessage,
  StreamEvent,
  TaskItem,
} from './types';
```

Add `getTasks` method to the `Transport` interface (after `getMessages`):

```typescript
getTasks(sessionId: string): Promise<{ tasks: TaskItem[] }>;
```

#### 3. HttpTransport (`gateway/src/client/lib/http-transport.ts`)

Add import for TaskItem:

```typescript
import type {
  Session,
  CreateSessionRequest,
  UpdateSessionRequest,
  CommandRegistry,
  HistoryMessage,
  StreamEvent,
  TaskItem,
} from '@shared/types';
```

Add `getTasks` method after `getMessages`:

```typescript
async getTasks(sessionId: string): Promise<{ tasks: TaskItem[] }> {
  const res = await fetch(`${this.baseUrl}/sessions/${sessionId}/tasks`);
  if (!res.ok) return { tasks: [] };
  return res.json();
}
```

#### 4. DirectTransport (`gateway/src/client/lib/direct-transport.ts`)

Add TaskItem to imports:

```typescript
import type {
  StreamEvent,
  Session,
  CreateSessionRequest,
  UpdateSessionRequest,
  PermissionMode,
  HistoryMessage,
  CommandRegistry,
  TaskItem,
} from '@shared/types';
```

Add `readTasks` to the `transcriptReader` typing in `DirectTransportServices` interface:

```typescript
transcriptReader: {
  listSessions(vaultRoot: string): Promise<Session[]>;
  getSession(vaultRoot: string, id: string): Promise<Session | null>;
  readTranscript(vaultRoot: string, id: string): Promise<HistoryMessage[]>;
  readTasks(vaultRoot: string, sessionId: string): Promise<TaskItem[]>;
};
```

Add `getTasks` method to `DirectTransport` class (after `getMessages`):

```typescript
async getTasks(sessionId: string): Promise<{ tasks: TaskItem[] }> {
  const tasks = await this.services.transcriptReader.readTasks(
    this.services.vaultRoot,
    sessionId,
  );
  return { tasks };
}
```

**Acceptance criteria:**
- GET /api/sessions/:id/tasks returns `{ tasks: TaskItem[] }`
- Returns 404 when session transcript doesn't exist
- Transport interface includes getTasks method
- HttpTransport.getTasks calls the correct endpoint and returns `{ tasks: [] }` on error
- DirectTransport.getTasks calls transcriptReader.readTasks directly
- TypeScript compiles without errors

---

## Phase 2: Client State & UI

### Task 2.1: Create use-task-state.ts hook

**File:** `gateway/src/client/hooks/use-task-state.ts` (new file)
**Dependencies:** Task 1.1, Task 1.4
**ActiveForm:** Creating use-task-state hook

Create a new React hook that manages task state from both streaming events and historical data.

**Create `gateway/src/client/hooks/use-task-state.ts`:**

```typescript
import { useState, useCallback, useEffect, useRef } from 'react';
import { useTransport } from '../contexts/TransportContext';
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

**Note:** The import uses `'../contexts/TransportContext'` to match the existing pattern in `use-chat-session.ts` (line 4 of that file).

**Acceptance criteria:**
- Task creation via handleTaskEvent adds to map with auto-incrementing IDs
- Task update modifies existing task properties
- Task update for non-existent ID is a no-op
- Sort order: in_progress first, pending second, completed last
- Max 10 tasks visible (11th task not in returned array)
- activeForm returns the in_progress task's activeForm
- activeForm is null when no in_progress task
- clearTasks resets state
- toggleCollapse flips isCollapsed boolean
- Historical tasks load on sessionId change

---

### Task 2.2: Add task_update handling to use-chat-session.ts

**File:** `gateway/src/client/hooks/use-chat-session.ts`
**Dependencies:** Task 1.1, Task 1.2
**ActiveForm:** Adding task_update event handling to use-chat-session

Add an `onTaskEvent` callback option to `useChatSession` so that task_update SSE events are forwarded to the task state hook.

**Add import for TaskUpdateEvent (line 3):**

```typescript
import type { TextDelta, ToolCallEvent, ApprovalEvent, QuestionPromptEvent, ErrorEvent, SessionStatusEvent, QuestionItem, TaskUpdateEvent } from '@shared/types';
```

**Modify the `ChatSessionOptions` interface (line ~37-39):**

```typescript
interface ChatSessionOptions {
  /** Transform message content before sending to server (e.g., prepend context) */
  transformContent?: (content: string) => string | Promise<string>;
  /** Callback for task_update events from the SSE stream */
  onTaskEvent?: (event: TaskUpdateEvent) => void;
}
```

**Add a case to the `handleStreamEvent` switch statement (around line 232, before the 'done' case):**

```typescript
case 'task_update': {
  const taskEvent = data as TaskUpdateEvent;
  options.onTaskEvent?.(taskEvent);
  break;
}
```

**Acceptance criteria:**
- task_update events in the SSE stream invoke the onTaskEvent callback
- When onTaskEvent is not provided, task_update events are silently ignored
- No changes to existing event handling behavior

---

### Task 2.3: Create TaskListPanel.tsx component

**File:** `gateway/src/client/components/chat/TaskListPanel.tsx` (new file)
**Dependencies:** Task 1.1
**ActiveForm:** Creating TaskListPanel component

Create a compact, collapsible task list panel component.

**Create `gateway/src/client/components/chat/TaskListPanel.tsx`:**

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

**Acceptance criteria:**
- Renders nothing when tasks array is empty
- Renders header with correct counts (done, in progress, open)
- Renders task items with correct status icons (spinner for in_progress, circle for pending, checkmark for completed)
- Completed tasks have line-through and muted styling
- In-progress tasks have bold styling
- Collapsed state hides task list but shows header
- ActiveForm spinner shown when provided and not collapsed
- Long task subjects are truncated

---

### Task 2.4: Integrate TaskListPanel into ChatPanel.tsx

**File:** `gateway/src/client/components/chat/ChatPanel.tsx`
**Dependencies:** Task 2.1, Task 2.2, Task 2.3
**ActiveForm:** Integrating TaskListPanel into ChatPanel

Wire up the task state hook, connect it to the chat session's task events, and render the TaskListPanel between the message list and input area.

**Add imports (after existing imports around line 1-9):**

```typescript
import { TaskListPanel } from './TaskListPanel';
import { useTaskState } from '../../hooks/use-task-state';
```

**Add task state hook inside the `ChatPanel` function (after the existing `useChatSession` call, around line 18-19):**

```typescript
const taskState = useTaskState({ sessionId });
```

**Modify the `useChatSession` call to pass `onTaskEvent`:**

Change:
```typescript
const { messages, input, setInput, handleSubmit, status, error, stop, isLoadingHistory, sessionStatus } =
  useChatSession(sessionId, { transformContent });
```

To:
```typescript
const { messages, input, setInput, handleSubmit, status, error, stop, isLoadingHistory, sessionStatus } =
  useChatSession(sessionId, {
    transformContent,
    onTaskEvent: taskState.handleTaskEvent,
  });
```

**Add TaskListPanel JSX between the MessageList and the error/input section. Insert after the closing parenthesis of the ternary that renders MessageList (after line 114) and before the error div (line 116):**

```tsx
<TaskListPanel
  tasks={taskState.tasks}
  activeForm={taskState.activeForm}
  isCollapsed={taskState.isCollapsed}
  onToggleCollapse={taskState.toggleCollapse}
/>
```

The resulting JSX structure should be:
1. Loading indicator / empty state / MessageList (existing ternary)
2. **TaskListPanel** (new)
3. Error banner (existing)
4. Input area with CommandPalette (existing)

**Acceptance criteria:**
- TaskListPanel renders between MessageList and the input area
- Task events from SSE stream update the task list in real-time
- Historical tasks load when opening a past session
- Collapsing/expanding works
- ActiveForm spinner displays during in_progress tasks
- No regressions to existing message display or streaming

---

## Phase 3: Polish

### Task 3.1: Write all tests

**Files:** Multiple new test files
**Dependencies:** Task 2.4 (all implementation complete)
**ActiveForm:** Writing tests for task list feature

Create comprehensive tests for all new functionality.

#### Test File 1: `gateway/src/server/services/__tests__/build-task-event.test.ts`

```typescript
import { describe, it, expect } from 'vitest';

// Import buildTaskEvent - it needs to be exported from agent-manager.ts
// If not exported, test the behavior through the full sendMessage flow instead
import { buildTaskEvent } from '../agent-manager';

describe('buildTaskEvent', () => {
  it('TaskCreate produces create action with pending status', () => {
    const result = buildTaskEvent('TaskCreate', {
      subject: 'Test task',
      description: 'A test description',
      activeForm: 'Creating test task',
    });
    expect(result).toEqual({
      action: 'create',
      task: {
        id: '',
        subject: 'Test task',
        description: 'A test description',
        activeForm: 'Creating test task',
        status: 'pending',
      },
    });
  });

  it('TaskUpdate produces update action with provided fields', () => {
    const result = buildTaskEvent('TaskUpdate', {
      taskId: '1',
      subject: 'Updated subject',
      status: 'in_progress',
      activeForm: 'Working on task',
      description: 'Updated desc',
      addBlockedBy: ['2', '3'],
      addBlocks: ['4'],
      owner: 'agent-1',
    });
    expect(result).toEqual({
      action: 'update',
      task: {
        id: '1',
        subject: 'Updated subject',
        status: 'in_progress',
        activeForm: 'Working on task',
        description: 'Updated desc',
        blockedBy: ['2', '3'],
        blocks: ['4'],
        owner: 'agent-1',
      },
    });
  });

  it('TaskUpdate with only taskId and status works', () => {
    const result = buildTaskEvent('TaskUpdate', {
      taskId: '1',
      status: 'completed',
    });
    expect(result).not.toBeNull();
    expect(result!.task.status).toBe('completed');
    expect(result!.task.id).toBe('1');
  });

  it('TaskList returns null', () => {
    expect(buildTaskEvent('TaskList', {})).toBeNull();
  });

  it('TaskGet returns null', () => {
    expect(buildTaskEvent('TaskGet', { taskId: '1' })).toBeNull();
  });

  it('Unknown tool name returns null', () => {
    expect(buildTaskEvent('SomeOtherTool', {})).toBeNull();
  });
});
```

#### Test File 2: `gateway/src/server/services/__tests__/transcript-reader-tasks.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TranscriptReader } from '../transcript-reader';

vi.mock('fs/promises');

describe('TranscriptReader.readTasks', () => {
  let reader: TranscriptReader;

  beforeEach(() => {
    reader = new TranscriptReader();
    vi.resetAllMocks();
  });

  function makeJsonl(lines: object[]): string {
    return lines.map(l => JSON.stringify(l)).join('\n');
  }

  function taskCreateLine(subject: string, extra: Record<string, unknown> = {}) {
    return {
      type: 'assistant',
      message: {
        content: [{
          type: 'tool_use',
          name: 'TaskCreate',
          id: 'tool_' + Math.random().toString(36).slice(2),
          input: { subject, ...extra },
        }],
      },
    };
  }

  function taskUpdateLine(taskId: string, updates: Record<string, unknown>) {
    return {
      type: 'assistant',
      message: {
        content: [{
          type: 'tool_use',
          name: 'TaskUpdate',
          id: 'tool_' + Math.random().toString(36).slice(2),
          input: { taskId, ...updates },
        }],
      },
    };
  }

  it('returns empty array for empty JSONL', async () => {
    const fs = await import('fs/promises');
    (fs.readFile as ReturnType<typeof vi.fn>).mockResolvedValue('');
    const tasks = await reader.readTasks('/vault', 'session-1');
    expect(tasks).toEqual([]);
  });

  it('creates tasks with pending status from TaskCreate', async () => {
    const fs = await import('fs/promises');
    (fs.readFile as ReturnType<typeof vi.fn>).mockResolvedValue(
      makeJsonl([taskCreateLine('First task'), taskCreateLine('Second task')])
    );
    const tasks = await reader.readTasks('/vault', 'session-1');
    expect(tasks).toHaveLength(2);
    expect(tasks[0]).toMatchObject({ id: '1', subject: 'First task', status: 'pending' });
    expect(tasks[1]).toMatchObject({ id: '2', subject: 'Second task', status: 'pending' });
  });

  it('applies TaskUpdate to existing tasks', async () => {
    const fs = await import('fs/promises');
    (fs.readFile as ReturnType<typeof vi.fn>).mockResolvedValue(
      makeJsonl([
        taskCreateLine('My task'),
        taskUpdateLine('1', { status: 'in_progress', activeForm: 'Working' }),
      ])
    );
    const tasks = await reader.readTasks('/vault', 'session-1');
    expect(tasks[0]).toMatchObject({ status: 'in_progress', activeForm: 'Working' });
  });

  it('accumulates blockedBy arrays', async () => {
    const fs = await import('fs/promises');
    (fs.readFile as ReturnType<typeof vi.fn>).mockResolvedValue(
      makeJsonl([
        taskCreateLine('My task'),
        taskUpdateLine('1', { addBlockedBy: ['2'] }),
        taskUpdateLine('1', { addBlockedBy: ['3'] }),
      ])
    );
    const tasks = await reader.readTasks('/vault', 'session-1');
    expect(tasks[0].blockedBy).toEqual(['2', '3']);
  });

  it('ignores TaskUpdate for non-existent task', async () => {
    const fs = await import('fs/promises');
    (fs.readFile as ReturnType<typeof vi.fn>).mockResolvedValue(
      makeJsonl([taskUpdateLine('999', { status: 'completed' })])
    );
    const tasks = await reader.readTasks('/vault', 'session-1');
    expect(tasks).toEqual([]);
  });

  it('ignores non-task tool_use blocks', async () => {
    const fs = await import('fs/promises');
    (fs.readFile as ReturnType<typeof vi.fn>).mockResolvedValue(
      makeJsonl([{
        type: 'assistant',
        message: {
          content: [{
            type: 'tool_use',
            name: 'Read',
            id: 'tool_read',
            input: { file_path: '/foo' },
          }],
        },
      }])
    );
    const tasks = await reader.readTasks('/vault', 'session-1');
    expect(tasks).toEqual([]);
  });

  it('ignores non-assistant messages', async () => {
    const fs = await import('fs/promises');
    (fs.readFile as ReturnType<typeof vi.fn>).mockResolvedValue(
      makeJsonl([{
        type: 'user',
        message: { role: 'user', content: 'Hello' },
      }])
    );
    const tasks = await reader.readTasks('/vault', 'session-1');
    expect(tasks).toEqual([]);
  });

  it('returns empty array when file not found', async () => {
    const fs = await import('fs/promises');
    (fs.readFile as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('ENOENT'));
    const tasks = await reader.readTasks('/vault', 'session-1');
    expect(tasks).toEqual([]);
  });
});
```

#### Test File 3: `gateway/src/client/hooks/__tests__/use-task-state.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useTaskState } from '../use-task-state';
import type { TaskUpdateEvent } from '@shared/types';

// Mock the transport context
const mockGetTasks = vi.fn().mockResolvedValue({ tasks: [] });

vi.mock('../../contexts/TransportContext', () => ({
  useTransport: () => ({
    getTasks: mockGetTasks,
  }),
}));

describe('useTaskState', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetTasks.mockResolvedValue({ tasks: [] });
  });

  it('starts with empty tasks', () => {
    const { result } = renderHook(() => useTaskState({ sessionId: 'test' }));
    expect(result.current.tasks).toEqual([]);
    expect(result.current.activeForm).toBeNull();
  });

  it('adds tasks via handleTaskEvent create', () => {
    const { result } = renderHook(() => useTaskState({ sessionId: 'test' }));

    act(() => {
      result.current.handleTaskEvent({
        action: 'create',
        task: { id: '', subject: 'Task A', status: 'pending' },
      });
    });

    expect(result.current.tasks).toHaveLength(1);
    expect(result.current.tasks[0].subject).toBe('Task A');
    expect(result.current.tasks[0].id).toBe('1');
  });

  it('auto-increments IDs for created tasks', () => {
    const { result } = renderHook(() => useTaskState({ sessionId: 'test' }));

    act(() => {
      result.current.handleTaskEvent({
        action: 'create',
        task: { id: '', subject: 'Task A', status: 'pending' },
      });
      result.current.handleTaskEvent({
        action: 'create',
        task: { id: '', subject: 'Task B', status: 'pending' },
      });
    });

    expect(result.current.tasks[0].id).not.toBe(result.current.tasks[1].id);
  });

  it('updates existing tasks', () => {
    const { result } = renderHook(() => useTaskState({ sessionId: 'test' }));

    act(() => {
      result.current.handleTaskEvent({
        action: 'create',
        task: { id: '', subject: 'Task A', status: 'pending' },
      });
    });

    act(() => {
      result.current.handleTaskEvent({
        action: 'update',
        task: { id: '1', subject: 'Task A', status: 'in_progress', activeForm: 'Working' },
      });
    });

    expect(result.current.tasks[0].status).toBe('in_progress');
    expect(result.current.activeForm).toBe('Working');
  });

  it('ignores update for non-existent task', () => {
    const { result } = renderHook(() => useTaskState({ sessionId: 'test' }));

    act(() => {
      result.current.handleTaskEvent({
        action: 'update',
        task: { id: '999', subject: '', status: 'completed' },
      });
    });

    expect(result.current.tasks).toHaveLength(0);
  });

  it('sorts tasks: in_progress > pending > completed', () => {
    const { result } = renderHook(() => useTaskState({ sessionId: 'test' }));

    act(() => {
      result.current.handleTaskEvent({
        action: 'create',
        task: { id: '', subject: 'Completed', status: 'pending' },
      });
      result.current.handleTaskEvent({
        action: 'create',
        task: { id: '', subject: 'In Progress', status: 'pending' },
      });
      result.current.handleTaskEvent({
        action: 'create',
        task: { id: '', subject: 'Pending', status: 'pending' },
      });
    });

    act(() => {
      result.current.handleTaskEvent({
        action: 'update',
        task: { id: '1', subject: 'Completed', status: 'completed' },
      });
      result.current.handleTaskEvent({
        action: 'update',
        task: { id: '2', subject: 'In Progress', status: 'in_progress' },
      });
    });

    expect(result.current.tasks[0].subject).toBe('In Progress');
    expect(result.current.tasks[1].subject).toBe('Pending');
    expect(result.current.tasks[2].subject).toBe('Completed');
  });

  it('limits visible tasks to 10', () => {
    const { result } = renderHook(() => useTaskState({ sessionId: 'test' }));

    act(() => {
      for (let i = 0; i < 11; i++) {
        result.current.handleTaskEvent({
          action: 'create',
          task: { id: '', subject: `Task ${i + 1}`, status: 'pending' },
        });
      }
    });

    expect(result.current.tasks).toHaveLength(10);
  });

  it('activeForm is null when no in_progress task', () => {
    const { result } = renderHook(() => useTaskState({ sessionId: 'test' }));

    act(() => {
      result.current.handleTaskEvent({
        action: 'create',
        task: { id: '', subject: 'Task', status: 'pending', activeForm: 'Doing stuff' },
      });
    });

    expect(result.current.activeForm).toBeNull();
  });

  it('clearTasks resets state', () => {
    const { result } = renderHook(() => useTaskState({ sessionId: 'test' }));

    act(() => {
      result.current.handleTaskEvent({
        action: 'create',
        task: { id: '', subject: 'Task', status: 'pending' },
      });
    });

    expect(result.current.tasks).toHaveLength(1);

    act(() => {
      result.current.clearTasks();
    });

    expect(result.current.tasks).toHaveLength(0);
  });

  it('toggleCollapse flips boolean', () => {
    const { result } = renderHook(() => useTaskState({ sessionId: 'test' }));

    expect(result.current.isCollapsed).toBe(false);

    act(() => {
      result.current.toggleCollapse();
    });

    expect(result.current.isCollapsed).toBe(true);

    act(() => {
      result.current.toggleCollapse();
    });

    expect(result.current.isCollapsed).toBe(false);
  });

  it('loads historical tasks on sessionId change', async () => {
    mockGetTasks.mockResolvedValue({
      tasks: [
        { id: '1', subject: 'Historical task', status: 'completed' },
      ],
    });

    const { result, rerender } = renderHook(
      ({ sessionId }) => useTaskState({ sessionId }),
      { initialProps: { sessionId: 'session-1' } },
    );

    // Wait for the async effect to resolve
    await vi.waitFor(() => {
      expect(result.current.tasks).toHaveLength(1);
    });

    expect(result.current.tasks[0].subject).toBe('Historical task');
  });
});
```

#### Test File 4: `gateway/src/client/components/chat/__tests__/TaskListPanel.test.tsx`

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskListPanel } from '../TaskListPanel';
import type { TaskItem } from '@shared/types';

// Mock motion/react to render plain elements
vi.mock('motion/react', () => ({
  AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  motion: {
    div: ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => <div {...props}>{children}</div>,
    ul: ({ children, ...props }: React.HTMLAttributes<HTMLUListElement>) => <ul {...props}>{children}</ul>,
  },
}));

const baseTasks: TaskItem[] = [
  { id: '1', subject: 'First task', status: 'completed' },
  { id: '2', subject: 'Second task', status: 'in_progress', activeForm: 'Working on it' },
  { id: '3', subject: 'Third task', status: 'pending' },
];

describe('TaskListPanel', () => {
  it('renders nothing when tasks array is empty', () => {
    const { container } = render(
      <TaskListPanel tasks={[]} activeForm={null} isCollapsed={false} onToggleCollapse={() => {}} />
    );
    expect(container.innerHTML).toBe('');
  });

  it('renders header with correct counts', () => {
    render(
      <TaskListPanel tasks={baseTasks} activeForm={null} isCollapsed={false} onToggleCollapse={() => {}} />
    );
    expect(screen.getByText(/3 tasks/)).toBeInTheDocument();
    expect(screen.getByText(/1 done/)).toBeInTheDocument();
    expect(screen.getByText(/1 in progress/)).toBeInTheDocument();
    expect(screen.getByText(/1 open/)).toBeInTheDocument();
  });

  it('renders task items', () => {
    render(
      <TaskListPanel tasks={baseTasks} activeForm={null} isCollapsed={false} onToggleCollapse={() => {}} />
    );
    expect(screen.getByText('First task')).toBeInTheDocument();
    expect(screen.getByText('Second task')).toBeInTheDocument();
    expect(screen.getByText('Third task')).toBeInTheDocument();
  });

  it('completed tasks have line-through styling', () => {
    render(
      <TaskListPanel tasks={baseTasks} activeForm={null} isCollapsed={false} onToggleCollapse={() => {}} />
    );
    const completedItem = screen.getByText('First task').closest('li');
    expect(completedItem?.className).toContain('line-through');
  });

  it('in-progress tasks have font-medium styling', () => {
    render(
      <TaskListPanel tasks={baseTasks} activeForm={null} isCollapsed={false} onToggleCollapse={() => {}} />
    );
    const inProgressItem = screen.getByText('Second task').closest('li');
    expect(inProgressItem?.className).toContain('font-medium');
  });

  it('calls onToggleCollapse when header clicked', () => {
    const onToggle = vi.fn();
    render(
      <TaskListPanel tasks={baseTasks} activeForm={null} isCollapsed={false} onToggleCollapse={onToggle} />
    );
    fireEvent.click(screen.getByRole('button'));
    expect(onToggle).toHaveBeenCalledOnce();
  });

  it('shows activeForm spinner when provided and not collapsed', () => {
    render(
      <TaskListPanel tasks={baseTasks} activeForm="Doing something" isCollapsed={false} onToggleCollapse={() => {}} />
    );
    expect(screen.getByText('Doing something')).toBeInTheDocument();
  });

  it('hides activeForm when collapsed', () => {
    render(
      <TaskListPanel tasks={baseTasks} activeForm="Doing something" isCollapsed={true} onToggleCollapse={() => {}} />
    );
    expect(screen.queryByText('Doing something')).not.toBeInTheDocument();
  });
});
```

**Note on buildTaskEvent testing:** The `buildTaskEvent` function must be exported from `agent-manager.ts` for direct unit testing. If keeping it as a module-private function is preferred, test it indirectly through the streaming pipeline. The export approach is recommended for cleaner tests.

**Acceptance criteria:**
- All test files created and passing
- buildTaskEvent: 6 test cases covering all tool names and edge cases
- transcript-reader readTasks: 7 test cases covering JSONL parsing
- use-task-state: 10 test cases covering hook behavior
- TaskListPanel: 7 test cases covering rendering and interaction
- All tests run with `npm run test:run`

---

## Summary

| Task | Phase | Subject | Dependencies |
|------|-------|---------|--------------|
| 1.1 | P1 | Add shared task types to types.ts | None |
| 1.2 | P1 | Add task tool detection in agent-manager.ts | 1.1 |
| 1.3 | P1 | Add readTasks() to transcript-reader.ts | 1.1 |
| 1.4 | P1 | Add API endpoint and Transport methods | 1.1, 1.3 |
| 2.1 | P2 | Create use-task-state.ts hook | 1.1, 1.4 |
| 2.2 | P2 | Add task_update handling to use-chat-session.ts | 1.1, 1.2 |
| 2.3 | P2 | Create TaskListPanel.tsx component | 1.1 |
| 2.4 | P2 | Integrate into ChatPanel.tsx | 2.1, 2.2, 2.3 |
| 3.1 | P3 | Write all tests | 2.4 |
