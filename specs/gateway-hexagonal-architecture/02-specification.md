# Gateway Hexagonal Architecture

**Status:** Draft
**Authors:** Claude Code, 2026-02-08
**Ideation:** [01-ideation.md](./01-ideation.md)

---

## Overview

Refactor the LifeOS Gateway from a transport-coupled architecture (Express HTTP throughout) to a hexagonal (ports-and-adapters) architecture with a `Transport` interface. This enables the Obsidian plugin to run server services in-process without a separate Express server, while the standalone web client continues using HTTP/SSE.

## Background / Problem Statement

The Obsidian copilot plugin currently requires the Gateway Express server running on `localhost:6942`. This means users must start a separate terminal process before using the plugin. The core services (AgentManager, TranscriptReader, CommandRegistry) have no transport coupling in their interfaces -- they already use `AsyncGenerator<StreamEvent>` and return typed Promises. The coupling exists in two places:

1. **Client side:** `api.ts` hardcodes `fetch()` calls, and `use-chat-session.ts` hardcodes SSE stream parsing
2. **Plugin side:** `obsidian-adapter.ts` hardcodes `http://localhost:6942/api`

By introducing a Transport abstraction, the same services can be called directly (in-process) or over HTTP, determined at app startup.

## Goals

- Define a unified `Transport` interface covering all client-server operations
- Implement `HttpTransport` (wraps current fetch/SSE logic) for standalone web client
- Implement `DirectTransport` (wraps service instances) for Obsidian plugin
- Inject Transport via React Context so components are transport-agnostic
- Obsidian plugin works without running the Express server
- No regression to standalone web client behavior
- Architecture documented in `guides/architecture.md`

## Non-Goals

- Removing the Express server (standalone mode still needs it)
- WebSocket, gRPC, or other transport types (future work)
- Electron main process IPC proxy (only if renderer SDK fails)
- Splitting Transport interface by domain (unified for now)
- Changing service internals (AgentManager, TranscriptReader, CommandRegistry stay as-is)

## Technical Dependencies

- `@anthropic-ai/claude-agent-sdk` -- spawns Claude CLI child process. Must work in Obsidian's Electron renderer (Node.js available). Bundled into plugin.
- `@tanstack/react-query` ^5.62.0 -- server state management (hooks use it)
- `zustand` ^5.0.0 -- client state
- `gray-matter` ^4.0.3 -- command frontmatter parsing (bundled into plugin)
- Node.js `fs/promises`, `path`, `os`, `child_process` -- used by services, available in Obsidian's Electron

## Detailed Design

### Transport Interface

```typescript
// src/shared/transport.ts

import type {
  Session,
  CreateSessionRequest,
  CommandRegistry,
  HistoryMessage,
  StreamEvent,
} from './types';

export interface Transport {
  createSession(opts: CreateSessionRequest): Promise<Session>;
  listSessions(): Promise<Session[]>;
  getSession(id: string): Promise<Session>;
  getMessages(sessionId: string): Promise<{ messages: HistoryMessage[] }>;
  sendMessage(
    sessionId: string,
    content: string,
    onEvent: (event: StreamEvent) => void,
    signal?: AbortSignal,
  ): Promise<void>;
  approveTool(sessionId: string, toolCallId: string): Promise<{ ok: boolean }>;
  denyTool(sessionId: string, toolCallId: string): Promise<{ ok: boolean }>;
  getCommands(refresh?: boolean): Promise<CommandRegistry>;
  health(): Promise<{ status: string; version: string; uptime: number }>;
}
```

Key design: `sendMessage` uses a callback (`onEvent`) rather than returning an AsyncGenerator. This normalizes both transports -- HttpTransport parses SSE and calls back, DirectTransport iterates the AsyncGenerator and calls back. The consumer code is identical either way.

### TransportContext (React DI)

```typescript
// src/client/contexts/TransportContext.tsx

import { createContext, useContext } from 'react';
import type { Transport } from '@shared/transport';

const TransportContext = createContext<Transport | null>(null);

export function TransportProvider({
  transport,
  children,
}: {
  transport: Transport;
  children: React.ReactNode;
}) {
  return (
    <TransportContext.Provider value={transport}>
      {children}
    </TransportContext.Provider>
  );
}

export function useTransport(): Transport {
  const transport = useContext(TransportContext);
  if (!transport) {
    throw new Error('useTransport must be used within a TransportProvider');
  }
  return transport;
}
```

