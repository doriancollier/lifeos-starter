---
slug: gateway-command-palette-keyboard-nav
status: ready
---

# Command Palette Keyboard Navigation - Specification

## Overview

The gateway's slash command autocomplete palette currently renders command suggestions using cmdk but cannot be navigated via keyboard. The root cause is that DOM focus remains in the textarea while cmdk's built-in keyboard handlers require focus on its internal `Command.Input` element, which is hidden with `sr-only` and `autoFocus={false}`.

This specification details the "Event Forwarding" approach: intercept keyboard events in the textarea's `onKeyDown` handler, manage a `selectedIndex` in React state at the ChatPanel level, and pass it down to CommandPalette for visual highlighting and scroll-into-view behavior. cmdk is retained for filtering and grouping only, with a critical change: filtering is moved to the parent so that ChatPanel owns the authoritative filtered command list needed for index-based selection. The implementation follows the WAI-ARIA combobox pattern used by Discord, Slack, GitHub, and Notion.

## Technical Design

### Architecture Changes

The current architecture has three layers: ChatPanel (orchestrator), ChatInput (textarea + keydown), and CommandPalette (cmdk wrapper). This enhancement adds two new cross-cutting concerns:

1. **Selection state** -- a `selectedIndex` number managed in ChatPanel, reset on filter changes, incremented/decremented by arrow keys, consumed by CommandPalette for highlighting.
2. **Filtered command list ownership** -- currently cmdk filters internally and the parent has no access to the filtered result set. This must change so ChatPanel can map `selectedIndex` to a specific `CommandEntry` and pass the count to arrow key wrapping logic.

The component tree and data flow after the change:

```
ChatPanel (state owner)
  |-- selectedIndex: number
  |-- filteredCommands: CommandEntry[]
  |-- showCommands, commandQuery (existing)
  |
  +-- CommandPalette
  |     props: filteredCommands, selectedIndex, onSelect, onClose
  |     renders: grouped items with ARIA attributes, scroll-into-view
  |
  +-- ChatInput
        props: isPaletteOpen, onArrowUp, onArrowDown, onCommandSelect, onEscape (existing), ...
        renders: textarea with ARIA combobox attributes
```

No changes are needed to hooks (`use-commands.ts`, `use-chat-session.ts`), the API layer, shared types, or any server code.

### Component Changes

#### 1. ChatInput.tsx

**Interface changes:**

```typescript
interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  onStop?: () => void;
  onEscape?: () => void;
  // New props for palette keyboard navigation
  isPaletteOpen?: boolean;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onCommandSelect?: () => void;
  activeDescendantId?: string;
}
```

**handleKeyDown changes:**

The existing `handleKeyDown` callback gains a palette-aware branch. When `isPaletteOpen` is true, arrow keys, Enter, and Tab are intercepted before the existing logic runs:

```typescript
const handleKeyDown = useCallback(
  (e: React.KeyboardEvent) => {
    // Escape always fires (palette or no palette)
    if (e.key === 'Escape') {
      onEscape?.();
      return;
    }

    // --- Palette-open interceptions ---
    if (isPaletteOpen) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        onArrowDown?.();
        return;
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        onArrowUp?.();
        return;
      }
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        onCommandSelect?.();
        return;
      }
      if (e.key === 'Tab') {
        e.preventDefault();
        onCommandSelect?.();
        return;
      }
    }

    // --- Default behavior (palette closed) ---
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && value.trim()) {
        onSubmit();
      }
    }
  },
  [isLoading, value, onSubmit, onEscape, isPaletteOpen, onArrowUp, onArrowDown, onCommandSelect]
);
```

Key behavioral notes:
- `ArrowDown` and `ArrowUp` call `preventDefault()` to suppress the textarea's default cursor movement behavior (moving to end/start of text).
- `Enter` (without Shift) selects the highlighted command instead of submitting the chat message. This matches Discord/Slack/Notion behavior.
- `Tab` selects the highlighted command instead of moving focus to the next focusable element.
- `Escape` fires `onEscape` regardless of palette state (existing behavior preserved).
- When `isPaletteOpen` is false (or undefined), the existing behavior is completely unchanged.

**onBlur handler:**

A new `onBlur` handler on the textarea auto-closes the palette when the user clicks outside:

```typescript
const handleBlur = useCallback(() => {
  if (isPaletteOpen) {
    onEscape?.();
  }
}, [isPaletteOpen, onEscape]);
```

