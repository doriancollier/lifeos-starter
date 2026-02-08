import type { CommandRegistry } from '../../shared/types.js';
declare class CommandRegistryService {
    private cache;
    private readonly commandsDir;
    constructor(vaultRoot: string);
    getCommands(forceRefresh?: boolean): Promise<CommandRegistry>;
    invalidateCache(): void;
}
export { CommandRegistryService };
//# sourceMappingURL=command-registry.d.ts.map