### HttpTransport

```typescript
// src/client/lib/http-transport.ts

import type { Transport } from '@shared/transport';
import type { StreamEvent } from '@shared/types';

export class HttpTransport implements Transport {
  constructor(private baseUrl: string) {} // '/api' for web, full URL if needed

  private async fetchJSON<T>(url: string, opts?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseUrl}${url}`, {
      headers: { 'Content-Type': 'application/json' },
      ...opts,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(error.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  createSession(opts) { return this.fetchJSON('/sessions', { method: 'POST', body: JSON.stringify(opts) }); }
  listSessions() { return this.fetchJSON('/sessions'); }
  getSession(id) { return this.fetchJSON(`/sessions/${id}`); }
  getMessages(sessionId) { return this.fetchJSON(`/sessions/${sessionId}/messages`); }
  getCommands(refresh) { return this.fetchJSON(`/commands${refresh ? '?refresh=true' : ''}`); }
  health() { return this.fetchJSON('/health'); }
  approveTool(sessionId, toolCallId) {
    return this.fetchJSON(`/sessions/${sessionId}/approve`, { method: 'POST', body: JSON.stringify({ toolCallId }) });
  }
  denyTool(sessionId, toolCallId) {
    return this.fetchJSON(`/sessions/${sessionId}/deny`, { method: 'POST', body: JSON.stringify({ toolCallId }) });
  }

  async sendMessage(sessionId, content, onEvent, signal?) {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
      signal,
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      let eventType = '';
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith('data: ') && eventType) {
          const data = JSON.parse(line.slice(6));
          onEvent({ type: eventType, data } as StreamEvent);
          eventType = '';
        }
      }
    }
  }
}
```

This extracts the SSE parsing logic currently in `use-chat-session.ts` (lines 122-143) into the transport. The `fetchJSON` helper is extracted from current `api.ts`.

### DirectTransport

```typescript
// src/client/lib/direct-transport.ts

import type { Transport } from '@shared/transport';
import type { StreamEvent, Session, CreateSessionRequest } from '@shared/types';

interface DirectTransportServices {
  agentManager: {
    ensureSession(id: string, opts: { permissionMode: 'default' | 'dangerously-skip' }): void;
    sendMessage(id: string, content: string, opts?: { permissionMode?: 'default' | 'dangerously-skip' }): AsyncGenerator<StreamEvent>;
    approveTool(id: string, toolCallId: string, approved: boolean): boolean;
    getSdkSessionId(id: string): string | undefined;
  };
  transcriptReader: {
    listSessions(vaultRoot: string): Promise<Session[]>;
    getSession(vaultRoot: string, id: string): Promise<Session | null>;
    readTranscript(vaultRoot: string, id: string): Promise<import('@shared/types').HistoryMessage[]>;
  };
  commandRegistry: {
    getCommands(forceRefresh?: boolean): Promise<import('@shared/types').CommandRegistry>;
  };
  vaultRoot: string;
}

export class DirectTransport implements Transport {
  constructor(private services: DirectTransportServices) {}

  async createSession(opts: CreateSessionRequest): Promise<Session> {
    const id = crypto.randomUUID();
    this.services.agentManager.ensureSession(id, {
      permissionMode: opts.permissionMode ?? 'default',
    });
    return {
      id,
      title: 'New session',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      permissionMode: opts.permissionMode ?? 'default',
    };
  }

  async listSessions() {
    return this.services.transcriptReader.listSessions(this.services.vaultRoot);
  }

  async getSession(id: string) {
    const session = await this.services.transcriptReader.getSession(this.services.vaultRoot, id);
    if (!session) throw new Error(`Session ${id} not found`);
    return session;
  }

  async getMessages(sessionId: string) {
    const messages = await this.services.transcriptReader.readTranscript(this.services.vaultRoot, sessionId);
    return { messages };
  }