This is attached to the textarea element: `onBlur={handleBlur}`.

Important edge case: clicking a CommandPalette item fires `onBlur` on the textarea before `onClick` on the item. To prevent the palette from closing before the click registers, the `onBlur` handler must use a short `setTimeout` (0ms, microtask-level) or the CommandPalette items must use `onMouseDown` with `preventDefault()` to suppress the blur. The recommended approach is `onMouseDown` + `preventDefault()` on the palette container, which is cleaner and avoids timing issues. See CommandPalette.tsx changes below.

**ARIA attributes on textarea:**

When the palette is open, the textarea must communicate its combobox role to assistive technology:

```tsx
<textarea
  ref={textareaRef}
  value={value}
  onChange={handleChange}
  onKeyDown={handleKeyDown}
  onBlur={handleBlur}
  role="combobox"
  aria-autocomplete="list"
  aria-controls="command-palette-listbox"
  aria-expanded={isPaletteOpen ?? false}
  aria-activedescendant={isPaletteOpen ? activeDescendantId : undefined}
  placeholder="Type a message or / for commands..."
  className="..."
  rows={1}
  disabled={isLoading}
/>
```

The `role="combobox"` and `aria-autocomplete="list"` attributes are always present. `aria-expanded` reflects the palette state. `aria-activedescendant` points to the `id` of the currently highlighted option element, which is constructed as `command-item-${selectedIndex}` and passed down from ChatPanel as the `activeDescendantId` prop.

Note: `aria-controls` always references the listbox ID. When the palette is closed and the listbox is not in the DOM, this is still valid per the WAI-ARIA spec (the attribute value is an IDREF, not required to resolve to a present element).

#### 2. ChatPanel.tsx

**New state:**

```typescript
const [selectedIndex, setSelectedIndex] = useState(0);
```

**Filtered commands (lifting filtering out of cmdk):**

Currently, cmdk handles filtering internally and the parent has no access to the filtered list. Since ChatPanel needs to:
1. Know how many filtered items exist (for wrap-around modulo)
2. Map `selectedIndex` to a specific `CommandEntry` (for selection)

Filtering must be lifted to ChatPanel. This is a simple substring match replicating cmdk's behavior:

```typescript
const { data: registry } = useCommands();
const allCommands = registry?.commands ?? [];

const filteredCommands = useMemo(() => {
  if (!commandQuery) return allCommands;
  const q = commandQuery.toLowerCase();
  return allCommands.filter((cmd) => {
    const searchText = `${cmd.fullCommand} ${cmd.description}`.toLowerCase();
    return searchText.includes(q);
  });
}, [allCommands, commandQuery]);
```

CommandPalette will receive the pre-filtered list and render with `shouldFilter={false}`, disabling cmdk's internal filtering.

**Reset selectedIndex on filter changes:**

```typescript
useEffect(() => {
  setSelectedIndex(0);
}, [commandQuery, showCommands]);
```

This resets the highlight to the first item whenever the user types more of the command query or whenever the palette opens/closes. This prevents stale selection pointing at an item that no longer exists in the filtered list.

**Clamp selectedIndex when filteredCommands shrinks:**

An additional guard ensures `selectedIndex` is always valid:

```typescript
useEffect(() => {
  if (filteredCommands.length > 0 && selectedIndex >= filteredCommands.length) {
    setSelectedIndex(filteredCommands.length - 1);
  }
}, [filteredCommands.length, selectedIndex]);
```

This handles the edge case where the user has arrowed down to item 5, then types a character that filters the list to 3 items. Without this, `selectedIndex` would point past the end of the list.

**Arrow handlers with wrap-around:**

```typescript
const handleArrowDown = useCallback(() => {
  setSelectedIndex((prev) =>
    filteredCommands.length === 0 ? 0 : (prev + 1) % filteredCommands.length
  );
}, [filteredCommands.length]);

const handleArrowUp = useCallback(() => {
  setSelectedIndex((prev) =>
    filteredCommands.length === 0
      ? 0
      : (prev - 1 + filteredCommands.length) % filteredCommands.length
  );
}, [filteredCommands.length]);
```

ArrowDown at the last item wraps to item 0. ArrowUp at item 0 wraps to the last item.

**Command selection handler:**

