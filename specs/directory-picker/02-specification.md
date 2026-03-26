---
slug: directory-picker
type: specification
status: draft
---

# Specification: Directory Picker for Claude Code Working Directory

**Slug:** directory-picker
**Author:** Claude Code
**Date:** 2026-02-09
**Ideation:** [01-ideation.md](./01-ideation.md)

---

## Overview

Add a global project directory selector to the gateway. The selected directory determines:
1. Which sessions are shown in the sidebar (SDK transcripts are stored per-project slug)
2. Where new sessions are created (passed as `cwd` to SDK `query()`)

The default directory is the server's working directory (`process.cwd()`). Users change it via a folder picker button in the sidebar header.

---

## Technical Design

### Architecture

The feature adds three layers:

1. **Server API**: New `GET /api/directory` endpoint for filesystem browsing, plus `cwd` query param on existing session endpoints
2. **Transport**: New `browseDirectory()` method on Transport interface; `listSessions()` and `createSession()` gain `cwd` parameter
3. **Client**: Zustand state for `selectedCwd`, folder picker UI component triggered from sidebar header, session queries keyed by `selectedCwd`

### API Design

#### New Endpoint: `GET /api/directory`

Browse directories on the server filesystem (restricted to home directory).

**Request:**
```
GET /api/directory?path=/Users/name/projects&showHidden=false
```

**Query Parameters (Zod schema):**
```typescript
export const BrowseDirectoryQuerySchema = z
  .object({
    path: z.string().min(1).optional(),       // defaults to os.homedir()
    showHidden: z.coerce.boolean().optional().default(false),
  })
  .openapi('BrowseDirectoryQuery');
```

**Response:**
```typescript
export const DirectoryEntrySchema = z
  .object({
    name: z.string(),
    path: z.string(),
    isDirectory: z.boolean(),
  })
  .openapi('DirectoryEntry');

export const BrowseDirectoryResponseSchema = z
  .object({
    path: z.string(),          // resolved absolute path
    entries: z.array(DirectoryEntrySchema),
    parent: z.string().nullable(),  // null if at root or home boundary
  })
  .openapi('BrowseDirectoryResponse');
```

**Security:**
- Resolve path with `fs.realpath()` to prevent symlink traversal
- Validate resolved path starts with `os.homedir()`
- Reject paths containing null bytes
- Return 403 for paths outside home directory
- Return 404 for non-existent directories
- Return 403 for permission errors (`EACCES`)

**Implementation:**
```typescript
// src/server/routes/directory.ts
import { Router } from 'express';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';
import { BrowseDirectoryQuerySchema } from '@shared/schemas';

const router = Router();
const HOME = os.homedir();

router.get('/', async (req, res) => {
  const parsed = BrowseDirectoryQuerySchema.safeParse(req.query);
  if (!parsed.success) return res.status(400).json({ error: 'Invalid query', details: parsed.error.format() });
  const { path: userPath, showHidden } = parsed.data;

  // Resolve path (default to home)
  const targetPath = userPath || HOME;
  let resolved: string;
  try {
    resolved = await fs.realpath(targetPath);
  } catch (err: any) {
    if (err.code === 'ENOENT') return res.status(404).json({ error: 'Directory not found' });
    if (err.code === 'EACCES') return res.status(403).json({ error: 'Permission denied' });
    throw err;
  }

  // Security: restrict to home directory
  if (!resolved.startsWith(HOME)) {
    return res.status(403).json({ error: 'Access denied: path outside home directory' });
  }

  // Read directory entries (directories only)
  const dirents = await fs.readdir(resolved, { withFileTypes: true });
  const entries = dirents
    .filter(d => d.isDirectory())
    .filter(d => showHidden || !d.name.startsWith('.'))
    .map(d => ({
      name: d.name,
      path: path.join(resolved, d.name),
      isDirectory: true,
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

  const parent = path.dirname(resolved);
  const hasParent = parent !== resolved && parent.startsWith(HOME);

  res.json({
    path: resolved,
    entries,
    parent: hasParent ? parent : null,
  });
});
```

