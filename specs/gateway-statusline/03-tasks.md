# Task Breakdown: Gateway Statusline
Generated: 2026-02-08
Source: specs/gateway-statusline/02-specification.md
Last Decompose: 2026-02-08

## Overview

Add an interactive status line below the chat text entry in the Gateway client. The status line displays session metadata (model, permission mode, context usage, cost) that updates dynamically after each response, and allows users to change settings (permission mode, model) by clicking status items. The feature spans the full vertical slice: shared types, server-side event forwarding, Transport interface extension, client hooks, and UI components.

## Phase 1: Data Pipeline

### Task 1.1: Expand shared types with SessionStatusEvent, PermissionMode, and UpdateSessionRequest

**Objective:** Add new types to `src/shared/types.ts` to support the session status event pipeline and session update mutations.

**Files modified:**
- `gateway/src/shared/types.ts`

**Changes:**

1. Add `PermissionMode` type alias:
```typescript
export type PermissionMode = 'default' | 'plan' | 'acceptEdits' | 'bypassPermissions';
```

2. Add `SessionStatusEvent` interface:
```typescript
export interface SessionStatusEvent {
  sessionId: string;
  model?: string;
  costUsd?: number;
  contextTokens?: number;
  contextMaxTokens?: number;
}
```

3. Add `UpdateSessionRequest` interface:
```typescript
export interface UpdateSessionRequest {
  permissionMode?: PermissionMode;
  model?: string;
}
```

4. Add `'session_status'` to `StreamEventType` union:
```typescript
export type StreamEventType =
  | 'text_delta'
  | 'tool_call_start'
  | 'tool_call_delta'
  | 'tool_call_end'
  | 'tool_result'
  | 'approval_required'
  | 'error'
  | 'done'
  | 'session_status';
```

5. Add `SessionStatusEvent` to `StreamEvent.data` union:
```typescript
export interface StreamEvent {
  type: StreamEventType;
  data: TextDelta | ToolCallEvent | ApprovalEvent | ErrorEvent | DoneEvent | SessionStatusEvent;
}
```

6. Update `Session` interface to use `PermissionMode`:
```typescript
export interface Session {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  lastMessagePreview?: string;
  permissionMode: PermissionMode;
}
```

7. Update `CreateSessionRequest` to use `PermissionMode`:
```typescript
export interface CreateSessionRequest {
  permissionMode?: PermissionMode;
}
```

**Acceptance criteria:**
- All existing type usages compile without errors
- New types are exported and importable from `@shared/types`
- Existing tests pass (no runtime changes)

---

### Task 1.2: Forward session status events from AgentManager

**Objective:** Modify `agent-manager.ts` to emit `session_status` events from `result` and `system.init` SDK messages, add `updateSession` method, expand `AgentSession` with `model`, and handle all four permission modes.

**Files modified:**
- `gateway/src/server/services/agent-manager.ts`

**Changes:**

1. Import `PermissionMode` from shared types.

2. Update `AgentSession` interface:
```typescript
interface AgentSession {
  sdkSessionId: string;
  lastActivity: number;
  permissionMode: PermissionMode;
  model?: string;
  hasStarted: boolean;
  pendingApproval?: {
    toolCallId: string;
    resolve: (approved: boolean) => void;
  };
}
```

3. Update `ensureSession` signature to accept `PermissionMode`:
```typescript
ensureSession(sessionId: string, opts: { permissionMode: PermissionMode }): void
```

4. Update `sendMessage` signature and auto-create to use `PermissionMode`:
```typescript
async *sendMessage(
  sessionId: string,
  content: string,
  opts?: { permissionMode?: PermissionMode }
): AsyncGenerator<StreamEvent>
```

5. In `sendMessage`, apply model from session state to SDK options:
```typescript
if (session.model) {
  sdkOptions.model = session.model;
}
```

6. Update permission mode mapping to handle all four modes:
```typescript
switch (session.permissionMode) {
  case 'bypassPermissions':
    sdkOptions.permissionMode = 'bypassPermissions';
    sdkOptions.allowDangerouslySkipPermissions = true;
    break;
  case 'plan':
    sdkOptions.permissionMode = 'plan';
    break;
  case 'acceptEdits':
    sdkOptions.permissionMode = 'acceptEdits';
    break;
  default:
    sdkOptions.permissionMode = 'default';
}
```

