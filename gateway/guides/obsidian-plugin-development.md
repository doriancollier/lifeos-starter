# Obsidian Plugin Development Guide

> Developer reference for building the LifeOS Gateway Obsidian plugin — embedding our React chat client as an Obsidian copilot sidebar.

---

## 1. Obsidian Plugin Fundamentals

### Plugin File Structure

Every Obsidian plugin consists of three files installed to `.obsidian/plugins/<plugin-id>/`:

```
my-plugin/
├── manifest.json   # Plugin metadata (required)
├── main.js         # Compiled JavaScript entry (required)
└── styles.css      # Plugin styles (optional)
```

### manifest.json

```json
{
  "id": "lifeos-copilot",
  "name": "LifeOS Copilot",
  "version": "0.1.0",
  "minAppVersion": "1.5.0",
  "description": "AI copilot sidebar powered by LifeOS Gateway",
  "author": "LifeOS",
  "authorUrl": "https://github.com/your-repo",
  "isDesktopOnly": true
}
```

Key fields:
- `id`: Unique identifier, must match the plugin folder name
- `minAppVersion`: Minimum Obsidian version required
- `isDesktopOnly`: Set `true` since we depend on localhost network access

### Plugin Lifecycle

```typescript
import { Plugin } from "obsidian";

export default class CopilotPlugin extends Plugin {
  async onload() {
    // Called when plugin is enabled
    // Register views, commands, event listeners, settings
  }

  async onunload() {
    // Called when plugin is disabled
    // Clean up resources, detach views
  }
}
```

---

## 2. Creating a Sidebar View (ItemView)

The plugin renders our React client inside an `ItemView` in Obsidian's right sidebar.

### ItemView Pattern

```typescript
import { ItemView, WorkspaceLeaf } from "obsidian";
import { createRoot, Root } from "react-dom/client";

export const VIEW_TYPE_COPILOT = "lifeos-copilot-view";

export class CopilotView extends ItemView {
  root: Root | null = null;

  constructor(leaf: WorkspaceLeaf) {
    super(leaf);
  }

  getViewType(): string {
    return VIEW_TYPE_COPILOT;
  }

  getDisplayText(): string {
    return "LifeOS Copilot";
  }

  getIcon(): string {
    return "bot"; // Lucide icon name
  }

  async onOpen(): Promise<void> {
    const container = this.containerEl.children[1];
    container.empty();
    container.addClass("copilot-view-content");

    // Mount React app
    this.root = createRoot(container as HTMLElement);
    this.root.render(
      <CopilotApp app={this.app} />
    );
  }

  async onClose(): Promise<void> {
    // CRITICAL: unmount React to prevent memory leaks
    this.root?.unmount();
    this.root = null;
  }
}
```

### Registering the View

```typescript
// In plugin onload()
this.registerView(
  VIEW_TYPE_COPILOT,
  (leaf) => new CopilotView(leaf)
);

// Add ribbon icon to open
this.addRibbonIcon("bot", "Open Copilot", () => {
  this.activateView();
});

// Add command palette entry
this.addCommand({
  id: "open-copilot",
  name: "Open Copilot",
  callback: () => this.activateView(),
});
```

### Opening the View

```typescript
async activateView() {
  const { workspace } = this.app;

  // Close existing instances
  workspace.detachLeavesOfType(VIEW_TYPE_COPILOT);

  // Create in right sidebar
  const leaf = workspace.getRightLeaf(false);
  if (leaf) {
    await leaf.setViewState({
      type: VIEW_TYPE_COPILOT,
      active: true,
    });
    workspace.revealLeaf(leaf);
  }
}
```

---

## 3. Mounting React in Obsidian

### Direct Mount (Recommended Approach)

We mount our React tree directly inside the ItemView container. This gives React components full access to the Obsidian API without iframe serialization overhead.

```typescript
// CopilotView.onOpen()
this.root = createRoot(container as HTMLElement);
this.root.render(
  <ObsidianProvider app={this.app}>
    <QueryClientProvider client={queryClient}>
      <CopilotApp />
    </QueryClientProvider>
  </ObsidianProvider>
);
```

### ObsidianContext Provider

Pass the Obsidian `App` instance through React Context so any component can access vault, workspace, etc.