```typescript
const handleKeyboardCommandSelect = useCallback(() => {
  if (filteredCommands.length > 0 && selectedIndex < filteredCommands.length) {
    handleCommandSelect(filteredCommands[selectedIndex]);
  }
}, [filteredCommands, selectedIndex, handleCommandSelect]);
```

This is the callback triggered by Enter or Tab when the palette is open. It maps `selectedIndex` to the corresponding `CommandEntry` and delegates to the existing `handleCommandSelect`, which sets the input value and closes the palette.

**Active descendant ID computation:**

```typescript
const activeDescendantId =
  showCommands && filteredCommands.length > 0
    ? `command-item-${selectedIndex}`
    : undefined;
```

**Updated JSX:**

```tsx
<div className="relative border-t p-4">
  {showCommands && (
    <CommandPalette
      filteredCommands={filteredCommands}
      selectedIndex={selectedIndex}
      onSelect={handleCommandSelect}
      onClose={() => setShowCommands(false)}
    />
  )}

  <ChatInput
    value={input}
    onChange={handleInputChange}
    onSubmit={handleSubmit}
    isLoading={status === 'streaming'}
    onStop={stop}
    onEscape={() => setShowCommands(false)}
    isPaletteOpen={showCommands}
    onArrowUp={handleArrowUp}
    onArrowDown={handleArrowDown}
    onCommandSelect={handleKeyboardCommandSelect}
    activeDescendantId={activeDescendantId}
  />
</div>
```

#### 3. CommandPalette.tsx

**Interface changes:**

```typescript
interface CommandPaletteProps {
  filteredCommands: CommandEntry[];
  selectedIndex: number;
  onSelect: (cmd: CommandEntry) => void;
  onClose: () => void;
}
```

The `query` prop is removed because filtering now happens in the parent. The `filteredCommands` prop provides the pre-filtered list. The `selectedIndex` prop drives highlighting.

**Prevent blur on click:**

The outermost container div must prevent the textarea's blur event from firing when the user clicks inside the palette:

```tsx
<div
  className="absolute bottom-full left-0 right-0 mb-2 max-h-80 overflow-hidden rounded-lg border bg-popover shadow-lg"
  onMouseDown={(e) => e.preventDefault()}
>
```

The `onMouseDown` + `preventDefault()` call prevents the `mousedown` event from causing the textarea to lose focus, which would fire the `onBlur` handler and close the palette before the `onClick` on the command item has a chance to fire. This is the standard pattern used by autocomplete dropdown implementations.

**cmdk configuration:**

cmdk is kept for its rendering structure (Command.List, Command.Group, Command.Item, Command.Empty) but filtering is disabled:

```tsx
<Command shouldFilter={false}>
  <Command.Input value="" className="sr-only" autoFocus={false} />
  <Command.List
    id="command-palette-listbox"
    role="listbox"
    className="max-h-72 overflow-y-auto p-2"
  >
    ...
  </Command.List>
</Command>
```

`shouldFilter={false}` tells cmdk not to filter items internally. The `Command.Input` value is set to empty string since filtering is handled externally. The `Command.List` element gets the listbox `id` and `role` for ARIA compliance.

**Grouping the filtered commands:**

Grouping is computed from the pre-filtered list:

```typescript
const grouped = filteredCommands.reduce<Record<string, CommandEntry[]>>(
  (acc, cmd) => {
    (acc[cmd.namespace] ??= []).push(cmd);
    return acc;
  },
  {}
);
```

**Flat index tracking:**

Because commands are rendered in groups but `selectedIndex` is a flat index across all filtered commands, a running index counter is needed:

```typescript
let flatIndex = 0;
```

Then inside the render loop:

```tsx
{Object.entries(grouped).map(([namespace, cmds]) => (
  <Command.Group key={namespace} heading={namespace}>
    {cmds.map((cmd) => {
      const currentIndex = flatIndex++;
      const isSelected = currentIndex === selectedIndex;
      return (
        <Command.Item
          key={cmd.fullCommand}
          value={cmd.fullCommand}
          id={`command-item-${currentIndex}`}
          role="option"
          aria-selected={isSelected}
          data-selected={isSelected}
          onSelect={() => onSelect(cmd)}
          className="flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer data-[selected=true]:bg-accent"
        >
          <span className="font-mono text-sm">{cmd.fullCommand}</span>
          <span className="text-xs text-muted-foreground truncate">
            {cmd.description}
          </span>
          {cmd.argumentHint && (
            <span className="text-xs text-muted-foreground/60 ml-auto">
              {cmd.argumentHint}
            </span>
          )}
        </Command.Item>
      );
    })}
  </Command.Group>
))}
```

