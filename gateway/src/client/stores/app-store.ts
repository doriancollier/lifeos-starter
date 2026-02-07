import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface AppState {
  sidebarOpen: boolean;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>()(devtools((set) => ({
  sidebarOpen: true,

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}), { name: 'app-store' }));
