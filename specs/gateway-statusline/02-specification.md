---
slug: gateway-statusline
phase: specification
status: draft
---

# Gateway Statusline - Specification

**Slug:** gateway-statusline
**Author:** Claude Code
**Date:** 2026-02-08
**Branch:** preflight/obsidian-copilot-plugin
**Ideation:** [01-ideation.md](./01-ideation.md)

---

## Overview

Add an interactive status line below the chat text entry in the Gateway client. The status line displays session metadata (model, permission mode, context usage, cost) that updates dynamically after each response, and allows users to change settings (permission mode, model) by clicking status items. The feature spans the full vertical slice: shared types, server-side event forwarding, Transport interface extension, client hooks, and UI components.

## Technical Design

### Architecture

**Pattern:** Compound Component with data hook

The StatusLine is composed of:
1. **`useSessionStatus` hook** -- aggregates session metadata from TanStack Query (`getSession`) and streaming state (new `session_status` event from `useChatSession`)
2. **`StatusLine` container** -- `role="toolbar"` wrapper, renders status items horizontally with separator dots
3. **`StatusLineItem` components** -- individual items, each self-contained with icon, label, and optional click interaction (dropdown for interactive items, static display for read-only items)

This matches the existing compound component pattern used by `ToolCallCard`, `SessionItem`, and `CommandPalette`.

### Data Pipeline

#### Layer 1: Shared Types (`src/shared/types.ts`)

Add new `SessionStatusEvent` type and expand `StreamEventType`:

```typescript
// New event type for session metadata
export interface SessionStatusEvent {
  sessionId: string;
  model?: string;
  costUsd?: number;
  contextTokens?: number;
  contextMaxTokens?: number;
}

// Add to StreamEventType union
export type StreamEventType =
  | 'text_delta'
  | 'tool_call_start'
  | 'tool_call_delta'
  | 'tool_call_end'
  | 'tool_result'
  | 'approval_required'
  | 'error'
  | 'done'
  | 'session_status';  // NEW

// Update StreamEvent data union
export interface StreamEvent {
  type: StreamEventType;
  data: TextDelta | ToolCallEvent | ApprovalEvent | ErrorEvent | DoneEvent | SessionStatusEvent;
}
```

Expand `Session` type with permission mode options and add `UpdateSessionRequest`:

```typescript
export type PermissionMode = 'default' | 'plan' | 'acceptEdits' | 'bypassPermissions';

export interface Session {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  lastMessagePreview?: string;
  permissionMode: PermissionMode;
}

export interface CreateSessionRequest {
  permissionMode?: PermissionMode;
}

export interface UpdateSessionRequest {
  permissionMode?: PermissionMode;
  model?: string;
}
```

**Note on permission mode naming:** The SDK uses `bypassPermissions` internally but the UI currently displays `dangerously-skip`. We'll adopt the SDK's naming (`default`, `plan`, `acceptEdits`, `bypassPermissions`) throughout the codebase and translate to display labels in the UI component only.

#### Layer 2: AgentManager (`src/server/services/agent-manager.ts`)

**Forward `result` message metadata.** Currently `mapSdkMessage` yields only `{ type: 'done', data: { sessionId } }` when it encounters a `result` message. Change to yield a `session_status` event BEFORE the `done` event:

```typescript
if (message.type === 'result') {
  const result = message as Record<string, unknown>;
  yield {
    type: 'session_status',
    data: {
      sessionId,
      model: result.model as string | undefined,
      costUsd: result.total_cost_usd as number | undefined,
      contextTokens: result.usage?.input_tokens as number | undefined,
      contextMaxTokens: result.usage?.context_window as number | undefined,
    },
  };
  yield {
    type: 'done',
    data: { sessionId },
  };
}
```

**Forward model from `system.init` message.** The init message includes the model name before any result is available:

```typescript
if (message.type === 'system' && 'subtype' in message && message.subtype === 'init') {
  session.sdkSessionId = message.session_id;
  session.hasStarted = true;
  // Forward model info from init
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

**Add `updateSession` method** to AgentManager for mid-session permission/model changes:

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

Update `AgentSession` interface to include `model`:

```typescript
interface AgentSession {
  sdkSessionId: string;
  lastActivity: number;
  permissionMode: PermissionMode;
  model?: string;
  hasStarted: boolean;
  pendingApproval?: { ... };
}
```

Update `sendMessage` to apply `model` from session state to SDK options:

```typescript
if (session.model) {
  sdkOptions.model = session.model;
}
```

Update permission mode mapping to handle all modes:

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

#### Layer 3: Transport Interface (`src/shared/transport.ts`)

Add `updateSession` method to the Transport interface:

```typescript
export interface Transport {
  // ... existing 9 methods ...
  updateSession(id: string, opts: UpdateSessionRequest): Promise<Session>;
}
```

#### Layer 4a: HttpTransport (`src/client/lib/http-transport.ts`)

```typescript
updateSession(id: string, opts: UpdateSessionRequest): Promise<Session> {
  return fetchJSON<Session>(this.baseUrl, `/sessions/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(opts),
  });
}
```

#### Layer 4b: DirectTransport (`src/client/lib/direct-transport.ts`)

Add `updateSession` to `DirectTransportServices.agentManager`:

```typescript
export interface DirectTransportServices {
  agentManager: {
    // ... existing methods ...
    updateSession(
      sessionId: string,
      opts: { permissionMode?: PermissionMode; model?: string },
    ): boolean;
  };
  // ...
}
```

Implementation:

```typescript
async updateSession(id: string, opts: UpdateSessionRequest): Promise<Session> {
  const updated = this.services.agentManager.updateSession(id, opts);
  if (!updated) throw new Error(`Session not found: ${id}`);
  // Return refreshed session metadata
  return this.getSession(id);
}
```

#### Layer 5: Express Route (`src/server/routes/sessions.ts`)

Add PATCH endpoint:

```typescript
// PATCH /api/sessions/:id - Update session settings
router.patch('/:id', async (req, res) => {
  const { permissionMode, model } = req.body;
  const updated = agentManager.updateSession(req.params.id, { permissionMode, model });
  if (!updated) return res.status(404).json({ error: 'Session not found' });

  // Return updated session (from transcript for consistency)
  const session = await transcriptReader.getSession(vaultRoot, req.params.id);
  if (session) {
    // Overlay the in-memory permission mode since transcript may not reflect it yet
    session.permissionMode = permissionMode ?? session.permissionMode;
  }
  res.json(session ?? { id: req.params.id, permissionMode, model });
});
```

#### Layer 6: Client Hooks

**`useChatSession` changes** -- expose `sessionStatus` from streaming:

Add state for session status and forward `session_status` events:

```typescript
const [sessionStatus, setSessionStatus] = useState<SessionStatusEvent | null>(null);

// In handleStreamEvent:
case 'session_status': {
  setSessionStatus(data as SessionStatusEvent);
  break;
}

// Add to return value:
return { messages, input, setInput, handleSubmit, status, error, stop, isLoadingHistory, sessionStatus };
```

**New `useSessionStatus` hook** (`src/client/hooks/use-session-status.ts`):

Aggregates data from multiple sources into a single status object:

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

  // Session metadata from server (permission mode)
  const { data: session } = useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => transport.getSession(sessionId),
    staleTime: 30_000,
  });

  // Compute aggregated status
  const statusData: SessionStatusData = {
    permissionMode: session?.permissionMode ?? 'default',
    model: streamingStatus?.model ?? null,
    costUsd: streamingStatus?.costUsd ?? null,
    contextPercent: streamingStatus?.contextTokens && streamingStatus?.contextMaxTokens
      ? Math.round((streamingStatus.contextTokens / streamingStatus.contextMaxTokens) * 100)
      : null,
    isStreaming,
  };

  // Mutation for updating session settings
  async function updateSession(opts: UpdateSessionRequest) {
    const updated = await transport.updateSession(sessionId, opts);
    queryClient.setQueryData(['session', sessionId], updated);
    return updated;
  }

  return { ...statusData, updateSession };
}
```

#### Layer 7: UI Components

**File structure:**

```
src/client/components/status/
  StatusLine.tsx          -- Container component
  StatusLineItem.tsx      -- Generic item (icon + label + optional click)
  PermissionModeItem.tsx  -- Interactive: dropdown to cycle permission modes
  ModelItem.tsx           -- Interactive: dropdown to switch models
  CostItem.tsx            -- Read-only: session cost display
  ContextItem.tsx         -- Read-only: context usage percentage
