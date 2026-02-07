import { App, TFile } from 'obsidian';
import { PlatformAdapter } from '../../client/lib/platform';
import { useAppStore } from '../../client/stores/app-store';

export function createObsidianAdapter(app: App): PlatformAdapter {
  return {
    apiBaseUrl: 'http://localhost:6942/api',
    isEmbedded: true,
    getSessionId: () => useAppStore.getState().sessionId,
    setSessionId: (id) => useAppStore.getState().setSessionId(id),
    openFile: async (path: string) => {
      const file = app.vault.getAbstractFileByPath(path);
      if (file instanceof TFile) {
        await app.workspace.getLeaf(false).openFile(file);
      }
    },
  };
}