```typescript
import { createContext, useContext, ReactNode } from "react";
import { App } from "obsidian";

interface ObsidianContextValue {
  app: App;
}

const ObsidianContext = createContext<ObsidianContextValue | null>(null);

export function ObsidianProvider({
  app,
  children,
}: {
  app: App;
  children: ReactNode;
}) {
  return (
    <ObsidianContext.Provider value={{ app }}>
      {children}
    </ObsidianContext.Provider>
  );
}

export function useObsidian(): ObsidianContextValue {
  const ctx = useContext(ObsidianContext);
  if (!ctx) {
    throw new Error("useObsidian must be used within ObsidianProvider");
  }
  return ctx;
}
```

### Why Not Iframe?

| Factor | Direct Mount | Iframe |
| --- | --- | --- |
| Obsidian API access | Direct (React Context) | Indirect (postMessage) |
| CSS isolation | Needs scoping | Full isolation |
| Drag-and-drop | Standard React handlers | Cross-boundary complexity |
| Performance | No serialization | postMessage overhead |
| Build complexity | One build (Vite library mode) | Two builds + message protocol |
| Code sharing | Import directly | Duplicate or postMessage bridge |

Direct mount wins for our use case because deep Obsidian integration (active file tracking, file opening, drag-drop) requires frequent API calls that would be painful through postMessage.

---

## 4. Tracking the Active File

### Listening for Active File Changes

Obsidian fires `active-leaf-change` when the user switches tabs/panes.

```typescript
// In plugin or view setup
this.registerEvent(
  this.app.workspace.on("active-leaf-change", (leaf) => {
    const file = this.app.workspace.getActiveFile();
    // file is TFile | null
    if (file) {
      console.log("Active file:", file.path, file.basename);
    }
  })
);
```

### React Hook for Active File

```typescript
import { useState, useEffect } from "react";
import { TFile } from "obsidian";
import { useObsidian } from "../contexts/ObsidianContext";

export function useActiveFile(): TFile | null {
  const { app } = useObsidian();
  const [activeFile, setActiveFile] = useState<TFile | null>(
    app.workspace.getActiveFile()
  );

  useEffect(() => {
    const handler = () => {
      setActiveFile(app.workspace.getActiveFile());
    };

    // Obsidian event registration
    const ref = app.workspace.on("active-leaf-change", handler);

    return () => {
      app.workspace.offref(ref);
    };
  }, [app]);

  return activeFile;
}
```

### Reading File Contents

```typescript
import { TFile } from "obsidian";

// Read full content
const content = await app.vault.read(file);

// Read cached content (faster, may be stale)
const cached = await app.vault.cachedRead(file);

// Get metadata (frontmatter, tags, etc.)
const metadata = app.metadataCache.getFileCache(file);
```

---

## 5. Opening Files in Obsidian

When the chat client references a file (e.g., in a tool call or response), we need to open it in Obsidian.

### Basic File Opening

```typescript
// Open by path
const file = app.vault.getAbstractFileByPath("path/to/note.md");
if (file instanceof TFile) {
  await app.workspace.getLeaf(false).openFile(file);
}

// Open by link text (handles aliases, headings)
await app.workspace.openLinkText("note-name", "", false);
```

### Open in New Pane vs Existing

```typescript
// false = reuse existing leaf, true = new split
const leaf = app.workspace.getLeaf(false);
await leaf.openFile(file);

// Open in a specific position
const leaf = app.workspace.getLeaf("split", "vertical");
await leaf.openFile(file);
```

### React Helper

```typescript
export function useFileOpener() {
  const { app } = useObsidian();

  const openFile = async (path: string) => {
    const file = app.vault.getAbstractFileByPath(path);
    if (file instanceof TFile) {
      const leaf = app.workspace.getLeaf(false);
      await leaf.openFile(file);
    }
  };

  return { openFile };
}
```

---

## 6. Drag-and-Drop from Obsidian

Obsidian's file explorer emits drag events with file paths in `text/plain` format in the DataTransfer object.

### Drop Zone Implementation

```typescript
interface ContextFile {
  path: string;
  basename: string;
  id: string;
}

function DropZone({ onFilesAdded }: { onFilesAdded: (files: ContextFile[]) => void }) {
  const { app } = useObsidian();
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    // Obsidian puts the file path in text/plain
    const path = e.dataTransfer.getData("text/plain");

    if (path) {
      const file = app.vault.getAbstractFileByPath(path);
      if (file instanceof TFile) {
        onFilesAdded([{
          path: file.path,
          basename: file.basename,
          id: crypto.randomUUID(),
        }]);
      }
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`drop-zone ${isDragOver ? "drag-over" : ""}`}
    >
      {/* children */}
    </div>
  );
}
```

### Key Details

