import type { Session } from '@shared/types';

interface SessionItemProps {
  session: Session;
  isActive: boolean;
  onClick: () => void;
}

export function SessionItem({ session, isActive, onClick }: SessionItemProps) {
  return (
    <div
      onClick={onClick}
      className={`group flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm cursor-pointer transition-colors duration-150 ${
        isActive ? 'bg-accent text-accent-foreground' : 'hover:bg-accent/50'
      }`}
    >
      <div className="flex-1 min-w-0">
        <div className="font-medium truncate">{session.title}</div>
        {session.lastMessagePreview && (
          <div className="text-xs text-muted-foreground truncate">
            {session.lastMessagePreview}
          </div>
        )}
      </div>
      {session.permissionMode === 'dangerously-skip' && (
        <span className="text-xs text-red-500 flex-shrink-0">!</span>
      )}
    </div>
  );
}
