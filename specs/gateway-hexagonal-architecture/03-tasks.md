# Gateway Hexagonal Architecture - Task Breakdown

**Feature Slug:** gateway-hexagonal-architecture
**Last Decompose:** 2026-02-08
**Mode:** Full
**Status:** TASK_CREATION_INCOMPLETE (TaskCreate tool not available in agent context)
**Total Tasks:** 16
**Phases:** 9

---

## Phase Overview

| Phase | Tasks | Dependencies | Description |
|-------|-------|-------------|-------------|
| P1 | 1-2 | None | Transport Interface + TransportContext |
| P2 | 3 | P1 | HttpTransport implementation |
| P3 | 4-8 | P2 | Refactor client hooks + delete api.ts |
| P4 | 9 | P3 | Verify standalone mode |
| P5 | 10-11 | P1 | DirectTransport + export service classes |
| P6 | 12-13 | P3, P5 | Plugin wiring |
| P7 | 14 | P6 | Plugin build config |
| P8 | 15 | P7 | Documentation |
| P9 | 16 | P3 | Tests |

## Parallel Execution Opportunities

- **P1 tasks (1-2)** can run in parallel with each other
- **P3 tasks (4-8)** can run in parallel with each other (all depend on P2)
- **P5 tasks (10-11)** can run in parallel with P3 (both depend on P1)
- **P9 task (16)** can start after P3

---

## Tasks

### Task 1: [gateway-hexagonal-architecture] [P1] Create Transport interface

**Active Form:** Creating Transport interface in shared types

**Description:**

Create the `Transport` interface that defines the contract between client code and server services. This is the core port in the hexagonal architecture.

Create file `gateway/src/shared/transport.ts`:

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

Key design decisions:
- `sendMessage` uses a callback (`onEvent`) rather than returning an AsyncGenerator. This normalizes both transports -- HttpTransport parses SSE and calls back, DirectTransport iterates the AsyncGenerator and calls back. Consumer code is identical either way.
- Interface covers all 9 operations currently in `api.ts` (except `getMessageStreamUrl` which is HTTP-specific and being removed).
- Uses existing types from `./types` -- no new type definitions needed.

**Acceptance Criteria:**
- File exists at `gateway/src/shared/transport.ts`
- TypeScript compiles without errors
- Interface has all 9 methods matching the spec

---

### Task 2: [gateway-hexagonal-architecture] [P1] Create TransportContext for React DI

**Active Form:** Creating TransportContext React context for dependency injection

**Description:**

Create a React Context that provides the Transport instance to all components and hooks. This replaces the direct `import { api }` pattern with dependency injection.

Create file `gateway/src/client/contexts/TransportContext.tsx`:

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

**Acceptance Criteria:**
- File exists at `gateway/src/client/contexts/TransportContext.tsx`
- `TransportProvider` accepts a `transport` prop and `children`
- `useTransport()` throws if used outside provider
- TypeScript compiles without errors

---

### Task 3: [gateway-hexagonal-architecture] [P2] Create HttpTransport implementation

**Active Form:** Creating HttpTransport class that wraps fetch/SSE logic

**Dependencies:** Task 1, Task 2

**Description:**

Create the `HttpTransport` class that extracts the current HTTP communication logic from `api.ts` and the SSE streaming logic from `use-chat-session.ts`. This is the adapter for standalone web client mode.

Create file `gateway/src/client/lib/http-transport.ts`:

