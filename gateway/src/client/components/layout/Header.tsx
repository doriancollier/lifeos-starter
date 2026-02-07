import { useAppStore } from '../../stores/app-store';
import { PanelLeft } from 'lucide-react';

export function Header() {
  const { toggleSidebar } = useAppStore();

  return (
    <header className="flex items-center gap-2 border-b px-4 py-2 h-12">
      <button
        onClick={toggleSidebar}
        className="p-1 rounded hover:bg-accent"
        aria-label="Toggle sidebar"
      >
        <PanelLeft className="h-5 w-5" />
      </button>
      <h1 className="text-sm font-semibold flex-1">LifeOS Gateway</h1>
    </header>
  );
}