#### Modified: `GET /api/sessions`

Add optional `cwd` query parameter.

**Schema change:**
```typescript
export const ListSessionsQuerySchema = z
  .object({
    limit: z.coerce.number().int().min(1).max(500).optional().default(200),
    cwd: z.string().optional(),  // NEW: project directory to list sessions for
  })
  .openapi('ListSessionsQuery');
```

**Route change:** Pass `cwd` (or default) to `transcriptReader.listSessions()`:
```typescript
router.get('/', async (req, res) => {
  const parsed = ListSessionsQuerySchema.safeParse(req.query);
  // ...
  const projectDir = parsed.data.cwd || vaultRoot;
  const sessions = await transcriptReader.listSessions(projectDir);
  res.json(sessions.slice(0, parsed.data.limit));
});
```

#### Modified: `POST /api/sessions`

Add optional `cwd` to request body.

**Schema change:**
```typescript
export const CreateSessionRequestSchema = z
  .object({
    permissionMode: PermissionModeSchema.optional(),
    cwd: z.string().optional(),  // NEW: working directory for this session
  })
  .openapi('CreateSessionRequest');
```

**Route change:** Pass `cwd` to `agentManager.ensureSession()`:
```typescript
router.post('/', async (req, res) => {
  const { permissionMode = 'default', cwd } = req.body;
  const sessionId = crypto.randomUUID();
  agentManager.ensureSession(sessionId, { permissionMode, cwd });
  res.json({
    id: sessionId,
    title: 'New Session',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    permissionMode,
    cwd,
  });
});
```

#### New Endpoint: `GET /api/directory/default`

Returns the server's default working directory.

```
GET /api/directory/default
→ { "path": "/Users/name/projects/my-app" }
```

This lets the client know the initial default cwd on startup, without hardcoding it.

### Transport Interface Changes

```typescript
export interface Transport {
  // MODIFIED: listSessions gains optional cwd
  listSessions(cwd?: string): Promise<Session[]>;

  // MODIFIED: createSession type already includes cwd via CreateSessionRequest schema change

  // NEW: directory browsing
  browseDirectory(path?: string, showHidden?: boolean): Promise<BrowseDirectoryResponse>;

  // NEW: get server's default working directory
  getDefaultCwd(): Promise<{ path: string }>;

  // ... all existing methods unchanged
}
```

**HttpTransport implementation:**
```typescript
async listSessions(cwd?: string): Promise<Session[]> {
  const params = new URLSearchParams();
  if (cwd) params.set('cwd', cwd);
  const res = await fetch(`${this.baseUrl}/api/sessions?${params}`);
  return res.json();
}

async browseDirectory(dirPath?: string, showHidden?: boolean): Promise<BrowseDirectoryResponse> {
  const params = new URLSearchParams();
  if (dirPath) params.set('path', dirPath);
  if (showHidden) params.set('showHidden', 'true');
  const res = await fetch(`${this.baseUrl}/api/directory?${params}`);
  if (!res.ok) throw new Error(`Browse failed: ${res.status}`);
  return res.json();
}

async getDefaultCwd(): Promise<{ path: string }> {
  const res = await fetch(`${this.baseUrl}/api/directory/default`);
  return res.json();
}
```

**DirectTransport implementation:**
```typescript
async listSessions(cwd?: string): Promise<Session[]> {
  return this.services.transcriptReader.listSessions(cwd || this.repoRoot);
}

async browseDirectory(dirPath?: string, showHidden?: boolean): Promise<BrowseDirectoryResponse> {
  // Direct filesystem access (same logic as server route)
  return this.services.directoryService.browse(dirPath, showHidden);
}

async getDefaultCwd(): Promise<{ path: string }> {
  return { path: this.repoRoot };
}
```

### Server-Side Changes