```typescript
// src/client/lib/http-transport.ts

import type { Transport } from '@shared/transport';
import type {
  Session,
  CreateSessionRequest,
  CommandRegistry,
  HistoryMessage,
  StreamEvent,
} from '@shared/types';

export class HttpTransport implements Transport {
  constructor(private baseUrl: string) {}

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

  createSession(opts: CreateSessionRequest): Promise<Session> {
    return this.fetchJSON('/sessions', {
      method: 'POST',
      body: JSON.stringify(opts),
    });
  }

  listSessions(): Promise<Session[]> {
    return this.fetchJSON('/sessions');
  }

  getSession(id: string): Promise<Session> {
    return this.fetchJSON(`/sessions/${id}`);
  }

  getMessages(sessionId: string): Promise<{ messages: HistoryMessage[] }> {
    return this.fetchJSON(`/sessions/${sessionId}/messages`);
  }

  getCommands(refresh = false): Promise<CommandRegistry> {
    return this.fetchJSON(`/commands${refresh ? '?refresh=true' : ''}`);
  }

  health(): Promise<{ status: string; version: string; uptime: number }> {
    return this.fetchJSON('/health');
  }

  approveTool(sessionId: string, toolCallId: string): Promise<{ ok: boolean }> {
    return this.fetchJSON(`/sessions/${sessionId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ toolCallId }),
    });
  }

  denyTool(sessionId: string, toolCallId: string): Promise<{ ok: boolean }> {
    return this.fetchJSON(`/sessions/${sessionId}/deny`, {
      method: 'POST',
      body: JSON.stringify({ toolCallId }),
    });
  }

  async sendMessage(
    sessionId: string,
    content: string,
    onEvent: (event: StreamEvent) => void,
    signal?: AbortSignal,
  ): Promise<void> {
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

Then wire it into `gateway/src/client/main.tsx`. Update the render to wrap `<App />` with `TransportProvider`:

```typescript
// main.tsx changes:
import { HttpTransport } from './lib/http-transport';
import { TransportProvider } from './contexts/TransportContext';

const transport = new HttpTransport('/api');

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <NuqsAdapter>
      <TransportProvider transport={transport}>
        <QueryClientProvider client={queryClient}>
          <App />
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </TransportProvider>
    </NuqsAdapter>
  </React.StrictMode>
);
```

**Source reference:** The `fetchJSON` helper is extracted from `gateway/src/client/lib/api.ts` (lines 10-20). The SSE parsing in `sendMessage` is extracted from `gateway/src/client/hooks/use-chat-session.ts` (lines 122-143).

**Acceptance Criteria:**
- `HttpTransport` class implements all `Transport` interface methods
- `main.tsx` wraps app in `TransportProvider` with `HttpTransport('/api')`
- TypeScript compiles without errors
- SSE parsing logic matches current behavior in `use-chat-session.ts`

---

### Task 4: [gateway-hexagonal-architecture] [P3] Refactor use-chat-session.ts to use Transport

**Active Form:** Refactoring use-chat-session hook to use useTransport instead of direct fetch

**Dependencies:** Task 3

**Description:**

Refactor `gateway/src/client/hooks/use-chat-session.ts` to use `useTransport()` instead of hardcoded `fetch()` and SSE parsing.

**Changes to make:**

1. Remove imports:
   - Remove `import { api } from '../lib/api';`
   - Remove `import { getPlatform } from '../lib/platform';`

2. Add import:
   - Add `import { useTransport } from '../contexts/TransportContext';`

3. Inside `useChatSession()`, add at the top of the function body:
   ```typescript
   const transport = useTransport();
   ```

4. Replace the `historyQuery` queryFn (line 51):
   ```typescript
   // Before:
   queryFn: () => api.getMessages(sessionId),
   // After:
   queryFn: () => transport.getMessages(sessionId),
   ```

5. Replace the entire streaming section in `handleSubmit` (lines 107-144). Remove:
   ```typescript
   const response = await fetch(`${getPlatform().apiBaseUrl}/sessions/${sessionId}/messages`, {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       content: options.transformContent
         ? await options.transformContent(userMessage.content)
         : userMessage.content,
     }),
     signal: abortController.signal,
   });

   if (!response.ok) {
     throw new Error(`HTTP ${response.status}`);
   }

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
         handleStreamEvent(eventType, data, assistantId);
         eventType = '';
       }
     }
   }
   ```

   Replace with:
   ```typescript
   const finalContent = options.transformContent
     ? await options.transformContent(userMessage.content)
     : userMessage.content;

   await transport.sendMessage(
     sessionId,
     finalContent,
     (event) => handleStreamEvent(event.type, event.data, assistantId),
     abortController.signal,
   );
   ```

6. Update the `handleStreamEvent` function signature -- no changes needed since it already accepts `(type: string, data: unknown, assistantId: string)`.

7. Update the `useCallback` dependency array for `handleSubmit` -- add `transport`:
   ```typescript
   }, [input, status, sessionId, transport]);
   ```

**Acceptance Criteria:**
- No imports from `api.ts` or `platform.ts` remain in the file
- `useTransport()` is called at the top of the hook
- SSE parsing is fully removed from this file (handled by HttpTransport)
- `handleStreamEvent` and all ref-based state management is unchanged
- TypeScript compiles without errors

---

### Task 5: [gateway-hexagonal-architecture] [P3] Refactor use-sessions.ts to use Transport

**Active Form:** Refactoring use-sessions hook to use useTransport

**Dependencies:** Task 3

**Description:**

Refactor `gateway/src/client/hooks/use-sessions.ts` to use `useTransport()` instead of `api`.

**Changes to make in `gateway/src/client/hooks/use-sessions.ts`:**

1. Remove import:
   ```typescript
   // Remove:
   import { api } from '../lib/api';
   ```

2. Add import:
   ```typescript
   import { useTransport } from '../contexts/TransportContext';
   ```

3. Add at the top of `useSessions()` function body:
   ```typescript
   const transport = useTransport();
   ```

4. Update `sessionsQuery` (line 11):
   ```typescript
   // Before:
   queryFn: api.listSessions,
   // After:
   queryFn: () => transport.listSessions(),
   ```

5. Update `createSession` mutation (line 17):
   ```typescript
   // Before:
   mutationFn: (opts: CreateSessionRequest) => api.createSession(opts),
   // After:
   mutationFn: (opts: CreateSessionRequest) => transport.createSession(opts),
   ```

The final file should look like:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTransport } from '../contexts/TransportContext';
import { useSessionId } from './use-session-id';
import type { CreateSessionRequest } from '@shared/types';

export function useSessions() {
  const queryClient = useQueryClient();
  const transport = useTransport();
  const [activeSessionId, setActiveSession] = useSessionId();

  const sessionsQuery = useQuery({
    queryKey: ['sessions'],
    queryFn: () => transport.listSessions(),
    refetchInterval: 30_000,
  });

  const createSession = useMutation({
    mutationFn: (opts: CreateSessionRequest) => transport.createSession(opts),
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      setActiveSession(session.id);
    },
  });

  return {
    sessions: sessionsQuery.data ?? [],
    isLoading: sessionsQuery.isLoading,
    createSession,
    activeSessionId,
    setActiveSession,
  };
}
```

**Acceptance Criteria:**
- No import from `api.ts` remains
- `useTransport()` provides the transport instance
- `listSessions()` and `createSession()` go through transport
- TypeScript compiles without errors

---

### Task 6: [gateway-hexagonal-architecture] [P3] Refactor use-commands.ts to use Transport

**Active Form:** Refactoring use-commands hook to use useTransport

**Dependencies:** Task 3

**Description:**

Refactor `gateway/src/client/hooks/use-commands.ts` to use `useTransport()` instead of `api`.

**Changes to make in `gateway/src/client/hooks/use-commands.ts`:**

1. Remove import:
   ```typescript
   // Remove:
   import { api } from '../lib/api';
   ```

2. Add import:
   ```typescript
   import { useTransport } from '../contexts/TransportContext';
   ```

3. Update `useCommands()`:
   ```typescript
   export function useCommands() {
     const transport = useTransport();
     return useQuery<CommandRegistry>({
       queryKey: ['commands'],
       queryFn: () => transport.getCommands(),
       staleTime: 5 * 60 * 1000,
       gcTime: 30 * 60 * 1000,
     });
   }
   ```

4. Update `useRefreshCommands()`:
   ```typescript
   export function useRefreshCommands() {
     const transport = useTransport();
     return useQuery<CommandRegistry>({
       queryKey: ['commands', 'refresh'],
       queryFn: () => transport.getCommands(true),
       enabled: false,
     });
   }
   ```

**Acceptance Criteria:**
- No import from `api.ts` remains
- Both hooks use `useTransport()` for data fetching
- TypeScript compiles without errors

---

### Task 7: [gateway-hexagonal-architecture] [P3] Refactor PermissionBanner and ToolApproval to use Transport

**Active Form:** Refactoring PermissionBanner and ToolApproval components to use useTransport

**Dependencies:** Task 3

**Description:**

Update two components that directly import `api` to use `useTransport()` instead.

**Changes to `gateway/src/client/components/layout/PermissionBanner.tsx`:**

1. Remove: `import { api } from '../../lib/api';`
2. Add: `import { useTransport } from '../../contexts/TransportContext';`
3. Add at top of component: `const transport = useTransport();`
4. Change queryFn:
   ```typescript
   // Before:
   queryFn: () => api.getSession(sessionId!),
   // After:
   queryFn: () => transport.getSession(sessionId!),
   ```

Full updated file:
```typescript
import { useQuery } from '@tanstack/react-query';
import { useTransport } from '../../contexts/TransportContext';

