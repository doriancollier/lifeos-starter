import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api';

export function PermissionBanner({ sessionId }: { sessionId: string | null }) {
  const { data: session } = useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => api.getSession(sessionId!),
    enabled: !!sessionId,
  });

  if (!session || session.permissionMode !== 'dangerously-skip') return null;

  return (
    <div className="bg-red-600 text-white text-center text-sm py-1 px-4">
      Permissions bypassed - all tool calls auto-approved
    </div>
  );
}
