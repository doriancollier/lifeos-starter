---
slug: gateway-statusline
---

# Gateway Statusline

**Slug:** gateway-statusline
**Author:** Claude Code
**Date:** 2026-02-08
**Branch:** preflight/obsidian-copilot-plugin

---

## 1) Intent & Assumptions

**Task brief:** Add an interactive status line below the chat text entry in the Gateway client. The status line should display session metadata (model, permission mode, context usage, cost), update dynamically during streaming, and allow users to change settings (permission mode, model) by clicking on status items.

**Assumptions:**
- The status line is scoped to the chat area (below `ChatInput`), not a global app footer
- The Claude Agent SDK's `result` message provides cost/token data we can surface
- The status line must work in both standalone (`HttpTransport`) and embedded/Obsidian (`DirectTransport`) modes -- all data plumbing goes through the `Transport` interface
- Interactive items (permission mode, model) require new `Transport` methods (not just REST endpoints) with implementations in both `HttpTransport` and `DirectTransport`
- Some data (context usage %, cost) is only available during/after streaming and will show as empty/placeholder until then
- No new npm dependencies required -- shadcn/ui primitives (DropdownMenu, Popover) already available via Radix

**Out of scope:**
- Token-level context window visualization (progress bar of exact tokens)
- Cost budgets or spending alerts
- Persistable user preferences for which status items to show/hide
- Status line in the session sidebar

## 2) Pre-reading Log

- `gateway/guides/architecture.md`: **Hexagonal architecture** -- Transport interface is the central abstraction. Two implementations: `HttpTransport` (standalone web, Express + SSE) and `DirectTransport` (Obsidian plugin, in-process calls to services). All client code uses `useTransport()` and is transport-agnostic. Tests use `createMockTransport()` pattern
- `gateway/CLAUDE.md`: Architecture overview -- server (Express + SDK), client (React 19 + Tailwind 4 + shadcn/ui), shared types
- `gateway/src/client/App.tsx`: Top-level layout. `PermissionBanner` sits above chat, `ChatPanel` renders in `<main>`. Two modes: standalone (push sidebar) and embedded (overlay sidebar)
- `gateway/src/client/components/chat/ChatPanel.tsx`: Contains `MessageList` + `ChatInput` in a flex column. The status line goes after `ChatInput` inside the `<div className="relative border-t p-4">` section
- `gateway/src/client/components/chat/ChatInput.tsx`: Textarea + send/stop button. Pure presentational, no knowledge of session metadata
- `gateway/src/client/hooks/use-chat-session.ts`: SSE streaming hook. Uses `transport.sendMessage()` with `onEvent` callback. Handles `text_delta`, `tool_call_*`, `error`, `done` events. Does NOT currently expose model, cost, or context data
- `gateway/src/client/hooks/use-sessions.ts`: TanStack Query hook for session list. Fetches `Session` objects which include `permissionMode`
- `gateway/src/client/stores/app-store.ts`: Zustand store for UI state (sidebar, sessionId, contextFiles). Candidate for statusline-related UI state
- `gateway/src/client/contexts/TransportContext.tsx`: Transport DI via React Context. `TransportProvider` wraps app root, `useTransport()` hook consumed by all hooks/components
- `gateway/src/shared/types.ts`: `Session` has `permissionMode`. `StreamEvent` types don't include model/cost/context. `DoneEvent` only has `sessionId`
- `gateway/src/shared/transport.ts`: Transport interface (the "port"). 9 methods covering all client-server communication. `sendMessage` uses `onEvent` callback pattern that normalizes both HttpTransport (SSE parsing) and DirectTransport (AsyncGenerator iteration)
- `gateway/src/client/lib/http-transport.ts`: HTTP/SSE adapter. `fetch()` for CRUD, `ReadableStream` for SSE streaming
- `gateway/src/client/lib/direct-transport.ts`: In-process adapter. Calls `AgentManager`, `TranscriptReader`, `CommandRegistryService` directly. No HTTP serialization
- `gateway/src/server/services/agent-manager.ts`: Maps SDK messages to `StreamEvent`. The `system` init message has `session_id` but model/cost data from `result` message is NOT forwarded -- it yields a `done` event with only `sessionId`
- `gateway/src/server/routes/sessions.ts`: Express route handlers for HttpTransport. DirectTransport bypasses these entirely
- `gateway/src/client/components/layout/PermissionBanner.tsx`: Queries session via `useTransport().getSession()`, shows red banner for `dangerously-skip` mode
- `gateway/src/client/components/sessions/SessionItem.tsx`: Shows permission mode in detail row. Uses `ShieldOff` icon
- `gateway/src/client/index.css`: Theme variables (light/dark), custom text sizes (`text-2xs`, `text-3xs`), animation keyframes

## 3) Codebase Map

**Primary Components/Modules:**
- `src/client/components/chat/ChatPanel.tsx` -- Chat container where statusline will be inserted
- `src/client/components/chat/ChatInput.tsx` -- Text entry (statusline goes below this)
- `src/client/components/layout/PermissionBanner.tsx` -- Existing permission mode display (top banner)
- `src/client/hooks/use-chat-session.ts` -- SSE streaming hook (needs to expose new data)
- `src/client/hooks/use-sessions.ts` -- Session list/metadata hook
- `src/client/stores/app-store.ts` -- Zustand UI state store

