---
slug: obsidian-copilot-plugin
---

# Obsidian Copilot Plugin

**Slug:** obsidian-copilot-plugin
**Author:** Claude Code
**Date:** 2026-02-07
**Branch:** preflight/obsidian-copilot-plugin

---

## 1) Intent & Assumptions

**Task brief:** Create an Obsidian plugin that embeds the gateway web client (`gateway/src/client/`) as an AI copilot sidebar. The client must function standalone (via browser) or embedded inside Obsidian. When running in Obsidian, it should: track the active file as context, accept drag-and-drop files as additional context, display context files as chips (like Cursor), and open files in Obsidian on demand.

**Assumptions:**
- The gateway server (`localhost:6942`) will be running separately — the plugin does not bundle the server
- The Obsidian plugin targets desktop only (Electron environment gives us Node.js access)
- We will mount React directly in an ItemView (not use an iframe) for deep Obsidian integration
- The existing client components (ChatPanel, MessageList, etc.) will be shared between standalone and plugin builds
- The client already uses Zustand + TanStack Query — we'll extend these, not replace them
- Tailwind CSS will need adaptation to work within Obsidian's styling context

**Out of scope:**
- Obsidian Mobile support (iOS/Android)
- Publishing to Obsidian Community Plugins initially
- Bundling the gateway server inside the plugin
- Modifying the existing gateway server API

---

## 2) Pre-reading Log

### Gateway Client
- `gateway/src/client/main.tsx`: Entry point — React 19, QueryClientProvider, NuqsAdapter, StrictMode. Mounts to `#root`
- `gateway/src/client/App.tsx`: Root layout with animated sidebar (Motion), mobile/desktop responsive. Uses Zustand store + nuqs for session URL state
- `gateway/src/client/hooks/use-chat-session.ts`: Core chat logic — SSE streaming, text_delta/tool_call events, ref-based batching for performance
- `gateway/src/client/hooks/use-session-id.ts`: URL-based session persistence via nuqs `useQueryState('session')`
- `gateway/src/client/hooks/use-is-mobile.ts`: Media query hook (< 768px)
- `gateway/src/client/stores/app-store.ts`: Zustand with devtools — just `sidebarOpen` toggle
- `gateway/src/client/lib/api.ts`: REST client — sessions CRUD, messages (SSE), tool approval, commands
- `gateway/src/client/components/chat/ChatPanel.tsx`: Main chat view — history loading, streaming, command palette
- `gateway/src/client/components/chat/ChatInput.tsx`: Textarea with auto-grow, keyboard shortcuts, slash commands
- `gateway/src/client/components/chat/StreamingText.tsx`: Markdown via Streamdown + Shiki themes
- `gateway/src/client/components/sessions/SessionSidebar.tsx`: Session list with temporal grouping, new chat button
- `gateway/src/client/index.css`: Tailwind CSS 4 with CSS custom properties for theming
- `gateway/package.json`: Vite 6, React 19, TanStack Query 5, Zustand 5, Motion 12, Streamdown, nuqs
- `gateway/vite.config.ts`: Dev on port 3000, proxies `/api` to server on port 6942
- `gateway/src/shared/types.ts`: Shared types between client and server

---

## 3) Codebase Map

**Primary Components/Modules:**

| File | Role |
| --- | --- |
| `gateway/src/client/App.tsx` | Root layout, sidebar + main panel |
| `gateway/src/client/components/chat/ChatPanel.tsx` | Chat view with streaming |
| `gateway/src/client/components/chat/ChatInput.tsx` | Message input with slash commands |
| `gateway/src/client/components/chat/MessageList.tsx` | Scrollable message container |
| `gateway/src/client/components/chat/MessageItem.tsx` | Individual message rendering |
| `gateway/src/client/components/chat/StreamingText.tsx` | Markdown rendering |
| `gateway/src/client/components/chat/ToolCallCard.tsx` | Tool call display |
| `gateway/src/client/components/chat/ToolApproval.tsx` | Approve/deny tool calls |
| `gateway/src/client/components/sessions/SessionSidebar.tsx` | Session management |
| `gateway/src/client/components/commands/CommandPalette.tsx` | Slash command palette |

**Shared Dependencies:**

| Dependency | Usage |
| --- | --- |
| `zustand` | Client state (sidebar open/closed) |
| `@tanstack/react-query` | Server state (sessions, messages, commands) |
| `nuqs` | URL query param state (session ID) |
| `motion` | Animations (sidebar, messages) |
| `streamdown` | Markdown rendering in chat |
| `lucide-react` | Icons |

**Data Flow:**
```
User Input → ChatInput → useChatSession → POST /api/sessions/:id/messages
                                            → SSE stream (text_delta, tool_call_*, done)
                                            → ref-based accumulation → batch state update
                                            → MessageList → MessageItem → StreamingText
```

**Feature Flags/Config:**
- `permissionMode`: 'default' | 'dangerously-skip' (tool approval bypass)
- API base URL hardcoded as `/api` in `lib/api.ts`

