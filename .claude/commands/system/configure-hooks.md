---
description: Regenerate settings.json from integration configuration
argument-hint: [--dry-run] [--verbose] [--list-hooks]
allowed-tools: Bash, Read
---

# System Configure Hooks Command

Regenerate `.claude/settings.json` based on enabled integrations in `.user/integrations.yaml`.

## Purpose

This command maintains the hook configuration by:
1. Reading `.user/integrations.yaml` to see which integrations are enabled
2. Generating `.claude/settings.json` with appropriate hooks

### Core Hooks (Always Enabled)

These provide essential vault functionality:
- `session-context-loader.py` - Load daily context
- `prompt-timestamp.py` - Add timestamps
- `directory-guard.py` - Enforce directory structure
- `calendar-protection.py` - Protect calendar events
- `frontmatter-validator.py` - Validate YAML frontmatter
- `task-format-validator.py` - Validate task formatting
- `table-format-validator.py` - Validate table formatting
- `task-sync-detector.py` - Queue task syncs

### Integration Hooks (Conditional)

These are enabled based on `.user/integrations.yaml`:

| Integration | Hooks |
|-------------|-------|
| `reminders` | `reminders-session-sync.py`, `reminders-task-detector.py` |
| `health` | `health-session-sync.py` |

## Arguments

- `$ARGUMENTS` - Optional flags:
  - `--dry-run` - Show what would be generated without writing
  - `--verbose` - Show detailed hook configuration
  - `--list-hooks` - List all available hooks and their integrations

## Task

### Step 1: Check Prerequisites

Verify that `.user/integrations.yaml` exists. If not, use defaults (core hooks only).

### Step 2: Run Configuration Script

Execute the hook configuration script:

```bash
python ./.claude/scripts/configure_hooks.py $ARGUMENTS
```

### Step 3: Report Results

Show:
- Number of hooks enabled
- Which integrations are active
- Any warnings about missing hook files

## Output Format

**Success:**
```
Hook configuration complete. 12 hooks enabled.

Enabled integrations:
- reminders: 2 hooks
- (calendar: MCP-based, no hooks needed)

Core hooks: 9
```

**Dry run:**
```
Dry run - settings.json not modified.

Would enable 12 hooks:
  SessionStart: 3 hooks
  UserPromptSubmit: 1 hook
  PreToolUse: 2 hooks
  PostToolUse: 5 hooks
  SessionEnd: 1 hook
```

**List hooks:**
```
Available hooks:

Core hooks (always enabled):
  session-context-loader.py [SessionStart] - Load daily context
  prompt-timestamp.py [UserPromptSubmit] - Add timestamps
  ...

Integration hooks:
  reminders-session-sync.py [SessionStart] - Sync Reminders (requires: reminders)
  reminders-task-detector.py [PostToolUse] - Push tasks to Reminders (requires: reminders)
  health-session-sync.py [SessionStart] - Sync health data (requires: health)
```

## When to Use

- After enabling/disabling integrations in `.user/integrations.yaml`
- After `/setup:onboard` Phase 4 (integration configuration)
- When troubleshooting hook issues

## Note on Extensions

This command configures core hooks only. User extensions in `extensions/` are managed separately via `/extensions:sync`. The upgrade workflow calls both automatically.

## Related Commands

- `/extensions:sync` - Sync user extension symlinks
- `/system:inject` - Regenerate templated files
- `/system:upgrade` - Full system upgrade workflow
- `/setup:onboard` - Initial vault configuration