  async sendMessage(sessionId: string, content: string, onEvent: (event: StreamEvent) => void, signal?: AbortSignal) {
    const generator = this.services.agentManager.sendMessage(sessionId, content);
    for await (const event of generator) {
      if (signal?.aborted) break;
      onEvent(event);
    }
  }

  async approveTool(sessionId: string, toolCallId: string) {
    const ok = this.services.agentManager.approveTool(sessionId, toolCallId, true);
    return { ok };
  }

  async denyTool(sessionId: string, toolCallId: string) {
    const ok = this.services.agentManager.approveTool(sessionId, toolCallId, false);
    return { ok };
  }

  async getCommands(refresh = false) {
    return this.services.commandRegistry.getCommands(refresh);
  }

  async health() {
    return { status: 'ok', version: '0.1.0', uptime: 0 };
  }
}
```

DirectTransport wraps the same service instances the Express routes use. The `sendMessage` method iterates the AsyncGenerator from `agentManager.sendMessage()` and calls `onEvent` for each yielded StreamEvent -- the exact same events HttpTransport parses from SSE.

### Hook Refactoring

**use-chat-session.ts changes:**

The SSE parsing logic (fetch + ReadableStream + buffer) moves into `HttpTransport.sendMessage()`. The hook becomes transport-agnostic:

```typescript
// Before (in handleSubmit):
const response = await fetch(`${getPlatform().apiBaseUrl}/sessions/${sessionId}/messages`, { ... });
const reader = response.body!.getReader();
// ... 20 lines of SSE parsing ...

// After (in handleSubmit):
const transport = useTransport();
await transport.sendMessage(
  sessionId,
  finalContent,
  (event) => handleStreamEvent(event.type, event.data, assistantId),
  abortController.signal,
);
```

The `handleStreamEvent` function and all ref-based state management stays exactly the same. Only the transport call changes.

**use-sessions.ts changes:**

```typescript
// Before:
const sessionsQuery = useQuery({ queryKey: ['sessions'], queryFn: api.listSessions });
const createSession = useMutation({ mutationFn: (opts) => api.createSession(opts) });

// After:
const transport = useTransport();
const sessionsQuery = useQuery({ queryKey: ['sessions'], queryFn: () => transport.listSessions() });
const createSession = useMutation({ mutationFn: (opts) => transport.createSession(opts) });
```

**use-commands.ts changes:**

```typescript
// Before:
queryFn: () => api.getCommands()

// After:
const transport = useTransport();
queryFn: () => transport.getCommands()
```

**PermissionBanner.tsx changes:**

```typescript
// Before:
queryFn: () => api.getSession(sessionId!)

// After:
const transport = useTransport();
queryFn: () => transport.getSession(sessionId!)
```

**ToolApproval.tsx changes:**

```typescript
// Before:
await api.approveTool(sessionId, toolCallId);
await api.denyTool(sessionId, toolCallId);

// After:
const transport = useTransport();
await transport.approveTool(sessionId, toolCallId);
await transport.denyTool(sessionId, toolCallId);
```

### Standalone Wiring (main.tsx)

```typescript
// Before:
<App />

// After:
const transport = new HttpTransport('/api');
<TransportProvider transport={transport}>
  <App />
</TransportProvider>
```

### Plugin Wiring (CopilotView.tsx)

```typescript
import { AgentManager } from '../../server/services/agent-manager';
import { TranscriptReader } from '../../server/services/transcript-reader';
import { CommandRegistryService } from '../../server/services/command-registry';
import { DirectTransport } from '../../client/lib/direct-transport';
import { TransportProvider } from '../../client/contexts/TransportContext';

// In onOpen():
const vaultRoot = (this.app.vault.adapter as any).basePath;
const agentManager = new AgentManager();       // new instance per view
const transcriptReader = new TranscriptReader();
const commandRegistry = new CommandRegistryService(vaultRoot);

const transport = new DirectTransport({
  agentManager,
  transcriptReader,
  commandRegistry,
  vaultRoot,
});