7. In `mapSdkMessage`, forward model info from `system.init`:
```typescript
if (message.type === 'system' && 'subtype' in message && message.subtype === 'init') {
  session.sdkSessionId = message.session_id;
  session.hasStarted = true;
  yield {
    type: 'session_status',
    data: {
      sessionId,
      model: (message as Record<string, unknown>).model as string | undefined,
    },
  };
  return;
}
```

8. In `mapSdkMessage`, emit `session_status` before `done` from `result`:
```typescript
if (message.type === 'result') {
  const result = message as Record<string, unknown>;
  yield {
    type: 'session_status',
    data: {
      sessionId,
      model: result.model as string | undefined,
      costUsd: result.total_cost_usd as number | undefined,
      contextTokens: (result.usage as Record<string, unknown>)?.input_tokens as number | undefined,
      contextMaxTokens: (result.usage as Record<string, unknown>)?.context_window as number | undefined,
    },
  };
  yield {
    type: 'done',
    data: { sessionId },
  };
}
```

9. Add `updateSession` method:
```typescript
updateSession(sessionId: string, opts: { permissionMode?: PermissionMode; model?: string }): boolean {
  const session = this.sessions.get(sessionId);
  if (!session) return false;
  if (opts.permissionMode) {
    session.permissionMode = opts.permissionMode;
  }
  if (opts.model) {
    session.model = opts.model;
  }
  return true;
}
```

**Acceptance criteria:**
- `session_status` event is emitted from both `system.init` and `result` messages
- `session_status` from init contains `model`
- `session_status` from result contains `model`, `costUsd`, `contextTokens`, `contextMaxTokens`
- `done` event is still emitted after `session_status` from result
- `updateSession` returns true for existing sessions, false for missing
- All four permission modes map correctly to SDK options
- Existing agent-manager tests pass (update as needed for new permission mode type)

---

### Task 1.3: Add updateSession to Transport interface and both implementations

**Objective:** Extend the `Transport` interface with `updateSession`, implement it in `HttpTransport` and `DirectTransport`.

**Files modified:**
- `gateway/src/shared/transport.ts`
- `gateway/src/client/lib/http-transport.ts`
- `gateway/src/client/lib/direct-transport.ts`

**Changes:**

1. **`transport.ts`** -- Add `updateSession` to interface:
```typescript
import type {
  Session,
  CreateSessionRequest,
  UpdateSessionRequest,
  CommandRegistry,
  HistoryMessage,
  StreamEvent,
} from './types';

export interface Transport {
  // ... existing 9 methods ...
  updateSession(id: string, opts: UpdateSessionRequest): Promise<Session>;
}
```

