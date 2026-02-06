---
description: Sync extensions from extensions/ to .claude/ via symlinks
allowed-tools: Bash, Read
---

# Extensions Sync

Sync extensions from `extensions/` to `.claude/` via symlinks.

## What This Does

1. Reads `extensions/manifest.json` for registered extensions
2. Creates symlinks in `.claude/` for enabled extensions (prefixed with `ext--`)
3. Removes symlinks for disabled extensions
4. Cleans up orphaned symlinks pointing to non-existent targets
5. Updates `settings.json` for extension hooks

## Execution

Run the sync script:

```bash
python3 scripts/sync-extensions.py sync
```

## Output

Report what was synced, removed, and cleaned:

```
Syncing extensions...

Skills:
  + Linked skill: my-custom-skill

Commands:
  + Linked commands: myns

Hooks:
  (no changes)

Cleanup:
  (no orphans)

Done. Synced: 2, Removed: 0, Cleaned: 0
```

## When to Run

- After adding new extensions to `extensions/`
- After running `/system:upgrade` (run automatically)
- After enabling/disabling extensions
- If extensions aren't being discovered by Claude

## Related

- `/extensions:list` - Show registered extensions
- `/extensions:enable` - Enable an extension
- `/extensions:disable` - Disable an extension
- `extensions/README.md` - How to create extensions