this.root.render(
  <NuqsAdapter>
    <TransportProvider transport={transport}>
      <ObsidianProvider app={this.app}>
        <QueryClientProvider client={this.queryClient}>
          <ObsidianApp />
        </QueryClientProvider>
      </ObsidianProvider>
    </TransportProvider>
  </NuqsAdapter>
);
```

**Note:** Services are currently singletons. For the plugin, we either import the singleton or instantiate new instances. Since the plugin runs in its own process, new instances are cleaner. The `AgentManager` class and `TranscriptReader` class need to be exported (not just the singleton). This is a minor change -- add `export class` alongside the existing singleton export.

### ObsidianApp Changes

- Remove `ConnectionStatus` import and rendering
- Add auto-session-creation on mount (restore the `useEffect` + `useMutation` that was removed)
- Session creation now goes through `useTransport().createSession()` via `useSessions()` hook

### PlatformAdapter Simplification

Remove `apiBaseUrl` from `PlatformAdapter` since the Transport handles communication. Keep:
- `isEmbedded: boolean`
- `getSessionId() / setSessionId()` -- session ID storage
- `openFile(path: string)` -- file opening

The Obsidian adapter no longer needs the hardcoded HTTP URL.

### File Organization

```
src/
  shared/
    types.ts              (unchanged)
    transport.ts           (NEW - Transport interface)
  client/
    lib/
      api.ts              (DELETE)
      platform.ts          (simplified - remove apiBaseUrl)
      http-transport.ts    (NEW - HttpTransport class)
      direct-transport.ts  (NEW - DirectTransport class)
    contexts/
      TransportContext.tsx  (NEW - React context + useTransport hook)
    hooks/
      use-chat-session.ts  (refactored - use transport.sendMessage)
      use-sessions.ts      (refactored - use useTransport)
      use-commands.ts      (refactored - use useTransport)
    components/
      layout/
        PermissionBanner.tsx (refactored - use useTransport)
      chat/
        ToolApproval.tsx     (refactored - use useTransport)
    main.tsx               (add TransportProvider + HttpTransport)
  server/
    services/
      agent-manager.ts     (export class alongside singleton)
      transcript-reader.ts (export class alongside singleton)
      command-registry.ts  (already exports class)
  plugin/
    views/
      CopilotView.tsx      (wire DirectTransport + TransportProvider)
    components/
      ObsidianApp.tsx      (remove ConnectionStatus, add auto-session)
      ConnectionStatus.tsx (DELETE)
    lib/
      obsidian-adapter.ts  (remove apiBaseUrl)
