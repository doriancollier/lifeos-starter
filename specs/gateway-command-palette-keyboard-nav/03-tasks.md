---
slug: gateway-command-palette-keyboard-nav
status: ready
last-decompose: "2026-02-07"
---

# Command Palette Keyboard Navigation - Task Breakdown

## Task Overview

| # | Task ID | Phase | Title | Depends On | Est. |
|---|---------|-------|-------|------------|------|
| 1 | P1-FILTER | 1 | Lift filtering to ChatPanel and add selection state | -- | M |
| 2 | P1-PALETTE | 1 | Update CommandPalette to accept filtered list and selection index | P1-FILTER | M |
| 3 | P1-INPUT | 1 | Add palette keyboard event forwarding to ChatInput | -- | M |
| 4 | P1-WIRE | 1 | Wire keyboard navigation in ChatPanel orchestrator | P1-FILTER, P1-PALETTE, P1-INPUT | M |
| 5 | P2-ARIA | 2 | Add WAI-ARIA combobox attributes to ChatInput and CommandPalette | P1-WIRE | S |
| 6 | P3-BLUR | 3 | Add blur-to-close and mousedown preventDefault for palette | P1-WIRE | S |
| 7 | P3-SCROLL | 3 | Add scroll-into-view and index clamping | P1-WIRE | S |

**Phase 2 and Phase 3 tasks can run in parallel after Phase 1 is complete.**

---

## Task 1: [gateway-command-palette-keyboard-nav] [P1] Lift filtering to ChatPanel and add selection state

**Active Form**: Lifting filtering logic to ChatPanel and adding selection state

### Goal

Move command filtering from cmdk's internal engine to ChatPanel so the parent owns the authoritative filtered command list. Add `selectedIndex` state with reset-on-query-change behavior.

### Files to Modify

- `gateway/src/client/components/chat/ChatPanel.tsx`

### Implementation Details

**Add imports:**

```typescript
import { useState, useMemo, useEffect, useCallback } from 'react';
import { useCommands } from '../../hooks/use-commands';
```

**Add new state and derived data after existing state declarations (lines 15-16):**

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

const [selectedIndex, setSelectedIndex] = useState(0);

// Reset selectedIndex when filter changes or palette opens/closes
useEffect(() => {
  setSelectedIndex(0);
}, [commandQuery, showCommands]);
```

**Key decisions:**
- `filteredCommands` is a `useMemo` derived from `allCommands` and `commandQuery`
- Substring match on `fullCommand + description` (matches cmdk's default behavior)
- `selectedIndex` resets to 0 whenever `commandQuery` or `showCommands` changes
- `useCommands()` is called in ChatPanel now (it was previously only called inside CommandPalette)

### Tests

No separate test file for ChatPanel currently exists. The filtering logic will be validated through the integration in Task 4 (P1-WIRE) and through the existing CommandPalette tests being updated.

### Acceptance Criteria

- [ ] `filteredCommands` is computed via `useMemo` in ChatPanel
- [ ] `selectedIndex` state exists in ChatPanel, initialized to 0
- [ ] `selectedIndex` resets to 0 when `commandQuery` changes
- [ ] `selectedIndex` resets to 0 when `showCommands` changes
- [ ] `useCommands()` hook is called in ChatPanel

---

## Task 2: [gateway-command-palette-keyboard-nav] [P1] Update CommandPalette to accept filtered list and selection index

**Active Form**: Updating CommandPalette to render from parent-provided filtered commands with selection highlighting

### Goal

Change CommandPalette from internally filtering via cmdk to rendering a pre-filtered list with explicit selection index for highlighting. Remove the `query` prop. Add `filteredCommands` and `selectedIndex` props.

### Files to Modify

- `gateway/src/client/components/commands/CommandPalette.tsx`
- `gateway/src/client/components/commands/__tests__/CommandPalette.test.tsx`

### Implementation Details

**Replace the entire `CommandPalette.tsx` with:**

```typescript
import { Command } from 'cmdk';
import type { CommandEntry } from '@shared/types';

interface CommandPaletteProps {
  filteredCommands: CommandEntry[];
  selectedIndex: number;
  onSelect: (cmd: CommandEntry) => void;
  onClose: () => void;
}

