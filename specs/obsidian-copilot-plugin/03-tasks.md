---
slug: obsidian-copilot-plugin
last-decompose: 2026-02-07
---

# Obsidian Copilot Plugin - Task Breakdown

**Spec**: [02-specification.md](./02-specification.md)
**Total Tasks**: 13
**Phases**: 3

---

## Phase 1: Foundation (Plugin Shell + Shared Adapter)

---

### Task 1.1: Create Platform Adapter Interface and Web Default

**Objective**: Create `gateway/src/client/lib/platform.ts` with the `PlatformAdapter` interface and default web implementation.

**Dependencies**: None

**Implementation**:

Create the file `gateway/src/client/lib/platform.ts`:

```typescript
// gateway/src/client/lib/platform.ts

export interface PlatformAdapter {
  /** Base URL for API calls */
  apiBaseUrl: string;
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
  apiBaseUrl: '/api',
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

**Acceptance Criteria**:
- [ ] `PlatformAdapter` interface exported with all 5 members
- [ ] `getPlatform()` returns the web adapter by default
- [ ] `setPlatformAdapter()` replaces the current adapter
- [ ] Web adapter uses `/api` as `apiBaseUrl`
- [ ] Web adapter has `isEmbedded: false`
- [ ] Web adapter `getSessionId` reads from URL search params
- [ ] Web adapter `setSessionId` updates URL via `history.replaceState`
- [ ] Web adapter `openFile` is a no-op async function
- [ ] Existing standalone client is unaffected (no regressions)

---

### Task 1.2: Refactor API Client to Use Platform Adapter

**Objective**: Modify `gateway/src/client/lib/api.ts` to replace the hardcoded `BASE_URL` constant with dynamic resolution from `getPlatform().apiBaseUrl`.

**Dependencies**: Task 1.1

**Implementation**:

Modify `gateway/src/client/lib/api.ts`:

1. Remove the hardcoded `const BASE_URL = '/api';` line
2. Add import: `import { getPlatform } from './platform';`
3. Change `fetchJSON` to use dynamic base URL:

```typescript
import type {
  Session,
  CreateSessionRequest,
  CommandRegistry,
  HistoryMessage,
} from '@shared/types';
import { getPlatform } from './platform';

