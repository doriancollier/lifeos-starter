---
description: Upgrade system files while preserving user configuration
argument-hint: [--check] [--backup]
allowed-tools: Bash, Read, Write, Edit, Glob, AskUserQuestion
---

# System Upgrade Command

Safely upgrade LifeOS system files while preserving all user configuration in `.user/`.

## Purpose

When LifeOS templates or system files are updated, this command:
1. Preserves all `.user/` configuration (your data is safe)
2. Regenerates personalized files from updated templates
3. Reconfigures hooks based on your integration settings
4. Verifies the upgrade was successful

## Arguments

- `$ARGUMENTS` - Optional flags:
  - `--check` - Check for available updates without applying
  - `--backup` - Create a backup before upgrading

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      YOUR DATA                              │
│  .user/                                                     │
│  ├── identity.yaml      (preserved)                         │
│  ├── integrations.yaml  (preserved)                         │
│  ├── companies.yaml     (preserved)                         │
│  └── ...                                                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   TEMPLATE FILES                            │
│  (may be updated)                                           │
│  ├── CLAUDE.template.md                                     │
│  └── .claude/rules/coaching.template.md                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  GENERATED FILES                            │
│  (regenerated from templates + your config)                 │
│  ├── CLAUDE.md                                              │
│  ├── .claude/rules/coaching.md                              │
│  └── .claude/settings.json                                  │
└─────────────────────────────────────────────────────────────┘
```

## Task

### Step 1: Pre-flight Check

1. Verify `.user/` directory exists and has required files
2. Check that `onboarding_complete: true` in `.user/identity.yaml`
3. If prerequisites fail, inform user to run `/setup:onboard` first

### Step 2: Backup (if --backup flag)

If `--backup` is specified:

```bash
# Create timestamped backup of generated files
backup_dir="$CLAUDE_PROJECT_DIR/.claude/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
cp "$CLAUDE_PROJECT_DIR/CLAUDE.md" "$backup_dir/" 2>/dev/null || true
cp "$CLAUDE_PROJECT_DIR/.claude/rules/coaching.md" "$backup_dir/" 2>/dev/null || true
cp "$CLAUDE_PROJECT_DIR/.claude/settings.json" "$backup_dir/" 2>/dev/null || true
```

### Step 3: Check for Updates (if --check flag)

If `--check` is specified, compare template files to generated files:
- Show which templates have been modified
- List new placeholders that would be applied
- Do not make any changes

### Step 4: Run Template Injection

Execute the injection script:

```bash
python "$CLAUDE_PROJECT_DIR/.claude/scripts/inject_placeholders.py" --verbose
```

### Step 5: Run Hook Configuration

Execute the hook configuration script:

```bash
python "$CLAUDE_PROJECT_DIR/.claude/scripts/configure_hooks.py" --verbose
```

### Step 6: Verification

Verify the upgrade:
1. Check that CLAUDE.md exists and contains expected content
2. Check that coaching.md exists
3. Check that settings.json is valid JSON
4. Report any placeholder warnings

### Step 7: Report Results

Present upgrade summary:

```markdown
## Upgrade Complete

### Files Regenerated
- CLAUDE.md - Personalized from template
- .claude/rules/coaching.md - Personalized from template
- .claude/settings.json - Configured with X hooks

### Configuration Preserved
All files in .user/ were preserved:
- identity.yaml
- integrations.yaml
- companies.yaml
- coaching.yaml
- health.yaml
- calendars.yaml

### Warnings (if any)
- [Any placeholder or configuration warnings]

### Next Steps
- Review CLAUDE.md for any new features
- Check .claude/settings.json if hook behavior changed
```

## Output Format

**Success:**
```
System upgrade complete.

Regenerated:
  - CLAUDE.md (23 placeholders replaced)
  - coaching.md (8 placeholders replaced)
  - settings.json (12 hooks configured)

Your .user/ configuration was preserved.
```

**Check only:**
```
System upgrade check.

Templates modified since last generation:
  - CLAUDE.template.md (updated 2025-01-15)

New placeholders in templates:
  - {{new_feature_flag}}

Run without --check to apply upgrade.
```

## When to Use

- After updating LifeOS from a new release
- After manually editing template files
- When troubleshooting configuration issues
- Periodically to ensure files are in sync

## Related Commands

- `/system:inject` - Just regenerate templated files
- `/system:configure-hooks` - Just reconfigure hooks
- `/setup:onboard` - Initial vault configuration

## Safety Notes

1. **Your data is safe** - `.user/` is never modified by upgrades
2. **Generated files are regenerated** - CLAUDE.md, coaching.md, settings.json
3. **Use --backup** if you've manually edited generated files (not recommended)
4. **Template changes** - New template features may introduce new placeholders
