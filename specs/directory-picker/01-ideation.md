---
slug: directory-picker
---

# Directory Picker for Claude Code Working Directory

**Slug:** directory-picker
**Author:** Claude Code
**Date:** 2026-02-09
**Branch:** preflight/obsidian-copilot-plugin

---

## 1) Intent & Assumptions

**Task brief:** Add a feature that allows the user to select which folder Claude Code runs in. The selected directory acts as a **global project context** -- it determines which sessions are shown in the sidebar and where new sessions are created. This is a "project switcher" pattern, not a per-session setting.

**Core behavior:**
1. **Default directory** is the directory the Node process is running in (`process.cwd()`)
2. Users can **change the directory** via a folder selector component in the UI
3. The **session list shows sessions for the selected directory** (SDK stores transcripts per-project)
4. **New sessions are started in the selected directory** (passed as `cwd` to SDK `query()`)

**Assumptions:**
- The selected directory is global app state (not per-session)
- Changing the directory refreshes the entire session list (different project = different JSONL files)
- The SDK derives the transcripts directory from `cwd` via a path slug: `~/.claude/projects/{slug}/`
- The feature works in both standalone web mode (HttpTransport) and Obsidian plugin mode (DirectTransport)
- Only directories are shown in the picker (not files)

**Out of scope:**
- File browsing/editing/viewing
- Per-session cwd overrides (all sessions in a view share the same project directory)
- Drag-and-drop file upload
- Project scaffolding or template selection
- Git repository detection or special handling
- Remote filesystem browsing

---

## 2) Pre-reading Log

- `gateway/src/server/services/agent-manager.ts`: AgentManager accepts `cwd` in constructor, passes to SDK `query()` as `sdkOptions.cwd`. Currently set once at startup. The constructor default is `path.resolve(__dirname, '../../../../')` (repo root).
- `gateway/src/server/routes/sessions.ts`: GET `/api/sessions` calls `transcriptReader.listSessions(vaultRoot)` where `vaultRoot` is hardcoded to `path.resolve(__dirname, '../../../../')`. This needs to become dynamic based on selected directory.
- `gateway/src/server/services/transcript-reader.ts`: **Critical** -- `getProjectSlug()` converts a path to a slug (`/foo/bar` → `-foo-bar`), then looks up transcripts at `~/.claude/projects/{slug}/`. Currently caches a single `projectSlug`. Must support multiple directories.
- `gateway/src/shared/schemas.ts`: Zod schemas with OpenAPI metadata. `SessionSchema` already has `cwd?: string` field.
- `gateway/src/shared/transport.ts`: Transport interface with 9 methods. `getSessions()` currently takes no directory parameter.
- `gateway/src/client/lib/http-transport.ts`: HTTP adapter implementing Transport.
- `gateway/src/client/lib/direct-transport.ts`: In-process adapter for Obsidian.
- `gateway/src/client/components/status/CwdItem.tsx`: Display-only component showing current folder name. Currently not interactive.
- `gateway/src/client/components/sessions/SessionSidebar.tsx`: Session list + new chat button. Session fetching doesn't parameterize by directory.
- `gateway/src/client/hooks/use-session-status.ts`: Manages session status state including `cwd`.
- `gateway/src/server/services/openapi-registry.ts`: Auto-generates OpenAPI spec from Zod schemas.
- `gateway/src/server/app.ts`: Express app setup, mounts route groups.
- `gateway/src/plugin/views/CopilotView.tsx`: Obsidian plugin view. Computes `repoRoot = path.resolve(vaultPath, '..')` and passes to AgentManager.

---

## 3) Codebase Map

**Primary components/modules:**