export function PermissionBanner({ sessionId }: { sessionId: string | null }) {
  const transport = useTransport();
  const { data: session } = useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => transport.getSession(sessionId!),
    enabled: !!sessionId,
  });

  if (!session || session.permissionMode !== 'dangerously-skip') return null;

  return (
    <div className="bg-red-600 text-white text-center text-sm py-1 px-4">
      Permissions bypassed - all tool calls auto-approved
    </div>
  );
}
```

**Changes to `gateway/src/client/components/chat/ToolApproval.tsx`:**

1. Remove: `import { api } from '../../lib/api';`
2. Add: `import { useTransport } from '../../contexts/TransportContext';`
3. Add at top of component: `const transport = useTransport();`
4. Change approve call:
   ```typescript
   // Before:
   await api.approveTool(sessionId, toolCallId);
   // After:
   await transport.approveTool(sessionId, toolCallId);
   ```
5. Change deny call:
   ```typescript
   // Before:
   await api.denyTool(sessionId, toolCallId);
   // After:
   await transport.denyTool(sessionId, toolCallId);
   ```

Full updated file:
```typescript
import { useState } from 'react';
import { Check, X, Shield } from 'lucide-react';
import { useTransport } from '../../contexts/TransportContext';

interface ToolApprovalProps {
  sessionId: string;
  toolCallId: string;
  toolName: string;
  input: string;
}

export function ToolApproval({ sessionId, toolCallId, toolName, input }: ToolApprovalProps) {
  const transport = useTransport();
  const [responding, setResponding] = useState(false);
  const [decided, setDecided] = useState<'approved' | 'denied' | null>(null);

  async function handleApprove() {
    setResponding(true);
    try {
      await transport.approveTool(sessionId, toolCallId);
      setDecided('approved');
    } catch (err) {
      console.error('Approval failed:', err);
    } finally {
      setResponding(false);
    }
  }

  async function handleDeny() {
    setResponding(true);
    try {
      await transport.denyTool(sessionId, toolCallId);
      setDecided('denied');
    } catch (err) {
      console.error('Deny failed:', err);
    } finally {
      setResponding(false);
    }
  }

  // ... rest of JSX unchanged
}
```

**Acceptance Criteria:**
- Neither file imports from `api.ts`
- Both use `useTransport()` for server communication
- TypeScript compiles without errors
- UI behavior unchanged

---

### Task 8: [gateway-hexagonal-architecture] [P3] Delete api.ts and simplify platform.ts

**Active Form:** Deleting api.ts and removing apiBaseUrl from platform adapter

**Dependencies:** Task 4, Task 5, Task 6, Task 7

**Description:**

After all consumers have been migrated to `useTransport()`, delete the old `api.ts` file and simplify `platform.ts` by removing the `apiBaseUrl` property.

**Step 1: Delete `gateway/src/client/lib/api.ts`**

Remove the file entirely. All its functionality has been absorbed by `HttpTransport`.

**Step 2: Simplify `gateway/src/client/lib/platform.ts`**

Remove `apiBaseUrl` from the `PlatformAdapter` interface and the `webAdapter` default:

```typescript
export interface PlatformAdapter {
  /** Whether running inside Obsidian */
  isEmbedded: boolean;
  /** Get current session ID */
  getSessionId: () => string | null;
  /** Set current session ID */
  setSessionId: (id: string | null) => void;
  /** Open a file by path (no-op in standalone) */
  openFile: (path: string) => Promise<void>;
}

// Default: standalone web adapter
const webAdapter: PlatformAdapter = {
  isEmbedded: false,
  getSessionId: () => new URLSearchParams(location.search).get('session'),
  setSessionId: (id) => {
    const url = new URL(location.href);
    if (id) url.searchParams.set('session', id);
    else url.searchParams.delete('session');
    history.replaceState(null, '', url);
  },
  openFile: async () => {},
};

let currentAdapter: PlatformAdapter = webAdapter;

export function setPlatformAdapter(adapter: PlatformAdapter) {
  currentAdapter = adapter;
}