**Potential Blast Radius:**
- `lib/api.ts` — needs configurable base URL
- `hooks/use-session-id.ts` — nuqs won't work in Obsidian (no URL bar), needs alternative
- `App.tsx` — layout needs to work in sidebar width (~300px)
- `index.css` — Tailwind may conflict with Obsidian styles
- `main.tsx` — new entry point needed for plugin mount

---

## 4) Root Cause Analysis

N/A — this is a new feature, not a bug fix.

---

## 5) Research

### Approach 1: Direct React Mounting in ItemView (Recommended)

Mount the React app directly into an Obsidian `ItemView` using `createRoot`. The plugin creates a view in the right sidebar, and React components have direct access to the Obsidian API via React Context.

**Pros:**
- Full access to Obsidian API (Vault, Workspace, etc.) from React components
- No serialization overhead — pass TFile objects directly
- Theme integration via CSS variables
- Best performance — no iframe boundary
- Hot reload works with community hot-reload plugin
- Can use Obsidian's built-in event system (`workspace.on()`)

**Cons:**
- Tailwind CSS may conflict with Obsidian styles — needs prefixing or scoping
- Build system needs to output CJS `main.js` for Obsidian (separate from Vite web build)
- React and dependencies are bundled into the plugin (increases size ~200KB)
- Must externalize `obsidian` module in build config

**Complexity:** Medium
**Maintenance:** Low

### Approach 2: Iframe Embedding

Embed the standalone client in an iframe inside the ItemView. Communication via `postMessage`.

**Pros:**
- Complete style isolation — no CSS conflicts
- Client code stays identical between standalone and embedded
- Can point at dev server during development for HMR
- Clear separation of concerns

**Cons:**
- Communication overhead — all data must be serialized through postMessage
- No direct access to Obsidian API from React components
- Drag-and-drop across iframe boundary is complex
- Security considerations with origin validation
- Two separate build processes to maintain
- Latency on every Obsidian → client interaction

**Complexity:** Medium-High
**Maintenance:** High

### Approach 3: Hybrid — Shared Package + Dual Entry Points

Extract core chat components into a shared package. Both the web app and Obsidian plugin import from it but have different entry points and platform adapters.

**Pros:**
- Maximum code reuse with proper boundaries
- Each platform gets exactly what it needs
- Clean architecture — platform adapters are explicit
- Testing is cleaner (shared components tested independently)

**Cons:**
- Requires restructuring into monorepo/packages
- More build configuration
- Higher upfront investment
- May be premature for current codebase size

**Complexity:** High
**Maintenance:** Medium

### Recommendation

**Approach 1 (Direct React Mounting)** for the initial implementation. The codebase is small enough (~20 client files) that sharing via import paths is sufficient — we don't need a full package extraction yet. The key architectural decision is:

1. Make `lib/api.ts` accept a configurable base URL
2. Create an `ObsidianContext` provider that wraps the app when running in Obsidian
3. Replace `useSessionId` (nuqs) with a Zustand-based alternative that works without URL state
4. Add a `useObsidianContext` hook for active file, drag-drop context
5. Build with Vite in library mode for the plugin output

### Environment Detection

The client detects its environment via:
```typescript
// Injected by the plugin when mounting React
const isObsidian = !!(window as any).__OBSIDIAN_COPILOT__;

// Or check for Obsidian's app object
const isObsidian = typeof (window as any).app?.vault !== 'undefined';
```

### Communication Architecture (Direct Mount)

```
Obsidian Plugin (main.ts)
  └── ItemView (CopilotView.ts)
       └── createRoot() → React Tree
            ├── ObsidianProvider (passes app, vault, workspace)
            ├── QueryClientProvider (TanStack Query)
            ├── App.tsx (shared layout)
            │   ├── ContextBar (active file + dropped files as chips)
            │   ├── ChatPanel (shared)
            │   └── SessionSidebar (shared)
            └── Event listeners
                 ├── workspace.on('active-leaf-change') → update context
                 ├── onDrop handler → add files to context
                 └── file-open requests → workspace.openLinkText()
```

---

## 6) Clarification

1. **Gateway server lifecycle**: Should the plugin attempt to start/stop the gateway server, or assume it's already running? Starting it would require spawning a Node process from Electron.

2. **Context injection into messages**: When sending a message with context files, should the file contents be prepended to the user's message (like Cursor does), or sent as a separate field in the API? This may require a server-side API change.

3. **Session persistence**: In standalone mode, sessions persist via URL params. In Obsidian, should sessions be per-vault, per-file, or manual (user creates/selects sessions)?

4. **Tailwind CSS strategy**: Should we (a) prefix all Tailwind classes to avoid Obsidian conflicts, (b) use Obsidian's CSS variables instead of Tailwind for the plugin build, or (c) scope Tailwind under a container class?

5. **Active file context depth**: Should we send just the file path, the file path + frontmatter, or the full file content as context? Full content could be large for some files.

6. **Build architecture**: Should the Obsidian plugin live in `gateway/obsidian-plugin/` as a sibling, or in a separate top-level directory like `obsidian-plugin/`?