Note: the `flatIndex` counter increments across groups so that the flat `selectedIndex` from ChatPanel correctly maps to the right item regardless of which group it belongs to. The `value` prop on `Command.Item` is set to `cmd.fullCommand` to satisfy cmdk's requirement (it needs a value for internal state), but since `shouldFilter={false}` this does not affect rendering.

**Scroll active item into view:**

A `useEffect` watches `selectedIndex` and scrolls the active item into the viewport:

```typescript
useEffect(() => {
  const activeEl = document.getElementById(`command-item-${selectedIndex}`);
  if (activeEl) {
    activeEl.scrollIntoView({ block: 'nearest' });
  }
}, [selectedIndex]);
```

`block: 'nearest'` ensures the element scrolls only if it is outside the visible area of the scrollable `Command.List` container, minimizing jarring scroll jumps. This is the same approach used by the WAI-ARIA combobox pattern examples.

**Styling note:**

The existing class `data-[selected=true]:bg-accent` on `Command.Item` already handles highlighting. Previously this was driven by cmdk's internal selection state. Now it is driven by the explicit `data-selected` attribute set from the `selectedIndex` prop. Because `shouldFilter={false}` disables cmdk's internal keyboard navigation, cmdk will no longer set its own `data-selected` attribute, so there is no conflict.

### Data Flow

Complete data flow after enhancement:

```
1. User types "/" in textarea
   -> ChatInput.onChange fires
   -> ChatPanel.handleInputChange matches regex /(^|\s)\/(\w*)$/
   -> setShowCommands(true), setCommandQuery(match[2])
   -> selectedIndex resets to 0 (useEffect)

2. ChatPanel computes filteredCommands via useMemo
   -> Passes filteredCommands + selectedIndex to CommandPalette
   -> CommandPalette renders grouped items, item 0 highlighted

3. User types more characters (e.g., "da")
   -> commandQuery updates to "da"
   -> filteredCommands re-computed (e.g., only /daily:plan, /daily:eod)
   -> selectedIndex resets to 0

4. User presses ArrowDown
   -> ChatInput.handleKeyDown detects isPaletteOpen + ArrowDown
   -> preventDefault() (suppress textarea cursor movement)
   -> Calls onArrowDown prop
   -> ChatPanel increments selectedIndex: (0 + 1) % 2 = 1
   -> CommandPalette re-renders with selectedIndex=1
   -> Item at index 1 gets data-selected=true, bg-accent class
   -> useEffect scrolls item into view if needed

5. User presses ArrowDown again (at last item)
   -> selectedIndex: (1 + 1) % 2 = 0 (wraps to first)

6. User presses ArrowUp (at first item)
   -> selectedIndex: (0 - 1 + 2) % 2 = 1 (wraps to last)

7. User presses Enter (or Tab)
   -> ChatInput.handleKeyDown detects isPaletteOpen + Enter/Tab
   -> preventDefault()
   -> Calls onCommandSelect prop
   -> ChatPanel reads filteredCommands[selectedIndex]
   -> handleCommandSelect sets input to fullCommand + " "
   -> setShowCommands(false), palette closes

8. User presses Escape
   -> ChatInput.handleKeyDown calls onEscape
   -> ChatPanel sets showCommands to false
   -> Palette unmounts

9. User clicks a command item
   -> onMouseDown on palette container calls preventDefault() (keeps textarea focus)
   -> onClick on Command.Item fires onSelect callback
   -> handleCommandSelect sets input to fullCommand + " "
   -> setShowCommands(false), palette closes

10. User clicks outside textarea (blur)
    -> textarea onBlur fires
    -> handleBlur checks isPaletteOpen, calls onEscape
    -> Palette closes
```

### State Management

All new state lives in ChatPanel:

