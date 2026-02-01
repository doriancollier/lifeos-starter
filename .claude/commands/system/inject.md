---
description: Regenerate personalized files from templates using .user/ configuration
argument-hint: [--dry-run] [--verbose]
allowed-tools: Bash, Read
---

# System Inject Command

Regenerate personalized system files (CLAUDE.md, coaching.md) from their templates using values from `.user/` configuration files.

## Purpose

This command bridges the gap between user configuration and system files. It reads:
- `.user/identity.yaml` - Name, timezone, personality, family
- `.user/companies.yaml` - Company definitions
- `.user/coaching.yaml` - Coaching preferences
- `.user/integrations.yaml` - Integration settings
- `.user/health.yaml` - Health configuration
- `.user/calendars.yaml` - Calendar settings

And generates:
- `CLAUDE.md` from `CLAUDE.template.md`
- `.claude/rules/coaching.md` from `.claude/rules/coaching.template.md`

## Arguments

- `$ARGUMENTS` - Optional flags:
  - `--dry-run` - Show what would be generated without writing files
  - `--verbose` - Show detailed output including placeholder replacements
  - `--list-placeholders` - Show all available placeholders and their values

## Task

### Step 1: Check Prerequisites

Verify that:
1. `.user/identity.yaml` exists (onboarding completed)
2. Template files exist (`CLAUDE.template.md`, `.claude/rules/coaching.template.md`)

If prerequisites are missing, inform the user:
- If `.user/identity.yaml` missing: "Run `/setup:onboard` first to configure your vault."
- If templates missing: "Template files not found. Your vault may need an update."

### Step 2: Run Injection Script

Execute the injection script with any provided flags:

```bash
python ./.claude/scripts/inject_placeholders.py $ARGUMENTS
```

### Step 3: Report Results

- If `--dry-run`: Show what would be changed
- If `--verbose`: Show detailed replacement information
- Otherwise: Confirm successful generation

## Output Format

**Success:**
```
Template injection complete.
- CLAUDE.md: Generated (X placeholders replaced)
- coaching.md: Generated (Y placeholders replaced)
```

**With warnings:**
```
Template injection complete.
- CLAUDE.md: Generated (X placeholders replaced)
  Warning: 3 placeholders not replaced: {{custom_placeholder}}
```

**Dry run:**
```
Dry run - no files modified.
Would write: CLAUDE.md (X placeholders replaced)
Would write: coaching.md (Y placeholders replaced)
```

## When to Use

- After modifying any `.user/*.yaml` files manually
- After a system upgrade that updates template files
- When troubleshooting placeholder issues

## Related Commands

- `/system:configure-hooks` - Regenerate settings.json from integrations
- `/system:upgrade` - Full system upgrade workflow
- `/setup:onboard` - Initial vault configuration
