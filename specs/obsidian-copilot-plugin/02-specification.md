---
slug: obsidian-copilot-plugin
status: Draft
---

# Obsidian Copilot Plugin Specification

**Status:** Draft
**Authors:** Claude Code
**Date:** 2026-02-07
**Ideation:** [01-ideation.md](./01-ideation.md)

---

## 1. Overview

Build an Obsidian plugin that embeds the LifeOS Gateway chat client as a copilot sidebar. The React client already works as a standalone web app; this spec adds Obsidian as a second deployment target. The plugin mounts shared React components directly in an Obsidian `ItemView` (not iframe), gaining native access to the Obsidian API for file tracking, drag-and-drop, and navigation.

The key design principle is **shared core, platform adapters** — chat components remain identical between standalone and plugin builds, while platform-specific behavior (API base URL, session storage, file context) is handled by an adapter layer.

---

## 2. Background / Problem Statement

The LifeOS Gateway provides an AI chat interface via web browser. Users who work in Obsidian must switch between the browser and their vault to interact with Claude. This creates friction:

- No awareness of what file the user is currently editing
- No way to reference vault files as context for conversations
- Context switching between browser and Obsidian breaks flow
- No way for Claude's responses to trigger file navigation in Obsidian

An embedded copilot eliminates this friction by making the chat client a native sidebar in Obsidian with deep vault integration.

---

## 3. Goals

- Embed the existing chat client in Obsidian's right sidebar as a first-class view
- Track the active file and display it as context automatically
- Support drag-and-drop of files from Obsidian's file explorer into the chat as additional context
- Display context files as dismissible chips (Cursor-style) above the chat input
- Open files in Obsidian when referenced in chat responses
- Maintain the standalone web client with zero regressions
- Match Obsidian's theme (light/dark) automatically

---

## 4. Non-Goals

- Obsidian Mobile support (iOS/Android) — desktop only for now
- Publishing to Obsidian Community Plugins (manual install initially)
- Bundling the gateway server inside the plugin
- Server-side API changes for structured context
- Selected text context (future enhancement)
- Vault search or file browsing within the copilot

---

## 5. Technical Dependencies

| Dependency | Version | Purpose |
| --- | --- | --- |
| `obsidian` | latest | Plugin API (externalized at build time) |
| `react` | 19.x | UI framework (bundled in plugin) |
| `react-dom` | 19.x | React DOM rendering (bundled) |
| `zustand` | 5.x | Client state management (bundled) |
| `@tanstack/react-query` | 5.x | Server state + caching (bundled) |
| `motion` | 12.x | Animations (bundled) |
| `streamdown` | latest | Markdown rendering (bundled) |
| `lucide-react` | latest | Icons (bundled) |
| `vite` | 6.x | Build tool (dev dependency) |

The `obsidian` package is **externalized** — not bundled into `main.js`. Obsidian provides it at runtime. All other dependencies are bundled.

---

## 6. Detailed Design

### 6.1 Architecture Overview

```
gateway/
├── src/
│   ├── client/                     # Shared React components (unchanged)
│   │   ├── components/chat/        # ChatPanel, ChatInput, MessageList, etc.
│   │   ├── hooks/                  # useChatSession, useCommands, etc.
│   │   ├── lib/
│   │   │   ├── api.ts              # MODIFIED: configurable baseUrl
│   │   │   └── platform.ts         # NEW: platform detection + adapter
│   │   ├── stores/app-store.ts     # MODIFIED: add sessionId, contextFiles
│   │   ├── App.tsx                 # MODIFIED: accept platform context
│   │   ├── main.tsx                # Standalone entry (unchanged)
│   │   └── index.css               # MODIFIED: add Obsidian variable bridge
│   ├── plugin/                     # NEW: Obsidian plugin code
│   │   ├── main.ts                 # Plugin entry (onload/onunload)
│   │   ├── views/
│   │   │   └── CopilotView.tsx     # ItemView with React mount
│   │   ├── contexts/
│   │   │   └── ObsidianContext.tsx  # React Context for Obsidian API
│   │   ├── hooks/
│   │   │   ├── use-active-file.ts  # Track active file
│   │   │   └── use-file-opener.ts  # Open files in Obsidian
│   │   ├── components/
│   │   │   ├── ContextBar.tsx      # Context chips + drop zone
│   │   │   ├── ConnectionStatus.tsx # Gateway connection indicator
│   │   │   └── ObsidianApp.tsx     # Plugin-specific App wrapper
│   │   └── lib/
│   │       └── obsidian-adapter.ts # Obsidian platform adapter
│   ├── server/                     # Unchanged
│   └── shared/types.ts             # Unchanged
├── manifest.json                   # NEW: Obsidian plugin manifest
├── vite.config.ts                  # Standalone build (unchanged)
├── vite.config.obsidian.ts         # NEW: Plugin build config
└── package.json                    # MODIFIED: add obsidian dep + build scripts
```