export function getPlatform(): PlatformAdapter {
  return currentAdapter;
}
```

**Step 3: Verify no remaining imports**

Search the codebase to ensure nothing still imports from `api.ts`:
- `grep -rn "from.*lib/api" gateway/src/` should return 0 results
- `grep -rn "apiBaseUrl" gateway/src/` should return 0 results (except possibly in tests that need updating)

**Step 4: Delete `gateway/src/client/lib/__tests__/api.test.ts`**

This test file tests the old `api.ts` module. It should be deleted since `api.ts` no longer exists. Transport-level tests are created in Task 16.

**Acceptance Criteria:**
- `api.ts` is deleted
- `api.test.ts` is deleted
- `PlatformAdapter` interface no longer has `apiBaseUrl`
- No files import from `api.ts` or reference `apiBaseUrl`
- TypeScript compiles without errors

---

### Task 9: [gateway-hexagonal-architecture] [P4] Verify standalone mode works

**Active Form:** Verifying standalone web client works with HttpTransport

**Dependencies:** Task 8

**Description:**

Run the full test suite and verify the standalone web client works identically with the new `HttpTransport`.

**Steps:**

1. Run the TypeScript compiler:
   ```bash
   cd gateway && npx tsc --noEmit
   ```
   Expect: 0 errors

2. Run all tests:
   ```bash
   cd gateway && npm run test:run
   ```
   Expect: All existing tests pass (some may need minor updates to mock `useTransport()` instead of `api`)

3. Run the dev server and manually verify:
   ```bash
   cd gateway && npm run dev
   ```
   Verify: Can create sessions, send messages, see streaming responses, approve/deny tools, view session list, use command palette.

4. Build the client:
   ```bash
   cd gateway && npm run build
   ```
   Expect: Build succeeds without errors

**Test Updates Required:**

If tests that mock `api` fail, update them to mock `useTransport()` instead:
- `use-chat-session.test.tsx` -- mock `../contexts/TransportContext` instead of `../lib/api`
- `use-sessions.test.tsx` -- mock `../contexts/TransportContext` instead of `../lib/api`
- `PermissionBanner.test.tsx` -- mock `../../contexts/TransportContext` instead of `../../lib/api`

The mock pattern changes from:
```typescript
vi.mock('../lib/api', () => ({ api: { listSessions: vi.fn(), ... } }));
```
To:
```typescript
const mockTransport = { listSessions: vi.fn(), createSession: vi.fn(), ... };
vi.mock('../contexts/TransportContext', () => ({
  useTransport: () => mockTransport,
}));
```

**Acceptance Criteria:**
- `tsc --noEmit` passes
- All tests pass
- Dev server starts and app works
- Production build succeeds

---

### Task 10: [gateway-hexagonal-architecture] [P5] Export service classes for DirectTransport

**Active Form:** Exporting AgentManager and TranscriptReader classes alongside singletons

**Dependencies:** Task 1

**Description:**

The `DirectTransport` needs to instantiate service classes directly. Currently, `agent-manager.ts` only exports the singleton `agentManager`, and `transcript-reader.ts` only exports the singleton `transcriptReader`. The classes need to be exported too.

**Changes to `gateway/src/server/services/agent-manager.ts`:**

Add `export` to the class declaration (line 20):

```typescript
// Before:
class AgentManager {
// After:
export class AgentManager {
```

The singleton export `export const agentManager = new AgentManager();` stays as-is on line 236. Both exports coexist.

**Changes to `gateway/src/server/services/transcript-reader.ts`:**

Add `export` to the class declaration (line 41):

```typescript
// Before:
class TranscriptReader {
// After:
export class TranscriptReader {
```

The singleton export `export const transcriptReader = new TranscriptReader();` stays as-is on line 272. Both exports coexist.

**Note:** `command-registry.ts` already exports the class (`export { CommandRegistryService }` on line 71). No changes needed.

**Acceptance Criteria:**
- `AgentManager` class is exported from agent-manager.ts
- `TranscriptReader` class is exported from transcript-reader.ts
- Singleton exports remain unchanged
- TypeScript compiles without errors
- No changes to Express routes (they continue using singletons)

---

### Task 11: [gateway-hexagonal-architecture] [P5] Create DirectTransport implementation

**Active Form:** Creating DirectTransport class that wraps service instances

**Dependencies:** Task 1, Task 10

**Description:**

Create the `DirectTransport` class that calls service methods directly (in-process) instead of going through HTTP. This is used by the Obsidian plugin.

Create file `gateway/src/client/lib/direct-transport.ts`:

```typescript
// src/client/lib/direct-transport.ts

import type { Transport } from '@shared/transport';
import type { StreamEvent, Session, CreateSessionRequest, CommandRegistry, HistoryMessage } from '@shared/types';

export interface DirectTransportServices {
  agentManager: {
    ensureSession(id: string, opts: { permissionMode: 'default' | 'dangerously-skip' }): void;
    sendMessage(id: string, content: string, opts?: { permissionMode?: 'default' | 'dangerously-skip' }): AsyncGenerator<StreamEvent>;
    approveTool(id: string, toolCallId: string, approved: boolean): boolean;
    getSdkSessionId(id: string): string | undefined;
  };
  transcriptReader: {
    listSessions(vaultRoot: string): Promise<Session[]>;
    getSession(vaultRoot: string, id: string): Promise<Session | null>;
    readTranscript(vaultRoot: string, id: string): Promise<HistoryMessage[]>;
  };
  commandRegistry: {
    getCommands(forceRefresh?: boolean): Promise<CommandRegistry>;
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

  async listSessions(): Promise<Session[]> {
    return this.services.transcriptReader.listSessions(this.services.vaultRoot);
  }

  async getSession(id: string): Promise<Session> {
    const session = await this.services.transcriptReader.getSession(this.services.vaultRoot, id);
    if (!session) throw new Error(`Session ${id} not found`);
    return session;
  }

  async getMessages(sessionId: string): Promise<{ messages: HistoryMessage[] }> {
    const messages = await this.services.transcriptReader.readTranscript(this.services.vaultRoot, sessionId);
    return { messages };
  }

  async sendMessage(
    sessionId: string,
    content: string,
    onEvent: (event: StreamEvent) => void,
    signal?: AbortSignal,
  ): Promise<void> {
    const generator = this.services.agentManager.sendMessage(sessionId, content);
    for await (const event of generator) {
      if (signal?.aborted) break;
      onEvent(event);
    }
  }

  async approveTool(sessionId: string, toolCallId: string): Promise<{ ok: boolean }> {
    const ok = this.services.agentManager.approveTool(sessionId, toolCallId, true);
    return { ok };
  }

  async denyTool(sessionId: string, toolCallId: string): Promise<{ ok: boolean }> {
    const ok = this.services.agentManager.approveTool(sessionId, toolCallId, false);
    return { ok };
  }

  async getCommands(refresh = false): Promise<CommandRegistry> {
    return this.services.commandRegistry.getCommands(refresh);
  }

  async health(): Promise<{ status: string; version: string; uptime: number }> {
    return { status: 'ok', version: '0.1.0', uptime: 0 };
  }
}
```

Key design notes:
- Uses `DirectTransportServices` interface rather than concrete class imports to keep the dependency lightweight
- `sendMessage` iterates the `AsyncGenerator<StreamEvent>` from `agentManager.sendMessage()` and calls `onEvent` for each event -- same events that `HttpTransport` parses from SSE
- `createSession` generates a UUID and calls `ensureSession` directly (same logic as the Express route)
- `health()` returns a static response since services are in-process (no connectivity concerns)

**Acceptance Criteria:**
- `DirectTransport` implements all `Transport` interface methods
- `DirectTransportServices` interface matches the public API of the service classes
- `sendMessage` correctly iterates AsyncGenerator and respects AbortSignal
- TypeScript compiles without errors

---

### Task 12: [gateway-hexagonal-architecture] [P6] Wire DirectTransport into CopilotView and ObsidianApp

**Active Form:** Wiring DirectTransport into Obsidian plugin view

**Dependencies:** Task 5, Task 11

**Description:**

Update `CopilotView.tsx` to instantiate services and `DirectTransport`, and wrap the React tree with `TransportProvider`. Update `ObsidianApp.tsx` to remove `ConnectionStatus` and add auto-session creation.

**Changes to `gateway/src/plugin/views/CopilotView.tsx`:**

```typescript
import { ItemView, WorkspaceLeaf } from 'obsidian';
import { createRoot, Root } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { NuqsAdapter } from 'nuqs/adapters/react';
import { setPlatformAdapter } from '../../client/lib/platform';
import { createObsidianAdapter } from '../lib/obsidian-adapter';
import { ObsidianProvider } from '../contexts/ObsidianContext';
import { ObsidianApp } from '../components/ObsidianApp';
import { TransportProvider } from '../../client/contexts/TransportContext';
import { DirectTransport } from '../../client/lib/direct-transport';
import { AgentManager } from '../../server/services/agent-manager';
import { TranscriptReader } from '../../server/services/transcript-reader';
import { CommandRegistryService } from '../../server/services/command-registry';
import type CopilotPlugin from '../main';
import '../styles/plugin.css';

export const VIEW_TYPE_COPILOT = 'lifeos-copilot-view';

export class CopilotView extends ItemView {
  root: Root | null = null;
  plugin: CopilotPlugin;
  queryClient: QueryClient;