| State | Type | Initial | Owner | Flows To |
|-------|------|---------|-------|----------|
| `selectedIndex` | `number` | `0` | ChatPanel | CommandPalette (highlighting), ChatInput (activeDescendantId) |
| `filteredCommands` | `CommandEntry[]` | derived via `useMemo` | ChatPanel | CommandPalette (rendering), arrow handlers (wrap count), select handler (lookup) |
| `showCommands` | `boolean` | `false` | ChatPanel (existing) | ChatInput (isPaletteOpen), conditional render of CommandPalette |
| `commandQuery` | `string` | `''` | ChatPanel (existing) | filteredCommands derivation, selectedIndex reset trigger |

No new state is introduced in ChatInput or CommandPalette. ChatInput is purely a controlled component that forwards events via callbacks. CommandPalette is a pure render of its props.

## Implementation Phases

### Phase 1: Core Keyboard Navigation

**Goal:** Arrow keys navigate, Enter/Tab select, wrap-around works.

**Steps:**

1. **Lift filtering to ChatPanel.** Add `useMemo` for `filteredCommands` with substring match on `fullCommand + description`. Add `selectedIndex` state with reset effect on `commandQuery`/`showCommands`.

2. **Update CommandPalette props.** Change from `{ query, onSelect, onClose }` to `{ filteredCommands, selectedIndex, onSelect, onClose }`. Set `shouldFilter={false}` on cmdk `Command`. Render with flat index tracking and `data-selected` attribute.

3. **Update ChatInput props.** Add `isPaletteOpen`, `onArrowUp`, `onArrowDown`, `onCommandSelect`. Update `handleKeyDown` with the palette-open branch. Wire `activeDescendantId` prop (can be deferred to Phase 2 but is minimal effort here).

4. **Wire everything in ChatPanel.** Create `handleArrowUp`, `handleArrowDown`, `handleKeyboardCommandSelect` callbacks. Pass all new props to both children. Compute `activeDescendantId`.

5. **Fix existing test breakage.** Update `ChatInput.test.tsx` default props if the new optional props change the component signature. Update `CommandPalette.test.tsx` to pass `filteredCommands` instead of `query`.

**Validation:** Manually verify arrow navigation, Enter selection, Tab selection, wrap-around.

### Phase 2: Accessibility

**Goal:** Full WAI-ARIA combobox pattern compliance.

**Steps:**

1. **Add ARIA attributes to textarea** in ChatInput: `role="combobox"`, `aria-autocomplete="list"`, `aria-controls="command-palette-listbox"`, `aria-expanded`, `aria-activedescendant`.

2. **Add ARIA attributes to CommandPalette:** `id="command-palette-listbox"` and `role="listbox"` on `Command.List`, `role="option"` and `aria-selected` on each `Command.Item`.

3. **Validate with screen reader.** Test with VoiceOver (macOS) to confirm:
   - Textarea announces as combobox
   - Arrow keys announce the active command name
   - Enter/Tab selection is announced
   - Palette open/close state is communicated

**Validation:** VoiceOver + keyboard-only navigation through the full flow.

### Phase 3: Polish and Edge Cases

**Goal:** Blur handling, scroll-into-view, index clamping, click-inside-palette fix.

**Steps:**

1. **Add onBlur handler** to ChatInput textarea. Close palette on blur when `isPaletteOpen` is true.

2. **Add onMouseDown preventDefault** to CommandPalette container div. This prevents textarea blur when clicking inside the palette.

3. **Add scroll-into-view effect** in CommandPalette: `useEffect` on `selectedIndex` that calls `scrollIntoView({ block: 'nearest' })` on the active item element.

4. **Add selectedIndex clamping effect** in ChatPanel: `useEffect` that clamps `selectedIndex` to `filteredCommands.length - 1` when the list shrinks.

5. **Edge case: empty filtered list.** When `filteredCommands.length === 0`, arrow handlers and select handler should be no-ops. CommandPalette renders `Command.Empty` ("No commands found."). `aria-activedescendant` should be `undefined`.

6. **Edge case: commands still loading.** When `useCommands()` returns `isLoading: true` or `data: undefined`, `filteredCommands` will be an empty array. The palette renders the empty state. Keyboard handlers are no-ops.

**Validation:** Click-outside dismisses palette. Click-on-item works without palette closing first. Long lists scroll selected item into view. Rapid typing with arrow keys does not cause index-out-of-bounds.

## Acceptance Criteria

