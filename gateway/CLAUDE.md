# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

LifeOS Gateway is a web-based interface and REST/SSE API for Claude Code, built with the Claude Agent SDK. It provides a chat UI for interacting with Claude Code sessions, with tool approval flows and slash command discovery.

The Agent SDK is fully integrated via `agent-manager.ts`, which calls the SDK's `query()` function and maps streaming events to the gateway's `StreamEvent` types. SDK JSONL transcript files are the single source of truth for all session data.

## Commands

```bash
npm run dev            # Start both Express server (port 6942) and Vite dev server (port 3000)
npm run dev:server     # Express server only (tsx watch, auto-reload)
npm run dev:client     # Vite dev server only (React UI with HMR)
npm run test           # Vitest in watch mode
npm run test:run       # Vitest single run
npm run build          # Build client (Vite) + compile server (tsc)
npm start              # Production server (serves built React app)
```

Run a single test file: `npx vitest run src/server/services/__tests__/transcript-reader.test.ts`

## Architecture

### Server (`src/server/`)

Express server on port `GATEWAY_PORT` (default 6942). Three route groups:

- **`routes/sessions.ts`** - Session listing (from SDK transcripts), session creation, SSE message streaming, message history, tool approve/deny endpoints
- **`routes/commands.ts`** - Scans `../../.claude/commands/` for slash commands using gray-matter frontmatter parsing
- **`routes/health.ts`** - Health check

Three services:

- **`services/agent-manager.ts`** - Manages Claude Agent SDK sessions. Calls `query()` with streaming, maps SDK events (`stream_event`, `tool_use_summary`, `result`) to gateway `StreamEvent` types. Tracks active sessions in-memory with 30-minute timeout. All sessions use `resume: sessionId` for SDK continuity.
- **`services/transcript-reader.ts`** - Single source of truth for session data. Reads SDK JSONL transcript files from `~/.claude/projects/{slug}/`. Provides `listSessions()` (scans directory, extracts metadata), `getSession()` (single session metadata), and `readTranscript()` (full message history). Extracts titles from first user message, permission mode from init message, timestamps from file stats.
- **`services/stream-adapter.ts`** - SSE helpers (`initSSEStream`, `sendSSEEvent`, `endSSEStream`) that format `StreamEvent` objects as SSE wire protocol.

### Session Architecture

Sessions are derived entirely from SDK JSONL files on disk (`~/.claude/projects/{slug}/*.jsonl`). There is no separate session store - the `TranscriptReader` scans these files to build the session list. This means:

- All sessions are visible (CLI-started, gateway-started, etc.)
- Session ID = SDK session ID (UUID from JSONL filename)
- No delete endpoint (sessions persist in SDK storage)
- Session metadata (title, preview, timestamps) is extracted from file content and stats on every request

### Client (`src/client/`)

React 19 + Vite 6 + Tailwind CSS 4 + shadcn/ui (new-york style, pure neutral gray palette).

- **State**: Zustand for UI state (`app-store.ts`), TanStack Query for server state (`use-sessions.ts`, `use-commands.ts`)
- **Chat**: `useChatSession` hook loads message history on mount via `api.getMessages()`, then handles SSE streaming via `fetch` + `ReadableStream`. Tracks text deltas and tool call lifecycle in refs for performance. Exposes `isLoadingHistory` for UI feedback.
- **Components**: `ChatPanel` > `MessageList` > `MessageItem` + `ToolCallCard`; `SessionSidebar`; `CommandPalette`; `PermissionBanner` + `ToolApproval` for tool approval flow
- **Markdown Rendering**: Assistant messages are rendered as rich markdown via the `streamdown` library (Vercel). `StreamingText` wraps the `<Streamdown>` component with `github-light`/`github-dark` Shiki themes and shows a blinking cursor during active streaming. User messages remain plain text. The `@source` directive in `index.css` ensures Streamdown's Tailwind classes are included in the CSS output.
- **Animations**: `motion` (motion.dev) for UI animations. `App.tsx` wraps the app in `<MotionConfig reducedMotion="user">` to respect `prefers-reduced-motion`. Used for: message entrance animations (new messages only, not history), tool card expand/collapse, command palette enter/exit, sidebar width toggle, button micro-interactions. Tests mock `motion/react` to render plain elements.
- **Design System**: Color palette, typography, spacing (8pt grid), and motion specs are documented in `guides/design-system.md`.

### Shared (`src/shared/`)

`types.ts` defines all shared interfaces: `Session`, `StreamEvent` (with discriminated `type` field), `HistoryMessage`, `CommandEntry`, etc. Imported via `@shared/*` path alias.

### Path Aliases

- `@/*` -> `./src/client/*`
- `@shared/*` -> `./src/shared/*`

Configured in both `tsconfig.json` (for IDE/tsc) and `vite.config.ts` (for bundling).

### SSE Streaming Protocol

Messages flow: client POST to `/api/sessions/:id/messages` -> server yields `StreamEvent` objects as SSE -> client parses in `useChatSession`.

Event types: `text_delta`, `tool_call_start`, `tool_call_delta`, `tool_call_end`, `tool_result`, `approval_required`, `error`, `done`.

### Session History

When a session is opened, the client fetches message history via GET `/api/sessions/:id/messages`. The server reads the SDK's JSONL transcript file at `~/.claude/projects/{slug}/{sessionId}.jsonl`, parsing user and assistant messages. This works for sessions started from any client (CLI, gateway, etc.) since all use the same SDK storage.

### Vault Root Resolution

The server resolves the parent LifeOS vault root as `path.resolve(__dirname, '../../../../')` from service files. The `CommandRegistryService` uses this to find `.claude/commands/`. The `AgentManager` and `TranscriptReader` use it for SDK operations.

## Testing

Tests use Vitest with `vi.mock()` for Node modules and `vi.resetModules()` pattern to get fresh singleton instances per test. Server tests mock `fs/promises` for transcript reading. Client tests use React Testing Library with jsdom and mock `api` module for history loading.

Tests live alongside source in `__tests__/` directories (e.g., `src/server/services/__tests__/transcript-reader.test.ts`).
