import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SessionSidebar } from '../SessionSidebar';
import { api } from '../../../lib/api';
import type { Session } from '@shared/types';

// Mock motion/react
vi.mock('motion/react', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock api
vi.mock('../../../lib/api', () => ({
  api: {
    listSessions: vi.fn(),
    createSession: vi.fn(),
  },
}));

// Mock useSessionId (nuqs-backed)
const mockSetSessionId = vi.fn();
vi.mock('../../../hooks/use-session-id', () => ({
  useSessionId: () => [null, mockSetSessionId] as const,
}));

// Mock app store (sidebar state)
const mockSetSidebarOpen = vi.fn();
vi.mock('../../../stores/app-store', () => ({
  useAppStore: () => ({ setSidebarOpen: mockSetSidebarOpen }),
}));

// Mock useIsMobile
vi.mock('../../../hooks/use-is-mobile', () => ({
  useIsMobile: () => false,
}));

// Mock session-utils to avoid time-dependent behavior
vi.mock('../../../lib/session-utils', () => ({
  groupSessionsByTime: (sessions: Session[]) => {
    if (sessions.length === 0) return [];
    // Group all sessions under a single label for simplicity
    const today = sessions.filter(s => s.updatedAt >= '2026-02-07');
    const older = sessions.filter(s => s.updatedAt < '2026-02-07');
    const groups = [];
    if (today.length > 0) groups.push({ label: 'Today', sessions: today });
    if (older.length > 0) groups.push({ label: 'Older', sessions: older });
    return groups;
  },
  formatRelativeTime: (iso: string) => iso >= '2026-02-07' ? '1h ago' : 'Jan 1, 3pm',
}));

function makeSession(overrides: Partial<Session> = {}): Session {
  return {
    id: overrides.id ?? 'session-1',
    title: overrides.title ?? 'Test session',
    createdAt: overrides.createdAt ?? '2026-02-07T10:00:00Z',
    updatedAt: overrides.updatedAt ?? '2026-02-07T14:00:00Z',
    permissionMode: overrides.permissionMode ?? 'default',
    ...overrides,
  };
}

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
}

describe('SessionSidebar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.listSessions).mockResolvedValue([]);
    mockSetSidebarOpen.mockClear();
  });
  afterEach(() => {
    cleanup();
  });

  it('renders "New chat" button', () => {
    renderWithQuery(<SessionSidebar />);
    expect(screen.getByText('New chat')).toBeDefined();
  });

  it('renders permission toggle defaulting to "Require approval"', () => {
    renderWithQuery(<SessionSidebar />);
    expect(screen.getByText('Require approval')).toBeDefined();
  });

  it('toggles permission mode on click', () => {
    renderWithQuery(<SessionSidebar />);
    fireEvent.click(screen.getByText('Require approval'));
    expect(screen.getByText('Skip permissions')).toBeDefined();
  });

  it('shows empty state when no sessions', async () => {
    renderWithQuery(<SessionSidebar />);
    await waitFor(() => {
      expect(screen.getByText('No conversations yet')).toBeDefined();
    });
  });

  it('renders sessions grouped by time', async () => {
    vi.mocked(api.listSessions).mockResolvedValue([
      makeSession({ id: 's1', title: 'Today session', updatedAt: '2026-02-07T12:00:00Z' }),
      makeSession({ id: 's2', title: 'Old session', updatedAt: '2025-06-01T10:00:00Z' }),
    ]);

    renderWithQuery(<SessionSidebar />);

    await waitFor(() => {
      expect(screen.getByText('Today')).toBeDefined();
      expect(screen.getByText('Older')).toBeDefined();
    });

    expect(screen.getByText('Today session')).toBeDefined();
    expect(screen.getByText('Old session')).toBeDefined();
  });

  it('creates session on "New chat" click', async () => {
    const newSession = makeSession({ id: 'new-1', title: 'New session' });
    vi.mocked(api.createSession).mockResolvedValue(newSession);

    renderWithQuery(<SessionSidebar />);
    fireEvent.click(screen.getByText('New chat'));

    await waitFor(() => {
      expect(vi.mocked(api.createSession).mock.calls[0][0]).toEqual({ permissionMode: 'default' });
    });
  });

  it('renders close sidebar button', () => {
    renderWithQuery(<SessionSidebar />);
    expect(screen.getByLabelText('Close sidebar')).toBeDefined();
  });

  it('closes sidebar when close button clicked', () => {
    renderWithQuery(<SessionSidebar />);
    fireEvent.click(screen.getByLabelText('Close sidebar'));
    expect(mockSetSidebarOpen).toHaveBeenCalledWith(false);
  });

  it('hides "Today" header when it is the only group', async () => {
    vi.mocked(api.listSessions).mockResolvedValue([
      makeSession({ id: 's1', title: 'Only today', updatedAt: '2026-02-07T12:00:00Z' }),
    ]);

    renderWithQuery(<SessionSidebar />);

    await waitFor(() => {
      expect(screen.getByText('Only today')).toBeDefined();
    });

    expect(screen.queryByText('Today')).toBeNull();
  });

  it('creates session with dangerously-skip when toggled', async () => {
    const newSession = makeSession({ id: 'new-1', permissionMode: 'dangerously-skip' });
    vi.mocked(api.createSession).mockResolvedValue(newSession);

    renderWithQuery(<SessionSidebar />);

    fireEvent.click(screen.getByText('Require approval'));
    expect(screen.getByText('Skip permissions')).toBeDefined();

    fireEvent.click(screen.getByText('New chat'));

    await waitFor(() => {
      expect(vi.mocked(api.createSession).mock.calls[0][0]).toEqual({ permissionMode: 'dangerously-skip' });
    });
  });
});