2. **`http-transport.ts`** -- Add implementation:
```typescript
updateSession(id: string, opts: UpdateSessionRequest): Promise<Session> {
  return fetchJSON<Session>(this.baseUrl, `/sessions/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(opts),
  });
}
```

3. **`direct-transport.ts`** -- Update `DirectTransportServices` interface:
```typescript
export interface DirectTransportServices {
  agentManager: {
    // ... existing methods (update permissionMode types to PermissionMode) ...
    updateSession(
      sessionId: string,
      opts: { permissionMode?: PermissionMode; model?: string },
    ): boolean;
  };
  // ...
}
```

Add implementation:
```typescript
async updateSession(id: string, opts: UpdateSessionRequest): Promise<Session> {
  const updated = this.services.agentManager.updateSession(id, opts);
  if (!updated) throw new Error(`Session not found: ${id}`);
  return this.getSession(id);
}
```

Also update all `'default' | 'dangerously-skip'` type references in `DirectTransportServices` to use `PermissionMode`.

**Acceptance criteria:**
- Transport interface has `updateSession` method
- HttpTransport sends PATCH request with correct body
- DirectTransport delegates to agentManager.updateSession and returns refreshed session
- All existing transport consumers compile
- `createMockTransport()` in tests updated to include `updateSession` mock

---

### Task 1.4: Add PATCH endpoint to sessions route

**Objective:** Add `PATCH /api/sessions/:id` Express route for updating session settings (permission mode, model).

**Files modified:**
- `gateway/src/server/routes/sessions.ts`

**Changes:**

Add before the existing approve/deny endpoints:
```typescript
// PATCH /api/sessions/:id - Update session settings
router.patch('/:id', async (req, res) => {
  const { permissionMode, model } = req.body;
  const updated = agentManager.updateSession(req.params.id, { permissionMode, model });
  if (!updated) return res.status(404).json({ error: 'Session not found' });

  const session = await transcriptReader.getSession(vaultRoot, req.params.id);
  if (session) {
    session.permissionMode = permissionMode ?? session.permissionMode;
  }
  res.json(session ?? { id: req.params.id, permissionMode, model });
});
```

**Acceptance criteria:**
- PATCH `/api/sessions/:id` with `{ permissionMode: 'plan' }` returns updated session
- PATCH to non-existent session returns 404
- Permission mode and model are applied to the in-memory agent session

---

## Phase 2: Client Hooks

### Task 2.1: Handle session_status events in useChatSession

**Objective:** Extend `useChatSession` to capture `session_status` stream events and expose them in its return value.

**Files modified:**
- `gateway/src/client/hooks/use-chat-session.ts`

**Changes:**

1. Import `SessionStatusEvent` from shared types:
```typescript
import type { TextDelta, ToolCallEvent, ErrorEvent, SessionStatusEvent } from '@shared/types';
```

2. Add state for session status:
```typescript
const [sessionStatus, setSessionStatus] = useState<SessionStatusEvent | null>(null);
```

3. Add `session_status` case to `handleStreamEvent`:
```typescript
case 'session_status': {
  setSessionStatus(data as SessionStatusEvent);
  break;
}
```

4. Expand return value:
```typescript
return { messages, input, setInput, handleSubmit, status, error, stop, isLoadingHistory, sessionStatus };
```

**Acceptance criteria:**
- `sessionStatus` is null before first response
- `sessionStatus` updates when `session_status` events arrive during streaming
- `sessionStatus` retains its value after streaming ends (not reset to null)
- Existing useChatSession tests pass (sessionStatus is additive)

---

### Task 2.2: Create useSessionStatus aggregation hook

**Objective:** Create a new hook that aggregates session metadata from TanStack Query and streaming state into a single status object with an update mutation.

**Files created:**
- `gateway/src/client/hooks/use-session-status.ts`

**Implementation:**
```typescript
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useTransport } from '../contexts/TransportContext';
import type { SessionStatusEvent, PermissionMode, UpdateSessionRequest } from '@shared/types';

export interface SessionStatusData {
  permissionMode: PermissionMode;
  model: string | null;
  costUsd: number | null;
  contextPercent: number | null;  // 0-100
  isStreaming: boolean;
}

export function useSessionStatus(
  sessionId: string,
  streamingStatus: SessionStatusEvent | null,
  isStreaming: boolean,
) {
  const transport = useTransport();
  const queryClient = useQueryClient();

  const { data: session } = useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => transport.getSession(sessionId),
    staleTime: 30_000,
  });

  const statusData: SessionStatusData = {
    permissionMode: session?.permissionMode ?? 'default',
    model: streamingStatus?.model ?? null,
    costUsd: streamingStatus?.costUsd ?? null,
    contextPercent: streamingStatus?.contextTokens && streamingStatus?.contextMaxTokens
      ? Math.round((streamingStatus.contextTokens / streamingStatus.contextMaxTokens) * 100)
      : null,
    isStreaming,
  };

  async function updateSession(opts: UpdateSessionRequest) {
    const updated = await transport.updateSession(sessionId, opts);
    queryClient.setQueryData(['session', sessionId], updated);
    return updated;
  }

  return { ...statusData, updateSession };
}
```

**Acceptance criteria:**
- Returns `permissionMode` from session query
- Returns `model`, `costUsd`, `contextPercent` from streaming status
- `contextPercent` correctly computes percentage (0-100)
- `contextPercent` is null when tokens or maxTokens are missing
- `updateSession` calls transport and updates query cache
- Hook works with both HttpTransport and DirectTransport

---

## Phase 3: UI Components

### Task 3.1: Create StatusLine container and Separator

**Objective:** Create the StatusLine container component that renders status items horizontally with separator dots.

**Files created:**
- `gateway/src/client/components/status/StatusLine.tsx`

**Implementation:**
```tsx
import { useSessionStatus } from '../../hooks/use-session-status';
import { PermissionModeItem } from './PermissionModeItem';
import { ModelItem } from './ModelItem';
import { CostItem } from './CostItem';
import { ContextItem } from './ContextItem';
import type { SessionStatusEvent } from '@shared/types';