  constructor(leaf: WorkspaceLeaf, plugin: CopilotPlugin) {
    super(leaf);
    this.plugin = plugin;
    this.queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 1 } } });
  }

  getViewType(): string { return VIEW_TYPE_COPILOT; }
  getDisplayText(): string { return 'Copilot'; }
  getIcon(): string { return 'bot'; }

  async onOpen(): Promise<void> {
    setPlatformAdapter(createObsidianAdapter(this.app));

    const vaultRoot = (this.app.vault.adapter as any).basePath;
    const agentManager = new AgentManager();
    const transcriptReader = new TranscriptReader();
    const commandRegistry = new CommandRegistryService(vaultRoot);

    const transport = new DirectTransport({
      agentManager,
      transcriptReader,
      commandRegistry,
      vaultRoot,
    });

    const container = this.containerEl.children[1] as HTMLElement;
    container.empty();
    container.addClass('copilot-view-content');

    this.root = createRoot(container);
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
  }

  async onClose(): Promise<void> {
    this.root?.unmount();
    this.root = null;
  }
}
```

**Changes to `gateway/src/plugin/components/ObsidianApp.tsx`:**

1. Remove `ConnectionStatus` import and usage:
   ```typescript
   // Remove:
   import { ConnectionStatus } from './ConnectionStatus';
   // Remove from JSX:
   <ConnectionStatus />
   ```

2. Add auto-session creation on mount using `useSessions()`:
   ```typescript
   import { useEffect } from 'react';  // add useEffect
   import { useSessions } from '../../client/hooks/use-sessions';
   ```

   Inside the component, add:
   ```typescript
   const { activeSessionId, createSession } = useSessions();

