---
description: Disable an extension without uninstalling it
argument-hint: <name>
allowed-tools: Bash, Read
---

# Extensions Disable

Disable an extension without uninstalling it.

## Arguments

- `name` (required): The name of the extension to disable

## What This Does

1. Sets `enabled: false` in `extensions/manifest.json` for the extension
2. Runs sync to remove symlinks from `.claude/`

The extension files remain in `extensions/` and can be re-enabled later.

## Execution

```bash
python3 .claude/scripts/sync-extensions.py disable <name>
```

Example:
```bash
python3 .claude/scripts/sync-extensions.py disable my-custom-skill
```

## Output

```
Extension 'my-custom-skill' disabled
Syncing extensions...

Skills:
  - Removed skill: my-custom-skill

...

Done. Synced: 0, Removed: 1, Cleaned: 0
```

## Use Cases

- Temporarily disable an extension for debugging
- Stop using an extension without deleting it
- Test what behavior changes without the extension

## Errors

If extension not found:
```
Extension 'unknown-skill' not found
```

## Related

- `/extensions:enable` - Enable an extension
- `/extensions:list` - Show registered extensions
- `/extensions:sync` - Sync extensions to .claude/