### 6.2 Platform Adapter Pattern

A new `platform.ts` module provides environment-agnostic configuration. Components never import from `obsidian` directly — they use the adapter.

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

The Obsidian plugin sets the adapter before mounting React:

```typescript
// gateway/src/plugin/lib/obsidian-adapter.ts

import { App, TFile } from 'obsidian';
import { PlatformAdapter, setPlatformAdapter } from '../../client/lib/platform';

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

### 6.3 API Client Changes

The API client (`lib/api.ts`) currently hardcodes `/api`. Change to use the platform adapter:

```typescript
// Current:
const res = await fetch(`/api/sessions`, { ... });

// After:
import { getPlatform } from './platform';

const res = await fetch(`${getPlatform().apiBaseUrl}/sessions`, { ... });
```

This is applied to every `fetch` call in `api.ts`. The standalone build continues using `/api` (Vite proxy). The plugin build uses `http://localhost:6942/api` (direct).

### 6.4 Store Changes

Extend the Zustand store to hold session ID and context files:

```typescript
// gateway/src/client/stores/app-store.ts

interface ContextFile {
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
```

### 6.5 Session ID Hook Refactor

The current `use-session-id.ts` uses nuqs (URL query params). Refactor to support both modes:

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

### 6.6 Plugin Entry Point

```typescript
// gateway/src/plugin/main.ts

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

### 6.7 CopilotView (ItemView + React Mount)

```typescript
// gateway/src/plugin/views/CopilotView.tsx

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

### 6.8 ObsidianContext

```typescript
// gateway/src/plugin/contexts/ObsidianContext.tsx

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

### 6.9 Active File Hook

```typescript
// gateway/src/plugin/hooks/use-active-file.ts

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

### 6.10 ContextBar Component

The context bar sits above the chat input area, showing the active file and any drag-dropped files as chips.

```typescript
// gateway/src/plugin/components/ContextBar.tsx

interface ContextBarProps {
  activeFile: ActiveFileInfo | null;
  contextFiles: ContextFile[];
  onRemoveFile: (id: string) => void;
  onDrop: (path: string, basename: string) => void;
  onFileClick: (path: string) => void;
}
```

**Layout:**
```
┌──────────────────────────────────────┐
│ [📄 active-file.md (active)]        │
│ [📄 dropped-1.md ✕] [📄 dropped-2… │
│ ─ ─ ─ ─ Drop files here ─ ─ ─ ─ ─  │
└──────────────────────────────────────┘
```

**Drag-and-drop handler:**
```typescript
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
```

**Chip behavior:**
- Active file chip: non-removable, shows "(active)" badge, click opens file
- Dropped file chips: removable via X button, click opens file
- Duplicate prevention: if a file is already in context, don't add again
- Active file auto-updates when user switches tabs

### 6.11 Context Injection on Send

When the user sends a message, context files are read and prepended:

