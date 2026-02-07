import { ItemView, WorkspaceLeaf } from 'obsidian';
import { createRoot, Root } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { setPlatformAdapter } from '../../client/lib/platform';
import { createObsidianAdapter } from '../lib/obsidian-adapter';
import { ObsidianProvider } from '../contexts/ObsidianContext';
import { ObsidianApp } from '../components/ObsidianApp';
import type CopilotPlugin from '../main';

export const VIEW_TYPE_COPILOT = 'lifeos-copilot-view';

export class CopilotView extends ItemView {
  root: Root | null = null;
  plugin: CopilotPlugin;
  queryClient: QueryClient;

  constructor(leaf: WorkspaceLeaf, plugin: CopilotPlugin) {
    super(leaf);
    this.plugin = plugin;
    this.queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 1 } } });
  }

  getViewType(): string { return VIEW_TYPE_COPILOT; }
  getDisplayText(): string { return 'Copilot'; }
  getIcon(): string { return 'bot'; }

  async onOpen(): Promise<void> {
    setPlatformAdapter(createObsidianAdapter(this.app));
    const container = this.containerEl.children[1] as HTMLElement;
    container.empty();
    container.addClass('copilot-view-content');
    this.root = createRoot(container);
    this.root.render(
      <ObsidianProvider app={this.app}>
        <QueryClientProvider client={this.queryClient}>
          <ObsidianApp />
        </QueryClientProvider>
      </ObsidianProvider>
    );
  }

  async onClose(): Promise<void> {
    this.root?.unmount();
    this.root = null;
  }
}