- Obsidian's file explorer drag puts the vault-relative path in `e.dataTransfer.getData("text/plain")`
- Always call `e.preventDefault()` in both `dragOver` and `drop` handlers
- Use `getAbstractFileByPath()` to resolve the path to a `TFile` object
- Check `instanceof TFile` to exclude folders (`TFolder`)

---

## 7. Context Chips UI (Cursor-Style)

The context bar shows the active file and any drag-dropped files as dismissible chips above the chat input.

### Context State

```typescript
interface ContextState {
  activeFile: TFile | null;       // Auto-tracked, not dismissible
  contextFiles: ContextFile[];     // Manually added via drag-drop
  addContextFile: (file: ContextFile) => void;
  removeContextFile: (id: string) => void;
  clearContextFiles: () => void;
  getContextForMessage: () => string; // Serialize for API
}
```

### ContextChips Component

```typescript
function ContextChips({
  activeFile,
  contextFiles,
  onRemove,
}: {
  activeFile: TFile | null;
  contextFiles: ContextFile[];
  onRemove: (id: string) => void;
}) {
  const { openFile } = useFileOpener();

  return (
    <div className="context-chips">
      {/* Active file — auto-tracked, no remove button */}
      {activeFile && (
        <div className="chip chip-active" title={activeFile.path}>
          <span className="chip-icon">&#128196;</span>
          <button
            className="chip-label"
            onClick={() => openFile(activeFile.path)}
          >
            {activeFile.basename}
          </button>
          <span className="chip-badge">active</span>
        </div>
      )}

      {/* Dropped files — removable */}
      {contextFiles.map((cf) => (
        <div key={cf.id} className="chip" title={cf.path}>
          <span className="chip-icon">&#128196;</span>
          <button
            className="chip-label"
            onClick={() => openFile(cf.path)}
          >
            {cf.basename}
          </button>
          <button
            className="chip-remove"
            onClick={() => onRemove(cf.id)}
          >
            x
          </button>
        </div>
      ))}
    </div>
  );
}
```

### Cursor-Style Behavior

- The active file chip updates automatically as the user navigates
- Drag-dropped files persist until explicitly removed
- Clicking a chip name opens the file in Obsidian
- When sending a message, context files are included (path + content summary)
- After sending, context files could optionally auto-clear or persist (user preference)

---

## 8. Environment Detection

The client needs to know whether it's running standalone (browser) or embedded in Obsidian.

### Detection Strategy

```typescript
// Option A: Check for Obsidian's global app object
export function isObsidianEnvironment(): boolean {
  return typeof (window as any).app?.vault !== "undefined";
}

// Option B: Check for injected flag (set by plugin before mounting)
export function isObsidianEnvironment(): boolean {
  return !!(window as any).__LIFEOS_OBSIDIAN__;
}

// Option C: Check for Electron (Obsidian runs in Electron)
export function isElectronEnvironment(): boolean {
  return typeof (window as any).require === "function"
    && typeof process !== "undefined";
}
```

**Recommended: Option B** — The plugin sets a flag before mounting React. This is explicit, testable, and doesn't depend on Obsidian internals.

### Conditional Behavior Map

| Feature | Standalone (Browser) | Obsidian |
| --- | --- | --- |
| API base URL | `/api` (Vite proxy) | `http://localhost:6942/api` |
| Session ID storage | URL query param (nuqs) | Zustand store |
| Layout | Full viewport, responsive | Fixed sidebar width (~300px) |
| Active file context | N/A | Tracked via workspace events |
| File drag-drop | N/A | From Obsidian file explorer |
| Open file action | N/A | `workspace.openFile()` |
| Theme | CSS custom properties | Obsidian CSS variables |

### Platform Adapter Pattern

```typescript
interface PlatformAdapter {
  getApiBaseUrl(): string;
  getSessionId(): string | null;
  setSessionId(id: string): void;
  isEmbedded(): boolean;
}

// Standalone adapter
const webAdapter: PlatformAdapter = {
  getApiBaseUrl: () => "/api",
  getSessionId: () => new URLSearchParams(location.search).get("session"),
  setSessionId: (id) => { /* nuqs or pushState */ },
  isEmbedded: () => false,
};

// Obsidian adapter
const obsidianAdapter: PlatformAdapter = {
  getApiBaseUrl: () => "http://localhost:6942/api",
  getSessionId: () => store.getState().sessionId,
  setSessionId: (id) => store.setState({ sessionId: id }),
  isEmbedded: () => true,
};
```

---

## 9. Build Configuration

### Vite Config for Plugin Build

The plugin needs a separate Vite build that outputs a single `main.js` file (CJS format) with `obsidian` externalized.

