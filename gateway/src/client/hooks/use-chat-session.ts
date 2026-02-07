import { useState, useCallback, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { TextDelta, ToolCallEvent, ErrorEvent } from '@shared/types';
import { api } from '../lib/api';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: ToolCallState[];
  timestamp: string;
}

export type GroupPosition = 'only' | 'first' | 'middle' | 'last';

export interface MessageGrouping {
  position: GroupPosition;
  groupIndex: number;
}

export interface ToolCallState {
  toolCallId: string;
  toolName: string;
  input: string;
  result?: string;
  status: 'pending' | 'running' | 'complete' | 'error';
}

type ChatStatus = 'idle' | 'streaming' | 'error';

export function useChatSession(sessionId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState<ChatStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const currentAssistantRef = useRef<string>('');
  const currentToolCallsRef = useRef<ToolCallState[]>([]);
  const historySeededRef = useRef(false);

  // Load message history from SDK transcript via TanStack Query
  const historyQuery = useQuery({
    queryKey: ['messages', sessionId],
    queryFn: () => api.getMessages(sessionId),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  // Seed local messages state from history (once per mount)
  useEffect(() => {
    if (historyQuery.data && !historySeededRef.current) {
      historySeededRef.current = true;
      const history = historyQuery.data.messages;
      if (history.length > 0) {
        setMessages(history.map(m => ({
          id: m.id,
          role: m.role,
          content: m.content,
          toolCalls: m.toolCalls?.map(tc => ({
            toolCallId: tc.toolCallId,
            toolName: tc.toolName,
            input: '',
            status: 'complete' as const,
          })),
          timestamp: m.timestamp || '',
        })));
      }
    }
  }, [historyQuery.data]);

  const handleSubmit = useCallback(async () => {
    if (!input.trim() || status === 'streaming') return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setStatus('streaming');
    setError(null);
    currentAssistantRef.current = '';
    currentToolCallsRef.current = [];

    const assistantId = crypto.randomUUID();
    setMessages(prev => [...prev, {
      id: assistantId,
      role: 'assistant',
      content: '',
      toolCalls: [],
      timestamp: new Date().toISOString(),
    }]);

    const abortController = new AbortController();
    abortRef.current = abortController;

    try {
      const response = await fetch(`/api/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: userMessage.content }),
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let eventType = '';
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7).trim();
          } else if (line.startsWith('data: ') && eventType) {
            const data = JSON.parse(line.slice(6));
            handleStreamEvent(eventType, data, assistantId);
            eventType = '';
          }
        }
      }

      setStatus('idle');
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setError((err as Error).message);
        setStatus('error');
      }
    }
  }, [input, status, sessionId]);

  function handleStreamEvent(type: string, data: unknown, assistantId: string) {
    switch (type) {
      case 'text_delta': {
        const { text } = data as TextDelta;
        currentAssistantRef.current += text;
        updateAssistantMessage(assistantId);
        break;
      }
      case 'tool_call_start': {
        const tc = data as ToolCallEvent;
        currentToolCallsRef.current.push({
          toolCallId: tc.toolCallId,
          toolName: tc.toolName,
          input: '',
          status: 'running',
        });
        updateAssistantMessage(assistantId);
        break;
      }
      case 'tool_call_delta': {
        const tc = data as ToolCallEvent;
        const existing = currentToolCallsRef.current.find(t => t.toolCallId === tc.toolCallId);
        if (existing && tc.input) {
          existing.input += tc.input;
        }
        updateAssistantMessage(assistantId);
        break;
      }
      case 'tool_call_end': {
        const tc = data as ToolCallEvent;
        const existing = currentToolCallsRef.current.find(t => t.toolCallId === tc.toolCallId);
        if (existing) {
          existing.status = 'complete';
        }
        updateAssistantMessage(assistantId);
        break;
      }
      case 'tool_result': {
        const tc = data as ToolCallEvent;
        const existing = currentToolCallsRef.current.find(t => t.toolCallId === tc.toolCallId);
        if (existing) {
          existing.result = tc.result;
          existing.status = 'complete';
        }
        updateAssistantMessage(assistantId);
        break;
      }
      case 'error': {
        const { message } = data as ErrorEvent;
        setError(message);
        setStatus('error');
        break;
      }
      case 'done': {
        setStatus('idle');
        break;
      }
    }
  }

  function updateAssistantMessage(assistantId: string) {
    setMessages(prev =>
      prev.map(m =>
        m.id === assistantId
          ? {
              ...m,
              content: currentAssistantRef.current,
              toolCalls: [...currentToolCallsRef.current],
            }
          : m
      )
    );
  }

  const stop = useCallback(() => {
    abortRef.current?.abort();
    setStatus('idle');
  }, []);

  const isLoadingHistory = historyQuery.isLoading;

  return { messages, input, setInput, handleSubmit, status, error, stop, isLoadingHistory };
}
