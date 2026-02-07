import { useRef, useCallback, useState } from 'react';
import { motion } from 'motion/react';
import { Send, Square } from 'lucide-react';
import { cn } from '../../lib/utils';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  onStop?: () => void;
  onEscape?: () => void;
  isPaletteOpen?: boolean;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onCommandSelect?: () => void;
  activeDescendantId?: string;
}

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
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = useState(false);

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

  const handleFocus = useCallback(() => setIsFocused(true), []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
    if (isPaletteOpen) {
      onEscape?.();
    }
  }, [isPaletteOpen, onEscape]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      onChange(e.target.value);
      // Auto-resize textarea
      const textarea = textareaRef.current;
      if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
      }
    },
    [onChange]
  );

  return (
    <div className="flex items-end gap-2">
      <div
        className={cn(
          'flex-1 rounded-lg border transition-colors duration-150',
          isFocused ? 'border-ring' : 'border-border'
        )}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          role="combobox"
          aria-autocomplete="list"
          aria-controls="command-palette-listbox"
          aria-expanded={isPaletteOpen ?? false}
          aria-activedescendant={isPaletteOpen ? activeDescendantId : undefined}
          placeholder="Message Claude..."
          className="w-full resize-none bg-transparent px-3 py-2 text-sm focus:outline-none min-h-[40px] max-h-[200px]"
          rows={1}
          disabled={isLoading}
        />
      </div>
      {isLoading ? (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.97 }}
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
          onClick={onStop}
          className="rounded-lg bg-destructive p-2 text-destructive-foreground hover:bg-destructive/90"
          aria-label="Stop generating"
        >
          <Square className="h-4 w-4" />
        </motion.button>
      ) : (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.97 }}
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
          onClick={onSubmit}
          disabled={!value.trim()}
          className="rounded-lg bg-primary p-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          aria-label="Send message"
        >
          <Send className="h-4 w-4" />
        </motion.button>
      )}
    </div>
  );
}
