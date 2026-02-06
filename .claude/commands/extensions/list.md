---
description: Show all registered extensions and their status
allowed-tools: Bash, Read
---

# Extensions List

Show all registered extensions and their status.

## What This Does

Reads `extensions/manifest.json` and displays:
- Extension name and type
- Enabled/disabled status
- Path to extension files
- Components (skills, commands, hooks)

## Execution

Run the list command:

```bash
python3 scripts/sync-extensions.py list
```

## Output Example

```
Registered extensions:

  my-custom-skill (skill) - enabled
    Path: skills/my-custom-skill
    Skills: my-custom-skill

  todoist (integration) - enabled
    Path: integrations/todoist
    Skills: todoist
    Hooks: sync.py

  old-extension (skill) - disabled
    Path: skills/old-extension
    Skills: old-extension
```

## No Extensions

If no extensions are registered:

```
No extensions registered
```

## Related

- `/extensions:sync` - Sync extensions to .claude/
- `/extensions:enable` - Enable an extension
- `/extensions:disable` - Disable an extension
- `extensions/README.md` - How to create extensions
