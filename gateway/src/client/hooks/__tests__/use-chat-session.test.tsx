import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChatSession } from '../use-chat-session';
import { createMockReadableStream, formatSSE } from '../../../test-utils/react-helpers';

// Mock the api module so getMessages doesn't hit real fetch on mount
vi.mock('../../lib/api', () => ({
  api: {
    getMessages: vi.fn().mockResolvedValue({ messages: [] }),
  },
}));

import { api } from '../../lib/api';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

// Mock crypto.randomUUID
const mockUUID = vi.fn();
let uuidCounter = 0;
mockUUID.mockImplementation(() => `uuid-${++uuidCounter}`);
Object.defineProperty(globalThis.crypto, 'randomUUID', {
  value: mockUUID,
  writable: true,
});

describe('useChatSession', () => {
  const fetchSpy = vi.spyOn(globalThis, 'fetch');

  beforeEach(() => {
    vi.clearAllMocks();
    uuidCounter = 0;
    // Default: return empty history
    (api.getMessages as ReturnType<typeof vi.fn>).mockResolvedValue({ messages: [] });
  });

  afterEach(() => {
    fetchSpy.mockReset();
  });

  it('initializes with empty messages and transitions to idle', async () => {
    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    // Wait for history loading to complete
    await waitFor(() => {
      expect(result.current.status).toBe('idle');
    });

    expect(result.current.messages).toEqual([]);
    expect(result.current.error).toBeNull();
    expect(result.current.input).toBe('');
  });

  it('loads history messages on mount', async () => {
    (api.getMessages as ReturnType<typeof vi.fn>).mockResolvedValue({
      messages: [
        { id: 'h1', role: 'user', content: 'Previous question' },
        { id: 'h2', role: 'assistant', content: 'Previous answer', toolCalls: [
          { toolCallId: 'tc1', toolName: 'Read', status: 'complete' },
        ]},
      ],
    });

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => {
      expect(result.current.messages).toHaveLength(2);
    });

    expect(result.current.messages[0].content).toBe('Previous question');
    expect(result.current.messages[1].content).toBe('Previous answer');
    expect(result.current.messages[1].toolCalls).toHaveLength(1);
    expect(result.current.messages[1].toolCalls![0].toolName).toBe('Read');
    expect(result.current.isLoadingHistory).toBe(false);
  });

  it('ignores empty input on submit', async () => {
    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('   ');
      await result.current.handleSubmit();
    });

    expect(result.current.messages).toEqual([]);
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('adds user message on submit and clears input', async () => {
    const sseText = formatSSE('done', { sessionId: 's1' });
    const stream = createMockReadableStream([sseText]);
    fetchSpy.mockResolvedValueOnce(new Response(stream, { status: 200 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('Hello');
    });

    await act(async () => {
      await result.current.handleSubmit();
    });

    expect(result.current.input).toBe('');
    // Should have user message + assistant placeholder
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].role).toBe('user');
    expect(result.current.messages[0].content).toBe('Hello');
  });

  it('parses text_delta events into assistant message content', async () => {
    const sseText =
      formatSSE('text_delta', { text: 'Hello ' }) +
      formatSSE('text_delta', { text: 'World' }) +
      formatSSE('done', { sessionId: 's1' });
    const stream = createMockReadableStream([sseText]);
    fetchSpy.mockResolvedValueOnce(new Response(stream, { status: 200 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('Hi');
    });
    await act(async () => {
      await result.current.handleSubmit();
    });

    const assistantMsg = result.current.messages.find(m => m.role === 'assistant');
    expect(assistantMsg?.content).toBe('Hello World');
  });

  it('handles tool_call_start -> tool_call_delta -> tool_call_end lifecycle', async () => {
    const sseText =
      formatSSE('tool_call_start', { toolCallId: 'tc1', toolName: 'Read', status: 'running' }) +
      formatSSE('tool_call_delta', { toolCallId: 'tc1', toolName: 'Read', input: '{"path": "/foo"}', status: 'running' }) +
      formatSSE('tool_call_end', { toolCallId: 'tc1', toolName: 'Read', status: 'complete' }) +
      formatSSE('done', { sessionId: 's1' });
    const stream = createMockReadableStream([sseText]);
    fetchSpy.mockResolvedValueOnce(new Response(stream, { status: 200 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('Read file');
    });
    await act(async () => {
      await result.current.handleSubmit();
    });

    const assistantMsg = result.current.messages.find(m => m.role === 'assistant');
    expect(assistantMsg?.toolCalls).toHaveLength(1);
    expect(assistantMsg?.toolCalls![0].toolName).toBe('Read');
    expect(assistantMsg?.toolCalls![0].status).toBe('complete');
    expect(assistantMsg?.toolCalls![0].input).toBe('{"path": "/foo"}');
  });

  it('handles tool_result events', async () => {
    const sseText =
      formatSSE('tool_call_start', { toolCallId: 'tc1', toolName: 'Read', status: 'running' }) +
      formatSSE('tool_result', { toolCallId: 'tc1', toolName: 'Read', result: 'file contents', status: 'complete' }) +
      formatSSE('done', { sessionId: 's1' });
    const stream = createMockReadableStream([sseText]);
    fetchSpy.mockResolvedValueOnce(new Response(stream, { status: 200 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('Read');
    });
    await act(async () => {
      await result.current.handleSubmit();
    });

    const assistantMsg = result.current.messages.find(m => m.role === 'assistant');
    expect(assistantMsg?.toolCalls![0].result).toBe('file contents');
    expect(assistantMsg?.toolCalls![0].status).toBe('complete');
  });

  it('sets error message on error events', async () => {
    const sseText =
      formatSSE('error', { message: 'Something went wrong' }) +
      formatSSE('done', { sessionId: 's1' });
    const stream = createMockReadableStream([sseText]);
    fetchSpy.mockResolvedValueOnce(new Response(stream, { status: 200 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('fail');
    });
    await act(async () => {
      await result.current.handleSubmit();
    });

    expect(result.current.error).toBe('Something went wrong');
  });

  it('returns to idle on done events', async () => {
    const sseText = formatSSE('done', { sessionId: 's1' });
    const stream = createMockReadableStream([sseText]);
    fetchSpy.mockResolvedValueOnce(new Response(stream, { status: 200 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('test');
    });
    await act(async () => {
      await result.current.handleSubmit();
    });

    expect(result.current.status).toBe('idle');
  });

  it('handles multiple SSE events across separate chunks', async () => {
    const chunk1 = formatSSE('text_delta', { text: 'chunk1' });
    const chunk2 = formatSSE('text_delta', { text: 'chunk2' });
    const chunk3 = formatSSE('done', { sessionId: 's1' });
    const stream = createMockReadableStream([chunk1, chunk2, chunk3]);
    fetchSpy.mockResolvedValueOnce(new Response(stream, { status: 200 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('test');
    });
    await act(async () => {
      await result.current.handleSubmit();
    });

    const assistantMsg = result.current.messages.find(m => m.role === 'assistant');
    expect(assistantMsg?.content).toBe('chunk1chunk2');
  });

  it('stop() aborts the fetch controller', async () => {
    // Create a stream that never ends
    let controllerRef: ReadableStreamDefaultController<Uint8Array> | null = null;
    const neverEndingStream = new ReadableStream<Uint8Array>({
      start(controller) {
        controllerRef = controller;
      },
    });
    fetchSpy.mockResolvedValueOnce(new Response(neverEndingStream, { status: 200 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('test');
    });

    // Start streaming (don't await - it will hang)
    let submitPromise: Promise<void>;
    act(() => {
      submitPromise = result.current.handleSubmit();
    });

    // Stop immediately
    await act(async () => {
      result.current.stop();
    });

    expect(result.current.status).toBe('idle');

    // Clean up
    controllerRef?.close();
  });

  it('handles HTTP error responses', async () => {
    fetchSpy.mockResolvedValueOnce(new Response('Not Found', { status: 404 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('test');
    });
    await act(async () => {
      await result.current.handleSubmit();
    });

    expect(result.current.status).toBe('error');
    expect(result.current.error).toBe('HTTP 404');
  });

  it('sends correct fetch request', async () => {
    const sseText = formatSSE('done', { sessionId: 's1' });
    const stream = createMockReadableStream([sseText]);
    fetchSpy.mockResolvedValueOnce(new Response(stream, { status: 200 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.status).toBe('idle'));

    await act(async () => {
      result.current.setInput('Hello');
    });
    await act(async () => {
      await result.current.handleSubmit();
    });

    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/sessions/s1/messages',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: 'Hello' }),
      })
    );
  });

  it('appends new messages after history', async () => {
    (api.getMessages as ReturnType<typeof vi.fn>).mockResolvedValue({
      messages: [
        { id: 'h1', role: 'user', content: 'Old message' },
        { id: 'h2', role: 'assistant', content: 'Old reply' },
      ],
    });

    const sseText =
      formatSSE('text_delta', { text: 'New reply' }) +
      formatSSE('done', { sessionId: 's1' });
    const stream = createMockReadableStream([sseText]);
    fetchSpy.mockResolvedValueOnce(new Response(stream, { status: 200 }));

    const { result } = renderHook(() => useChatSession('s1'), { wrapper: createWrapper() });

    await waitFor(() => {
      expect(result.current.messages).toHaveLength(2);
    });

    await act(async () => {
      result.current.setInput('New question');
    });
    await act(async () => {
      await result.current.handleSubmit();
    });

    // 2 history + 1 new user + 1 new assistant = 4
    expect(result.current.messages).toHaveLength(4);
    expect(result.current.messages[2].role).toBe('user');
    expect(result.current.messages[2].content).toBe('New question');
    expect(result.current.messages[3].role).toBe('assistant');
    expect(result.current.messages[3].content).toBe('New reply');
  });
});
