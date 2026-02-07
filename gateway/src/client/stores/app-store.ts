import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface ContextFile {
  id: string;
  path: string;
  basename: string;
}

interface AppState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;

  sessionId: string | null;
  setSessionId: (id: string | null) => void;

  contextFiles: ContextFile[];
  addContextFile: (file: Omit<ContextFile, 'id'>) => void;
  removeContextFile: (id: string) => void;
  clearContextFiles: () => void;
}

export const useAppStore = create<AppState>()(devtools((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  sessionId: null,
  setSessionId: (id) => set({ sessionId: id }),

  contextFiles: [],
  addContextFile: (file) =>
    set((s) => {
      if (s.contextFiles.some((f) => f.path === file.path)) return s;
      return { contextFiles: [...s.contextFiles, { ...file, id: crypto.randomUUID() }] };
    }),
  removeContextFile: (id) =>
    set((s) => ({ contextFiles: s.contextFiles.filter((f) => f.id !== id) })),
  clearContextFiles: () => set({ contextFiles: [] }),
}), { name: 'app-store' }));