| File | Role |
|------|------|
| `src/server/services/agent-manager.ts` | SDK session management; passes `cwd` to `query()` |
| `src/server/services/transcript-reader.ts` | Reads JSONL transcripts; derives project slug from cwd |
| `src/server/routes/sessions.ts` | Session CRUD endpoints; hardcodes `vaultRoot` |
| `src/shared/schemas.ts` | Zod schemas (source of truth for types) |
| `src/shared/transport.ts` | Transport interface (client-server abstraction) |
| `src/client/components/sessions/SessionSidebar.tsx` | Session list + creation |
| `src/client/components/status/CwdItem.tsx` | Displays current cwd |
| `src/client/hooks/use-sessions.ts` | TanStack Query hooks for session data |

**Shared dependencies:**
- TanStack Query (data fetching/caching)
- Zustand (UI state)
- Lucide React (icons)
- `cn()` utility (Tailwind class merging)
- shadcn/ui (only dropdown-menu installed; breadcrumb available to install)

**Data flow (current):**
```
Server startup → AgentManager(vaultRoot) stores global cwd
  → GET /api/sessions → transcriptReader.listSessions(vaultRoot)
    → getProjectSlug(vaultRoot) → derives slug → scans ~/.claude/projects/{slug}/
    → Returns sessions for THAT project only
  → POST /api/sessions/:id/messages → sdkOptions.cwd = this.cwd (hardcoded)
  → SDK writes JSONL to ~/.claude/projects/{slug}/
```

**Data flow (proposed):**
```
App loads → default cwd = process.cwd() (or server-reported default)
  → Client stores selectedCwd in global state (Zustand or URL param)
  → GET /api/sessions?cwd=/selected/path → transcriptReader.listSessions(selectedCwd)
    → getProjectSlug(selectedCwd) → derives NEW slug → scans DIFFERENT transcript dir
    → Returns sessions for SELECTED project
  → User opens DirectoryPicker, selects new folder
    → selectedCwd updates → session list query re-fetches with new cwd
    → Sidebar shows different sessions
  → POST /api/sessions { cwd: selectedCwd }
    → AgentManager uses selectedCwd for this session's SDK query()
  → POST /api/sessions/:id/messages → sdkOptions.cwd = selectedCwd
```

**Key insight:** The SDK's transcript storage is keyed by project slug (derived from cwd). Changing the selected directory inherently shows a different set of sessions because it points to a different `~/.claude/projects/{slug}/` directory.