#### TranscriptReader

Remove cached `projectSlug` field. Make `getProjectSlug()` a pure function:

```typescript
// BEFORE (stateful)
private projectSlug: string | null = null;

getProjectSlug(vaultRoot: string): string {
  if (this.projectSlug) return this.projectSlug;
  this.projectSlug = vaultRoot.replace(/\//g, '-');
  return this.projectSlug;
}

// AFTER (stateless)
getProjectSlug(cwd: string): string {
  return cwd.replace(/\//g, '-');
}
```

The `metaCache` (Map<sessionId, metadata>) is fine -- session IDs are globally unique UUIDs.

#### AgentManager

Store `cwd` per-session in `AgentSession` interface:

```typescript
interface AgentSession {
  sdkSessionId: string;
  lastActivity: number;
  permissionMode: PermissionMode;
  model?: string;
  cwd?: string;                    // NEW: per-session working directory
  hasStarted: boolean;
  pendingInteractions: Map<string, PendingInteraction>;
  eventQueue: StreamEvent[];
  eventQueueNotify?: () => void;
}
```

Update `ensureSession()`:
```typescript
ensureSession(sessionId: string, opts: {
  permissionMode: PermissionMode;
  cwd?: string;                    // NEW
}): void {
  if (!this.sessions.has(sessionId)) {
    this.sessions.set(sessionId, {
      sdkSessionId: sessionId,
      lastActivity: Date.now(),
      permissionMode: opts.permissionMode,
      cwd: opts.cwd,               // NEW
      hasStarted: false,
      pendingInteractions: new Map(),
      eventQueue: [],
    });
  }
}
```

Update `sendMessage()` to use per-session cwd:
```typescript
const session = this.sessions.get(sessionId)!;
const sdkOptions: Options = {
  cwd: session.cwd ?? this.cwd,   // per-session cwd falls back to constructor default
  // ... rest unchanged
};
```

### Client-Side Changes

#### Zustand Store (`app-store.ts`)

Add `selectedCwd` state:

```typescript
interface AppState {
  // ... existing fields

  selectedCwd: string | null;       // null = use server default (not yet loaded)
  setSelectedCwd: (cwd: string) => void;

  recentCwds: string[];             // persisted to localStorage
  addRecentCwd: (cwd: string) => void;
}
```

Persist `recentCwds` to localStorage:
```typescript
// On setSelectedCwd, also update recentCwds
setSelectedCwd: (cwd) => set((s) => {
  const recents = [cwd, ...s.recentCwds.filter(r => r !== cwd)].slice(0, 10);
  localStorage.setItem('gateway-recent-cwds', JSON.stringify(recents));
  return { selectedCwd: cwd, recentCwds: recents };
}),
```

Initialize from localStorage on store creation:
```typescript
recentCwds: JSON.parse(localStorage.getItem('gateway-recent-cwds') || '[]'),
```

#### Session Queries (`use-sessions.ts`)

Key sessions query by `selectedCwd`:

```typescript
export function useSessions() {
  const { selectedCwd } = useAppStore();
  const transport = useTransport();

  const sessionsQuery = useQuery({
    queryKey: ['sessions', selectedCwd],
    queryFn: () => transport.listSessions(selectedCwd ?? undefined),
    refetchInterval: 60_000,
    enabled: selectedCwd !== null,   // wait until default cwd is loaded
  });

  const createSession = useMutation({
    mutationFn: (opts: CreateSessionRequest) =>
      transport.createSession({ ...opts, cwd: selectedCwd ?? undefined }),
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ['sessions', selectedCwd] });
      setActiveSession(session.id);
    },
  });
  // ...
}
```

#### Default CWD Loading

On app mount, fetch the server's default cwd:

```typescript
// In App.tsx or a top-level hook
const transport = useTransport();
const { selectedCwd, setSelectedCwd } = useAppStore();

useQuery({
  queryKey: ['defaultCwd'],
  queryFn: () => transport.getDefaultCwd(),
  enabled: selectedCwd === null,
  onSuccess: (data) => setSelectedCwd(data.path),
});
```