interface StatusLineProps {
  sessionId: string;
  sessionStatus: SessionStatusEvent | null;
  isStreaming: boolean;
}

export function StatusLine({ sessionId, sessionStatus, isStreaming }: StatusLineProps) {
  const status = useSessionStatus(sessionId, sessionStatus, isStreaming);

  return (
    <div
      role="toolbar"
      aria-label="Session status"
      aria-live="polite"
      className="flex items-center gap-2 px-1 pt-2 text-xs text-muted-foreground"
    >
      <PermissionModeItem
        mode={status.permissionMode}
        onChangeMode={(mode) => status.updateSession({ permissionMode: mode })}
      />
      <Separator />
      {status.model && (
        <>
          <ModelItem
            model={status.model}
            onChangeModel={(model) => status.updateSession({ model })}
          />
          <Separator />
        </>
      )}
      {status.costUsd !== null && (
        <>
          <CostItem costUsd={status.costUsd} />
          <Separator />
        </>
      )}
      {status.contextPercent !== null && (
        <ContextItem percent={status.contextPercent} />
      )}
    </div>
  );
}

function Separator() {
  return <span className="text-muted-foreground/30" aria-hidden="true">&middot;</span>;
}
```

**Acceptance criteria:**
- Renders with `role="toolbar"` and `aria-label="Session status"`
- Has `aria-live="polite"` for screen reader updates
- Displays permission mode item always
- Conditionally displays model, cost, context items
- Separator dots between items
- Uses `text-xs text-muted-foreground` styling

---

### Task 3.2: Create PermissionModeItem with dropdown

**Objective:** Create an interactive status item showing the current permission mode with a dropdown to switch modes.

**Files created:**
- `gateway/src/client/components/status/PermissionModeItem.tsx`

**Implementation:**
Uses shadcn `DropdownMenu` with `DropdownMenuRadioGroup`. Four modes with icons:

```tsx
import { Shield, ShieldCheck, ShieldOff, ClipboardList } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import type { PermissionMode } from '@shared/types';

const PERMISSION_MODES: { value: PermissionMode; label: string; icon: typeof Shield; description: string }[] = [
  { value: 'default', label: 'Default', icon: Shield, description: 'Prompt for each tool call' },
  { value: 'acceptEdits', label: 'Accept Edits', icon: ShieldCheck, description: 'Auto-approve file edits' },
  { value: 'plan', label: 'Plan Mode', icon: ClipboardList, description: 'Research only, no edits' },
  { value: 'bypassPermissions', label: 'Bypass All', icon: ShieldOff, description: 'Auto-approve everything' },
];

interface PermissionModeItemProps {
  mode: PermissionMode;
  onChangeMode: (mode: PermissionMode) => void;
}

