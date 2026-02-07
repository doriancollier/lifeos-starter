---
slug: gateway-command-palette-keyboard-nav
---

# Command Palette Keyboard Navigation

**Slug:** gateway-command-palette-keyboard-nav
**Author:** Claude Code
**Date:** 2026-02-07
**Branch:** preflight/gateway-command-palette-keyboard-nav

---

## 1) Intent & Assumptions

- **Task brief:** Enhance the gateway's slash command autocomplete with full keyboard navigation: Tab completion, arrow up/down to navigate suggestions, Enter to select, plus any other standard interactions. Keep all existing features (type-to-filter, click-to-select, Escape to dismiss). Evaluate cmdk, shadcn components, or custom solutions.
- **Assumptions:**
  - The existing cmdk-based filtering and grouping should be preserved
  - Focus must stay in the textarea (users are typing a chat message)
  - No server-side changes needed (command registry API is already working)
  - The solution should be accessible (WAI-ARIA combobox pattern)
- **Out of scope:**
  - New slash commands or server-side command registry changes
  - Mobile gesture support
  - Multiple trigger characters (@mentions, #channels, etc.)
  - Caret-relative positioning of the palette (currently anchored to input container)

---

## 2) Pre-reading Log

- `gateway/src/client/components/commands/CommandPalette.tsx`: Uses raw cmdk (not shadcn wrapper). Command.Input is hidden (`sr-only`, `autoFocus={false}`), so it never receives keyboard focus. Items use `data-[selected=true]:bg-accent` for visual highlighting via cmdk's internal state.
- `gateway/src/client/components/chat/ChatInput.tsx`: Only handles Escape (close palette) and Enter+!Shift (submit message). No arrow key or Tab handling. Textarea auto-resizes on content change.
- `gateway/src/client/components/chat/ChatPanel.tsx`: Orchestrates command detection via regex `/(^|\s)\/(\w*)$/`. Manages `showCommands` and `commandQuery` state. Passes `onSelect` and `onClose` callbacks to CommandPalette.
- `gateway/src/client/hooks/use-commands.ts`: TanStack Query hook with 5-min stale time, fetches from `/api/commands`.
- `gateway/src/shared/types.ts`: `CommandEntry` has namespace, command, fullCommand, description, argumentHint, allowedTools, filePath. `CommandRegistry` wraps array + lastScanned timestamp.
- `gateway/package.json`: cmdk ^1.0.0, React 19, TanStack Query 5, Zustand 5, Tailwind CSS 4. No shadcn/ui components installed (components.json configured but no `src/client/components/ui/` directory).
- `gateway/src/client/components/chat/__tests__/ChatInput.test.tsx`: Tests Enter and Escape key handling. No arrow key or Tab tests.
- `gateway/src/client/components/commands/__tests__/CommandPalette.test.tsx`: Tests rendering, grouping, and descriptions. No keyboard navigation tests.

---

## 3) Codebase Map

**Primary components/modules:**

| File | Role |
|------|------|
| `src/client/components/chat/ChatPanel.tsx` | Orchestrator: slash detection, state management, event routing |
| `src/client/components/chat/ChatInput.tsx` | Textarea with keydown handler (Enter, Escape only) |
| `src/client/components/commands/CommandPalette.tsx` | cmdk-based dropdown: filtering, grouping, rendering |
| `src/client/hooks/use-commands.ts` | TanStack Query hook for command registry |

**Shared dependencies:**

| Dependency | Version | Role |
|------------|---------|------|
| cmdk | ^1.0.0 | Filtering, grouping, rendering command items |
| @tanstack/react-query | ^5.62.0 | Command data fetching/caching |
| tailwindcss | ^4.0.0 | Styling |
| lucide-react | latest | Icons (Send, Square) |

**Data flow:**
```
User types "/" in textarea
  -> ChatInput.onChange fires
  -> ChatPanel.handleInputChange matches regex
  -> setShowCommands(true), setCommandQuery(text after "/")
  -> CommandPalette renders with query prop
  -> cmdk filters items against "fullCommand + description"
  -> User sees filtered, grouped command list
  -> User clicks item -> onSelect fires -> setInput(fullCommand + " ")
```

**Current keyboard event flow:**
```
Textarea onKeyDown
  -> Escape: calls onEscape() -> ChatPanel closes palette
  -> Enter (no Shift): preventDefault, calls onSubmit() -> sends message
  -> ArrowUp/Down: NOT handled -> default textarea cursor movement
  -> Tab: NOT handled -> browser moves focus away from textarea
```

**Root cause of broken keyboard nav:**
- Textarea captures all keyboard events
- cmdk's `Command.Input` is `sr-only` and `autoFocus={false}` -- never receives focus
- cmdk's built-in arrow/Enter handlers require focus on Command.Input to work
- No event forwarding exists between textarea and cmdk

**Potential blast radius:**

| Impact | Files |
|--------|-------|
| Must change | `ChatInput.tsx`, `ChatPanel.tsx`, `CommandPalette.tsx` |
| Must add tests | `ChatInput.test.tsx`, `CommandPalette.test.tsx` |
| No change needed | `use-commands.ts`, `use-chat-session.ts`, `api.ts`, `types.ts`, server code |

---

## 4) Root Cause Analysis

N/A -- this is a feature enhancement, not a bug fix.

---

## 5) Research

### Potential Solutions

**1. Event Forwarding (keep cmdk for filtering, manage selection manually)**

Intercept ArrowUp/Down, Enter, Tab, Escape in the textarea's `onKeyDown`. Track `selectedIndex` in React state. Pass it to CommandPalette for visual highlighting. Use `aria-activedescendant` for accessibility. cmdk continues to handle filtering only.

- Pros:
  - Low complexity (~100 lines of code)
  - Preserves cmdk fuzzy search and grouping
  - Focus stays in textarea (best UX, matches Discord/Slack/Notion)
  - Fully accessible (WAI-ARIA combobox pattern)
  - No new dependencies
  - Tab-to-complete is trivial
- Cons:
  - Bypasses cmdk's built-in keyboard handling (managing selection manually)
  - Must manually scroll active item into view
  - Must clamp selectedIndex when filter results change
- Complexity: Low
- Maintenance: Low

**2. Focus Shift (move focus to cmdk Command.Input)**

When palette opens or arrow keys are pressed, temporarily shift DOM focus from textarea to cmdk's Command.Input. Let cmdk handle everything natively.

- Pros:
  - Leverages cmdk's full built-in keyboard handling
  - Less custom navigation code
- Cons:
  - Breaks UX: cursor position lost in textarea
  - Jarring focus jumps for screen reader users
  - Violates WAI-ARIA combobox pattern
  - Complex edge cases during focus transitions
- Complexity: Medium
- Maintenance: High

**3. Custom Hook (useCommandNavigation)**

Extract event forwarding logic (Approach 1) into a reusable hook. Returns `selectedIndex`, `handleKeyDown`, and ARIA props.

- Pros:
  - Reusable if more autocomplete features are added later
  - Testable in isolation
  - Same benefits as Approach 1
- Cons:
  - More upfront abstraction effort
  - Only one autocomplete feature exists currently
- Complexity: Medium
- Maintenance: Low

**4. Replace cmdk with Custom Dropdown**

Remove cmdk entirely. Build simple filtered list with manual keyboard handling.

- Pros:
  - Full control, no library abstractions
  - Smaller bundle
- Cons:
  - Lose fuzzy search
  - Lose grouping/separators
  - Reinventing filtering, rendering, keyboard logic
- Complexity: High
- Maintenance: Medium

**5. Radix Popover + Custom List**

Use Radix/shadcn Popover for positioning, build custom listbox inside.

- Pros:
  - Leverages Radix for positioning/portals
  - Full rendering control
- Cons:
  - Lose cmdk fuzzy search and grouping
  - Still need custom keyboard handling
  - More code than Approach 1
- Complexity: Medium
- Maintenance: Medium

**6. react-textarea-autocomplete Library**

Drop-in library specifically built for textarea autocomplete with trigger characters.

- Pros:
  - Keyboard nav works out of the box
  - Battle-tested
  - Minimal code
- Cons:
  - New dependency
  - No fuzzy search (substring only)
  - Harder to match shadcn/ui styling
  - May conflict with existing TanStack Query data flow
- Complexity: Low
- Maintenance: Low

### Recommendation

**Event Forwarding (Approach 1)** is the clear winner:

1. Lowest complexity while preserving all existing cmdk features
2. Follows the exact pattern used by Discord, Slack, GitHub, and Notion
3. Full WAI-ARIA combobox accessibility
4. No new dependencies
5. ~100 lines of focused, testable code

If the codebase later needs multiple autocomplete features (@mentions, etc.), the logic can be extracted into a hook (Approach 3) at that time.

### Accessibility Requirements (WAI-ARIA Combobox Pattern)

- Textarea must have `role="combobox"`, `aria-autocomplete="list"`, `aria-controls`, `aria-expanded`, `aria-activedescendant`
- Listbox container must have `role="listbox"` with unique `id`
- Each item must have `role="option"`, unique `id`, `aria-selected` for active item
- DOM focus must stay in textarea at all times
- Active option must be scrolled into view (browsers don't auto-scroll for `aria-activedescendant`)
- ArrowDown/ArrowUp, Enter, Escape, Tab must all be handled when palette is open

### Real-World Patterns

All major apps (Discord, Slack, GitHub, Notion) use the same approach:
- Focus stays in the input/textarea
- Arrow keys navigate the dropdown
- Enter selects the highlighted item
- Escape closes the dropdown
- Tab typically completes/selects the first or current item
- None move focus to the dropdown itself

---

## 6) Clarification

1. **Tab behavior:** Should Tab select the currently highlighted item (like Enter), or always select the first/top item regardless of arrow navigation?
2. **Loop navigation:** Should ArrowDown at the last item wrap to the first item (and ArrowUp at first wrap to last)? Discord/Slack do this.
3. **Enter behavior when palette is open:** Currently Enter submits the chat message. Should Enter select the highlighted command instead when the palette is visible? (This is the expected behavior in Discord/Slack/Notion.)
4. **Dismiss on blur:** If the user clicks outside the textarea (e.g., clicks on the message list), should the palette auto-close? Currently it only closes on Escape or command selection.