```typescript
// vite.config.obsidian.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: path.resolve(__dirname, "src/plugin/main.ts"),
      formats: ["cjs"],
      fileName: () => "main.js",
    },
    rollupOptions: {
      external: [
        "obsidian",
        "electron",
        "@codemirror/autocomplete",
        "@codemirror/collab",
        "@codemirror/commands",
        "@codemirror/language",
        "@codemirror/lint",
        "@codemirror/search",
        "@codemirror/state",
        "@codemirror/view",
        "@lezer/common",
        "@lezer/highlight",
        "@lezer/lr",
      ],
    },
    outDir: "dist-obsidian",
    emptyOutDir: true,
    sourcemap: "inline",
    cssCodeSplit: false, // Inline CSS or single file
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src/client"),
      "@shared": path.resolve(__dirname, "src/shared"),
    },
  },
});
```

### Package Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "dev:obsidian": "vite build --watch --config vite.config.obsidian.ts",
    "build:obsidian": "vite build --config vite.config.obsidian.ts"
  }
}
```

### Development Workflow

1. Run `npm run dev:obsidian` for watch mode
2. Symlink `dist-obsidian/` to your test vault's `.obsidian/plugins/lifeos-copilot/`
3. Copy `manifest.json` to the plugin directory
4. Install the [Hot Reload plugin](https://github.com/pjeby/hot-reload) in your test vault
5. Create a `.hotreload` file in the plugin directory
6. Changes auto-rebuild and hot-reload in Obsidian

---

## 10. Styling Strategy

### The Problem

Obsidian has its own CSS that can conflict with Tailwind classes. The standalone client uses Tailwind CSS 4 extensively.

### Recommended Approach: CSS Variable Bridge

Map Tailwind's design tokens to Obsidian's CSS variables so the same components look native in both environments.

```css
/* When running in Obsidian, override CSS custom properties */
.copilot-view-content {
  --background: var(--background-primary);
  --foreground: var(--text-normal);
  --card: var(--background-secondary);
  --card-foreground: var(--text-normal);
  --primary: var(--interactive-accent);
  --primary-foreground: var(--text-on-accent);
  --muted: var(--text-muted);
  --border: var(--background-modifier-border);
  --input: var(--background-modifier-form-field);
  --ring: var(--interactive-accent);
}
```

This approach lets the existing components work because they already reference CSS custom properties (defined in `index.css`). We just re-map them to Obsidian's variables.

### Key Obsidian CSS Variables

| Variable | Purpose |
| --- | --- |
| `--background-primary` | Main background |
| `--background-secondary` | Sidebar background |
| `--text-normal` | Primary text |
| `--text-muted` | Secondary text |
| `--interactive-accent` | Accent color (links, buttons) |
| `--interactive-accent-hover` | Accent hover state |
| `--text-on-accent` | Text on accent backgrounds |
| `--background-modifier-border` | Borders |
| `--background-modifier-form-field` | Input backgrounds |

---

## 11. Data Flow: Context to Chat Messages

When the user sends a message, context files need to be included. Here's the recommended flow:

### Option A: Client-Side Prepend (Simple, No API Change)

Prepend context to the user's message before sending:

```typescript
function buildMessageWithContext(
  userMessage: string,
  activeFile: TFile | null,
  contextFiles: ContextFile[],
  vault: Vault,
): string {
  const parts: string[] = [];

  if (activeFile) {
    const content = await vault.cachedRead(activeFile);
    parts.push(`<context file="${activeFile.path}">\n${content}\n</context>`);
  }

  for (const cf of contextFiles) {
    const file = vault.getAbstractFileByPath(cf.path);
    if (file instanceof TFile) {
      const content = await vault.cachedRead(file);
      parts.push(`<context file="${cf.path}">\n${content}\n</context>`);
    }
  }

  if (parts.length > 0) {
    return parts.join("\n\n") + "\n\n" + userMessage;
  }
  return userMessage;
}
```

### Option B: Structured Context Field (Requires API Change)

Add a `context` field to the message API:

```typescript
POST /api/sessions/:id/messages
{
  "content": "What does this function do?",
  "context": [
    { "path": "src/utils.ts", "content": "..." },
    { "path": "src/types.ts", "content": "..." }
  ]
}
```

**Recommendation:** Start with Option A for speed. Migrate to Option B when the API evolves.

---

## 12. Obsidian API Quick Reference

### Vault Operations

```typescript
// List all markdown files
const files = app.vault.getMarkdownFiles();