export function PermissionModeItem({ mode, onChangeMode }: PermissionModeItemProps) {
  const current = PERMISSION_MODES.find(m => m.value === mode) ?? PERMISSION_MODES[0];
  const Icon = current.icon;
  const isDangerous = mode === 'bypassPermissions';

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className={`inline-flex items-center gap-1 hover:text-foreground transition-colors duration-150 ${isDangerous ? 'text-red-500' : ''}`}
          aria-haspopup="menu"
        >
          <Icon className="h-3 w-3" />
          <span>{current.label}</span>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        <DropdownMenuLabel>Permission Mode</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuRadioGroup value={mode} onValueChange={(v) => onChangeMode(v as PermissionMode)}>
          {PERMISSION_MODES.map(m => {
            const MIcon = m.icon;
            return (
              <DropdownMenuRadioItem
                key={m.value}
                value={m.value}
                className={m.value === 'bypassPermissions' ? 'text-red-500' : ''}
              >
                <MIcon className="h-3 w-3 mr-2" />
                <div>
                  <div>{m.label}</div>
                  <div className="text-xs text-muted-foreground">{m.description}</div>
                </div>
              </DropdownMenuRadioItem>
            );
          })}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

**Acceptance criteria:**
- Displays current mode icon and label
- Clicking opens dropdown with all four modes
- Selecting a mode calls `onChangeMode`
- `bypassPermissions` styled in red/warning
- Keyboard accessible (Enter, arrow keys, Escape)

---

### Task 3.3: Create ModelItem, CostItem, and ContextItem components

**Objective:** Create the remaining three status item components.

**Files created:**
- `gateway/src/client/components/status/ModelItem.tsx`
- `gateway/src/client/components/status/CostItem.tsx`
- `gateway/src/client/components/status/ContextItem.tsx`

**ModelItem implementation:**
Dropdown listing Claude models. Displays shortened model name (e.g., "Sonnet 4.5" from "claude-sonnet-4-5-20250929"). Selecting a different model calls `onChangeModel`.

```tsx
import { Bot } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';

const MODEL_OPTIONS = [
  { value: 'claude-sonnet-4-5-20250929', label: 'Sonnet 4.5' },
  { value: 'claude-haiku-4-5-20251001', label: 'Haiku 4.5' },
  { value: 'claude-opus-4-6', label: 'Opus 4.6' },
];

function getModelLabel(model: string): string {
  const option = MODEL_OPTIONS.find(o => o.value === model);
  if (option) return option.label;
  // Fallback: extract name from model ID
  const match = model.match(/claude-(\w+)-/);
  return match ? match[1].charAt(0).toUpperCase() + match[1].slice(1) : model;
}

interface ModelItemProps {
  model: string;
  onChangeModel: (model: string) => void;
}

export function ModelItem({ model, onChangeModel }: ModelItemProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className="inline-flex items-center gap-1 hover:text-foreground transition-colors duration-150"
          aria-haspopup="menu"
        >
          <Bot className="h-3 w-3" />
          <span>{getModelLabel(model)}</span>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        <DropdownMenuLabel>Model</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuRadioGroup value={model} onValueChange={onChangeModel}>
          {MODEL_OPTIONS.map(m => (
            <DropdownMenuRadioItem key={m.value} value={m.value}>
              {m.label}
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

**CostItem implementation:**
Read-only. Shows `$X.XX` with DollarSign icon.

```tsx
import { DollarSign } from 'lucide-react';

interface CostItemProps {
  costUsd: number;
}

export function CostItem({ costUsd }: CostItemProps) {
  return (
    <span className="inline-flex items-center gap-1">
      <DollarSign className="h-3 w-3" />
      <span>${costUsd.toFixed(2)}</span>
    </span>
  );
}
```

**ContextItem implementation:**
Read-only. Shows `XX%` with color shift at high usage. Uses `Layers` icon.

```tsx
import { Layers } from 'lucide-react';

interface ContextItemProps {
  percent: number;
}

export function ContextItem({ percent }: ContextItemProps) {
  const colorClass = percent >= 95
    ? 'text-red-500'
    : percent >= 80
    ? 'text-amber-500'
    : '';

  return (
    <span className={`inline-flex items-center gap-1 ${colorClass}`}>
      <Layers className="h-3 w-3" />
      <span>{percent}%</span>
    </span>
  );
}
```

**Acceptance criteria:**
- ModelItem displays shortened model label and opens dropdown to switch
- CostItem displays `$X.XX` format
- ContextItem displays `XX%` with amber at 80%+ and red at 95%+
- All use 12px lucide icons
- Interactive items have hover effect `hover:text-foreground`
- No new npm dependencies

---

### Task 3.4: Integrate StatusLine into ChatPanel

**Objective:** Wire `StatusLine` into `ChatPanel` by passing `sessionStatus` from `useChatSession` and rendering it below `ChatInput`.

**Files modified:**
- `gateway/src/client/components/chat/ChatPanel.tsx`

**Changes:**

1. Import `StatusLine`:
```typescript
import { StatusLine } from '../status/StatusLine';
```

2. Destructure `sessionStatus` from `useChatSession`:
```typescript
const { messages, input, setInput, handleSubmit, status, error, stop, isLoadingHistory, sessionStatus } =
  useChatSession(sessionId, { transformContent });
```

3. Render `StatusLine` after `ChatInput` inside the `border-t` div:
```tsx
<div className="relative border-t p-4">
  <AnimatePresence>
    {showCommands && (
      <CommandPalette ... />
    )}
  </AnimatePresence>

  <ChatInput ... />

  <StatusLine
    sessionId={sessionId}
    sessionStatus={sessionStatus}
    isStreaming={status === 'streaming'}
  />
</div>
```

**Acceptance criteria:**
- StatusLine renders below ChatInput in both standalone and embedded modes
- Permission mode dropdown works end-to-end
- Model, cost, context display update after responses
- Cost and context are hidden until first response (graceful degradation)
- PermissionBanner continues to show for bypassPermissions mode
- ChatPanel layout does not shift unexpectedly
- No new npm dependencies

---

## Phase 4: Tests

### Task 4.1: Test session_status event emission in AgentManager

**Objective:** Add tests to `agent-manager.test.ts` verifying `session_status` events are emitted from `init` and `result` messages, and `updateSession` works correctly.

**Files modified:**
- `gateway/src/server/services/__tests__/agent-manager.test.ts`

**Tests to add:**

1. **`emits session_status from init message with model`**: Mock SDK to yield a system.init message with a model field. Assert that `session_status` event is yielded with the model.

2. **`emits session_status from result message with cost and context`**: Mock SDK to yield a result message with `total_cost_usd`, `usage.input_tokens`, and `usage.context_window`. Assert that `session_status` event is yielded before `done` event, containing `costUsd`, `contextTokens`, `contextMaxTokens`.

3. **`updateSession returns true for existing session`**: Create session, call `updateSession`, verify return value is true.

4. **`updateSession returns false for nonexistent session`**: Call `updateSession` on unknown ID, verify return value is false.

5. **`updateSession changes permission mode`**: Create session with 'default', call `updateSession({ permissionMode: 'plan' })`, verify next sendMessage uses the new mode.

6. **`handles all four permission modes correctly`**: Test that each PermissionMode value maps to the correct SDK options.

**Acceptance criteria:**
- All new tests pass
- All existing agent-manager tests pass (may need type updates from `'dangerously-skip'` to PermissionMode)

---

### Task 4.2: Test useSessionStatus hook and StatusLine component

**Objective:** Create test files for the `useSessionStatus` hook and `StatusLine` component.

**Files created:**
- `gateway/src/client/hooks/__tests__/use-session-status.test.tsx`
- `gateway/src/client/components/status/__tests__/StatusLine.test.tsx`

**useSessionStatus tests:**

1. **`returns default values when no streaming status`**: Render with null `streamingStatus`, verify `model` is null, `costUsd` is null, `contextPercent` is null.

2. **`computes contextPercent from streaming status`**: Pass `streamingStatus` with `contextTokens: 50000` and `contextMaxTokens: 200000`, verify `contextPercent` is 25.

3. **`returns permissionMode from session query`**: Mock `getSession` to return session with `permissionMode: 'plan'`, verify hook returns `permissionMode: 'plan'`.

4. **`updateSession calls transport and updates cache`**: Call `updateSession({ permissionMode: 'acceptEdits' })`, verify `transport.updateSession` was called and query cache was updated.

**StatusLine tests:**

1. **`renders with toolbar role and aria-label`**: Render StatusLine, verify `role="toolbar"` and `aria-label="Session status"`.

2. **`shows permission mode item`**: Render StatusLine, verify permission mode label is displayed.

3. **`hides model/cost/context when no streaming status`**: Render with null sessionStatus, verify model/cost/context are not rendered.

4. **`shows all items when streaming status is complete`**: Render with full sessionStatus, verify all items appear.

5. **`context item shows amber at 80%`**: Render with contextPercent 85, verify amber styling.

6. **`context item shows red at 95%`**: Render with contextPercent 97, verify red styling.

Use `createMockTransport()` pattern with `updateSession` mock. Wrap in `TransportProvider` + `QueryClientProvider`.

**Acceptance criteria:**
- All new tests pass
- Tests use the established `createMockTransport()` pattern
- Tests cover the critical data flow: streaming events -> hook -> UI components
- No flaky tests (no reliance on timing)

---

### Task 4.3: Update existing tests for type compatibility

**Objective:** Ensure all existing tests compile and pass with the new PermissionMode type and expanded Transport interface.

**Files modified:**
- `gateway/src/client/hooks/__tests__/use-chat-session.test.tsx` -- Update `createMockTransport` to include `updateSession`
- `gateway/src/server/services/__tests__/agent-manager.test.ts` -- Update permission mode string literals if needed
- Any other test files that reference `'dangerously-skip'` permission mode or create mock Transport objects

**Changes:**

1. Add `updateSession: vi.fn()` to all `createMockTransport()` helpers across the test suite.

2. Update any `'dangerously-skip'` references to `'bypassPermissions'` (or keep both if backward compat is needed in transcript-reader).

**Acceptance criteria:**
- `npm run test:run` passes with zero failures
- No TypeScript compilation errors
