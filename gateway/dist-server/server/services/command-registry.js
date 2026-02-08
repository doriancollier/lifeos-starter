import fs from 'fs/promises';
import path from 'path';
import matter from 'gray-matter';
class CommandRegistryService {
    cache = null;
    commandsDir;
    constructor(vaultRoot) {
        this.commandsDir = path.join(vaultRoot, '.claude', 'commands');
    }
    async getCommands(forceRefresh = false) {
        if (this.cache && !forceRefresh)
            return this.cache;
        const commands = [];
        try {
            const entries = await fs.readdir(this.commandsDir, {
                withFileTypes: true,
            });
            for (const entry of entries) {
                if (!entry.isDirectory())
                    continue;
                const nsPath = path.join(this.commandsDir, entry.name);
                const files = await fs.readdir(nsPath);
                for (const file of files) {
                    if (!file.endsWith('.md'))
                        continue;
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
                                .map((t) => t.trim()),
                            filePath: path.relative(process.cwd(), filePath),
                        });
                    }
                    catch (fileErr) {
                        console.warn(`[CommandRegistry] Skipping ${entry.name}/${file}: ${fileErr.message}`);
                    }
                }
            }
        }
        catch (err) {
            // Commands directory might not exist
            console.warn('[CommandRegistry] Could not read commands directory:', err.message);
        }
        commands.sort((a, b) => a.fullCommand.localeCompare(b.fullCommand));
        this.cache = { commands, lastScanned: new Date().toISOString() };
        return this.cache;
    }
    invalidateCache() {
        this.cache = null;
    }
}
export { CommandRegistryService };
//# sourceMappingURL=command-registry.js.map