#### Directory Picker Component

**Location:** `src/client/components/sessions/DirectoryPicker.tsx`

**Trigger:** Button in sidebar header (next to "New Chat"), with folder icon.

**UI structure:**
```
┌─────────────────────────────────────────────┐
│  Select Working Directory                    │
├─────────────────────────────────────────────┤
│  🏠 › Users › name › projects          [👁]  │  ← breadcrumb + show hidden toggle
├─────────────────────────────────────────────┤
│  📁 my-app                                   │
│  📁 other-project                            │  ← scrollable folder list
│  📁 archived                                 │
├─────────────────────────────────────────────┤
│  Recent:                                     │
│  📁 ~/projects/my-app                        │  ← from localStorage
│  📁 ~/work/client-project                    │
├─────────────────────────────────────────────┤
│  [Cancel]          [Select This Directory]   │
└─────────────────────────────────────────────┘
```

**Component behavior:**
- Opens as a modal (or popover from sidebar button)
- Default starting path: current `selectedCwd`
- Clicking a folder navigates into it (fetches via `transport.browseDirectory()`)
- Breadcrumb segments are clickable to navigate up
- "Select This Directory" sets `selectedCwd` in Zustand store
- Recent directories section shows last 10 from localStorage
- Show hidden toggle controls `showHidden` query param
- Breadcrumb collapses to ellipsis dropdown for deep paths (using shadcn Breadcrumb component)
- TanStack Query with `keepPreviousData: true` for smooth navigation

**Data fetching:**
```typescript
const { data, isLoading } = useQuery({
  queryKey: ['directory', currentPath, showHidden],
  queryFn: () => transport.browseDirectory(currentPath, showHidden),
  keepPreviousData: true,
  staleTime: 30_000,
});
```

#### Sidebar Integration

In `SessionSidebar.tsx`, add the directory picker trigger button:

```tsx
<div className="flex items-center gap-1.5">
  {/* NEW: Directory picker button */}
  <button
    onClick={() => setPickerOpen(true)}
    className="p-2 rounded-md hover:bg-accent transition-colors duration-150"
    aria-label="Change working directory"
    title={selectedCwd || 'Select directory'}
  >
    <FolderOpen className="h-4 w-4 text-muted-foreground" />
  </button>

  {/* Existing: New Chat button */}
  <button onClick={() => createMutation.mutate({ permissionMode })} ...>
    <Plus className="h-4 w-4" />
    New chat
  </button>

  {/* Existing: Collapse button */}
  <button onClick={() => setSidebarOpen(false)} ...>
    <PanelLeftClose className="h-4 w-4 text-muted-foreground" />
  </button>
</div>
```

---

## Implementation Phases

### Phase 1: Server API (Backend)

**Files to create:**
- `src/server/routes/directory.ts` - Browse directory endpoint + default cwd endpoint

**Files to modify:**
- `src/shared/schemas.ts` - Add `BrowseDirectoryQuerySchema`, `DirectoryEntrySchema`, `BrowseDirectoryResponseSchema`; add `cwd` to `CreateSessionRequestSchema` and `ListSessionsQuerySchema`
- `src/server/app.ts` - Mount `/api/directory` route
- `src/server/routes/sessions.ts` - Accept `cwd` query param on GET, `cwd` body param on POST
- `src/server/services/agent-manager.ts` - Add `cwd` to `AgentSession`, update `ensureSession()`, use per-session cwd in `sendMessage()`
- `src/server/services/transcript-reader.ts` - Remove `projectSlug` cache, make `getProjectSlug()` stateless
- `src/server/services/openapi-registry.ts` - Register `GET /api/directory` and `GET /api/directory/default`

**Tests to create:**
- `src/server/routes/__tests__/directory.test.ts`