```typescript
// In ObsidianApp.tsx, wrap the handleSubmit from useChatSession

async function handleSubmitWithContext() {
  const { contextFiles } = useAppStore.getState();
  const activeFile = currentActiveFile; // from useActiveFile()

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

  // Prepend context to the current input
  if (contextParts.length > 0) {
    const prefix = contextParts.join('\n\n');
    // Temporarily set input to prefixed version, submit, restore
    const originalInput = input;
    setInput(prefix + '\n\n' + originalInput);
    handleSubmit();
  } else {
    handleSubmit();
  }
}
```

### 6.12 Connection Status

```typescript
// gateway/src/plugin/components/ConnectionStatus.tsx

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

### 6.13 ObsidianApp Wrapper

The plugin-specific App component that wraps shared components with Obsidian-specific features:

```typescript
// gateway/src/plugin/components/ObsidianApp.tsx

export function ObsidianApp() {
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

### 6.14 CSS Variable Bridge

Add to `index.css` (scoped under the plugin container class):

```css
/* Obsidian theme bridge — maps our CSS vars to Obsidian's */
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

The existing components already reference these CSS custom properties, so they will automatically pick up Obsidian's theme values.

### 6.15 Build Configuration

```typescript
// gateway/vite.config.obsidian.ts

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

### 6.16 Manifest

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

---

## 7. User Experience

### Opening the Copilot

1. Click the robot icon in Obsidian's left ribbon, OR
2. Open command palette (Cmd+P) and type "Open Copilot"
3. The copilot sidebar opens in the right pane

### Chat Interaction

- Identical to the standalone client: type messages, stream responses, approve/deny tool calls
- Slash commands work the same way (fetched from gateway server)
- Session management via sidebar: create new chats, switch between sessions

### File Context

- The currently active file appears as a chip labeled with the filename and an "(active)" badge
- The chip updates automatically when switching tabs
- Drag files from the Obsidian file explorer onto the context bar to add them
- Click any chip to open that file in Obsidian
- Click X on dropped files to remove them from context
- When a message is sent, all context files' contents are included

### Connection Status

- If the gateway server is not running, a red banner appears: "Gateway not connected. Run the server on port 6942."
- The banner auto-dismisses when the server becomes available (checked every 30 seconds)

---

## 8. Testing Strategy

### Unit Tests

**Platform adapter tests:**
- `platform.ts`: Verify `getPlatform()` returns correct adapter after `setPlatformAdapter()`
- `api.ts`: Verify fetch calls use configured base URL
- `use-session-id.ts`: Verify store-based mode when `isEmbedded` is true

**Component tests:**
- `ContextBar`: Renders active file chip, renders dropped file chips, handles drop events, handles remove clicks
- `ConnectionStatus`: Shows banner when health check fails, hides when connected

**Store tests:**
- `app-store.ts`: Test `addContextFile`, `removeContextFile`, `clearContextFiles`, `setSessionId`

### Integration Tests

**Context injection test:**
- Mock vault.cachedRead, simulate send with context files
- Verify the message content includes `<context>` tags with file contents

**Active file tracking test:**
- Mock workspace events, verify `useActiveFile` updates when `active-leaf-change` fires

### Manual Testing Checklist

- [ ] Plugin loads in Obsidian without errors
- [ ] Ribbon icon opens copilot in right sidebar
- [ ] Command palette "Open Copilot" works
- [ ] Chat sends messages and streams responses
- [ ] Active file chip appears and updates on tab switch
- [ ] Drag file from explorer → chip appears
- [ ] Click chip → file opens in editor
- [ ] Click X on chip → chip removed
- [ ] Context included in sent messages
- [ ] Light and dark theme rendering
- [ ] Connection banner appears when server is down
- [ ] Standalone web client still works identically

---

## 9. Performance Considerations

| Concern | Mitigation |
| --- | --- |
| Plugin bundle size (~200KB+ for React) | Acceptable for desktop; tree-shake unused code |
| File content reading on every send | Use `vault.cachedRead()` (reads from cache, not disk) |
| Active file event frequency | Event only fires on tab switch, not on typing |
| TanStack Query cache duplication | Plugin creates its own QueryClient instance |
| Animations in narrow sidebar | Motion respects `prefers-reduced-motion`; sidebar is always ~300px |
| Health check polling | 30-second interval, single lightweight GET |

---

## 10. Security Considerations

- **Localhost-only communication**: Plugin talks to `localhost:6942` — no external network calls
- **No credential storage**: No API keys or tokens in the plugin
- **File access scope**: Plugin reads files through Obsidian's Vault API (respects vault boundaries)
- **No eval or dynamic code execution**: All code is compiled at build time
- **CORS**: Gateway server already has CORS enabled for localhost origins

---

## 11. Documentation

| Document | Action |
| --- | --- |
| `gateway/guides/obsidian-plugin-development.md` | Already created — comprehensive developer reference |
| `gateway/README.md` | Update with Obsidian plugin build instructions |
| `manifest.json` | Inline documentation via descriptive fields |

---

## 12. Implementation Phases

### Phase 1: Foundation (Plugin Shell + Shared Adapter)

**Goal:** Plugin loads in Obsidian, renders the chat client, sends messages.

1. Create `gateway/src/client/lib/platform.ts` — platform adapter interface + web default
2. Refactor `gateway/src/client/lib/api.ts` — use `getPlatform().apiBaseUrl` for all fetch calls
3. Extend `gateway/src/client/stores/app-store.ts` — add `sessionId`, `setSessionId`
4. Refactor `gateway/src/client/hooks/use-session-id.ts` — dual mode (nuqs vs store)
5. Create `gateway/src/plugin/main.ts` — plugin entry
6. Create `gateway/src/plugin/views/CopilotView.tsx` — ItemView + React mount
7. Create `gateway/src/plugin/contexts/ObsidianContext.tsx`
8. Create `gateway/src/plugin/lib/obsidian-adapter.ts`
9. Create `gateway/src/plugin/components/ObsidianApp.tsx` — minimal wrapper
10. Create `gateway/vite.config.obsidian.ts`
11. Create `gateway/manifest.json`
12. Add CSS variable bridge to `gateway/src/client/index.css`
13. Add build scripts to `package.json`

**Verification:** Plugin opens in Obsidian sidebar, chat works, theme matches.

### Phase 2: File Context

**Goal:** Active file tracking, drag-drop, context chips, context injection.

1. Create `gateway/src/plugin/hooks/use-active-file.ts`
2. Create `gateway/src/plugin/hooks/use-file-opener.ts`
3. Extend `app-store.ts` — add `contextFiles`, `addContextFile`, `removeContextFile`, `clearContextFiles`
4. Create `gateway/src/plugin/components/ContextBar.tsx` — chips + drop zone
5. Wire context injection into message sending (prepend `<context>` tags)
6. Update `ObsidianApp.tsx` — integrate ContextBar + file opener

**Verification:** Active file chip appears/updates, drag-drop works, context included in messages.

### Phase 3: Polish

**Goal:** Connection status, error handling, layout refinement.

1. Create `gateway/src/plugin/components/ConnectionStatus.tsx`
2. Add gateway health polling
3. Layout adjustments for sidebar width
4. Test light/dark theme in Obsidian
5. Write unit tests for platform adapter, store extensions, context injection
6. Update `gateway/README.md` with plugin build/install instructions

**Verification:** Full manual testing checklist passes.

---

## 13. Open Questions

*All questions were resolved during ideation. See `01-ideation.md` Section 6 for decisions.*

---

## 14. References

- [Obsidian Developer Docs](https://docs.obsidian.md/Home)
- [Obsidian API (TypeScript Definitions)](https://github.com/obsidianmd/obsidian-api)
- [React in Obsidian Plugins](https://docs.obsidian.md/Plugins/Getting+started/Use+React+in+your+plugin)
- [Obsidian Sample Plugin](https://github.com/obsidianmd/obsidian-sample-plugin)
- [Obsidian Vite Template](https://github.com/unxok/obsidian-vite)
- [Ideation Document](./01-ideation.md)
- [Developer Guide](../../gateway/guides/obsidian-plugin-development.md)
