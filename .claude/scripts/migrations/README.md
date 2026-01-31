# Migration Scripts

This directory contains version-specific migration scripts that run during upgrades.

## Naming Convention

Scripts are named after the version they migrate TO:
- `v0.6.0.py` - Runs when upgrading TO version 0.6.0 (from any earlier version)
- `v0.7.0.py` - Runs when upgrading TO version 0.7.0

## When Migrations Run

During `/system:upgrade`, migrations run automatically:
1. Determine current version (e.g., 0.5.0)
2. Determine target version (e.g., 0.7.0)
3. Run all migrations where: `current < migration_version <= target`

For example, upgrading from 0.5.0 to 0.7.0 runs both v0.6.0.py and v0.7.0.py.

## Writing Migration Scripts

```python
#!/usr/bin/env python3
"""
v0.6.0.py - Migration to version 0.6.0

Changes:
- Describe what this migration does
"""

import os
from pathlib import Path

def get_vault_root():
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    return Path(__file__).parent.parent.parent.parent

def main():
    vault_root = get_vault_root()

    # Your migration logic here
    # Example: rename a file, move content, update config format

    print("Migration v0.6.0 complete")
    return 0

if __name__ == "__main__":
    exit(main())
```

## Guidelines

1. **Idempotent**: Migrations should be safe to run multiple times
2. **Non-destructive**: Never delete user content; rename/archive if needed
3. **Verbose**: Print what you're doing for debugging
4. **Exit codes**: Return 0 on success, non-zero on failure
5. **Dependencies**: Only use Python stdlib (no pip packages required)

## Testing

Test migrations manually before release:

```bash
export CLAUDE_PROJECT_DIR=/path/to/vault
python .claude/scripts/migrations/v0.6.0.py
```