```

### Vite Obsidian Build Config

The plugin must now bundle server services and their dependencies:

```typescript
// vite.config.obsidian.ts changes:
rollupOptions: {
  external: [
    'obsidian', 'electron',
    // CodeMirror/Lezer externals stay the same
    // Node.js built-ins that Obsidian's Electron provides:
    'child_process', 'fs', 'path', 'os', 'url', 'crypto',
    'fs/promises', 'events', 'stream', 'util', 'net', 'http', 'https',
  ],
}
```

Key changes:
- `@anthropic-ai/claude-agent-sdk` is NOT external (bundled into plugin)
- `gray-matter` is NOT external (bundled)
- Node.js built-ins ARE external (provided by Electron runtime)
- `fs/promises` must be explicitly listed as external

## User Experience

**Standalone web client:** No visible change. Users run `npm run dev` and use the web UI as before.

**Obsidian plugin:** Users install the plugin and it works immediately. No need to start a separate server. The copilot pane opens, auto-creates a session, and is ready for chat. The only prerequisite is having Claude Code CLI installed.

## Testing Strategy

### Unit Tests

**Transport implementations:**
- `http-transport.test.ts` -- mock `fetch` and verify SSE parsing produces correct `onEvent` calls. Test buffer handling for incomplete lines. Test error propagation.
- `direct-transport.test.ts` -- mock service instances and verify methods delegate correctly. Test that `sendMessage` iterates the AsyncGenerator and calls `onEvent` for each event.
- `transport-context.test.tsx` -- verify `useTransport()` throws without provider. Verify provider passes transport to children.

**Refactored hooks:**
- Update `use-chat-session.test.tsx` -- mock `useTransport()` instead of `api`. Verify `sendMessage` is called with correct params and `onEvent` callback drives state updates.
- Update `use-sessions.test.tsx` -- mock `useTransport()` instead of `api`.
- No changes to component tests (they mock hooks, not transport).

### Integration Tests

- Standalone flow: verify Express routes still work end-to-end with `supertest`
- Build verification: `npm run build:obsidian` produces valid `main.js` with services bundled

### Mocking Strategy

Tests mock `useTransport()` via `vi.mock('../contexts/TransportContext')` returning a mock Transport object. This is simpler than mocking `fetch` since the Transport interface is well-typed.

## Performance Considerations

- **DirectTransport eliminates HTTP overhead:** No fetch, no SSE serialization/deserialization, no port binding. Events flow directly from AsyncGenerator to React state.
- **Negligible real-world difference:** LLM streaming is bottlenecked by the Anthropic API (~500ms+ per response start), not local transport (~1-5ms HTTP overhead).
- **Bundle size increase:** Plugin bundle grows to include AgentManager, TranscriptReader, CommandRegistry, gray-matter, and the Agent SDK. Acceptable since the plugin is local-only.

## Security Considerations

- **No port binding in plugin mode:** Services are not accessible from the network. Reduces attack surface compared to `localhost:6942`.
- **Renderer process:** Services run in Obsidian's Electron renderer with Node.js access. API keys for Anthropic are handled by the Claude CLI (spawned as child process), not stored in the plugin.
- **Input validation:** Transport implementations should not introduce new attack vectors since they delegate to the same services.

## Documentation

### New: `guides/architecture.md`

Document the hexagonal architecture:
- Ports-and-adapters diagram
- Transport interface contract
- How to add a new transport
- Standalone vs plugin wiring
- Service layer overview

### Update: `guides/obsidian-plugin-development.md`

- Remove references to requiring the Express server
- Document DirectTransport setup
- Update build configuration section

### Update: `gateway/CLAUDE.md`

- Add architecture section referencing `guides/architecture.md`
- Update "Architecture" section to mention Transport abstraction

## Implementation Phases

### Phase 1: Transport Interface + Context

Create `src/shared/transport.ts` with the `Transport` interface. Create `src/client/contexts/TransportContext.tsx` with `TransportProvider` and `useTransport()`.

### Phase 2: HttpTransport

Create `src/client/lib/http-transport.ts`. Extract `fetchJSON` from `api.ts` and SSE parsing from `use-chat-session.ts` into the `HttpTransport` class. Wire into `main.tsx` with `TransportProvider`.

### Phase 3: Refactor Client Hooks

Update `use-chat-session.ts`, `use-sessions.ts`, `use-commands.ts`, `PermissionBanner.tsx`, and `ToolApproval.tsx` to use `useTransport()` instead of importing `api`. Delete `api.ts`.

### Phase 4: Verify Standalone Mode

Run all tests. Verify standalone web client works identically with HttpTransport.

### Phase 5: DirectTransport

Create `src/client/lib/direct-transport.ts`. Export service classes from `agent-manager.ts` and `transcript-reader.ts` (alongside existing singletons).

### Phase 6: Plugin Wiring

Update `CopilotView.tsx` to instantiate services and DirectTransport. Add `TransportProvider` to the React tree. Update `ObsidianApp.tsx` (remove ConnectionStatus, add auto-session). Delete `ConnectionStatus.tsx`. Simplify `obsidian-adapter.ts` (remove `apiBaseUrl`).

### Phase 7: Plugin Build Config

Update `vite.config.obsidian.ts` to bundle services + SDK, externalize Node.js built-ins.

### Phase 8: Documentation

Write `guides/architecture.md`. Update `guides/obsidian-plugin-development.md` and `CLAUDE.md`.

### Phase 9: Tests

Update existing tests to mock `useTransport()`. Add new tests for HttpTransport, DirectTransport, and TransportContext.

## References

- [MCP TypeScript SDK Transport Pattern](https://github.com/modelcontextprotocol/typescript-sdk) -- reference implementation for transport abstraction
- [Hexagonal Architecture in TypeScript](https://medium.com/@yecaicedo/structuring-a-node-js-project-with-hexagonal-architecture-7be2ef1364e2)
- [React Context for DI](https://testdouble.com/insights/react-context-for-dependency-injection-not-state-management)
- [Ideation Document](./01-ideation.md) -- full research and decision log
- [Obsidian Plugin Development Guide](../../gateway/guides/obsidian-plugin-development.md)
