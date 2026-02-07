// @vitest-environment jsdom
import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import { MessageItem } from '../MessageItem';
import type { MessageGrouping } from '../../../hooks/use-chat-session';

afterEach(() => {
  cleanup();
});

// Mock motion/react to render plain elements (no animation delays)
vi.mock('motion/react', () => ({
  motion: {
    div: ({ children, initial, animate, exit, transition, ...props }: Record<string, unknown>) => {
      void initial; void animate; void exit; void transition;
      const { className, style, ...rest } = props as Record<string, unknown>;
      return <div className={className as string} style={style as React.CSSProperties} data-initial={JSON.stringify(initial)} {...rest}>{children as React.ReactNode}</div>;
    },
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock Streamdown to avoid complex rendering in unit tests
vi.mock('streamdown', () => ({
  Streamdown: ({ children }: { children: string }) => <div data-testid="streamdown">{children}</div>,
}));

const onlyGrouping: MessageGrouping = { position: 'only', groupIndex: 0 };
const firstGrouping: MessageGrouping = { position: 'first', groupIndex: 0 };
const middleGrouping: MessageGrouping = { position: 'middle', groupIndex: 0 };
const lastGrouping: MessageGrouping = { position: 'last', groupIndex: 0 };

describe('MessageItem', () => {
  it('renders user messages as plain text', () => {
    const msg = { id: '1', role: 'user' as const, content: '**not bold**', timestamp: new Date().toISOString() };
    render(<MessageItem message={msg} grouping={onlyGrouping} />);
    expect(screen.getByText('**not bold**')).toBeDefined();
    expect(screen.queryByTestId('streamdown')).toBeNull();
  });

  it('renders assistant messages with Streamdown', () => {
    const msg = { id: '1', role: 'assistant' as const, content: '# Heading', timestamp: new Date().toISOString() };
    render(<MessageItem message={msg} grouping={onlyGrouping} />);
    expect(screen.getByTestId('streamdown')).toBeDefined();
    expect(screen.getByText('# Heading')).toBeDefined();
  });

  it('does not render name labels', () => {
    const msg = { id: '1', role: 'user' as const, content: 'Test', timestamp: new Date().toISOString() };
    render(<MessageItem message={msg} grouping={onlyGrouping} />);
    expect(screen.queryByText('You')).toBeNull();
    expect(screen.queryByText('Claude')).toBeNull();
  });

  it('renders tool calls for assistant messages', () => {
    const msg = {
      id: '1',
      role: 'assistant' as const,
      content: 'Let me check.',
      toolCalls: [
        { toolCallId: 'tc-1', toolName: 'Read', input: '{}', status: 'complete' as const },
      ],
      timestamp: new Date().toISOString(),
    };
    render(<MessageItem message={msg} grouping={onlyGrouping} />);
    expect(screen.getByText('Read')).toBeDefined();
  });

  it('sets animation initial state when isNew is true', () => {
    const msg = { id: '1', role: 'assistant' as const, content: 'New message', timestamp: new Date().toISOString() };
    const { container } = render(<MessageItem message={msg} grouping={onlyGrouping} isNew={true} />);
    const motionDiv = container.firstElementChild;
    const initial = motionDiv?.getAttribute('data-initial');
    expect(initial).toBeDefined();
    const parsed = JSON.parse(initial!);
    expect(parsed.opacity).toBe(0);
    expect(parsed.y).toBe(8);
  });

  it('disables animation when isNew is false', () => {
    const msg = { id: '1', role: 'assistant' as const, content: 'Old message', timestamp: new Date().toISOString() };
    const { container } = render(<MessageItem message={msg} grouping={onlyGrouping} isNew={false} />);
    const motionDiv = container.firstElementChild;
    const initial = motionDiv?.getAttribute('data-initial');
    expect(initial).toBe('false');
  });

  it('renders dot indicator for assistant messages (first in group)', () => {
    const msg = { id: '1', role: 'assistant' as const, content: 'Reply', timestamp: new Date().toISOString() };
    render(<MessageItem message={msg} grouping={firstGrouping} />);
    expect(screen.getByText('●')).toBeDefined();
  });

  it('hides indicator for middle messages in a group', () => {
    const msg = { id: '1', role: 'assistant' as const, content: 'Reply', timestamp: new Date().toISOString() };
    render(<MessageItem message={msg} grouping={middleGrouping} />);
    expect(screen.queryByText('●')).toBeNull();
  });

  it('hides indicator for last messages in a group', () => {
    const msg = { id: '1', role: 'assistant' as const, content: 'Reply', timestamp: new Date().toISOString() };
    render(<MessageItem message={msg} grouping={lastGrouping} />);
    expect(screen.queryByText('●')).toBeNull();
  });

  it('shows chevron indicator for user on first and only positions', () => {
    const msg = { id: '1', role: 'user' as const, content: 'Test', timestamp: new Date().toISOString() };
    const { container: c1 } = render(<MessageItem message={msg} grouping={firstGrouping} />);
    // ChevronRight renders as an SVG
    expect(c1.querySelector('svg')).not.toBeNull();
    cleanup();
    const { container: c2 } = render(<MessageItem message={msg} grouping={onlyGrouping} />);
    expect(c2.querySelector('svg')).not.toBeNull();
  });

  it('renders timestamp from message on hover', () => {
    const ts = '2026-02-07T10:30:00.000Z';
    const msg = { id: '1', role: 'user' as const, content: 'Test', timestamp: ts };
    const { container } = render(<MessageItem message={msg} grouping={onlyGrouping} />);
    const timeEl = container.querySelector('.group-hover\\:text-muted-foreground\\/60');
    expect(timeEl).not.toBeNull();
    expect(timeEl!.textContent).toBeTruthy();
  });

  it('passes isStreaming to StreamingText for assistant messages', () => {
    const msg = { id: '1', role: 'assistant' as const, content: 'Streaming...', timestamp: new Date().toISOString() };
    const { container } = render(<MessageItem message={msg} grouping={onlyGrouping} isStreaming={true} />);
    const cursor = container.querySelector('[aria-hidden="true"]');
    expect(cursor).not.toBeNull();
  });

  it('renders divider on first-in-group when not the first group', () => {
    const msg = { id: '1', role: 'assistant' as const, content: 'Reply', timestamp: new Date().toISOString() };
    const grouping: MessageGrouping = { position: 'first', groupIndex: 1 };
    const { container } = render(<MessageItem message={msg} grouping={grouping} />);
    const divider = container.querySelector('.bg-border\\/20');
    expect(divider).not.toBeNull();
  });

  it('does not render divider on the first group', () => {
    const msg = { id: '1', role: 'user' as const, content: 'Hello', timestamp: new Date().toISOString() };
    const grouping: MessageGrouping = { position: 'first', groupIndex: 0 };
    const { container } = render(<MessageItem message={msg} grouping={grouping} />);
    const divider = container.querySelector('.bg-border\\/20');
    expect(divider).toBeNull();
  });

  it('uses msg-assistant class and max-width on content container', () => {
    const msg = { id: '1', role: 'assistant' as const, content: 'Reply', timestamp: new Date().toISOString() };
    const { container } = render(<MessageItem message={msg} grouping={onlyGrouping} />);
    const el = container.querySelector('.msg-assistant');
    expect(el).not.toBeNull();
    // max-w-[80ch] is on the parent content container (applies to text + tool calls)
    const contentContainer = container.querySelector('.max-w-\\[80ch\\]');
    expect(contentContainer).not.toBeNull();
    expect(contentContainer?.querySelector('.msg-assistant')).not.toBeNull();
  });

  it('applies tight spacing for middle messages', () => {
    const msg = { id: '1', role: 'user' as const, content: 'Mid', timestamp: new Date().toISOString() };
    const { container } = render(<MessageItem message={msg} grouping={middleGrouping} />);
    const el = container.firstElementChild;
    expect(el?.className).toContain('pt-0.5');
    expect(el?.className).toContain('pb-0.5');
  });

  it('applies larger spacing for first-in-group messages', () => {
    const msg = { id: '1', role: 'user' as const, content: 'First', timestamp: new Date().toISOString() };
    const { container } = render(<MessageItem message={msg} grouping={firstGrouping} />);
    const el = container.firstElementChild;
    expect(el?.className).toContain('pt-4');
  });
});
