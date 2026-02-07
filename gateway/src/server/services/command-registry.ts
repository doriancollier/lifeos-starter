import fs from 'fs/promises';
import path from 'path';
import matter from 'gray-matter';
import type { CommandEntry, CommandRegistry } from '../../shared/types.js';

class CommandRegistryService {
  private cache: CommandRegistry | null = null;
  private readonly commandsDir: string;

  constructor(vaultRoot: string) {
    this.commandsDir = path.join(vaultRoot, '.claude', 'commands');
  }

  async getCommands(forceRefresh = false): Promise<CommandRegistry> {
    if (this.cache && !forceRefresh) return this.cache;

    const commands: CommandEntry[] = [];

    try {
      const entries = await fs.readdir(this.commandsDir, {
        withFileTypes: true,
      });

      for (const entry of entries) {
        if (!entry.isDirectory()) continue;

        const nsPath = path.join(this.commandsDir, entry.name);
        const files = await fs.readdir(nsPath);

        for (const file of files) {
          if (!file.endsWith('.md')) continue;

          const filePath = path.join(nsPath, file);
          try {
            const content = await fs.readFile(filePath, 'utf-8');
            const { data: frontmatter } = matter(content);

            const commandName = file.replace('.md', '');
            commands.push({
              namespace: entry.name,
              command: commandName,
              fullCommand: `/${entry.name}:${commandName}`,
              description: frontmatter.description || '',
              argumentHint: frontmatter['argument-hint'],
              allowedTools: frontmatter['allowed-tools']
                ?.split(',')
                .map((t: string) => t.trim()),
              filePath: path.relative(process.cwd(), filePath),
            });
          } catch (fileErr) {
            console.warn(`[CommandRegistry] Skipping ${entry.name}/${file}: ${(fileErr as Error).message}`);
          }
        }
      }
    } catch (err) {
      // Commands directory might not exist
      console.warn('[CommandRegistry] Could not read commands directory:', (err as Error).message);
    }

    commands.sort((a, b) => a.fullCommand.localeCompare(b.fullCommand));

    this.cache = { commands, lastScanned: new Date().toISOString() };
    return this.cache;
  }

  invalidateCache(): void {
    this.cache = null;
  }
}

export { CommandRegistryService };