   // Auto-create session on mount if none exists
   useEffect(() => {
     if (!activeSessionId) {
       createSession.mutate({ permissionMode: 'default' });
     }
   }, []); // eslint-disable-line react-hooks/exhaustive-deps
   ```

Full updated file:
```typescript
import { useCallback, useEffect } from 'react';
import { TFile } from 'obsidian';
import { App } from '../../client/App';
import { useAppStore } from '../../client/stores/app-store';
import { useObsidian } from '../contexts/ObsidianContext';
import { useActiveFile } from '../hooks/use-active-file';
import { useFileOpener } from '../hooks/use-file-opener';
import { useSessions } from '../../client/hooks/use-sessions';
import { ContextBar } from './ContextBar';

export function ObsidianApp() {
  const { app } = useObsidian();
  const activeFile = useActiveFile();
  const { contextFiles, addContextFile, removeContextFile } = useAppStore();
  const { openFile } = useFileOpener();
  const { activeSessionId, createSession } = useSessions();

  // Auto-create session on mount if none exists
  useEffect(() => {
    if (!activeSessionId) {
      createSession.mutate({ permissionMode: 'default' });
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const transformContent = useCallback(async (content: string): Promise<string> => {
    const parts: string[] = [];

    if (activeFile) {
      const file = app.vault.getAbstractFileByPath(activeFile.path);
      if (file instanceof TFile) {
        const text = await app.vault.cachedRead(file);
        parts.push(`<context file="${activeFile.path}">\n${text}\n</context>`);
      }
    }

    for (const cf of contextFiles) {
      if (activeFile && cf.path === activeFile.path) continue;
      const file = app.vault.getAbstractFileByPath(cf.path);
      if (file instanceof TFile) {
        const text = await app.vault.cachedRead(file);
        parts.push(`<context file="${cf.path}">\n${text}\n</context>`);
      }
    }

    if (parts.length > 0) {
      return parts.join('\n\n') + '\n\n' + content;
    }
    return content;
  }, [app, activeFile, contextFiles]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center px-3 py-1.5 border-b">
        <ContextBar
          activeFile={activeFile}
          contextFiles={contextFiles}
          onRemoveFile={removeContextFile}
          onDrop={(path, basename) => addContextFile({ path, basename })}
          onFileClick={openFile}
        />
      </div>
      <App transformContent={transformContent} embedded />
    </div>
  );
}
```

**Acceptance Criteria:**
- `CopilotView` instantiates `AgentManager`, `TranscriptReader`, `CommandRegistryService`
- `DirectTransport` is created with service instances and `vaultRoot`
- `TransportProvider` wraps the React tree
- `ObsidianApp` no longer renders `ConnectionStatus`
- Auto-session creation works on mount
- TypeScript compiles without errors

---

### Task 13: [gateway-hexagonal-architecture] [P6] Delete ConnectionStatus and simplify obsidian-adapter

**Active Form:** Deleting ConnectionStatus component and simplifying obsidian-adapter

**Dependencies:** Task 12

**Description:**

Clean up files that are no longer needed after DirectTransport wiring.

**Step 1: Delete `gateway/src/plugin/components/ConnectionStatus.tsx`**

This component polls `GET /health` via HTTP. With DirectTransport, services are in-process and there's no concept of "gateway not connected." Delete the file entirely.

**Step 2: Simplify `gateway/src/plugin/lib/obsidian-adapter.ts`**

Remove the `apiBaseUrl` property since the Transport handles all communication:

```typescript
import { App, TFile } from 'obsidian';
import { PlatformAdapter } from '../../client/lib/platform';
import { useAppStore } from '../../client/stores/app-store';

export function createObsidianAdapter(app: App): PlatformAdapter {
  return {
    isEmbedded: true,
    getSessionId: () => useAppStore.getState().sessionId,
    setSessionId: (id) => useAppStore.getState().setSessionId(id),
    openFile: async (path: string) => {
      const file = app.vault.getAbstractFileByPath(path);
      if (file instanceof TFile) {
        await app.workspace.getLeaf(false).openFile(file);
      }
    },
  };
}
```

**Step 3: Verify no remaining references**

Check that nothing imports `ConnectionStatus`:
```bash
grep -rn "ConnectionStatus" gateway/src/
```
Should return 0 results after this task.

**Acceptance Criteria:**
- `ConnectionStatus.tsx` is deleted
- `obsidian-adapter.ts` no longer has `apiBaseUrl`
- No remaining imports of `ConnectionStatus` in the codebase
- TypeScript compiles without errors

---

### Task 14: [gateway-hexagonal-architecture] [P7] Update plugin build config

**Active Form:** Updating vite.config.obsidian.ts to bundle services and externalize Node.js built-ins

**Dependencies:** Task 12

**Description:**

Update `gateway/vite.config.obsidian.ts` to properly bundle server services and their dependencies while externalizing Node.js built-ins that Obsidian's Electron provides.

**Key changes:**
- `@anthropic-ai/claude-agent-sdk` must be bundled (NOT external) -- it's the core dependency for `AgentManager`
- `gray-matter` must be bundled (NOT external) -- used by `CommandRegistryService`
- Node.js built-ins must be external -- provided by Electron runtime
- `fs/promises` must be explicitly listed as external

Updated `gateway/vite.config.obsidian.ts`:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/plugin/main.ts'),
      formats: ['cjs'],
      fileName: () => 'main.js',
    },
    rollupOptions: {
      external: [
        'obsidian', 'electron',
        // CodeMirror/Lezer externals (provided by Obsidian)
        '@codemirror/autocomplete', '@codemirror/collab', '@codemirror/commands',
        '@codemirror/language', '@codemirror/lint', '@codemirror/search',
        '@codemirror/state', '@codemirror/view',
        '@lezer/common', '@lezer/highlight', '@lezer/lr',
        // Node.js built-ins (provided by Electron runtime)
        'child_process', 'fs', 'path', 'os', 'url', 'crypto',
        'fs/promises', 'events', 'stream', 'util', 'net', 'http', 'https',
      ],
      output: {
        inlineDynamicImports: true,
        exports: 'default',
      },
    },
    outDir: 'dist-obsidian',
    emptyOutDir: true,
    sourcemap: 'inline',
    cssCodeSplit: false,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src/client'),
      '@shared': path.resolve(__dirname, 'src/shared'),
    },
  },
});
```

**Note:** `@anthropic-ai/claude-agent-sdk` and `gray-matter` are NOT in the externals list, so they get bundled into the plugin. This increases bundle size but simplifies distribution.

**Verification:**

After updating, run:
```bash
cd gateway && npx vite build --config vite.config.obsidian.ts
```

Check that `dist-obsidian/main.js` is produced without errors. The file will be larger than before (includes SDK + gray-matter), which is acceptable.

**Acceptance Criteria:**
- Node.js built-ins are externalized (including `fs/promises`)
- `@anthropic-ai/claude-agent-sdk` is bundled (not external)
- `gray-matter` is bundled (not external)
- `npm run build:obsidian` or equivalent produces `dist-obsidian/main.js` without errors
- Existing CodeMirror/Lezer/Obsidian externals are preserved

---

### Task 15: [gateway-hexagonal-architecture] [P8] Write architecture documentation

**Active Form:** Writing architecture documentation and updating existing guides

**Dependencies:** Task 14

**Description:**

Create and update documentation to reflect the hexagonal architecture.

**Step 1: Create `gateway/guides/architecture.md`**

Document the hexagonal architecture with:

```markdown
# Architecture

## Overview

The LifeOS Gateway uses a hexagonal (ports-and-adapters) architecture to support two deployment modes:

1. **Standalone mode** -- React web client communicates with an Express server via HTTP/SSE
2. **Obsidian plugin mode** -- React components call server services directly in-process

Both modes share the same React components, hooks, and stores. The difference is the Transport adapter injected at startup.

## Transport Interface (Port)

The `Transport` interface (`src/shared/transport.ts`) defines the contract between client code and server services:

- `createSession()` -- Start a new Claude session
- `listSessions()` -- List all sessions from SDK transcripts
- `getSession()` -- Get session metadata
- `getMessages()` -- Load message history
- `sendMessage()` -- Stream a message (callback-based)
- `approveTool()` / `denyTool()` -- Tool approval flow
- `getCommands()` -- List slash commands
- `health()` -- Health check

### Key Design: Callback-Based Streaming

`sendMessage` uses `onEvent: (event: StreamEvent) => void` rather than returning an AsyncGenerator. This normalizes both transports:

- `HttpTransport` parses SSE from `fetch()` and calls `onEvent` for each parsed event
- `DirectTransport` iterates the AsyncGenerator from `AgentManager` and calls `onEvent` for each yielded event

Consumer code is identical either way.

## Transport Adapters

### HttpTransport (`src/client/lib/http-transport.ts`)

Used in standalone mode. Wraps `fetch()` for REST calls and SSE parsing for streaming.

Injected in `main.tsx`:
\`\`\`typescript
const transport = new HttpTransport('/api');
\`\`\`

### DirectTransport (`src/client/lib/direct-transport.ts`)

Used in Obsidian plugin mode. Wraps service instances (AgentManager, TranscriptReader, CommandRegistryService) for in-process calls.

Injected in `CopilotView.tsx`:
\`\`\`typescript
const transport = new DirectTransport({ agentManager, transcriptReader, commandRegistry, vaultRoot });
\`\`\`

## Dependency Injection

Transport is injected via React Context (`TransportContext`). All hooks and components call `useTransport()` to get the transport instance.

\`\`\`
main.tsx / CopilotView.tsx
  └─ TransportProvider (transport={HttpTransport | DirectTransport})
       └─ App
            ├─ useSessions() → transport.listSessions()
            ├─ useChatSession() → transport.sendMessage()
            ├─ useCommands() → transport.getCommands()
            └─ PermissionBanner → transport.getSession()
\`\`\`

## Service Layer

Three core services power both transports:

| Service | Purpose | Node.js Dependencies |
|---------|---------|---------------------|
| `AgentManager` | SDK session lifecycle, streaming | `child_process`, `path`, `url` |
| `TranscriptReader` | JSONL transcript reading | `fs/promises`, `path`, `os` |
| `CommandRegistryService` | Slash command scanning | `fs/promises`, `path`, `gray-matter` |

In standalone mode, Express routes instantiate these services. In plugin mode, `CopilotView` instantiates them directly.

## Adding a New Transport

1. Create a class implementing `Transport` in `src/client/lib/`
2. Inject it via `TransportProvider` at the appropriate entry point
3. No changes needed to hooks, components, or services

## File Organization

\`\`\`
src/
  shared/
    types.ts              -- Shared type definitions
    transport.ts           -- Transport interface (port)
  client/
    lib/
      http-transport.ts    -- HTTP/SSE adapter
      direct-transport.ts  -- In-process adapter
      platform.ts          -- Platform detection (embedded vs standalone)
    contexts/
      TransportContext.tsx  -- React context for DI
    hooks/                 -- Transport-agnostic hooks
    components/            -- Transport-agnostic components
    main.tsx               -- Standalone entry (HttpTransport)
  server/
    services/              -- Core services (transport-independent)
    routes/                -- Express routes (standalone only)
  plugin/
    views/CopilotView.tsx  -- Plugin entry (DirectTransport)
    components/            -- Plugin-specific components
\`\`\`
```

**Step 2: Update `gateway/guides/obsidian-plugin-development.md`**

Add a section about DirectTransport and remove any references to requiring the Express server. Add:
- The plugin no longer requires the Express server
- Services are instantiated in `CopilotView.onOpen()`
- `DirectTransport` provides in-process communication
- Build config bundles the SDK and gray-matter

**Step 3: Update `gateway/CLAUDE.md`**

Add architecture section referencing `guides/architecture.md`. Update the "Architecture" section to mention the Transport abstraction and the two deployment modes.

**Acceptance Criteria:**
- `gateway/guides/architecture.md` exists with complete documentation
- `gateway/guides/obsidian-plugin-development.md` is updated (no Express server requirement)
- `gateway/CLAUDE.md` references the new architecture docs

---

### Task 16: [gateway-hexagonal-architecture] [P9] Add tests for transports and update existing tests

**Active Form:** Adding transport tests and updating existing tests to mock useTransport

**Dependencies:** Task 8

**Description:**

Create new tests for transport implementations and update existing tests that mock `api` to mock `useTransport()` instead.

**New test 1: `gateway/src/client/lib/__tests__/http-transport.test.ts`**

Test HttpTransport by mocking `fetch`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { HttpTransport } from '../http-transport';

// Mock fetch globally
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

describe('HttpTransport', () => {
  let transport: HttpTransport;

  beforeEach(() => {
    transport = new HttpTransport('/api');
    mockFetch.mockReset();
  });

  describe('fetchJSON methods', () => {
    it('listSessions calls GET /sessions', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([{ id: '1', title: 'Test' }]),
      });

      const result = await transport.listSessions();
      expect(mockFetch).toHaveBeenCalledWith('/api/sessions', expect.objectContaining({
        headers: { 'Content-Type': 'application/json' },
      }));
      expect(result).toEqual([{ id: '1', title: 'Test' }]);
    });

    it('createSession calls POST /sessions', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ id: '1', title: 'New' }),
      });

      await transport.createSession({ permissionMode: 'default' });
      expect(mockFetch).toHaveBeenCalledWith('/api/sessions', expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ permissionMode: 'default' }),
      }));
    });

    it('throws on non-ok response', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({ error: 'Session not found' }),
      });

      await expect(transport.getSession('bad-id')).rejects.toThrow('Session not found');
    });
  });

  describe('sendMessage (SSE)', () => {
    it('parses SSE events and calls onEvent', async () => {
      const events: any[] = [];
      const sseData = [
        'event: text_delta\n',
        'data: {"text":"Hello"}\n',
        '\n',
        'event: done\n',
        'data: {"sessionId":"s1"}\n',
        '\n',
      ].join('');

      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode(sseData));
          controller.close();
        },
      });

      mockFetch.mockResolvedValue({
        ok: true,
        body: stream,
      });

      await transport.sendMessage('s1', 'Hello', (event) => events.push(event));

      expect(events).toHaveLength(2);
      expect(events[0]).toEqual({ type: 'text_delta', data: { text: 'Hello' } });
      expect(events[1]).toEqual({ type: 'done', data: { sessionId: 's1' } });
    });

    it('handles chunked SSE data across reads', async () => {
      const events: any[] = [];
      const encoder = new TextEncoder();
      const chunks = [
        'event: text_del',
        'ta\ndata: {"text":"Hi"}\n\n',
      ];

      const stream = new ReadableStream({
        start(controller) {
          for (const chunk of chunks) {
            controller.enqueue(encoder.encode(chunk));
          }
          controller.close();
        },
      });

      mockFetch.mockResolvedValue({ ok: true, body: stream });
      await transport.sendMessage('s1', 'Hi', (event) => events.push(event));

      expect(events).toHaveLength(1);
      expect(events[0].data.text).toBe('Hi');
    });
  });
});
```

**New test 2: `gateway/src/client/lib/__tests__/direct-transport.test.ts`**

Test DirectTransport by mocking service instances:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DirectTransport, type DirectTransportServices } from '../direct-transport';

describe('DirectTransport', () => {
  let transport: DirectTransport;
  let mockServices: DirectTransportServices;

  beforeEach(() => {
    mockServices = {
      agentManager: {
        ensureSession: vi.fn(),
        sendMessage: vi.fn(),
        approveTool: vi.fn(),
        getSdkSessionId: vi.fn(),
      },
      transcriptReader: {
        listSessions: vi.fn(),
        getSession: vi.fn(),
        readTranscript: vi.fn(),
      },
      commandRegistry: {
        getCommands: vi.fn(),
      },
      vaultRoot: '/test/vault',
    };
    transport = new DirectTransport(mockServices);
  });

  it('createSession generates UUID and calls ensureSession', async () => {
    const session = await transport.createSession({ permissionMode: 'default' });
    expect(session.id).toBeDefined();
    expect(session.title).toBe('New session');
    expect(mockServices.agentManager.ensureSession).toHaveBeenCalledWith(
      session.id,
      { permissionMode: 'default' },
    );
  });

  it('listSessions delegates to transcriptReader', async () => {
    const sessions = [{ id: '1', title: 'Test', createdAt: '', updatedAt: '', permissionMode: 'default' as const }];
    (mockServices.transcriptReader.listSessions as any).mockResolvedValue(sessions);

    const result = await transport.listSessions();
    expect(result).toEqual(sessions);
    expect(mockServices.transcriptReader.listSessions).toHaveBeenCalledWith('/test/vault');
  });

  it('getSession throws when session not found', async () => {
    (mockServices.transcriptReader.getSession as any).mockResolvedValue(null);
    await expect(transport.getSession('bad')).rejects.toThrow('Session bad not found');
  });

  it('sendMessage iterates AsyncGenerator and calls onEvent', async () => {
    const events = [
      { type: 'text_delta', data: { text: 'Hello' } },
      { type: 'done', data: { sessionId: 's1' } },
    ];

    async function* mockGenerator() {
      for (const event of events) {
        yield event;
      }
    }

    (mockServices.agentManager.sendMessage as any).mockReturnValue(mockGenerator());

    const received: any[] = [];
    await transport.sendMessage('s1', 'Hi', (event) => received.push(event));

    expect(received).toEqual(events);
  });

  it('sendMessage respects AbortSignal', async () => {
    const events = [
      { type: 'text_delta', data: { text: 'Hello' } },
      { type: 'text_delta', data: { text: ' world' } },
    ];

    async function* mockGenerator() {
      for (const event of events) {
        yield event;
      }
    }

    (mockServices.agentManager.sendMessage as any).mockReturnValue(mockGenerator());

    const controller = new AbortController();
    const received: any[] = [];

    // Abort after first event
    await transport.sendMessage('s1', 'Hi', (event) => {
      received.push(event);
      controller.abort();
    }, controller.signal);

    expect(received).toHaveLength(1);
  });

  it('approveTool delegates to agentManager', async () => {
    (mockServices.agentManager.approveTool as any).mockReturnValue(true);
    const result = await transport.approveTool('s1', 'tc1');
    expect(result).toEqual({ ok: true });
    expect(mockServices.agentManager.approveTool).toHaveBeenCalledWith('s1', 'tc1', true);
  });

  it('health returns static response', async () => {
    const result = await transport.health();
    expect(result.status).toBe('ok');
  });
});
```

