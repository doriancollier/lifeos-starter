---
slug: gateway-hexagonal-architecture
---

# Gateway Hexagonal Architecture

**Slug:** gateway-hexagonal-architecture
**Author:** Claude Code
**Date:** 2026-02-08
**Branch:** preflight/gateway-hexagonal-architecture

---

## 1) Intent & Assumptions

**Task brief:** Extract core gateway services (AgentManager, TranscriptReader, CommandRegistry) from the Express transport layer. Add a Direct adapter for in-process communication so the Obsidian plugin can run the server internally without requiring a separate process. The standalone web client continues to use Express/HTTP. Create and maintain architecture documentation in `gateway/guides/`.

**Assumptions:**
- Claude Code CLI must still be installed on the user's machine (the Agent SDK spawns it as a child process)
- The standalone web client + Express server remain fully functional (no regression)
- The Obsidian plugin currently works via HTTP to `localhost:6942` — this is what we're eliminating
- `@anthropic-ai/claude-agent-sdk` works in Obsidian's Electron renderer process (Node.js access is available; needs empirical verification)
- Both modes share the same React components, hooks, and stores
- The `PlatformAdapter` pattern already in place is a good foundation to extend

**Out of scope:**
- Removing the Express server entirely (standalone mode still needs it)
- Replacing the Agent SDK or changing how it spawns Claude CLI
- Mobile/web-only deployment (Obsidian is desktop Electron)
- WebSocket or gRPC transports (future extensions, not this iteration)
- Obsidian main process IPC proxy (only needed if renderer SDK doesn't work)

---

## 2) Pre-reading Log

### Codebase Files

- `src/server/services/agent-manager.ts`: Core service — manages SDK sessions, yields `AsyncGenerator<StreamEvent>`. 6 public methods. Uses `path` and `url` for vault root resolution, `@anthropic-ai/claude-agent-sdk` for `query()`.
- `src/server/services/transcript-reader.ts`: Core service — reads JSONL transcript files from `~/.claude/projects/{slug}/`. Uses `fs/promises`, `path`, `os`. 6 public methods.
- `src/server/services/command-registry.ts`: Core service — scans `.claude/commands/` for slash commands via gray-matter frontmatter. Uses `fs/promises`, `path`, `gray-matter`. 2 public methods.
- `src/server/services/stream-adapter.ts`: Express-coupled SSE helpers (`initSSEStream`, `sendSSEEvent`, `endSSEStream`). Takes Express `Response` object — cannot be reused for direct adapter.
- `src/server/routes/sessions.ts`: Express router — 7 endpoints. Wires `agentManager` + `transcriptReader` singletons to HTTP. SSE streaming via `res.write()`.
- `src/server/routes/commands.ts`: Express router — 1 endpoint. Instantiates `CommandRegistryService` with vault root.
- `src/server/routes/health.ts`: Express router — 1 endpoint. Health check.
- `src/client/lib/api.ts`: Client HTTP layer — 9 methods using `fetch()` with `getPlatform().apiBaseUrl`. This is the primary abstraction point for transport.
- `src/client/lib/platform.ts`: Platform adapter — `PlatformAdapter` interface with `apiBaseUrl`, `isEmbedded`, session management, file operations. Web default + Obsidian implementation.
- `src/client/hooks/use-chat-session.ts`: Chat streaming hook — hardcoded `fetch()` + `ReadableStream` SSE parsing. This is the tightest coupling to HTTP transport.
- `src/client/hooks/use-sessions.ts`: Session list — uses TanStack Query with `api.listSessions()`.
- `src/client/hooks/use-commands.ts`: Command list — uses TanStack Query with `api.getCommands()`.
- `src/plugin/views/CopilotView.tsx`: Plugin view — calls `setPlatformAdapter()` before React render. This is where DirectTransport will be injected.
- `src/plugin/lib/obsidian-adapter.ts`: Obsidian adapter — hardcoded `http://localhost:6942/api`. This is what we're replacing.
- `src/shared/types.ts`: Shared types — `Session`, `StreamEvent` (discriminated union with 8 event types), `HistoryMessage`, `CommandEntry`.
- `vite.config.obsidian.ts`: Plugin build — CJS output, `inlineDynamicImports`, externals for obsidian/electron/codemirror.
- `guides/design-system.md`: Existing guide — UI design specs.
- `guides/obsidian-plugin-development.md`: Existing guide — plugin development patterns.

### Research Sources

- Hexagonal architecture patterns in TypeScript/Node.js (ports-and-adapters)
- Electron renderer process constraints (Express not recommended, child_process limitations)
- Obsidian plugin architecture (direct services, no embedded HTTP servers)
- MCP TypeScript SDK transport abstraction (reference implementation)
- AsyncGenerator streaming patterns for React state updates
- Vite dual-target bundling (web ESM + Obsidian CJS)

---

## 3) Codebase Map

### Primary Components/Modules

| File | Role | Key Exports |
|------|------|-------------|
| `src/server/services/agent-manager.ts` | SDK session lifecycle | `agentManager` singleton |
| `src/server/services/transcript-reader.ts` | JSONL transcript storage | `transcriptReader` singleton |
| `src/server/services/command-registry.ts` | Slash command scanning | `CommandRegistryService` class |
| `src/server/services/stream-adapter.ts` | SSE wire protocol | `initSSEStream`, `sendSSEEvent`, `endSSEStream` |
| `src/server/routes/sessions.ts` | HTTP session endpoints | Express Router |
| `src/server/routes/commands.ts` | HTTP command endpoint | Express Router |
| `src/client/lib/api.ts` | Client fetch wrapper | `api` object (9 methods) |
| `src/client/lib/platform.ts` | Platform abstraction | `PlatformAdapter` interface |
| `src/client/hooks/use-chat-session.ts` | Chat streaming | `useChatSession()` hook |
| `src/plugin/lib/obsidian-adapter.ts` | Plugin platform impl | `createObsidianAdapter()` |
| `src/plugin/views/CopilotView.tsx` | Plugin React mount | `CopilotView` class |
| `src/shared/types.ts` | Shared interfaces | `StreamEvent`, `Session`, etc. |

### Shared Dependencies

- `@anthropic-ai/claude-agent-sdk` — spawns Claude CLI child process
- `@tanstack/react-query` — client data fetching
- `zustand` — client state management
- `gray-matter` — command frontmatter parsing
- `motion/react` — UI animations
- `nuqs` — URL query state (standalone only)

### Data Flow

```
User input → ChatPanel → useChatSession.handleSubmit()
  → fetch(POST /api/sessions/:id/messages) [HTTP Transport]
    → Express route → agentManager.sendMessage() → SDK query()
      → AsyncGenerator<StreamEvent>
        → sendSSEEvent(res, event) [SSE wire format]
          → ReadableStream parsing in client
            → handleStreamEvent() → React state updates
```

For DirectTransport, the flow collapses to:

```
User input → ChatPanel → useChatSession.handleSubmit()
  → serviceLayer.sendMessage() [Direct Transport]
    → agentManager.sendMessage() → SDK query()
      → AsyncGenerator<StreamEvent>
        → handleStreamEvent() → React state updates
```

### Feature Flags/Config

- `PlatformAdapter.isEmbedded` — distinguishes standalone vs plugin mode
- `GATEWAY_PORT` env var (default 6942) — standalone server port
- Build targets: `vite.config.ts` (web), `vite.config.obsidian.ts` (plugin)

### Potential Blast Radius

**Must change:**
- `src/client/lib/api.ts` — extract transport interface, HTTP implementation
- `src/client/hooks/use-chat-session.ts` — use transport instead of hardcoded fetch/SSE
- `src/client/lib/platform.ts` — extend with transport provider
- `src/plugin/lib/obsidian-adapter.ts` — instantiate DirectTransport with services
- `src/plugin/views/CopilotView.tsx` — wire up service instances
- `vite.config.obsidian.ts` — bundle services + SDK for plugin

**Must create:**
- `src/shared/service-layer.ts` — ServiceLayer interface
- `src/client/lib/http-transport.ts` — HTTP/SSE transport implementation
- `src/client/lib/direct-transport.ts` — in-process transport implementation
- `src/client/contexts/ServiceContext.tsx` — React context for DI
- `guides/architecture.md` — hexagonal architecture documentation

**May change (tests):**
- `src/client/hooks/__tests__/use-chat-session.test.tsx` — mock transport
- `src/client/lib/__tests__/api.test.ts` — update for new interface
- `src/client/lib/__tests__/platform.test.ts` — update adapter tests

---

## 4) Root Cause Analysis

N/A — this is not a bug fix.

---

## 5) Research

### Potential Solutions

**1. Transport Abstraction Layer (Recommended)**

Define a `Transport` interface that both `HttpTransport` and `DirectTransport` implement. Client code calls transport methods without knowing the underlying mechanism.

```typescript
interface Transport {
  createSession(opts: CreateSessionRequest): Promise<Session>;
  listSessions(): Promise<Session[]>;
  getSession(id: string): Promise<Session>;
  getMessages(sessionId: string): Promise<{ messages: HistoryMessage[] }>;
  sendMessage(sessionId: string, content: string, onEvent: (event: StreamEvent) => void, signal?: AbortSignal): Promise<void>;
  approveTool(sessionId: string, toolCallId: string): Promise<{ ok: boolean }>;
  denyTool(sessionId: string, toolCallId: string): Promise<{ ok: boolean }>;
  getCommands(refresh?: boolean): Promise<CommandRegistry>;
  health(): Promise<{ status: string; version: string; uptime: number }>;
}
```

- Pros: Clean abstraction, proven pattern (MCP SDK), easy to add future transports, services stay as-is
- Cons: Requires refactoring client API layer and chat streaming hook
- Complexity: Medium
- Maintenance: Low

**2. Service Layer Interface + DI (Combined with #1)**

Wrap the Transport in a ServiceLayer injected via React Context. Components consume services through `useService()` hook rather than importing `api` directly.

- Pros: Type-safe DI, easy testing (mock service in tests), no prop drilling
- Cons: Adds React Context layer, service interface can grow large
- Complexity: Medium
- Maintenance: Low

**3. Message Bus / Event-Driven**

Services emit events, client subscribes via EventEmitter pattern.

- Pros: Very decoupled, multi-subscriber support
- Cons: Over-engineered for this use case, harder to debug, weak type safety with string event names, request/response pattern is awkward
- Complexity: High
- Maintenance: High

**4. Hybrid — Keep HTTP in Plugin (Start Express inside Obsidian)**

Start Express server within the Obsidian plugin process. Client still uses fetch to localhost.

- Pros: Simplest implementation, no client code changes
- Cons: Port conflicts (multiple windows), HTTP overhead unnecessary, Electron renderer constraints (Express not recommended), child processes killed when window closes
- Complexity: Low
- Maintenance: Low but fragile

### Security Considerations

- Renderer process has web context — sensitive data (API keys) should be handled carefully
- Claude SDK spawns child process that needs network access to Anthropic API
- In-process services in Obsidian bypass network layer, reducing attack surface
- No port binding means no external access to services

### Performance Considerations

- HTTP adds ~1-5ms latency per call (negligible for LLM streaming bottlenecked by API)
- Direct calls eliminate JSON serialization/deserialization overhead
- AsyncGenerator is a native JS feature — zero dependency cost
- No port binding means no port conflict issues

### Recommendation

**Approach 1 + 2 combined: Transport Abstraction with React Context DI**

The `Transport` interface provides the abstraction boundary. `HttpTransport` wraps the current fetch/SSE logic. `DirectTransport` wraps service instances directly. A React Context provides the DI boundary, injecting the appropriate transport at the app root.

This is the architecture used by MCP TypeScript SDK and aligns with hexagonal architecture best practices. It's the minimum abstraction needed for dual-target support without over-engineering.

Key insight from research: **Do NOT embed Express in Obsidian**. Use direct in-process service calls. AsyncGenerator naturally bridges server streaming to React state.

### Claude SDK in Obsidian Renderer — Risk

The Agent SDK uses `child_process.spawn` to launch Claude CLI. This works in Electron renderer but with constraints:
- Child process killed when window closes
- No Electron IPC to child
- No `require('electron')` in child

This should work for Obsidian since the plugin process stays alive while the vault is open. If issues arise, a fallback is routing SDK calls through Electron's main process via IPC — but this is out of scope for v1.

---

## 6) Clarification (Resolved)

| # | Question | Decision |
|---|----------|----------|
| 1 | SDK bundling strategy | **Bundle into plugin.** SDK is thin (just spawns CLI). Updates come when plugin is rebuilt. Simplifies distribution. |
| 2 | Transport interface granularity | **Unified interface.** ~9 methods is small enough. Split later if it grows past ~15 methods or domains diverge. |
| 3 | api.ts refactor approach | **Replace api.ts with Transport directly.** Hooks/components use Transport via React Context. Cleaner architecture. |
| 4 | Health endpoint in direct mode | **Remove ConnectionStatus from plugin entirely.** In direct mode services are in-process; "gateway not connected" is meaningless. |
| 5 | Plugin bundle size | **Bundle everything.** Accept larger bundle. Plugin is local-only, not CDN-served. Simplicity over size. |
| 6 | Session auto-creation | **Auto-create on mount.** User opens copilot and can chat immediately. No extra clicks. |

### Additional clarifications from discussion:

- **MCP support:** MCPs configured in `.claude/settings.json` are handled by the Claude CLI automatically. The gateway transport doesn't need MCP-specific methods. Tool calls from MCPs show up as regular `tool_call` events in the stream.
- **SDK version updates:** When bundled, SDK version is locked to build time. Since SDK is thin (spawns CLI), version drift is low-risk. CLI itself is updated independently by the user.
- **Transport growth:** API surface is unlikely to grow significantly. Main future additions would be vault file operations or plugin-specific features, separate from the Claude communication layer.