**Potential blast radius:**
- Direct: 10-12 files modified/created
- Indirect: Tests for sessions, agent-manager, transcript-reader, sidebar
- Breaking change: `GET /api/sessions` and `POST /api/sessions` gain a `cwd` parameter (backward compatible -- defaults to server's process.cwd())

---

## 4) Root Cause Analysis

N/A (not a bug fix)

---

## 5) Research

### Potential Solutions for the Picker UI

**1. Breadcrumb + Flat List (Build from scratch)**
- Description: Modal with breadcrumb path bar, scrollable folder list, select button. Built with existing tools.
- Pros:
  - Zero new dependencies
  - Matches existing neutral gray palette and patterns
  - Simple UX for "select a folder" task
  - shadcn/ui has a Breadcrumb component ready to install
  - TanStack Query + `cn()` + Lucide already available
- Cons:
  - More initial code to write (~200-300 lines)
  - No tree overview of sibling folders
- Complexity: Low-Medium
- Maintenance: Low (no external deps)

**2. shadcn Community Tree View (neigebaie/shadcn-ui-tree-view)**
- Description: Community shadcn tree component with lazy loading, multi-select, search.
- Pros:
  - Full tree view with expand/collapse
  - Native shadcn/Tailwind integration
- Cons:
  - Overkill for folder selection
  - Community dependency
- Complexity: Low
- Maintenance: Medium

**3. Headless Tree (headless-tree)**
- Description: 10kB headless tree library, bring-your-own rendering.
- Pros: Tiny bundle, maximum flexibility, actively maintained
- Cons: More work to build UI layer, another dependency
- Complexity: Medium
- Maintenance: Medium

### API Design

**Directory browsing endpoint:**
```
GET /api/directory?path=/some/path&showHidden=false
```

Response:
```json
{
  "path": "/Users/name/projects",
  "entries": [
    { "name": "my-app", "path": "/Users/name/projects/my-app", "isDirectory": true },
    { "name": "other-project", "path": "/Users/name/projects/other-project", "isDirectory": true }
  ],
  "parent": "/Users/name"
}
```

**Session listing with cwd:**
```
GET /api/sessions?cwd=/selected/path
```

The server derives the project slug from the provided `cwd` and scans the corresponding transcript directory.

### Security Considerations
- **Path traversal**: Must canonicalize with `fs.realpath()` before validation
- **Symlinks**: Resolve with `fs.realpath()` to prevent TOCTOU attacks
- **Null bytes**: Reject paths containing `\0`
- **Access control**: Consider restricting to home directory or configurable allowed roots
- **URL decoding**: Always `decodeURIComponent()` before path resolution

### Performance Considerations
- Use `fs.readdir()` with `withFileTypes: true` (avoids extra `stat()` calls)
- Lazy load (depth-1 only per request)
- TanStack Query caching with 30-second stale time
- `keepPreviousData: true` for smooth navigation between folders
- TranscriptReader's `metaCache` is keyed by sessionId -- works across directories since session IDs are globally unique

### Recommendation

**Approach 1: Breadcrumb + Flat List** is recommended because:
- The use case is narrow (select a folder, not manage files)
- Only one shadcn component is currently installed; the project favors minimal dependencies
- shadcn/ui has an official Breadcrumb component that can be installed
- All other building blocks exist (TanStack Query, Lucide, cn(), react-virtual)
- The API is simple: one `GET /api/directory` endpoint with Zod validation

### Electron/Obsidian Consideration

In the Obsidian plugin (Electron), we could additionally offer a "Use System Picker" button that invokes Electron's `dialog.showOpenDialog({ properties: ['openDirectory'] })`. This provides native OS folder selection. The web-based breadcrumb picker would still be the fallback. This is a nice-to-have enhancement, not required for the initial implementation.

---

## 6) Clarification

1. **Restrict browsable paths**: Should we restrict directory browsing to the home directory tree, or allow browsing anywhere on the filesystem? (Security vs. flexibility trade-off)

2. **Recent directories**: Should we track recently-used directories for quick selection? If so, where to persist this (localStorage, server-side)?

3. **Show hidden folders**: Should the picker show hidden folders (dotfiles) by default, or have a toggle? Default to hidden seems right for most users.

4. **Picker placement**: Should the directory picker be triggered from the CwdItem in the status bar, from a dedicated button in the sidebar header, or both?

5. **TranscriptReader caching**: The current `TranscriptReader` caches a single `projectSlug`. When switching directories, should we invalidate the slug cache, or support multiple cached slugs? (Multiple is more efficient if users switch back and forth.)

---

## Appendix: Key Implementation Details

### TranscriptReader Changes

The `TranscriptReader` currently caches a single `projectSlug` (line 41). The `getProjectSlug()` method must become stateless (no caching of a single slug) or support multiple slugs, since different API calls may request sessions for different directories.

The `metaCache` (Map of sessionId -> metadata) works fine across directories since session IDs are UUIDs and globally unique.

### AgentManager Changes

`AgentManager` currently stores `cwd` as a constructor-level property used for all sessions. With this feature:
- The constructor default (`process.cwd()` equivalent) remains the fallback
- Each session's `AgentSession` stores its own `cwd` (from `POST /api/sessions { cwd }`)
- `sendMessage()` uses `session.cwd ?? this.cwd` when building `sdkOptions`

### Session List Query Key

The TanStack Query key for sessions must include the selected `cwd` so that changing directories triggers a re-fetch:
```typescript
useQuery({ queryKey: ['sessions', selectedCwd], queryFn: ... })
```

### Global State for Selected Directory

The selected directory lives in Zustand store (or URL search param) so it's accessible from:
- SessionSidebar (to pass cwd when fetching sessions and creating new ones)
- StatusLine/CwdItem (to display current project and trigger the picker)
- Any future component that needs the active project context