**New test 3: `gateway/src/client/contexts/__tests__/TransportContext.test.tsx`**

```typescript
import { describe, it, expect } from 'vitest';
import { renderHook } from '@testing-library/react';
import { TransportProvider, useTransport } from '../TransportContext';
import type { Transport } from '@shared/transport';

describe('TransportContext', () => {
  it('throws when used outside TransportProvider', () => {
    expect(() => {
      renderHook(() => useTransport());
    }).toThrow('useTransport must be used within a TransportProvider');
  });

  it('provides transport to children', () => {
    const mockTransport = { listSessions: async () => [] } as unknown as Transport;

    const { result } = renderHook(() => useTransport(), {
      wrapper: ({ children }) => (
        <TransportProvider transport={mockTransport}>{children}</TransportProvider>
      ),
    });

    expect(result.current).toBe(mockTransport);
  });
});
```

**Update existing tests:**

For `gateway/src/client/hooks/__tests__/use-chat-session.test.tsx`:
- Replace `vi.mock('../lib/api', ...)` with:
  ```typescript
  const mockTransport = {
    getMessages: vi.fn().mockResolvedValue({ messages: [] }),
    sendMessage: vi.fn(),
    // ... other methods as needed
  };
  vi.mock('../../contexts/TransportContext', () => ({
    useTransport: () => mockTransport,
  }));
  ```