**Shared Dependencies:**
- `src/shared/types.ts` -- Type definitions for events, sessions
- `src/shared/transport.ts` -- Transport interface (API contract)
- `src/client/contexts/TransportContext.tsx` -- DI for transport layer
- `lucide-react` -- Icons
- `motion/react` -- Animations
- Tailwind CSS 4 -- Styling (pure neutral gray palette)

**Data Flow:**
```
Standalone (HttpTransport):
  SDK query() → AgentManager.mapSdkMessage() → StreamEvent → SSE wire → HttpTransport.onEvent → useChatSession → UI

Embedded (DirectTransport):
  SDK query() → AgentManager.sendMessage() → AsyncGenerator<StreamEvent> → DirectTransport.onEvent → useChatSession → UI

Both paths converge at the onEvent callback -- consumer code is transport-agnostic.

Gap: AgentManager drops result message metadata (cost, model, tokens) -- only yields { type: 'done' }
```

**Feature Flags/Config:** None

**Potential Blast Radius:**
- Direct: ~10 new/modified files (components, hooks, types, transport interface, both transport implementations, routes, agent-manager)
- Indirect: `ChatPanel` layout change affects message area height; Transport interface change touches both HttpTransport and DirectTransport
- Tests: New test files for StatusLine components; update `ChatPanel` tests; mock transport tests for `updateSession`

## 4) Root Cause Analysis

N/A -- new feature, not a bug fix.

## 5) Research

### Potential Solutions

**1. Compound Component Pattern (Recommended)**
- StatusLine container + individual StatusLineItem components
- Each item is self-contained (icon, label, click handler, popover/dropdown)
- Data comes from a `useSessionStatus` hook that aggregates session metadata + streaming state
- Pros: Extensible, testable, each item isolated, matches shadcn/ui composition patterns
- Cons: More files, slightly more boilerplate
- Complexity: Medium
- Maintenance: Low

**2. Monolithic StatusBar Component**
- Single component with all items rendered inline
- All data fetching and state management in one place
- Pros: Simple, fewer files, quick to implement
- Cons: Hard to extend, large component, difficult to test individual items
- Complexity: Low
- Maintenance: High (grows unwieldy as items are added)

**3. Provider/Context Pattern**
- StatusBarProvider wraps chat area, provides context
- Individual consumer components read from context
- Pros: Clean separation of data and presentation
- Cons: Overkill for this scope -- Zustand already handles global state, TanStack Query handles server state. Adding another context layer adds complexity without benefit
- Complexity: High
- Maintenance: Medium

### Recommendation

**Compound Component Pattern** -- aligns with the existing codebase where each component owns its presentation (e.g., `ToolCallCard`, `SessionItem`, `CommandPalette`). A `useSessionStatus` hook provides data, and individual `StatusLineItem` components render each piece. Interactive items use shadcn DropdownMenu for click actions.

### Key Technical Decisions

**Data source for status items:**
- **Permission mode**: Already on `Session` type, available via `getSession()` query
- **Model name**: Available in SDK `system.init` message and `result` message -- needs to be forwarded through `StreamEvent`
- **Cost**: Available in SDK `result` message (`total_cost_usd`) -- needs new `StreamEvent` type
- **Context usage**: Available in SDK `result` message but NOT in per-event streaming. Best approach: forward from `result` message, show as "last known" value

**Changes needed (Transport-aware):**
1. New `StreamEvent` type: `session_status` with model, cost, context data
2. `AgentManager.mapSdkMessage()` needs to forward `result` message data instead of dropping it
3. New Transport method: `updateSession(id, opts)` for updating permission mode/model -- requires implementations in both `HttpTransport` (PATCH to Express endpoint) and `DirectTransport` (direct call to AgentManager)
4. Model switching: Requires new SDK query option or session restart

**ARIA & Accessibility:**
- Status line uses `role="toolbar"` with `aria-label="Session status"`
- Interactive items are buttons with `aria-haspopup="menu"` for dropdowns
- Status values use `aria-live="polite"` for screen reader announcements on change

## 6) Clarifications (Resolved)

1. **Model switching scope**: Change model for the next `query()` call within the same session. Conversation continuity preserved, no new session needed.

2. **Permission mode switching**: Allow mid-session switching via status line click. Expand beyond current `default`/`dangerously-skip` to support all SDK permission modes (plan mode, accept edits, etc.). Updates the in-memory `AgentSession` so the next `query()` call uses the new mode.

3. **Cost display**: Per-session cumulative cost from the SDK's `total_cost_usd` in the result message. Resets when switching sessions.

4. **Context usage display**: Show "last known" context usage that updates after each response completes. During streaming, the value stays at its previous level.

5. **PermissionBanner**: Keep the existing red banner as a redundant safety warning. Status line shows the mode; banner warns about danger.
