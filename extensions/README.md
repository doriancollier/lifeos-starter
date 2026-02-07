# Extensions

User extensions for LifeOS that survive system upgrades.

## Overview

Extensions allow you to add custom skills, commands, and hooks without modifying core LifeOS files. During system upgrades, the `.claude/` directory may be updated, but your extensions in `extensions/` remain untouched.

## Directory Structure

```
extensions/
├── manifest.json          # Registry of installed extensions
├── skills/                # Custom skills
│   └── my-skill/
│       └── SKILL.md
├── commands/              # Custom commands (by namespace)
│   └── my-namespace/
│       └── my-command.md
├── hooks/                 # Custom hooks
│   └── my-hook.py
├── integrations/          # Custom integrations
│   └── todoist/
│       ├── SKILL.md
│       └── sync.py
├── channels/              # Custom notification channels
│   └── discord/
│       └── notify.py
└── tasks/                 # Custom scheduled tasks
    └── my-task/
        └── run.py
```

## How Extensions Work

1. **You create** extension files in `extensions/`
2. **You register** the extension using `/extensions:sync` or the CLI
3. **Sync creates symlinks** in `.claude/` pointing to your extension
4. **Claude Code discovers** extensions via the symlinks

Symlinks use the `ext--` prefix to distinguish extensions from core components:
```
.claude/skills/ext--my-skill/  -->  extensions/skills/my-skill/
```

## Creating a Skill Extension

1. Create the skill directory:
   ```bash
   mkdir -p extensions/skills/my-skill
   ```

2. Create `SKILL.md` with frontmatter:
   ```markdown
   ---
   description: Brief description of what this skill does
   invocation: auto | explicit
   ---

   # My Skill

   Instructions for Claude when this skill is active...
   ```

3. Register and sync:
   ```
   /extensions:sync
   ```

The skill will be auto-registered based on the directory name.

## Creating a Command Extension

1. Create the command namespace directory:
   ```bash
   mkdir -p extensions/commands/myns
   ```

2. Create command files (one per command):
   ```markdown
   # extensions/commands/myns/greet.md

   # Greet Command

   Say hello to the user in a friendly way.
   ```

3. Register and sync:
   ```
   /extensions:sync
   ```

Commands are available as `/ext--myns:greet`.

## Creating an Integration Extension

Integrations combine skills, hooks, and potentially commands:

1. Create the integration directory:
   ```bash
   mkdir -p extensions/integrations/todoist
   ```

2. Add components:
   ```
   extensions/integrations/todoist/
   ├── SKILL.md           # Skill for understanding Todoist
   ├── sync.py            # Hook for syncing tasks
   └── README.md          # Documentation
   ```

3. Register manually (integrations need explicit registration):
   ```bash
   python3 .claude/scripts/sync-extensions.py register todoist integration integrations/todoist
   ```

4. Sync:
   ```
   /extensions:sync
   ```

## Managing Extensions

### Commands

| Command | Purpose |
|---------|---------|
| `/extensions:sync` | Sync manifest to .claude/ symlinks |
| `/extensions:list` | Show installed extensions and status |
| `/extensions:enable [name]` | Enable an extension |
| `/extensions:disable [name]` | Disable an extension |

### CLI

The sync script can also be used directly:

```bash
# Sync all extensions
python3 .claude/scripts/sync-extensions.py sync

# List extensions
python3 .claude/scripts/sync-extensions.py list

# Register an extension
python3 .claude/scripts/sync-extensions.py register my-skill skill skills/my-skill

# Enable/disable
python3 .claude/scripts/sync-extensions.py enable my-skill
python3 .claude/scripts/sync-extensions.py disable my-skill

# Unregister (remove from manifest)
python3 .claude/scripts/sync-extensions.py unregister my-skill
```

## Manifest Format

The `manifest.json` tracks all registered extensions:

```json
{
  "version": "1.0",
  "extensions": [
    {
      "name": "my-skill",
      "type": "skill",
      "path": "skills/my-skill",
      "enabled": true,
      "installed": "2026-02-06",
      "components": {
        "skills": ["my-skill"],
        "commands": [],
        "hooks": []
      }
    }
  ]
}
```

## Auto-Sync Points

Extensions are automatically synced during:
- `/system:upgrade` (after core files are updated)
- `/system:configure-hooks` (to update settings.json)

## Naming Conventions

- Extension names should be lowercase with hyphens: `my-custom-skill`
- Command namespaces should be short: `myns`
- Avoid names that conflict with core components

## Troubleshooting

### Extension not discovered

1. Check the symlink exists: `ls -la .claude/skills/ext--my-skill`
2. Verify the SKILL.md has proper frontmatter
3. Run `/extensions:sync` again

### Symlink broken after upgrade

Run `/extensions:sync` to recreate symlinks.

### Extension conflicts with core

Rename your extension to avoid the conflict. The `ext--` prefix should prevent most conflicts.

## Extension vs Core

| Aspect | Core (`.claude/`) | Extensions (`extensions/`) |
|--------|-------------------|---------------------------|
| Survives upgrades | No | Yes |
| Managed by | System | User |
| Prefix | None | `ext--` |
| Discovery | Direct | Via symlink |

## Best Practices

1. **Keep extensions focused** - One skill per directory
2. **Document your extensions** - Include README.md files
3. **Test after upgrades** - Run `/extensions:sync` after system updates
4. **Back up your extensions** - They contain your customizations
5. **Use descriptive names** - Make the purpose clear from the name