1. ArrowDown and ArrowUp navigate command suggestions with a visible highlight (bg-accent) on the active item.
2. Navigation wraps: ArrowDown at the last item moves to the first; ArrowUp at the first item moves to the last.
3. Enter (without Shift) selects the highlighted command when the palette is open. The input is set to the command's `fullCommand` followed by a space, and the palette closes.
4. Tab selects the highlighted command (same behavior as Enter).
5. Escape closes the palette without selecting anything (existing behavior preserved).
6. Clicking a command item in the palette still works: the click selects the command, sets the input, and closes the palette.
7. Type-to-filter still works: typing characters after "/" filters the command list via substring matching on `fullCommand + description`.
8. The palette auto-closes when the textarea loses focus (click outside).
9. The active item auto-scrolls into view within the dropdown's scrollable area when navigated to via keyboard.
10. Full WAI-ARIA combobox pattern is implemented:
    - Textarea: `role="combobox"`, `aria-autocomplete="list"`, `aria-controls="command-palette-listbox"`, `aria-expanded={true|false}`, `aria-activedescendant="command-item-{N}"`.
    - Dropdown container: `id="command-palette-listbox"`, `role="listbox"`.
    - Each item: `role="option"`, `id="command-item-{N}"`, `aria-selected={true|false}`.
11. `selectedIndex` resets to 0 when the filter query changes or the palette opens.
12. `selectedIndex` is clamped to the last valid index when the filtered list shrinks.
13. All existing ChatInput tests continue to pass without modification (the new props are optional).
14. All existing CommandPalette tests are updated to use the new props and continue to pass.
15. New tests cover all keyboard navigation scenarios (see Testing Strategy).
16. When the palette is open, ArrowDown/ArrowUp do not move the textarea cursor. Enter does not submit the chat message. Tab does not move focus.
17. When the palette is closed, all existing keyboard behavior is unchanged: Enter submits, ArrowUp/Down move cursor, Tab moves focus.

## Testing Strategy

### ChatInput.test.tsx -- New Tests

These tests verify that ChatInput correctly forwards keyboard events when the palette is open and preserves default behavior when the palette is closed.

**Palette-open keyboard tests:**

| Test | Setup | Action | Assertion |
|------|-------|--------|-----------|
| ArrowDown calls onArrowDown when palette open | `isPaletteOpen=true`, `onArrowDown=vi.fn()` | `fireEvent.keyDown(textarea, { key: 'ArrowDown' })` | `onArrowDown` called once, `preventDefault` called (verify via event default prevented) |
| ArrowUp calls onArrowUp when palette open | `isPaletteOpen=true`, `onArrowUp=vi.fn()` | `fireEvent.keyDown(textarea, { key: 'ArrowUp' })` | `onArrowUp` called once |
| Enter calls onCommandSelect when palette open | `isPaletteOpen=true`, `value="/daily"`, `onCommandSelect=vi.fn()`, `onSubmit=vi.fn()` | `fireEvent.keyDown(textarea, { key: 'Enter' })` | `onCommandSelect` called, `onSubmit` NOT called |
| Tab calls onCommandSelect when palette open | `isPaletteOpen=true`, `onCommandSelect=vi.fn()` | `fireEvent.keyDown(textarea, { key: 'Tab' })` | `onCommandSelect` called |
| Escape calls onEscape when palette open | `isPaletteOpen=true`, `onEscape=vi.fn()` | `fireEvent.keyDown(textarea, { key: 'Escape' })` | `onEscape` called (existing behavior) |
| Shift+Enter does not select command | `isPaletteOpen=true`, `onCommandSelect=vi.fn()` | `fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true })` | `onCommandSelect` NOT called |

**Palette-closed keyboard tests (regression):**

| Test | Setup | Action | Assertion |
|------|-------|--------|-----------|
| ArrowDown does NOT call onArrowDown when palette closed | `isPaletteOpen=false`, `onArrowDown=vi.fn()` | `fireEvent.keyDown(textarea, { key: 'ArrowDown' })` | `onArrowDown` NOT called |
| Enter submits when palette closed | `isPaletteOpen=false`, `value="hello"`, `onSubmit=vi.fn()`, `onCommandSelect=vi.fn()` | `fireEvent.keyDown(textarea, { key: 'Enter' })` | `onSubmit` called, `onCommandSelect` NOT called |

**Blur tests:**

| Test | Setup | Action | Assertion |
|------|-------|--------|-----------|
| Blur calls onEscape when palette open | `isPaletteOpen=true`, `onEscape=vi.fn()` | `fireEvent.blur(textarea)` | `onEscape` called |
| Blur does NOT call onEscape when palette closed | `isPaletteOpen=false`, `onEscape=vi.fn()` | `fireEvent.blur(textarea)` | `onEscape` NOT called |