export function CommandPalette({ filteredCommands, selectedIndex, onSelect, onClose }: CommandPaletteProps) {
  void onClose;

  // Group by namespace
  const grouped = filteredCommands.reduce<Record<string, CommandEntry[]>>(
    (acc, cmd) => {
      (acc[cmd.namespace] ??= []).push(cmd);
      return acc;
    },
    {}
  );

  // Track flat index across groups for selectedIndex mapping
  let flatIndex = 0;

  return (
    <div className="absolute bottom-full left-0 right-0 mb-2 max-h-80 overflow-hidden rounded-lg border bg-popover shadow-lg">
      <Command shouldFilter={false}>
        <Command.Input value="" className="sr-only" autoFocus={false} />
        <Command.List className="max-h-72 overflow-y-auto p-2">
          <Command.Empty>No commands found.</Command.Empty>
          {Object.entries(grouped).map(([namespace, cmds]) => (
            <Command.Group key={namespace} heading={namespace}>
              {cmds.map((cmd) => {
                const currentIndex = flatIndex++;
                const isSelected = currentIndex === selectedIndex;
                return (
                  <Command.Item
                    key={cmd.fullCommand}
                    value={cmd.fullCommand}
                    data-selected={isSelected}
                    onSelect={() => onSelect(cmd)}
                    className="flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer data-[selected=true]:bg-accent"
                  >
                    <span className="font-mono text-sm">
                      {cmd.fullCommand}
                    </span>
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
        </Command.List>
      </Command>
    </div>
  );
}
```

**Key changes from current code:**
1. Props change from `{ query, onSelect, onClose }` to `{ filteredCommands, selectedIndex, onSelect, onClose }`
2. Remove `useCommands()` hook call -- filtering is now done in parent
3. `shouldFilter={false}` on `Command` (was `shouldFilter={true}`)
4. `Command.Input value=""` (was `value={query}`) since filtering is external
5. `value={cmd.fullCommand}` on `Command.Item` (was `${cmd.fullCommand} ${cmd.description}`) -- just needs a value for cmdk internals but filtering is off
6. Flat index tracking with `let flatIndex = 0` and `const currentIndex = flatIndex++` inside the render loop
7. `data-selected={isSelected}` attribute driven by `selectedIndex` prop

**Update `CommandPalette.test.tsx`:**

Replace the entire test file with:

```typescript
// @vitest-environment jsdom
import { describe, it, expect, vi, beforeAll, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import { CommandPalette } from '../CommandPalette';

// cmdk requires browser APIs not available in jsdom
beforeAll(() => {
  globalThis.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
  // jsdom does not implement scrollIntoView
  Element.prototype.scrollIntoView = vi.fn();
});

afterEach(() => {
  cleanup();
});

const mockCommands = [
  { namespace: 'daily', command: 'plan', fullCommand: '/daily:plan', description: 'Morning planning', filePath: '' },
  { namespace: 'daily', command: 'eod', fullCommand: '/daily:eod', description: 'End of day review', filePath: '' },
  { namespace: 'meeting', command: 'prep', fullCommand: '/meeting:prep', description: 'Prepare for meeting', argumentHint: '[name]', filePath: '' },
];

describe('CommandPalette', () => {
  it('renders command items', () => {
    render(
      <CommandPalette filteredCommands={mockCommands} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
    );
    expect(screen.getByText('/daily:plan')).toBeDefined();
    expect(screen.getByText('/daily:eod')).toBeDefined();
    expect(screen.getByText('/meeting:prep')).toBeDefined();
  });

  it('shows descriptions', () => {
    render(
      <CommandPalette filteredCommands={mockCommands} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
    );
    expect(screen.getByText('Morning planning')).toBeDefined();
    expect(screen.getByText('End of day review')).toBeDefined();
  });

  it('shows argument hints', () => {
    render(
      <CommandPalette filteredCommands={mockCommands} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
    );
    expect(screen.getByText('[name]')).toBeDefined();
  });

  it('groups commands by namespace', () => {
    render(
      <CommandPalette filteredCommands={mockCommands} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
    );
    // cmdk renders group headings
    expect(screen.getByText('daily')).toBeDefined();
    expect(screen.getByText('meeting')).toBeDefined();
  });

  describe('selection highlighting', () => {
    it('highlights first item when selectedIndex=0', () => {
      render(
        <CommandPalette filteredCommands={mockCommands} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
      );
      const items = screen.getAllByRole('option');
      expect(items[0].getAttribute('data-selected')).toBe('true');
      expect(items[1].getAttribute('data-selected')).toBe('false');
      expect(items[2].getAttribute('data-selected')).toBe('false');
    });

    it('highlights third item when selectedIndex=2', () => {
      render(
        <CommandPalette filteredCommands={mockCommands} selectedIndex={2} onSelect={vi.fn()} onClose={vi.fn()} />
      );
      const items = screen.getAllByRole('option');
      expect(items[0].getAttribute('data-selected')).toBe('false');
      expect(items[1].getAttribute('data-selected')).toBe('false');
      expect(items[2].getAttribute('data-selected')).toBe('true');
    });

    it('updates highlight when selectedIndex changes', () => {
      const { rerender } = render(
        <CommandPalette filteredCommands={mockCommands} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
      );
      let items = screen.getAllByRole('option');
      expect(items[0].getAttribute('data-selected')).toBe('true');

      rerender(
        <CommandPalette filteredCommands={mockCommands} selectedIndex={1} onSelect={vi.fn()} onClose={vi.fn()} />
      );
      items = screen.getAllByRole('option');
      expect(items[0].getAttribute('data-selected')).toBe('false');
      expect(items[1].getAttribute('data-selected')).toBe('true');
    });
  });

  it('renders empty state when no commands match', () => {
    render(
      <CommandPalette filteredCommands={[]} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
    );
    expect(screen.getByText('No commands found.')).toBeDefined();
  });
});
```

**Key test changes:**
1. Remove `QueryClientProvider` wrapper -- no longer needed since `useCommands` is not called in CommandPalette
2. Remove `vi.mock('../../../hooks/use-commands')` -- no longer needed
3. All renders pass `filteredCommands={mockCommands}` and `selectedIndex={0}` instead of `query=""`
4. New `selection highlighting` describe block with 3 tests
5. New empty state test
6. Mock commands include `filePath: ''` to match the full `CommandEntry` type

### Acceptance Criteria

- [ ] CommandPalette accepts `filteredCommands` and `selectedIndex` props (not `query`)
- [ ] `shouldFilter={false}` is set on cmdk `Command` root
- [ ] Flat index tracking correctly maps `selectedIndex` to items across groups
- [ ] `data-selected` attribute is set correctly on each item
- [ ] `data-[selected=true]:bg-accent` class provides visual highlighting
- [ ] All existing tests pass with updated props
- [ ] New selection highlighting tests pass
- [ ] Empty state renders when `filteredCommands` is empty

---

## Task 3: [gateway-command-palette-keyboard-nav] [P1] Add palette keyboard event forwarding to ChatInput

**Active Form**: Adding palette-aware keyboard event handling to ChatInput

### Goal

Extend ChatInput's `handleKeyDown` to intercept ArrowUp, ArrowDown, Enter, and Tab when the palette is open, forwarding them to parent callbacks. Preserve all existing behavior when palette is closed.

### Files to Modify

- `gateway/src/client/components/chat/ChatInput.tsx`
- `gateway/src/client/components/chat/__tests__/ChatInput.test.tsx`

### Implementation Details

**Update the `ChatInputProps` interface:**

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

**Update the component destructuring:**

```typescript
export function ChatInput({
  value,
  onChange,
  onSubmit,
  isLoading,
  onStop,
  onEscape,
  isPaletteOpen,
  onArrowUp,
  onArrowDown,
  onCommandSelect,
  activeDescendantId,
}: ChatInputProps) {
```

**Replace the `handleKeyDown` callback:**

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

Note: All new props are optional with `?`, so existing callers are unaffected. The new `activeDescendantId` prop is used in the ARIA task (Task 5) but accepted here to avoid a second interface change.

**Add new tests to `ChatInput.test.tsx`:**

Append these test blocks after the existing tests (inside the outer `describe('ChatInput', ...)`):

```typescript
describe('palette-open keyboard handling', () => {
  it('calls onArrowDown when ArrowDown pressed and palette open', () => {
    const onArrowDown = vi.fn();
    render(<ChatInput {...defaultProps} isPaletteOpen={true} onArrowDown={onArrowDown} />);
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'ArrowDown' });
    expect(onArrowDown).toHaveBeenCalledOnce();
  });

  it('calls onArrowUp when ArrowUp pressed and palette open', () => {
    const onArrowUp = vi.fn();
    render(<ChatInput {...defaultProps} isPaletteOpen={true} onArrowUp={onArrowUp} />);
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'ArrowUp' });
    expect(onArrowUp).toHaveBeenCalledOnce();
  });

  it('calls onCommandSelect on Enter when palette open', () => {
    const onCommandSelect = vi.fn();
    const onSubmit = vi.fn();
    render(
      <ChatInput {...defaultProps} value="/daily" isPaletteOpen={true} onCommandSelect={onCommandSelect} onSubmit={onSubmit} />
    );
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Enter' });
    expect(onCommandSelect).toHaveBeenCalledOnce();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('calls onCommandSelect on Tab when palette open', () => {
    const onCommandSelect = vi.fn();
    render(<ChatInput {...defaultProps} isPaletteOpen={true} onCommandSelect={onCommandSelect} />);
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Tab' });
    expect(onCommandSelect).toHaveBeenCalledOnce();
  });

  it('calls onEscape on Escape when palette open', () => {
    const onEscape = vi.fn();
    render(<ChatInput {...defaultProps} isPaletteOpen={true} onEscape={onEscape} />);
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Escape' });
    expect(onEscape).toHaveBeenCalledOnce();
  });

  it('does not call onCommandSelect on Shift+Enter when palette open', () => {
    const onCommandSelect = vi.fn();
    render(<ChatInput {...defaultProps} isPaletteOpen={true} onCommandSelect={onCommandSelect} />);
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Enter', shiftKey: true });
    expect(onCommandSelect).not.toHaveBeenCalled();
  });
});

describe('palette-closed keyboard regression', () => {
  it('does not call onArrowDown when ArrowDown pressed and palette closed', () => {
    const onArrowDown = vi.fn();
    render(<ChatInput {...defaultProps} isPaletteOpen={false} onArrowDown={onArrowDown} />);
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'ArrowDown' });
    expect(onArrowDown).not.toHaveBeenCalled();
  });

  it('calls onSubmit on Enter when palette closed (not onCommandSelect)', () => {
    const onSubmit = vi.fn();
    const onCommandSelect = vi.fn();
    render(
      <ChatInput {...defaultProps} value="hello" isPaletteOpen={false} onSubmit={onSubmit} onCommandSelect={onCommandSelect} />
    );
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Enter' });
    expect(onSubmit).toHaveBeenCalledOnce();
    expect(onCommandSelect).not.toHaveBeenCalled();
  });
});
```

### Acceptance Criteria

- [ ] `ChatInputProps` has new optional props: `isPaletteOpen`, `onArrowUp`, `onArrowDown`, `onCommandSelect`, `activeDescendantId`
- [ ] ArrowDown/ArrowUp call respective callbacks and `preventDefault()` when palette is open
- [ ] Enter (non-Shift) calls `onCommandSelect` (not `onSubmit`) when palette is open
- [ ] Tab calls `onCommandSelect` when palette is open
- [ ] Escape calls `onEscape` regardless of palette state
- [ ] Shift+Enter does not trigger `onCommandSelect` when palette is open
- [ ] When palette is closed, all existing behavior is preserved (Enter submits, arrows move cursor, Tab moves focus)
- [ ] All existing ChatInput tests continue to pass without modification
- [ ] All new palette keyboard tests pass

---

## Task 4: [gateway-command-palette-keyboard-nav] [P1] Wire keyboard navigation in ChatPanel orchestrator

**Active Form**: Wiring arrow handlers, command selection, and active descendant computation in ChatPanel

### Goal

Create the arrow up/down handlers with wrap-around, the keyboard command selection handler, and the active descendant ID computation in ChatPanel. Pass all new props to both ChatInput and CommandPalette.

### Files to Modify

- `gateway/src/client/components/chat/ChatPanel.tsx`

### Implementation Details

This task builds on Task 1 (P1-FILTER). The final `ChatPanel.tsx` after Tasks 1 and 4 should look like:

```typescript
import { useState, useMemo, useEffect, useCallback } from 'react';
import { useChatSession } from '../../hooks/use-chat-session';
import { useCommands } from '../../hooks/use-commands';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { CommandPalette } from '../commands/CommandPalette';
import type { CommandEntry } from '@shared/types';

interface ChatPanelProps {
  sessionId: string;
}

export function ChatPanel({ sessionId }: ChatPanelProps) {
  const { messages, input, setInput, handleSubmit, status, error, stop, isLoadingHistory } =
    useChatSession(sessionId);
  const [showCommands, setShowCommands] = useState(false);
  const [commandQuery, setCommandQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

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

  // Reset selectedIndex when filter changes or palette opens/closes
  useEffect(() => {
    setSelectedIndex(0);
  }, [commandQuery, showCommands]);

  function handleInputChange(value: string) {
    setInput(value);
    // Detect slash command trigger
    const match = value.match(/(^|\s)\/(\w*)$/);
    if (match) {
      setShowCommands(true);
      setCommandQuery(match[2]);
    } else {
      setShowCommands(false);
    }
  }

  function handleCommandSelect(cmd: CommandEntry) {
    setInput(cmd.fullCommand + ' ');
    setShowCommands(false);
  }

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

  const handleKeyboardCommandSelect = useCallback(() => {
    if (filteredCommands.length > 0 && selectedIndex < filteredCommands.length) {
      handleCommandSelect(filteredCommands[selectedIndex]);
    }
  }, [filteredCommands, selectedIndex]);

  const activeDescendantId =
    showCommands && filteredCommands.length > 0
      ? `command-item-${selectedIndex}`
      : undefined;

  return (
    <div className="flex flex-col h-full">
      {isLoadingHistory ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-muted-foreground border-t-transparent" />
            Loading conversation history...
          </div>
        </div>
      ) : (
        <MessageList messages={messages} />
      )}

      {error && (
        <div className="mx-4 mb-2 rounded-lg bg-destructive/10 text-destructive px-3 py-2 text-sm">
          Error: {error}
        </div>
      )}

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
    </div>
  );
}
```

**Key additions from the current ChatPanel:**
1. `import { useState, useMemo, useEffect, useCallback } from 'react'` -- expanded imports
2. `import { useCommands } from '../../hooks/use-commands'` -- new import
3. `selectedIndex` state
4. `filteredCommands` useMemo (from Task 1)
5. `useEffect` to reset `selectedIndex` on query/palette change (from Task 1)
6. `handleArrowDown` with modulo wrap-around
7. `handleArrowUp` with modulo wrap-around (adds `filteredCommands.length` before mod to handle negative)
8. `handleKeyboardCommandSelect` that maps `selectedIndex` to a `CommandEntry` and delegates to `handleCommandSelect`
9. `activeDescendantId` computation
10. Updated `CommandPalette` JSX props: `filteredCommands`, `selectedIndex` (replaces `query`)
11. Updated `ChatInput` JSX props: `isPaletteOpen`, `onArrowUp`, `onArrowDown`, `onCommandSelect`, `activeDescendantId`

### Acceptance Criteria

- [ ] `handleArrowDown` increments `selectedIndex` with wrap-around (modulo `filteredCommands.length`)
- [ ] `handleArrowUp` decrements `selectedIndex` with wrap-around
- [ ] Both arrow handlers are no-ops when `filteredCommands.length === 0`
- [ ] `handleKeyboardCommandSelect` calls `handleCommandSelect` with the correct `CommandEntry`
- [ ] `handleKeyboardCommandSelect` is a no-op when `filteredCommands` is empty
- [ ] `activeDescendantId` is `command-item-{selectedIndex}` when palette is open with commands, `undefined` otherwise
- [ ] `CommandPalette` receives `filteredCommands` and `selectedIndex` props
- [ ] `ChatInput` receives all new keyboard navigation props
- [ ] Application compiles with no TypeScript errors
- [ ] Manual verification: ArrowDown/Up navigates, Enter/Tab selects, wrap-around works

---

## Task 5: [gateway-command-palette-keyboard-nav] [P2] Add WAI-ARIA combobox attributes to ChatInput and CommandPalette

**Active Form**: Adding WAI-ARIA combobox pattern attributes for screen reader accessibility

### Goal

Implement the full WAI-ARIA combobox pattern: `role="combobox"` on the textarea, `role="listbox"` on the command list, `role="option"` on each item, and the correct `aria-*` attributes.

### Files to Modify

- `gateway/src/client/components/chat/ChatInput.tsx`
- `gateway/src/client/components/commands/CommandPalette.tsx`
- `gateway/src/client/components/chat/__tests__/ChatInput.test.tsx`
- `gateway/src/client/components/commands/__tests__/CommandPalette.test.tsx`

### Implementation Details

**ChatInput.tsx -- Update the textarea element:**

Replace the current `<textarea>` JSX with:

```tsx
<textarea
  ref={textareaRef}
  value={value}
  onChange={handleChange}
  onKeyDown={handleKeyDown}
  role="combobox"
  aria-autocomplete="list"
  aria-controls="command-palette-listbox"
  aria-expanded={isPaletteOpen ?? false}
  aria-activedescendant={isPaletteOpen ? activeDescendantId : undefined}
  placeholder="Type a message or / for commands..."
  className="flex-1 resize-none rounded-lg border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring min-h-[40px] max-h-[200px]"
  rows={1}
  disabled={isLoading}
/>
```

**Key ARIA attributes:**
- `role="combobox"` -- always present (WAI-ARIA requirement)
- `aria-autocomplete="list"` -- always present (indicates list-based autocomplete)
- `aria-controls="command-palette-listbox"` -- always references the listbox ID (valid even when listbox is not in DOM per WAI-ARIA spec)
- `aria-expanded={isPaletteOpen ?? false}` -- reflects palette open state
- `aria-activedescendant={isPaletteOpen ? activeDescendantId : undefined}` -- points to highlighted item ID when palette is open, removed when closed

Note: Adding `role="combobox"` changes the element's queried role from `"textbox"` to `"combobox"`. Existing tests that use `screen.getByRole('textbox')` must be updated to `screen.getByRole('combobox')`.

**CommandPalette.tsx -- Add ARIA attributes:**

On `Command.List`, add `id` and `role`:

```tsx
<Command.List
  id="command-palette-listbox"
  role="listbox"
  className="max-h-72 overflow-y-auto p-2"
>
```

On each `Command.Item`, add `id`, `role`, and `aria-selected`:

```tsx
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
```

**Update ChatInput.test.tsx:**

Since the textarea now has `role="combobox"`, update ALL existing test queries from:
```typescript
screen.getByRole('textbox')
```
to:
```typescript
screen.getByRole('combobox')
```

This affects the following existing tests:
- `calls onChange when typing`
- `calls onSubmit on Enter key when value is non-empty`
- `does not submit on Shift+Enter`
- `does not submit when value is empty`
- `does not submit when loading`
- `disables textarea when loading`
- `calls onEscape when Escape pressed`
- All new palette keyboard tests from Task 3

And add these new ARIA-specific tests:

```typescript
describe('ARIA attributes', () => {
  it('textarea has combobox role', () => {
    render(<ChatInput {...defaultProps} />);
    expect(screen.getByRole('combobox')).toBeDefined();
  });

  it('has aria-expanded true when palette open', () => {
    render(<ChatInput {...defaultProps} isPaletteOpen={true} />);
    expect(screen.getByRole('combobox').getAttribute('aria-expanded')).toBe('true');
  });

  it('has aria-expanded false when palette closed', () => {
    render(<ChatInput {...defaultProps} isPaletteOpen={false} />);
    expect(screen.getByRole('combobox').getAttribute('aria-expanded')).toBe('false');
  });

  it('has aria-expanded false by default (no isPaletteOpen)', () => {
    render(<ChatInput {...defaultProps} />);
    expect(screen.getByRole('combobox').getAttribute('aria-expanded')).toBe('false');
  });

  it('has aria-activedescendant when palette open with activeDescendantId', () => {
    render(<ChatInput {...defaultProps} isPaletteOpen={true} activeDescendantId="command-item-2" />);
    expect(screen.getByRole('combobox').getAttribute('aria-activedescendant')).toBe('command-item-2');
  });

  it('does not have aria-activedescendant when palette closed', () => {
    render(<ChatInput {...defaultProps} isPaletteOpen={false} activeDescendantId="command-item-2" />);
    expect(screen.getByRole('combobox').getAttribute('aria-activedescendant')).toBeNull();
  });

  it('has aria-controls pointing to command palette listbox', () => {
    render(<ChatInput {...defaultProps} />);
    expect(screen.getByRole('combobox').getAttribute('aria-controls')).toBe('command-palette-listbox');
  });

  it('has aria-autocomplete set to list', () => {
    render(<ChatInput {...defaultProps} />);
    expect(screen.getByRole('combobox').getAttribute('aria-autocomplete')).toBe('list');
  });
});
```

**Update CommandPalette.test.tsx -- Add ARIA tests:**

Append to the test file:

```typescript
describe('ARIA attributes', () => {
  it('Command.List has listbox role and correct id', () => {
    render(
      <CommandPalette filteredCommands={mockCommands} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
    );
    const listbox = screen.getByRole('listbox');
    expect(listbox).toBeDefined();
    expect(listbox.getAttribute('id')).toBe('command-palette-listbox');
  });

  it('items have option role and unique sequential ids', () => {
    render(
      <CommandPalette filteredCommands={mockCommands} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
    );
    const options = screen.getAllByRole('option');
    expect(options).toHaveLength(3);
    expect(options[0].getAttribute('id')).toBe('command-item-0');
    expect(options[1].getAttribute('id')).toBe('command-item-1');
    expect(options[2].getAttribute('id')).toBe('command-item-2');
  });

  it('only active item has aria-selected true', () => {
    render(
      <CommandPalette filteredCommands={mockCommands} selectedIndex={1} onSelect={vi.fn()} onClose={vi.fn()} />
    );
    const options = screen.getAllByRole('option');
    expect(options[0].getAttribute('aria-selected')).toBe('false');
    expect(options[1].getAttribute('aria-selected')).toBe('true');
    expect(options[2].getAttribute('aria-selected')).toBe('false');
  });
});
```

### Acceptance Criteria

- [ ] Textarea has `role="combobox"`, `aria-autocomplete="list"`, `aria-controls="command-palette-listbox"`
- [ ] `aria-expanded` is `true` when palette open, `false` when closed
- [ ] `aria-activedescendant` points to active item ID when palette open, absent when closed
- [ ] `Command.List` has `id="command-palette-listbox"` and `role="listbox"`
- [ ] Each `Command.Item` has `role="option"`, unique `id="command-item-{N}"`, and `aria-selected`
- [ ] All existing tests updated from `getByRole('textbox')` to `getByRole('combobox')`
- [ ] All new ARIA tests pass
- [ ] VoiceOver announces the textarea as a combobox and reads active item on navigation

---

## Task 6: [gateway-command-palette-keyboard-nav] [P3] Add blur-to-close and mousedown preventDefault for palette

**Active Form**: Adding blur handler to close palette and mousedown prevention to preserve focus during palette clicks

### Goal

Close the command palette when the textarea loses focus (user clicks outside). Prevent the palette container from stealing focus when clicked (which would cause blur before the click registers).

### Files to Modify

- `gateway/src/client/components/chat/ChatInput.tsx`
- `gateway/src/client/components/commands/CommandPalette.tsx`
- `gateway/src/client/components/chat/__tests__/ChatInput.test.tsx`
- `gateway/src/client/components/commands/__tests__/CommandPalette.test.tsx`

### Implementation Details

**ChatInput.tsx -- Add `handleBlur` callback:**

Add after the `handleKeyDown` callback:

```typescript
const handleBlur = useCallback(() => {
  if (isPaletteOpen) {
    onEscape?.();
  }
}, [isPaletteOpen, onEscape]);
```

**ChatInput.tsx -- Attach `onBlur` to textarea:**

Add `onBlur={handleBlur}` to the textarea element:

```tsx
<textarea
  ref={textareaRef}
  value={value}
  onChange={handleChange}
  onKeyDown={handleKeyDown}
  onBlur={handleBlur}
  role="combobox"
  ...
/>
```

**CommandPalette.tsx -- Add `onMouseDown` + `preventDefault()` to container:**

Update the outermost div:

```tsx
<div
  className="absolute bottom-full left-0 right-0 mb-2 max-h-80 overflow-hidden rounded-lg border bg-popover shadow-lg"
  onMouseDown={(e) => e.preventDefault()}
>
```

This prevents the `mousedown` event on the palette from causing the textarea to lose focus. The click on a `Command.Item` will still fire its `onSelect` callback because `preventDefault()` on `mousedown` only prevents the default focus-stealing behavior, not the subsequent `click` event.

**ChatInput.test.tsx -- Add blur tests:**

```typescript
describe('blur handling', () => {
  it('calls onEscape on blur when palette is open', () => {
    const onEscape = vi.fn();
    render(<ChatInput {...defaultProps} isPaletteOpen={true} onEscape={onEscape} />);
    fireEvent.blur(screen.getByRole('combobox'));
    expect(onEscape).toHaveBeenCalledOnce();
  });

  it('does not call onEscape on blur when palette is closed', () => {
    const onEscape = vi.fn();
    render(<ChatInput {...defaultProps} isPaletteOpen={false} onEscape={onEscape} />);
    fireEvent.blur(screen.getByRole('combobox'));
    expect(onEscape).not.toHaveBeenCalled();
  });
});
```

**CommandPalette.test.tsx -- Add mousedown prevention test:**

```typescript
it('prevents default on mousedown to preserve textarea focus', () => {
  const { container } = render(
    <CommandPalette filteredCommands={mockCommands} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
  );
  const paletteContainer = container.firstElementChild!;
  const event = new MouseEvent('mousedown', { bubbles: true, cancelable: true });
  const prevented = !paletteContainer.dispatchEvent(event);
  expect(prevented).toBe(true);
});
```

### Acceptance Criteria

- [ ] Textarea `onBlur` calls `onEscape` when palette is open, closing the palette
- [ ] Textarea `onBlur` does nothing when palette is closed
- [ ] CommandPalette container `onMouseDown` calls `preventDefault()`, preventing textarea blur
- [ ] Clicking a command item in the palette works (blur does not fire before click)
- [ ] Clicking outside the textarea and palette closes the palette
- [ ] All blur tests pass
- [ ] The mousedown prevention test passes

---

## Task 7: [gateway-command-palette-keyboard-nav] [P3] Add scroll-into-view and index clamping

**Active Form**: Adding scroll-into-view behavior for keyboard navigation and selectedIndex clamping for safety

### Goal

Automatically scroll the active command item into the visible area when navigated to via keyboard. Clamp `selectedIndex` when the filtered list shrinks to prevent out-of-bounds access.

### Files to Modify

- `gateway/src/client/components/commands/CommandPalette.tsx`
- `gateway/src/client/components/chat/ChatPanel.tsx`
- `gateway/src/client/components/commands/__tests__/CommandPalette.test.tsx`

### Implementation Details

**CommandPalette.tsx -- Add `useEffect` for scroll-into-view:**

Add import at top:

```typescript
import { useEffect } from 'react';
```

Add inside the component body, after the `grouped` computation:

```typescript
useEffect(() => {
  const activeEl = document.getElementById(`command-item-${selectedIndex}`);
  if (activeEl) {
    activeEl.scrollIntoView({ block: 'nearest' });
  }
}, [selectedIndex]);
```

`block: 'nearest'` ensures the element only scrolls if it is outside the visible area of the scrollable `Command.List` container, preventing jarring jumps when the item is already visible.

**ChatPanel.tsx -- Add index clamping effect:**

Add after the existing `selectedIndex` reset effect:

```typescript
// Clamp selectedIndex when filteredCommands shrinks
useEffect(() => {
  if (filteredCommands.length > 0 && selectedIndex >= filteredCommands.length) {
    setSelectedIndex(filteredCommands.length - 1);
  }
}, [filteredCommands.length, selectedIndex]);
```

This handles the edge case where:
1. User arrows down to item 5
2. User types a character that filters the list to 3 items
3. Without clamping, `selectedIndex` (5) would point past the end of the list

**CommandPalette.test.tsx -- Add scroll-into-view test:**

```typescript
describe('scroll behavior', () => {
  it('scrolls active item into view when selectedIndex changes', () => {
    const { rerender } = render(
      <CommandPalette filteredCommands={mockCommands} selectedIndex={0} onSelect={vi.fn()} onClose={vi.fn()} />
    );

    // Clear any initial scrollIntoView calls
    vi.mocked(Element.prototype.scrollIntoView).mockClear();

    rerender(
      <CommandPalette filteredCommands={mockCommands} selectedIndex={2} onSelect={vi.fn()} onClose={vi.fn()} />
    );

    expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({ block: 'nearest' });
  });
});
```

Note: `Element.prototype.scrollIntoView` is already mocked as `vi.fn()` in the `beforeAll` block of the test file (from the existing setup).

### Acceptance Criteria

- [ ] Active item auto-scrolls into view when `selectedIndex` changes
- [ ] `scrollIntoView` uses `{ block: 'nearest' }` to minimize jarring scrolls
- [ ] `selectedIndex` is clamped to `filteredCommands.length - 1` when the list shrinks
- [ ] No index-out-of-bounds access when rapidly typing while arrowing
- [ ] Empty filtered list does not cause errors (arrow handlers are no-ops, `activeDescendantId` is `undefined`)
- [ ] Scroll-into-view test passes
- [ ] Commands still loading (`useCommands` returns `isLoading: true`) results in empty `filteredCommands` with no errors

---

## Dependency Graph

```
P1-FILTER (Task 1) ─────────┐
                             ├──> P1-WIRE (Task 4) ──┬──> P2-ARIA (Task 5)
P1-INPUT  (Task 3) ─────────┤                        ├──> P3-BLUR (Task 6)
                             │                        └──> P3-SCROLL (Task 7)
P1-PALETTE (Task 2) ────────┘
   (depends on Task 1)
```

**Phase 1 execution order:**
- Tasks 1 and 3 can run in parallel (no dependencies)
- Task 2 depends on Task 1 (needs to know the new prop interface)
- Task 4 depends on Tasks 1, 2, and 3 (wires everything together)

**Phase 2 and 3 execution order:**
- Tasks 5, 6, and 7 all depend on Task 4 (Phase 1 complete)
- Tasks 5, 6, and 7 can run in parallel with each other

## Validation Checklist

After all tasks are complete:

- [ ] `npm run test:run` passes all tests in the `gateway/` directory
- [ ] No TypeScript compilation errors (`npm run build`)
- [ ] Manual test: Type `/` -> palette appears -> ArrowDown highlights next item -> Enter selects it
- [ ] Manual test: ArrowUp at first item wraps to last; ArrowDown at last wraps to first
- [ ] Manual test: Tab selects highlighted command
- [ ] Manual test: Escape closes palette
- [ ] Manual test: Click on command item works (palette does not close before click registers)
- [ ] Manual test: Click outside textarea closes palette
- [ ] Manual test: Type `/da` -> only daily commands shown -> arrow navigation works within filtered set
- [ ] Manual test: Long command list scrolls active item into view
- [ ] VoiceOver: Textarea announced as combobox, active item announced on arrow key navigation