// Get file by path
const file = app.vault.getAbstractFileByPath("path/to/file.md");

// Read content
const content = await app.vault.read(file as TFile);

// Get metadata cache
const cache = app.metadataCache.getFileCache(file as TFile);
// cache.frontmatter, cache.tags, cache.headings, cache.links
```

### Workspace Operations

```typescript
// Get active file
const file = app.workspace.getActiveFile();

// Listen for changes
const ref = app.workspace.on("active-leaf-change", callback);
app.workspace.offref(ref); // unsubscribe

// Open file
await app.workspace.getLeaf(false).openFile(file);

// Get right sidebar leaf
const leaf = app.workspace.getRightLeaf(false);
```

### Event Registration (Memory-Safe)

Always use `this.registerEvent()` in plugin/view classes — it auto-cleans on unload:

```typescript
// In Plugin or ItemView
this.registerEvent(
  this.app.workspace.on("active-leaf-change", () => { ... })
);

// Also for DOM events
this.registerDomEvent(document, "keydown", (e) => { ... });
```

---

## 13. Proposed Directory Structure

```
gateway/
├── src/
│   ├── client/                    # Shared React components
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   │   └── api.ts             # MODIFY: configurable baseUrl
│   │   ├── stores/
│   │   ├── App.tsx
│   │   ├── main.tsx               # Standalone entry point
│   │   └── index.css
│   ├── plugin/                    # NEW: Obsidian plugin code
│   │   ├── main.ts                # Plugin entry (onload/onunload)
│   │   ├── views/
│   │   │   └── CopilotView.tsx    # ItemView with React mount
│   │   ├── contexts/
│   │   │   └── ObsidianContext.tsx # Obsidian API provider
│   │   ├── hooks/
│   │   │   ├── use-active-file.ts
│   │   │   ├── use-file-opener.ts
│   │   │   └── use-obsidian-context.ts
│   │   ├── components/
│   │   │   ├── ContextBar.tsx     # Active file + context chips
│   │   │   └── ObsidianApp.tsx    # Obsidian-specific App wrapper
│   │   └── lib/
│   │       └── platform-adapter.ts
│   ├── server/
│   └── shared/
├── manifest.json                  # Obsidian plugin manifest
├── vite.config.ts                 # Standalone web build
├── vite.config.obsidian.ts        # Plugin build
└── package.json
```

---

## 14. Testing and Debugging

### Setup Test Vault

```bash
mkdir -p test-vault/.obsidian/plugins/lifeos-copilot
ln -s $(pwd)/dist-obsidian/main.js test-vault/.obsidian/plugins/lifeos-copilot/main.js
ln -s $(pwd)/dist-obsidian/styles.css test-vault/.obsidian/plugins/lifeos-copilot/styles.css
cp manifest.json test-vault/.obsidian/plugins/lifeos-copilot/
```

### DevTools

Open Obsidian DevTools: `Cmd+Shift+I` (macOS) or `Ctrl+Shift+I`

- **Console**: Plugin logs, React errors
- **Elements**: Inspect component DOM, verify CSS
- **Network**: Verify API calls to gateway server
- **React DevTools**: Install as browser extension, works in Electron

### Common Issues

| Issue | Solution |
| --- | --- |
| "Cannot find module 'obsidian'" | Add to `external` in Vite rollupOptions |
| Styles not applying | Verify `styles.css` is in plugin dir, check CSS variable names |
| React not re-rendering | Ensure Obsidian events update React state (not just local vars) |
| Drag-drop not firing | Call `preventDefault()` on both `dragOver` and `drop` |
| Memory leaks | Always `root.unmount()` in `onClose()`, use `registerEvent()` |
| Hot reload not working | Create `.hotreload` file in plugin dir, install hot-reload plugin |

---

## 15. Reference Links

- [Obsidian Developer Docs](https://docs.obsidian.md/Home)
- [Obsidian API (TypeScript Definitions)](https://github.com/obsidianmd/obsidian-api)
- [Obsidian Sample Plugin](https://github.com/obsidianmd/obsidian-sample-plugin)
- [React in Obsidian Plugins](https://docs.obsidian.md/Plugins/Getting+started/Use+React+in+your+plugin)
- [Obsidian Vite Template](https://github.com/unxok/obsidian-vite)
- [Obsidian React Starter](https://github.com/obsidian-community/obsidian-react-starter)
- [Marcus Olsson's Plugin Docs](https://marcusolsson.github.io/obsidian-plugin-docs/)
- [Hot Reload Plugin](https://github.com/pjeby/hot-reload)
