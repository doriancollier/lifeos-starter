---
description: Enable a disabled extension
argument-hint: <name>
allowed-tools: Bash, Read
---

# Extensions Enable

Enable a disabled extension.

## Arguments

- `name` (required): The name of the extension to enable

## What This Does

1. Sets `enabled: true` in `extensions/manifest.json` for the extension
2. Runs sync to create symlinks in `.claude/`

## Execution

```bash
python3 scripts/sync-extensions.py enable <name>
```

Example:
```bash
python3 scripts/sync-extensions.py enable my-custom-skill
```

## Output

```
Extension 'my-custom-skill' enabled
Syncing extensions...

Skills:
  + Linked skill: my-custom-skill

...

Done. Synced: 1, Removed: 0, Cleaned: 0
```

## Errors

If extension not found:
```
Extension 'unknown-skill' not found
```

## Related

- `/extensions:disable` - Disable an extension
- `/extensions:list` - Show registered extensions
- `/extensions:sync` - Sync extensions to .claude/