async function fetchJSON<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${getPlatform().apiBaseUrl}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(error.error || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Sessions
  createSession: (body: CreateSessionRequest) =>
    fetchJSON<Session>('/sessions', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  listSessions: () => fetchJSON<Session[]>('/sessions'),

  getSession: (id: string) => fetchJSON<Session>(`/sessions/${id}`),

  // Messages
  getMessages: (sessionId: string) =>
    fetchJSON<{ messages: HistoryMessage[] }>(`/sessions/${sessionId}/messages`),

  getMessageStreamUrl: (sessionId: string) =>
    `${getPlatform().apiBaseUrl}/sessions/${sessionId}/messages`,

  // Tool approval
  approveTool: (sessionId: string, toolCallId: string) =>
    fetchJSON<{ ok: boolean }>(`/sessions/${sessionId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ toolCallId }),
    }),

  denyTool: (sessionId: string, toolCallId: string) =>
    fetchJSON<{ ok: boolean }>(`/sessions/${sessionId}/deny`, {
      method: 'POST',
      body: JSON.stringify({ toolCallId }),
    }),

  // Commands
  getCommands: (refresh = false) =>
    fetchJSON<CommandRegistry>(`/commands${refresh ? '?refresh=true' : ''}`),

  // Health
  health: () => fetchJSON<{ status: string; version: string; uptime: number }>('/health'),
};
```

Key changes:
- `const BASE_URL = '/api'` removed
- `fetchJSON` now uses `getPlatform().apiBaseUrl` dynamically
- `getMessageStreamUrl` also uses `getPlatform().apiBaseUrl` instead of `BASE_URL`

**Acceptance Criteria**:
- [ ] No hardcoded `BASE_URL` constant
- [ ] All fetch calls resolve base URL via `getPlatform().apiBaseUrl`
- [ ] `getMessageStreamUrl` also uses dynamic base URL
- [ ] Standalone client still works (default adapter returns `/api`)
- [ ] Existing tests pass without modification (or with minimal mock updates)

---

### Task 1.3: Extend App Store with Session ID and Context Files

**Objective**: Add `sessionId`, `setSessionId`, `contextFiles`, `addContextFile`, `removeContextFile`, and `clearContextFiles` to the Zustand store.

**Dependencies**: None

**Implementation**:

Modify `gateway/src/client/stores/app-store.ts`:

```typescript
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface ContextFile {
  id: string;        // crypto.randomUUID()
  path: string;      // vault-relative path
  basename: string;  // file name without extension
}

interface AppState {
  // Existing
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;

  // New: session management (used when nuqs unavailable)
  sessionId: string | null;
  setSessionId: (id: string | null) => void;

  // New: context files for Obsidian
  contextFiles: ContextFile[];
  addContextFile: (file: Omit<ContextFile, 'id'>) => void;
  removeContextFile: (id: string) => void;
  clearContextFiles: () => void;
}

export const useAppStore = create<AppState>()(devtools((set) => ({
  sidebarOpen: true,

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  // Session management
  sessionId: null,
  setSessionId: (id) => set({ sessionId: id }),

  // Context files
  contextFiles: [],
  addContextFile: (file) =>
    set((s) => {
      // Prevent duplicates
      if (s.contextFiles.some((f) => f.path === file.path)) return s;
      return {
        contextFiles: [...s.contextFiles, { ...file, id: crypto.randomUUID() }],
      };
    }),
  removeContextFile: (id) =>
    set((s) => ({
      contextFiles: s.contextFiles.filter((f) => f.id !== id),
    })),
  clearContextFiles: () => set({ contextFiles: [] }),
}), { name: 'app-store' }));
```

Key changes from current file:
- Export `ContextFile` interface
- Add `sessionId: string | null` and `setSessionId`
- Add `contextFiles: ContextFile[]` with `addContextFile`, `removeContextFile`, `clearContextFiles`
- `addContextFile` includes duplicate prevention by path
- `addContextFile` auto-generates `id` via `crypto.randomUUID()`

**Acceptance Criteria**:
- [ ] `ContextFile` interface exported
- [ ] `sessionId` defaults to `null`
- [ ] `setSessionId` updates `sessionId`
- [ ] `contextFiles` defaults to `[]`
- [ ] `addContextFile` adds file with auto-generated UUID
- [ ] `addContextFile` prevents duplicates (same path)
- [ ] `removeContextFile` removes by id
- [ ] `clearContextFiles` resets to empty array
- [ ] Existing sidebar toggle tests still pass
- [ ] New tests verify all new state operations

---

### Task 1.4: Refactor useSessionId Hook for Dual Mode

**Objective**: Refactor `gateway/src/client/hooks/use-session-id.ts` to support both nuqs (standalone) and Zustand store (Obsidian embedded) modes.

**Dependencies**: Task 1.1, Task 1.3

**Implementation**:

Modify `gateway/src/client/hooks/use-session-id.ts`:

```typescript
// gateway/src/client/hooks/use-session-id.ts

import { getPlatform } from '../lib/platform';
import { useQueryState } from 'nuqs';
import { useAppStore } from '../stores/app-store';

export function useSessionId(): [string | null, (id: string | null) => void] {
  const platform = getPlatform();

  // In Obsidian: use Zustand store
  const storeId = useAppStore((s) => s.sessionId);
  const setStoreId = useAppStore((s) => s.setSessionId);

  // In standalone: use URL params
  const [urlId, setUrlId] = useQueryState('session');

  if (platform.isEmbedded) {
    return [storeId, setStoreId];
  }
  return [urlId, setUrlId];
}
```

Key changes:
- Import `getPlatform` from platform adapter
- Import `useAppStore` from store
- Both hooks (nuqs and zustand) are always called (React rules of hooks)
- Return value depends on `platform.isEmbedded`
- Return type is explicit: `[string | null, (id: string | null) => void]`

**Acceptance Criteria**:
- [ ] Hook always calls both `useQueryState` and `useAppStore` (React rules)
- [ ] When `isEmbedded` is false, returns nuqs-based state (standalone behavior)
- [ ] When `isEmbedded` is true, returns Zustand store state
- [ ] Return type matches `[string | null, (id: string | null) => void]`
- [ ] Standalone client continues to work (nuqs mode)
- [ ] Existing tests updated or new tests added for dual mode

---

### Task 1.5: Create Obsidian Plugin Entry Point, View, Context, and Adapter

**Objective**: Create the core Obsidian plugin files: plugin entry, CopilotView, ObsidianContext, and obsidian-adapter.

**Dependencies**: Task 1.1

**Implementation**:

Create 4 files:

**File 1: `gateway/src/plugin/main.ts`**

```typescript
import { Plugin } from 'obsidian';
import { CopilotView, VIEW_TYPE_COPILOT } from './views/CopilotView';

export default class CopilotPlugin extends Plugin {
  async onload() {
    this.registerView(
      VIEW_TYPE_COPILOT,
      (leaf) => new CopilotView(leaf, this)
    );

    this.addRibbonIcon('bot', 'Open Copilot', () => {
      this.activateView();
    });

    this.addCommand({
      id: 'open-copilot',
      name: 'Open Copilot',
      callback: () => this.activateView(),
    });
  }

  async activateView() {
    const { workspace } = this.app;
    workspace.detachLeavesOfType(VIEW_TYPE_COPILOT);
    const leaf = workspace.getRightLeaf(false);
    if (leaf) {
      await leaf.setViewState({ type: VIEW_TYPE_COPILOT, active: true });
      workspace.revealLeaf(leaf);
    }
  }

  onunload() {
    // Views auto-cleanup via Obsidian lifecycle
  }
}
```

**File 2: `gateway/src/plugin/views/CopilotView.tsx`**

```typescript
import { ItemView, WorkspaceLeaf } from 'obsidian';
import { createRoot, Root } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { setPlatformAdapter } from '../../client/lib/platform';
import { createObsidianAdapter } from '../lib/obsidian-adapter';
import { ObsidianProvider } from '../contexts/ObsidianContext';
import { ObsidianApp } from '../components/ObsidianApp';
import type CopilotPlugin from '../main';

export const VIEW_TYPE_COPILOT = 'lifeos-copilot-view';

export class CopilotView extends ItemView {
  root: Root | null = null;
  plugin: CopilotPlugin;
  queryClient: QueryClient;

  constructor(leaf: WorkspaceLeaf, plugin: CopilotPlugin) {
    super(leaf);
    this.plugin = plugin;
    this.queryClient = new QueryClient({
      defaultOptions: {
        queries: { staleTime: 30_000, retry: 1 },
      },
    });
  }

  getViewType(): string { return VIEW_TYPE_COPILOT; }
  getDisplayText(): string { return 'Copilot'; }
  getIcon(): string { return 'bot'; }

  async onOpen(): Promise<void> {
    // Set platform adapter before mounting
    setPlatformAdapter(createObsidianAdapter(this.app));

    const container = this.containerEl.children[1] as HTMLElement;
    container.empty();
    container.addClass('copilot-view-content');

    this.root = createRoot(container);
    this.root.render(
      <ObsidianProvider app={this.app}>
        <QueryClientProvider client={this.queryClient}>
          <ObsidianApp />
        </QueryClientProvider>
      </ObsidianProvider>
    );
  }

  async onClose(): Promise<void> {
    this.root?.unmount();
    this.root = null;
  }
}
```

**File 3: `gateway/src/plugin/contexts/ObsidianContext.tsx`**

```typescript
import { createContext, useContext, ReactNode } from 'react';
import { App } from 'obsidian';

interface ObsidianContextValue {
  app: App;
}

const ObsidianContext = createContext<ObsidianContextValue | null>(null);

export function ObsidianProvider({ app, children }: { app: App; children: ReactNode }) {
  return (
    <ObsidianContext.Provider value={{ app }}>
      {children}
    </ObsidianContext.Provider>
  );
}

export function useObsidian(): ObsidianContextValue {
  const ctx = useContext(ObsidianContext);
  if (!ctx) throw new Error('useObsidian must be used within ObsidianProvider');
  return ctx;
}
```

**File 4: `gateway/src/plugin/lib/obsidian-adapter.ts`**

```typescript
import { App, TFile } from 'obsidian';
import { PlatformAdapter } from '../../client/lib/platform';
import { useAppStore } from '../../client/stores/app-store';

export function createObsidianAdapter(app: App): PlatformAdapter {
  return {
    apiBaseUrl: 'http://localhost:6942/api',
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

**Acceptance Criteria**:
- [ ] `CopilotPlugin` registers view type `lifeos-copilot-view`
- [ ] Plugin adds ribbon icon with 'bot' icon
- [ ] Plugin registers `open-copilot` command
- [ ] `activateView` opens view in right sidebar
- [ ] `CopilotView` extends `ItemView` correctly
- [ ] `CopilotView.onOpen()` sets platform adapter before React mount
- [ ] `CopilotView.onOpen()` adds `copilot-view-content` class to container
- [ ] `CopilotView.onClose()` unmounts React root
- [ ] `ObsidianProvider` provides app via React context
- [ ] `useObsidian()` throws if used outside provider
- [ ] Obsidian adapter uses `http://localhost:6942/api` as base URL
- [ ] Obsidian adapter reads/writes sessionId from Zustand store
- [ ] Obsidian adapter `openFile` uses Obsidian's vault API

---

### Task 1.6: Create Obsidian Build Configuration and Manifest

**Objective**: Create `gateway/vite.config.obsidian.ts`, `gateway/manifest.json`, add CSS variable bridge to `index.css`, and add build scripts to `package.json`.

**Dependencies**: Task 1.1

**Implementation**:

**File 1: `gateway/vite.config.obsidian.ts`**

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/plugin/main.ts'),
      formats: ['cjs'],
      fileName: () => 'main.js',
    },
    rollupOptions: {
      external: [
        'obsidian',
        'electron',
        '@codemirror/autocomplete',
        '@codemirror/collab',
        '@codemirror/commands',
        '@codemirror/language',
        '@codemirror/lint',
        '@codemirror/search',
        '@codemirror/state',
        '@codemirror/view',
        '@lezer/common',
        '@lezer/highlight',
        '@lezer/lr',
      ],
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

**File 2: `gateway/manifest.json`**

```json
{
  "id": "lifeos-copilot",
  "name": "LifeOS Copilot",
  "version": "0.1.0",
  "minAppVersion": "1.5.0",
  "description": "AI copilot sidebar powered by LifeOS Gateway",
  "author": "LifeOS",
  "isDesktopOnly": true
}
```

**Modification 1: Add to `gateway/src/client/index.css`** (append at end of file):

```css
/* Obsidian theme bridge -- maps our CSS vars to Obsidian's */
.copilot-view-content {
  --background: var(--background-primary);
  --foreground: var(--text-normal);
  --card: var(--background-secondary);
  --card-foreground: var(--text-normal);
  --primary: var(--interactive-accent);
  --primary-foreground: var(--text-on-accent);
  --muted: var(--background-secondary);
  --muted-foreground: var(--text-muted);
  --accent: var(--interactive-accent);
  --accent-foreground: var(--text-on-accent);
  --destructive: oklch(0.577 0.245 27.325);
  --border: var(--background-modifier-border);
  --input: var(--background-modifier-form-field);
  --ring: var(--interactive-accent);
}
```

**Modification 2: Add to `gateway/package.json` scripts**:

```json
{
  "scripts": {
    "build:obsidian": "vite build --config vite.config.obsidian.ts",
    "dev:obsidian": "vite build --config vite.config.obsidian.ts --watch"
  }
}
```

**Modification 3: Add to `gateway/package.json` dependencies**:

```json
{
  "devDependencies": {
    "obsidian": "latest"
  }
}
```

**Acceptance Criteria**:
- [ ] `vite.config.obsidian.ts` builds CJS library from plugin entry
- [ ] `obsidian` and all `@codemirror`/`@lezer` packages are externalized
- [ ] Build output goes to `dist-obsidian/main.js`
- [ ] CSS is not code-split (single file)
- [ ] Inline source maps enabled
- [ ] Path aliases `@` and `@shared` match standalone config
- [ ] `manifest.json` has correct plugin ID and metadata
- [ ] `manifest.json` has `isDesktopOnly: true`
- [ ] CSS variable bridge maps all theme vars under `.copilot-view-content`
- [ ] `build:obsidian` and `dev:obsidian` scripts work
- [ ] `obsidian` package added as dev dependency
- [ ] `npm run build` (standalone) still works
- [ ] `npm run build:obsidian` produces `dist-obsidian/main.js`

---

### Task 1.7: Create ObsidianApp Wrapper Component (Minimal)

**Objective**: Create `gateway/src/plugin/components/ObsidianApp.tsx` as a minimal wrapper that renders the shared `<App />` component. Will be extended in Phase 2.

**Dependencies**: Task 1.5

**Implementation**:

Create `gateway/src/plugin/components/ObsidianApp.tsx`:

```typescript
import { App } from '../../client/App';

export function ObsidianApp() {
  return (
    <div className="flex flex-col h-full">
      <App />
    </div>
  );
}
```

This is intentionally minimal for Phase 1. Phase 2 will add ConnectionStatus, ContextBar, and file hooks.

**Acceptance Criteria**:
- [ ] Component renders shared `<App />` component
- [ ] Wrapped in a full-height flex container
- [ ] Chat works end-to-end when loaded in Obsidian
- [ ] No regressions in standalone client

---

## Phase 2: File Context

---

### Task 2.1: Create Active File and File Opener Hooks

**Objective**: Create hooks for tracking the active file in Obsidian and opening files via the platform adapter.

**Dependencies**: Task 1.5

**Implementation**:

**File 1: `gateway/src/plugin/hooks/use-active-file.ts`**

```typescript
import { useState, useEffect } from 'react';
import { TFile } from 'obsidian';
import { useObsidian } from '../contexts/ObsidianContext';

export interface ActiveFileInfo {
  path: string;
  basename: string;
  extension: string;
}

export function useActiveFile(): ActiveFileInfo | null {
  const { app } = useObsidian();
  const [activeFile, setActiveFile] = useState<ActiveFileInfo | null>(() => {
    const file = app.workspace.getActiveFile();
    return file ? { path: file.path, basename: file.basename, extension: file.extension } : null;
  });

  useEffect(() => {
    const handler = () => {
      const file = app.workspace.getActiveFile();
      setActiveFile(file ? { path: file.path, basename: file.basename, extension: file.extension } : null);
    };

    const ref = app.workspace.on('active-leaf-change', handler);
    return () => { app.workspace.offref(ref); };
  }, [app]);

  return activeFile;
}
```

**File 2: `gateway/src/plugin/hooks/use-file-opener.ts`**

```typescript
import { useCallback } from 'react';
import { getPlatform } from '../../client/lib/platform';

export function useFileOpener() {
  const openFile = useCallback(async (path: string) => {
    await getPlatform().openFile(path);
  }, []);

  return { openFile };
}
```

**Acceptance Criteria**:
- [ ] `useActiveFile` returns current active file info on initial render
- [ ] `useActiveFile` updates when `active-leaf-change` fires
- [ ] `useActiveFile` returns `null` when no file is active
- [ ] `useActiveFile` cleans up event listener on unmount
- [ ] `ActiveFileInfo` interface exported with `path`, `basename`, `extension`
- [ ] `useFileOpener` returns `openFile` callback
- [ ] `openFile` delegates to `getPlatform().openFile(path)`

---

### Task 2.2: Create ContextBar Component

**Objective**: Create the context bar with active file chip, dragged file chips, drag-and-drop zone, and file removal.

**Dependencies**: Task 1.3

**Implementation**:

Create `gateway/src/plugin/components/ContextBar.tsx`:

```typescript
import { useState } from 'react';
import { X, FileText } from 'lucide-react';
import { TFile } from 'obsidian';
import { useObsidian } from '../contexts/ObsidianContext';
import type { ActiveFileInfo } from '../hooks/use-active-file';
import type { ContextFile } from '../../client/stores/app-store';

interface ContextBarProps {
  activeFile: ActiveFileInfo | null;
  contextFiles: ContextFile[];
  onRemoveFile: (id: string) => void;
  onDrop: (path: string, basename: string) => void;
  onFileClick: (path: string) => void;
}

export function ContextBar({ activeFile, contextFiles, onRemoveFile, onDrop, onFileClick }: ContextBarProps) {
  const { app } = useObsidian();
  const [isDragOver, setIsDragOver] = useState(false);

  const hasContext = activeFile || contextFiles.length > 0;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const path = e.dataTransfer.getData('text/plain');
    if (!path) return;

    const file = app.vault.getAbstractFileByPath(path);
    if (file instanceof TFile) {
      onDrop(file.path, file.basename);
    }
  };

  return (
    <div
      className={`px-3 py-2 border-b transition-colors ${isDragOver ? 'bg-accent/50' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="flex flex-wrap gap-1.5">
        {/* Active file chip */}
        {activeFile && (
          <button
            onClick={() => onFileClick(activeFile.path)}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 transition-colors"
          >
            <FileText className="h-3 w-3" />
            <span className="max-w-[120px] truncate">{activeFile.basename}</span>
            <span className="text-[10px] opacity-60">(active)</span>
          </button>
        )}

        {/* Dropped file chips */}
        {contextFiles.map((file) => (
          <span
            key={file.id}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs bg-muted text-muted-foreground border"
          >
            <button
              onClick={() => onFileClick(file.path)}
              className="inline-flex items-center gap-1 hover:text-foreground transition-colors"
            >
              <FileText className="h-3 w-3" />
              <span className="max-w-[120px] truncate">{file.basename}</span>
            </button>
            <button
              onClick={() => onRemoveFile(file.id)}
              className="ml-0.5 hover:text-destructive transition-colors"
              aria-label={`Remove ${file.basename}`}
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
      </div>

      {/* Drop zone hint */}
      {!hasContext && (
        <p className="text-[10px] text-muted-foreground text-center py-1">
          Drop files here for context
        </p>
      )}
    </div>
  );
}
```

**Acceptance Criteria**:
- [ ] Active file displayed as chip with "(active)" badge
- [ ] Active file chip is non-removable (no X button)
- [ ] Clicking active file chip calls `onFileClick`
- [ ] Dropped file chips show with X remove button
- [ ] Clicking dropped file chip calls `onFileClick`
- [ ] Clicking X on dropped file calls `onRemoveFile`
- [ ] Drag over shows visual feedback (bg-accent)
- [ ] Drop event extracts path from `dataTransfer`, validates via vault API
- [ ] Drop zone hint shown when no context files present
- [ ] File names truncated at 120px

---

### Task 2.3: Wire Context Injection and Update ObsidianApp

**Objective**: Implement context injection on message send and update `ObsidianApp.tsx` to integrate all Phase 2 components.

**Dependencies**: Task 1.3, Task 1.5, Task 1.7, Task 2.1, Task 2.2

**Implementation**:

Update `gateway/src/plugin/components/ObsidianApp.tsx`:

```typescript
import { useCallback } from 'react';
import { TFile } from 'obsidian';
import { App } from '../../client/App';
import { useAppStore } from '../../client/stores/app-store';
import { useObsidian } from '../contexts/ObsidianContext';
import { useActiveFile } from '../hooks/use-active-file';
import { useFileOpener } from '../hooks/use-file-opener';
import { ContextBar } from './ContextBar';
import { ConnectionStatus } from './ConnectionStatus';

export function ObsidianApp() {
  const { app } = useObsidian();
  const activeFile = useActiveFile();
  const { contextFiles, addContextFile, removeContextFile } = useAppStore();
  const { openFile } = useFileOpener();

  return (
    <div className="flex flex-col h-full">
      <ConnectionStatus />
      <ContextBar
        activeFile={activeFile}
        contextFiles={contextFiles}
        onRemoveFile={removeContextFile}
        onDrop={(path, basename) => addContextFile({ path, basename })}
        onFileClick={openFile}
      />
      {/* Shared App component handles sessions + chat */}
      <App />
    </div>
  );
}
```

**Context Injection**: The context injection logic needs to be wired into the chat submit flow. This requires modifying how the chat input's submit works in the Obsidian context. The approach is:

1. In `ObsidianApp`, read context files' contents before sending
2. Prepend `<context file="path">content</context>` tags to the user message
3. This is done by intercepting the submit flow

The exact integration point depends on how `useChatSession` exposes the submit handler. The implementation should:

```typescript
// Context injection helper (used in the submit flow)
async function buildContextPrefix(
  app: App_Obsidian,
  activeFile: ActiveFileInfo | null,
  contextFiles: ContextFile[]
): Promise<string> {
  const contextParts: string[] = [];

  // Add active file
  if (activeFile) {
    const file = app.vault.getAbstractFileByPath(activeFile.path);
    if (file instanceof TFile) {
      const content = await app.vault.cachedRead(file);
      contextParts.push(`<context file="${activeFile.path}">\n${content}\n</context>`);
    }
  }

  // Add dropped context files
  for (const cf of contextFiles) {
    const file = app.vault.getAbstractFileByPath(cf.path);
    if (file instanceof TFile) {
      const content = await app.vault.cachedRead(file);
      contextParts.push(`<context file="${cf.path}">\n${content}\n</context>`);
    }
  }

  return contextParts.length > 0 ? contextParts.join('\n\n') + '\n\n' : '';
}
```

Note: The exact mechanism for intercepting the submit flow will need to be determined based on the `useChatSession` hook's API. Options include:
- A callback prop on `<App />` for message preprocessing
- A store-based message transform
- Wrapping the chat input component

**Acceptance Criteria**:
- [ ] `ObsidianApp` renders `ConnectionStatus` at top
- [ ] `ObsidianApp` renders `ContextBar` between status and chat
- [ ] `ObsidianApp` renders shared `<App />` for chat
- [ ] Active file tracking works (chip updates on tab switch)
- [ ] Drag-and-drop adds files to context
- [ ] File clicks open files in Obsidian
- [ ] Context files' contents are included when sending messages
- [ ] Context uses `<context file="path">` XML tags
- [ ] Files are read via `vault.cachedRead()` (from cache, not disk)

---

## Phase 3: Polish

---

### Task 3.1: Create ConnectionStatus Component

**Objective**: Create a connection status banner that shows when the gateway server is not reachable.

**Dependencies**: Task 2.3 (ObsidianApp references it)

Note: This can be done in parallel with Phase 2 tasks since ObsidianApp can import it even if it's created later, but the wiring in Task 2.3 references it.

**Implementation**:

Create `gateway/src/plugin/components/ConnectionStatus.tsx`:

```typescript
import { useState, useEffect } from 'react';

export function ConnectionStatus() {
  const [connected, setConnected] = useState<boolean | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch('http://localhost:6942/api/health');
        setConnected(res.ok);
      } catch {
        setConnected(false);
      }
    };
    check();
    const interval = setInterval(check, 30_000);
    return () => clearInterval(interval);
  }, []);

  if (connected === null) return null; // Loading
  if (connected) return null; // Connected, no indicator needed

  return (
    <div className="px-3 py-2 text-xs text-center border-b bg-destructive/10 text-destructive">
      Gateway not connected. Run the server on port 6942.
    </div>
  );
}
```

**Acceptance Criteria**:
- [ ] Shows nothing during initial loading (returns null)
- [ ] Shows nothing when connected (returns null)
- [ ] Shows red banner when disconnected
- [ ] Banner text: "Gateway not connected. Run the server on port 6942."
- [ ] Checks health every 30 seconds
- [ ] Cleans up interval on unmount
- [ ] Health check hits `http://localhost:6942/api/health`
- [ ] Banner auto-dismisses when server becomes available

---

### Task 3.2: Write Unit Tests

**Objective**: Write unit tests for platform adapter, store extensions, useSessionId dual mode, ContextBar, and ConnectionStatus.

**Dependencies**: All Phase 1 and Phase 2 tasks

**Implementation**:

**Test 1: Platform Adapter (`gateway/src/client/lib/__tests__/platform.test.ts`)**

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { getPlatform, setPlatformAdapter, PlatformAdapter } from '../platform';

describe('platform adapter', () => {
  beforeEach(() => {
    // Reset to default web adapter
    setPlatformAdapter({
      apiBaseUrl: '/api',
      isEmbedded: false,
      getSessionId: () => null,
      setSessionId: () => {},
      openFile: async () => {},
    });
  });

  it('returns web adapter by default', () => {
    const platform = getPlatform();
    expect(platform.apiBaseUrl).toBe('/api');
    expect(platform.isEmbedded).toBe(false);
  });

  it('setPlatformAdapter replaces the adapter', () => {
    const custom: PlatformAdapter = {
      apiBaseUrl: 'http://localhost:6942/api',
      isEmbedded: true,
      getSessionId: () => 'test-id',
      setSessionId: () => {},
      openFile: async () => {},
    };
    setPlatformAdapter(custom);
    expect(getPlatform().apiBaseUrl).toBe('http://localhost:6942/api');
    expect(getPlatform().isEmbedded).toBe(true);
    expect(getPlatform().getSessionId()).toBe('test-id');
  });
});
```

**Test 2: App Store Extensions (`gateway/src/client/stores/__tests__/app-store.test.ts`)**

Add to existing test file:

```typescript
it('sessionId defaults to null', async () => {
  const { useAppStore } = await import('../../stores/app-store');
  expect(useAppStore.getState().sessionId).toBeNull();
});

it('setSessionId updates sessionId', async () => {
  const { useAppStore } = await import('../../stores/app-store');
  useAppStore.getState().setSessionId('abc-123');
  expect(useAppStore.getState().sessionId).toBe('abc-123');

  useAppStore.getState().setSessionId(null);
  expect(useAppStore.getState().sessionId).toBeNull();
});

it('contextFiles defaults to empty array', async () => {
  const { useAppStore } = await import('../../stores/app-store');
  expect(useAppStore.getState().contextFiles).toEqual([]);
});

it('addContextFile adds file with generated id', async () => {
  const { useAppStore } = await import('../../stores/app-store');
  useAppStore.getState().addContextFile({ path: 'test.md', basename: 'test' });
  const files = useAppStore.getState().contextFiles;
  expect(files).toHaveLength(1);
  expect(files[0].path).toBe('test.md');
  expect(files[0].basename).toBe('test');
  expect(files[0].id).toBeTruthy();
});

it('addContextFile prevents duplicates by path', async () => {
  const { useAppStore } = await import('../../stores/app-store');
  useAppStore.getState().addContextFile({ path: 'test.md', basename: 'test' });
  useAppStore.getState().addContextFile({ path: 'test.md', basename: 'test' });
  expect(useAppStore.getState().contextFiles).toHaveLength(1);
});

it('removeContextFile removes by id', async () => {
  const { useAppStore } = await import('../../stores/app-store');
  useAppStore.getState().addContextFile({ path: 'a.md', basename: 'a' });
  useAppStore.getState().addContextFile({ path: 'b.md', basename: 'b' });
  const id = useAppStore.getState().contextFiles[0].id;
  useAppStore.getState().removeContextFile(id);
  expect(useAppStore.getState().contextFiles).toHaveLength(1);
  expect(useAppStore.getState().contextFiles[0].path).toBe('b.md');
});

it('clearContextFiles resets to empty', async () => {
  const { useAppStore } = await import('../../stores/app-store');
  useAppStore.getState().addContextFile({ path: 'a.md', basename: 'a' });
  useAppStore.getState().addContextFile({ path: 'b.md', basename: 'b' });
  useAppStore.getState().clearContextFiles();
  expect(useAppStore.getState().contextFiles).toEqual([]);
});
```

**Test 3: ConnectionStatus (`gateway/src/plugin/components/__tests__/ConnectionStatus.test.tsx`)**

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { ConnectionStatus } from '../ConnectionStatus';

describe('ConnectionStatus', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('shows nothing when connected', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: true } as Response);
    const { container } = render(<ConnectionStatus />);
    await waitFor(() => {
      expect(container.innerHTML).toBe('');
    });
  });

  it('shows banner when disconnected', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Network error'));
    render(<ConnectionStatus />);
    await waitFor(() => {
      expect(screen.getByText(/Gateway not connected/)).toBeTruthy();
    });
  });

  it('shows banner when health check returns non-ok', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: false } as Response);
    render(<ConnectionStatus />);
    await waitFor(() => {
      expect(screen.getByText(/Gateway not connected/)).toBeTruthy();
    });
  });
});
```

**Acceptance Criteria**:
- [ ] Platform adapter tests verify default, swap, and adapter properties
- [ ] Store tests verify sessionId, contextFiles CRUD, duplicate prevention
- [ ] ConnectionStatus tests verify connected/disconnected/error states
- [ ] All existing tests still pass
- [ ] `npm run test:run` passes with no failures

---

### Task 3.3: Documentation and Final Verification

**Objective**: Update gateway README with plugin build/install instructions and run the manual testing checklist.

**Dependencies**: All other tasks

**Implementation**:

Add the following section to `gateway/README.md`:

```markdown
## Obsidian Plugin

The gateway includes an Obsidian plugin that embeds the chat client as a copilot sidebar.

### Building

```bash
npm run build:obsidian
```

Output: `dist-obsidian/main.js`

### Installing

1. Build the plugin: `npm run build:obsidian`
2. Create the plugin folder: `mkdir -p <vault>/.obsidian/plugins/lifeos-copilot`
3. Copy files:
   - `dist-obsidian/main.js` -> `<vault>/.obsidian/plugins/lifeos-copilot/main.js`
   - `manifest.json` -> `<vault>/.obsidian/plugins/lifeos-copilot/manifest.json`
4. Enable the plugin in Obsidian Settings > Community Plugins

### Development

```bash
npm run dev:obsidian   # Watch mode, rebuilds on changes
```

### Requirements

- Gateway server running on port 6942 (`npm run dev:server`)
- Obsidian desktop app (mobile not supported)
```

**Manual Testing Checklist**:
- [ ] Plugin loads in Obsidian without errors
- [ ] Ribbon icon opens copilot in right sidebar
- [ ] Command palette "Open Copilot" works
- [ ] Chat sends messages and streams responses
- [ ] Active file chip appears and updates on tab switch
- [ ] Drag file from explorer -> chip appears
- [ ] Click chip -> file opens in editor
- [ ] Click X on chip -> chip removed
- [ ] Context included in sent messages
- [ ] Light and dark theme rendering
- [ ] Connection banner appears when server is down
- [ ] Standalone web client still works identically

**Acceptance Criteria**:
- [ ] README updated with Obsidian plugin section
- [ ] Build instructions are accurate and tested
- [ ] Install instructions are complete
- [ ] Development workflow documented
- [ ] All manual testing checklist items pass

---

## Dependency Graph

```
T1.1 (Platform Adapter) ── no deps
T1.2 (API Refactor) ── depends on T1.1
T1.3 (Store Extensions) ── no deps
T1.4 (useSessionId) ── depends on T1.1, T1.3
T1.5 (Plugin Core) ── depends on T1.1
T1.6 (Build Config) ── depends on T1.1
T1.7 (ObsidianApp Min) ── depends on T1.5

T2.1 (File Hooks) ── depends on T1.5
T2.2 (ContextBar) ── depends on T1.3
T2.3 (Context Injection) ── depends on T1.3, T1.5, T1.7, T2.1, T2.2

T3.1 (ConnectionStatus) ── no deps (standalone component)
T3.2 (Tests) ── depends on all P1+P2
T3.3 (Docs) ── depends on all tasks
```

## Parallel Execution Opportunities

- **Phase 1**: T1.1 and T1.3 can run in parallel (no dependencies on each other)
- **Phase 1**: T1.2, T1.5, T1.6 can run in parallel after T1.1
- **Phase 1**: T1.4 runs after both T1.1 and T1.3
- **Phase 2**: T2.1 and T2.2 can run in parallel
- **Phase 3**: T3.1 can run in parallel with Phase 2 tasks
- **Critical Path**: T1.1 -> T1.5 -> T1.7 -> T2.3 -> T3.2 -> T3.3