```

**`StatusLine.tsx`:**

```tsx
export function StatusLine({ sessionId, sessionStatus, isStreaming }: StatusLineProps) {
  const status = useSessionStatus(sessionId, sessionStatus, isStreaming);

  return (
    <div
      role="toolbar"
      aria-label="Session status"
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

**`PermissionModeItem.tsx`:**

Uses a DropdownMenu (shadcn/Radix) with all four permission modes:

```tsx
const PERMISSION_MODES: { value: PermissionMode; label: string; icon: LucideIcon; description: string }[] = [
  { value: 'default', label: 'Default', icon: Shield, description: 'Prompt for each tool call' },
  { value: 'acceptEdits', label: 'Accept Edits', icon: ShieldCheck, description: 'Auto-approve file edits' },
  { value: 'plan', label: 'Plan Mode', icon: ClipboardList, description: 'Research only, no edits' },
  { value: 'bypassPermissions', label: 'Bypass All', icon: ShieldOff, description: 'Auto-approve everything' },
];
```

The currently active mode is displayed with its icon. Clicking opens a dropdown to select a different mode. The `bypassPermissions` option is styled with red/warning treatment.

**`ModelItem.tsx`:**

Dropdown listing common Claude models. The current model (from `session_status` event) is displayed. Selecting a different model calls `updateSession({ model })`.

Model options (hardcoded initially, can be made dynamic later):
- `claude-sonnet-4-5-20250929`
- `claude-haiku-4-5-20251001`
- `claude-opus-4-6`

**`CostItem.tsx`:**

Read-only display. Shows `$X.XX` format. Uses `DollarSign` icon from lucide.

**`ContextItem.tsx`:**

Read-only display. Shows `XX%` with a subtle color shift at high usage (amber at 80%+, red at 95%+). Uses `Database` or `Layers` icon.

### ChatPanel Integration

Insert `StatusLine` after `ChatInput` inside the `border-t` section:

```tsx
<div className="relative border-t p-4">
  <AnimatePresence>
    {showCommands && <CommandPalette ... />}
  </AnimatePresence>

  <ChatInput ... />

  <StatusLine
    sessionId={sessionId}
    sessionStatus={sessionStatus}
    isStreaming={status === 'streaming'}
  />
</div>
```

`ChatPanel` needs to receive `sessionStatus` from `useChatSession`, which means the hook's return value expands.

## Implementation Phases

### Phase 1: Data Pipeline (Types + AgentManager + Transport)

**Files modified:**
- `src/shared/types.ts` -- Add `SessionStatusEvent`, `PermissionMode`, `UpdateSessionRequest`; expand `StreamEventType` and `StreamEvent`
- `src/shared/transport.ts` -- Add `updateSession` method
- `src/server/services/agent-manager.ts` -- Forward `result`/`init` metadata as `session_status` events; add `updateSession` method; expand `AgentSession` with `model`; handle all permission modes
- `src/server/routes/sessions.ts` -- Add `PATCH /:id` endpoint
- `src/client/lib/http-transport.ts` -- Add `updateSession` implementation
- `src/client/lib/direct-transport.ts` -- Add `updateSession` implementation; update `DirectTransportServices` interface

**Verification:** Existing tests pass. Manual test: send a message, observe `session_status` event in SSE stream or debug console.

### Phase 2: Client Hooks

**Files modified:**
- `src/client/hooks/use-chat-session.ts` -- Handle `session_status` event, expose `sessionStatus` in return value

**Files created:**
- `src/client/hooks/use-session-status.ts` -- Aggregation hook

**Verification:** Hook returns correct data when session status events fire. `updateSession` mutation works for both transports.

### Phase 3: UI Components

**Files created:**
- `src/client/components/status/StatusLine.tsx`
- `src/client/components/status/StatusLineItem.tsx`
- `src/client/components/status/PermissionModeItem.tsx`
- `src/client/components/status/ModelItem.tsx`
- `src/client/components/status/CostItem.tsx`
- `src/client/components/status/ContextItem.tsx`

**Files modified:**
- `src/client/components/chat/ChatPanel.tsx` -- Import and render `StatusLine`

**Verification:** StatusLine renders below chat input. Permission mode dropdown works. Model dropdown works. Cost and context display update after responses.

### Phase 4: Tests

**Files created:**
- `src/client/components/status/__tests__/StatusLine.test.tsx`
- `src/client/hooks/__tests__/use-session-status.test.tsx`

**Files modified:**
- `src/server/services/__tests__/agent-manager.test.ts` (if exists) -- Test `session_status` event emission
- `src/client/components/chat/__tests__/ChatPanel.test.tsx` (if exists) -- Verify StatusLine renders

**Test approach:** Use `createMockTransport()` pattern per `guides/architecture.md`. Mock `updateSession` to verify mutations. Test that `session_status` events flow through to the hook.

## Styling

Follow `guides/design-system.md`:

- **Text:** `text-xs` (11px) for all status items, `text-muted-foreground` color
- **Icons:** 12px lucide icons, same `text-muted-foreground` color
- **Spacing:** `gap-2` (8px) between items, `px-1 pt-2` container padding
- **Hover:** Interactive items get `hover:text-foreground` transition (150ms)
- **Dropdown:** shadcn `DropdownMenu` with `DropdownMenuRadioGroup` for mode/model selection
- **Warning states:** `bypassPermissions` mode shows in `text-red-500`. Context usage at 80%+ shows amber, 95%+ shows red.
- **Dark/light:** Inherits from existing theme variables, no custom colors needed

## Accessibility

- `StatusLine` container: `role="toolbar"`, `aria-label="Session status"`
- Interactive items: `<button>` elements with `aria-haspopup="menu"`, `aria-expanded`
- Dropdowns: shadcn `DropdownMenu` provides full keyboard navigation (arrow keys, Enter, Escape)
- Status value changes: `aria-live="polite"` region wrapping the status line so screen readers announce updates
- All text meets 4.5:1 contrast ratio against backgrounds
- Focus visible rings per design system (`2px solid hsl(var(--ring))`, 2px offset)

## Acceptance Criteria

1. StatusLine renders below `ChatInput` in both standalone and embedded (Obsidian) modes
2. Permission mode displays correctly and can be changed via dropdown (all four modes)
3. Model name displays after first `session_status` event (from init or result)
4. Model can be changed via dropdown; next message uses the selected model
5. Session cumulative cost displays in `$X.XX` format after first response
6. Context usage percentage displays and updates after each response
7. Cost and context show as empty/hidden until first response (graceful degradation)
8. PermissionBanner continues to show for `bypassPermissions` mode (kept as redundant warning)
9. All status items are keyboard accessible
10. Works identically via HttpTransport and DirectTransport
11. No new npm dependencies
12. Existing tests continue to pass

## Open Questions

None -- all clarifications resolved in ideation phase.

## Non-Regression Requirements

- `ChatPanel` layout must not shift unexpectedly (status line has fixed minimal height)
- `PermissionBanner` behavior unchanged
- SSE streaming performance unaffected (one additional small event per response)
- Existing `useChatSession` consumers unaffected (new `sessionStatus` field is additive)
- `Transport` interface addition is backward-compatible (new method only)

## Out of Scope

- Token-level context window visualization (progress bar of exact tokens)
- Cost budgets or spending alerts
- Persistable user preferences for which status items to show/hide
- Status line in the session sidebar
- Dynamic model list from SDK (hardcoded initial list)
