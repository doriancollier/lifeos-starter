import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';

describe('api client', () => {
  const fetchSpy = vi.spyOn(globalThis, 'fetch');

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    fetchSpy.mockReset();
  });

  it('listSessions sends GET /api/sessions', async () => {
    const sessions = [{ id: 's1', title: 'S1' }];
    fetchSpy.mockResolvedValueOnce(
      new Response(JSON.stringify(sessions), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const { api } = await import('../../lib/api');
    const result = await api.listSessions();
    expect(result).toEqual(sessions);
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/sessions',
      expect.objectContaining({ headers: { 'Content-Type': 'application/json' } })
    );
  });

  it('createSession sends POST /api/sessions with body', async () => {
    const session = { id: 's1', title: 'New Session', createdAt: '2024-01-01', updatedAt: '2024-01-01', permissionMode: 'default' };
    fetchSpy.mockResolvedValueOnce(
      new Response(JSON.stringify(session), { status: 200, headers: { 'Content-Type': 'application/json' } })
    );

    const { api } = await import('../../lib/api');
    const result = await api.createSession({ permissionMode: 'default' });
    expect(result).toEqual(session);
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/sessions',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ permissionMode: 'default' }),
      })
    );
  });

  it('throws on non-ok response', async () => {
    fetchSpy.mockResolvedValueOnce(
      new Response(JSON.stringify({ error: 'Not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const { api } = await import('../../lib/api');
    await expect(api.getSession('missing')).rejects.toThrow('Not found');
  });

  it('getMessageStreamUrl returns correct URL', async () => {
    const { api } = await import('../../lib/api');
    expect(api.getMessageStreamUrl('s1')).toBe('/api/sessions/s1/messages');
  });
});