For `gateway/src/client/hooks/__tests__/use-sessions.test.tsx`:
- Replace `vi.mock('../lib/api', ...)` with mock `useTransport()`

For `gateway/src/client/components/layout/__tests__/PermissionBanner.test.tsx`:
- Replace `vi.mock('../../lib/api', ...)` with mock `useTransport()`

**Acceptance Criteria:**
- `http-transport.test.ts` exists with tests for all methods + SSE parsing
- `direct-transport.test.ts` exists with tests for all methods + AsyncGenerator iteration
- `TransportContext.test.tsx` exists with provider/consumer tests
- All existing tests updated to mock `useTransport()` instead of `api`
- `npm run test:run` passes all tests

---

## Dependency Graph

```
Task 1 (Transport interface) ─┬─→ Task 3 (HttpTransport) ─→ Tasks 4-7 (Hook refactors) ─→ Task 8 (Delete api.ts) ─→ Task 9 (Verify)
                               │                                       │                                              │
Task 2 (TransportContext) ─────┘                                       │                                              └─→ Task 16 (Tests)
                                                                       │
Task 10 (Export classes) ──────→ Task 11 (DirectTransport) ────────────┘
                                                                       │
                                                              Tasks 12-13 (Plugin wiring) ─→ Task 14 (Build config) ─→ Task 15 (Docs)
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Agent SDK doesn't work in Electron renderer | Low | High | Falls back to HTTP; test early in Phase 6 |
| Vite can't bundle SDK properly | Medium | Medium | May need custom Rollup plugin or manual resolution |
| Existing tests break during refactor | High | Low | Update mocks incrementally in Phase 3 |
| `import.meta.url` in agent-manager.ts | Medium | Medium | May need Vite `define` or path resolution workaround for CJS build |
