import { Router } from 'express';
import { CommandRegistryService } from '../services/command-registry';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const vaultRoot = path.resolve(__dirname, '../../../../');
const registry = new CommandRegistryService(vaultRoot);
const router = Router();

// GET /api/commands - List all commands (with optional refresh)
router.get('/', async (req, res) => {
  const refresh = req.query.refresh === 'true';
  const commands = await registry.getCommands(refresh);
  res.json(commands);
});

export default router;
