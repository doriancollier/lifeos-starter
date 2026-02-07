import { useCallback, useEffect } from 'react';
import { TFile } from 'obsidian';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { App } from '../../client/App';
import { useAppStore } from '../../client/stores/app-store';
import { useSessionId } from '../../client/hooks/use-session-id';
import { api } from '../../client/lib/api';
import { useObsidian } from '../contexts/ObsidianContext';
import { useActiveFile } from '../hooks/use-active-file';
import { useFileOpener } from '../hooks/use-file-opener';
import { ContextBar } from './ContextBar';
import { ConnectionStatus } from './ConnectionStatus';
import { Plus } from 'lucide-react';

export function ObsidianApp() {
  const { app } = useObsidian();
  const activeFile = useActiveFile();
  const { contextFiles, addContextFile, removeContextFile } = useAppStore();
  const { openFile } = useFileOpener();
  const [sessionId, setSessionId] = useSessionId();
  const queryClient = useQueryClient();

  const createSession = useMutation({
    mutationFn: () => api.createSession({ permissionMode: 'default' }),
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      setSessionId(session.id);
    },
  });

  // Auto-create session on mount if none active
  useEffect(() => {
    if (!sessionId && !createSession.isPending) {
      createSession.mutate();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const transformContent = useCallback(async (content: string): Promise<string> => {
    const parts: string[] = [];

    if (activeFile) {
      const file = app.vault.getAbstractFileByPath(activeFile.path);
      if (file instanceof TFile) {
        const text = await app.vault.cachedRead(file);
        parts.push(`<context file="${activeFile.path}">\n${text}\n</context>`);
      }
    }

    for (const cf of contextFiles) {
      if (activeFile && cf.path === activeFile.path) continue;
      const file = app.vault.getAbstractFileByPath(cf.path);
      if (file instanceof TFile) {
        const text = await app.vault.cachedRead(file);
        parts.push(`<context file="${cf.path}">\n${text}\n</context>`);
      }
    }

    if (parts.length > 0) {
      return parts.join('\n\n') + '\n\n' + content;
    }
    return content;
  }, [app, activeFile, contextFiles]);

  return (
    <div className="flex flex-col h-full">
      <ConnectionStatus />
      <div className="flex items-center justify-between px-3 py-1.5 border-b">
        <ContextBar
          activeFile={activeFile}
          contextFiles={contextFiles}
          onRemoveFile={removeContextFile}
          onDrop={(path, basename) => addContextFile({ path, basename })}
          onFileClick={openFile}
        />
        <button
          onClick={() => createSession.mutate()}
          disabled={createSession.isPending}
          className="shrink-0 p-1 rounded hover:bg-accent transition-colors"
          aria-label="New chat"
          title="New chat"
        >
          <Plus className="h-4 w-4 text-muted-foreground" />
        </button>
      </div>
      <App transformContent={transformContent} embedded />
    </div>
  );
}
