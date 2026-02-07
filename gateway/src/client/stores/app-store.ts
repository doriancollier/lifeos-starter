import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface AppState {
  activeSessionId: string | null;
  sidebarOpen: boolean;

  setActiveSession: (id: string | null) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>()(devtools((set) => ({
  activeSessionId: localStorage.getItem('activeSessionId'),
  sidebarOpen: true,

  setActiveSession: (id) => {
    if (id) {
      localStorage.setItem('activeSessionId', id);
    } else {
      localStorage.removeItem('activeSessionId');
    }
    set({ activeSessionId: id });
  },

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}), { name: 'app-store' }));