**ARIA attribute tests:**

| Test | Setup | Action | Assertion |
|------|-------|--------|-----------|
| Textarea has combobox role | Render with defaults | Query textarea | `role="combobox"` present |
| aria-expanded true when palette open | `isPaletteOpen=true` | Query textarea | `aria-expanded="true"` |
| aria-expanded false when palette closed | `isPaletteOpen=false` | Query textarea | `aria-expanded="false"` |
| aria-activedescendant set when palette open | `isPaletteOpen=true`, `activeDescendantId="command-item-2"` | Query textarea | `aria-activedescendant="command-item-2"` |
| aria-activedescendant absent when palette closed | `isPaletteOpen=false` | Query textarea | `aria-activedescendant` not present |

### CommandPalette.test.tsx -- Updated and New Tests

Existing tests must be updated to pass `filteredCommands` and `selectedIndex` instead of `query`. The mock for `useCommands` remains for the existing tests that check rendering.

**Updated existing tests:**

All existing tests (`renders command items`, `shows descriptions`, `shows argument hints`, `groups commands by namespace`) are updated to pass the full mock command list as `filteredCommands` and `selectedIndex={0}`.

**New highlighting tests:**

| Test | Setup | Action | Assertion |
|------|-------|--------|-----------|
| selectedIndex=0 highlights first item | `filteredCommands=[3 items]`, `selectedIndex=0` | Render | First `Command.Item` has `data-selected="true"` and `aria-selected="true"`, others have `"false"` |
| selectedIndex=2 highlights third item | `filteredCommands=[3 items]`, `selectedIndex=2` | Render | Third item has `data-selected="true"` |
| Changing selectedIndex updates highlight | Render with `selectedIndex=0`, rerender with `selectedIndex=1` | Rerender | First item loses highlight, second gains it |

**ARIA attribute tests:**

| Test | Setup | Action | Assertion |
|------|-------|--------|-----------|
| Command.List has listbox role and id | Render with commands | Query by role | Element with `role="listbox"` and `id="command-palette-listbox"` exists |
| Items have option role and unique ids | Render with 3 commands | Query all options | 3 elements with `role="option"`, ids are `command-item-0`, `command-item-1`, `command-item-2` |
| Active item has aria-selected true | `selectedIndex=1` | Query options | Only item at index 1 has `aria-selected="true"` |

**Scroll-into-view test:**

| Test | Setup | Action | Assertion |
|------|-------|--------|-----------|
| Scrolls active item into view on selectedIndex change | Render, mock `scrollIntoView` on element | Rerender with new selectedIndex | `scrollIntoView({ block: 'nearest' })` called on the active item element |

**onMouseDown preventDefault test:**

| Test | Setup | Action | Assertion |
|------|-------|--------|-----------|
| Palette container prevents default on mousedown | Render palette | `fireEvent.mouseDown(container)` | Event `defaultPrevented` is true |

### Integration-Level Tests (Optional, Lower Priority)

If integration tests are desired, they would render `ChatPanel` with mocked hooks and verify the full flow: type "/" -> palette appears -> ArrowDown -> Enter -> input contains command. These are more fragile and slower, so unit tests on the individual components are prioritized.

## Open Questions

1. ~~**cmdk value/onValueChange interaction.**~~ (RESOLVED)
   **Answer:** Validate during Phase 1 -- if cmdk sets its own `data-selected`, pass `value=""` on `Command` root to suppress. This is an implementation-time check, not a design decision.

2. ~~**Fuzzy vs. substring matching.**~~ (RESOLVED)
   **Answer:** Use substring matching for initial implementation. Users type exact prefixes (e.g., "daily:p"). If fuzzy is needed later, add a lightweight fuzzy match function -- it's a one-line change in the `useMemo` filter.

3. ~~**Multiple palettes on the same page.**~~ (RESOLVED)
   **Answer:** Not a concern. Only one ChatPanel exists. If multiple palettes are needed later, scope IDs with `useId()`.

4. ~~**cmdk Group heading rendering.**~~ (RESOLVED)
   **Answer:** Not an issue -- pre-filtering before grouping means empty groups are never passed to cmdk. Verify during implementation.
