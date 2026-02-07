// @vitest-environment jsdom
import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PermissionBanner } from '../PermissionBanner';

afterEach(() => {
  cleanup();
});

function createWrapper(sessionData?: Record<string, unknown>) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  if (sessionData) {
    queryClient.setQueryData(['session', sessionData.id], sessionData);
  }
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('PermissionBanner', () => {
  it('returns null when sessionId is null', () => {
    const { container } = render(
      <PermissionBanner sessionId={null} />,
      { wrapper: createWrapper() }
    );
    expect(container.textContent).toBe('');
  });

  it('returns null when session has no data yet', () => {
    const { container } = render(
      <PermissionBanner sessionId="s-unknown" />,
      { wrapper: createWrapper() }
    );
    expect(container.textContent).toBe('');
  });

  it('returns null for default permission mode', () => {
    const session = {
      id: 's1',
      permissionMode: 'default',
      title: 'Test',
      createdAt: '',
      updatedAt: '',
    };
    const { container } = render(
      <PermissionBanner sessionId="s1" />,
      { wrapper: createWrapper(session) }
    );
    expect(container.textContent).toBe('');
  });

  it('shows banner for dangerously-skip mode', () => {
    const session = {
      id: 's2',
      permissionMode: 'dangerously-skip',
      title: 'Test',
      createdAt: '',
      updatedAt: '',
    };
    render(
      <PermissionBanner sessionId="s2" />,
      { wrapper: createWrapper(session) }
    );
    expect(screen.getByText(/Permissions bypassed/)).toBeDefined();
  });

  it('banner contains auto-approved text', () => {
    const session = {
      id: 's3',
      permissionMode: 'dangerously-skip',
      title: 'Test Session',
      createdAt: '',
      updatedAt: '',
    };
    render(
      <PermissionBanner sessionId="s3" />,
      { wrapper: createWrapper(session) }
    );
    expect(screen.getByText(/auto-approved/)).toBeDefined();
  });
});