**Tests to update:**
- `src/server/routes/__tests__/sessions.test.ts` - Test `cwd` query/body params
- `src/server/services/__tests__/agent-manager.test.ts` - Test per-session cwd
- `src/server/services/__tests__/transcript-reader.test.ts` - Test stateless slug derivation

### Phase 2: Transport Layer (Plumbing)

**Files to modify:**
- `src/shared/transport.ts` - Add `browseDirectory()`, `getDefaultCwd()`; update `listSessions()` signature
- `src/client/lib/http-transport.ts` - Implement new/modified methods
- `src/client/lib/direct-transport.ts` - Implement new/modified methods

### Phase 3: Client UI (Frontend)

**Files to create:**
- `src/client/components/sessions/DirectoryPicker.tsx`
- `src/client/components/sessions/__tests__/DirectoryPicker.test.tsx`

**Files to modify:**
- `src/client/stores/app-store.ts` - Add `selectedCwd`, `recentCwds`, persistence
- `src/client/hooks/use-sessions.ts` - Key queries by `selectedCwd`, pass `cwd` to create
- `src/client/components/sessions/SessionSidebar.tsx` - Add picker trigger button

**shadcn components to install:**
- `breadcrumb` (for path navigation in picker)

### Phase 4: Deferred (Not in this spec)

- Obsidian plugin Electron native dialog (`dialog.showOpenDialog`)
- Making CwdItem in StatusLine clickable to open picker
- Path autocomplete / type-to-navigate

---

## Acceptance Criteria

1. **Default behavior unchanged**: On startup with no user action, the app shows sessions for `process.cwd()` (same as current behavior)
2. **Directory browsing works**: `GET /api/directory` returns folder listings restricted to home directory
3. **Security enforced**: Path traversal attacks return 403; symlinks resolved before validation
4. **Picker UI functional**: User can navigate folders via breadcrumb + list, select a directory
5. **Session list updates**: Selecting a new directory shows sessions for that project (different transcript slug)
6. **New sessions use selected cwd**: Sessions created after directory change use the selected path as `cwd`
7. **Recent directories persist**: Last 10 directories stored in localStorage, shown in picker
8. **Hidden folders togglable**: Picker hides dotfiles by default, toggle reveals them
9. **Both transports work**: Feature works in standalone web mode and Obsidian plugin mode
10. **Backward compatible**: All API changes are additive (optional params with defaults)

---

## Non-Regression Requirements

- Existing sessions remain accessible (no data migration needed)
- Session creation without `cwd` param still works (falls back to server default)
- `GET /api/sessions` without `cwd` param still works (falls back to server default)
- All existing tests continue to pass without modification (new params are optional)
- OpenAPI spec reflects new endpoints and updated schemas

---

## Testing Strategy

### Server Tests

| Test | Covers |
|------|--------|
| Directory browsing: valid path | Happy path listing |
| Directory browsing: no path (defaults to home) | Default behavior |
| Directory browsing: path outside home | 403 security check |
| Directory browsing: non-existent path | 404 handling |
| Directory browsing: showHidden toggle | Hidden file filtering |
| Directory browsing: path traversal (`../../../etc`) | Security |
| Sessions GET with cwd param | Filtered session list |
| Sessions POST with cwd param | Session creation with cwd |
| AgentManager: per-session cwd | cwd isolation between sessions |
| TranscriptReader: stateless slug | Multiple directories work |

### Client Tests

| Test | Covers |
|------|--------|
| DirectoryPicker: renders folder list | Component rendering |
| DirectoryPicker: navigate into folder | Breadcrumb updates |
| DirectoryPicker: select directory | Calls setSelectedCwd |
| DirectoryPicker: cancel | Closes without change |
| DirectoryPicker: recent directories | Shows localStorage items |
| DirectoryPicker: show hidden toggle | Refetches with showHidden |
| SessionSidebar: picker button visible | Integration |
| useSessions: queries keyed by cwd | Re-fetch on cwd change |
