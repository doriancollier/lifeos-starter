---
description: Upgrade LifeOS system files from upstream while preserving user configuration
argument-hint: [--check] [--force] [--rollback]
allowed-tools: Bash, Read, Write, Edit, Glob, AskUserQuestion
---

# System Upgrade Command

Safely upgrade LifeOS system files from the upstream repository while preserving all user configuration in `.user/`.

## Purpose

When LifeOS releases updates, this command:
1. Checks for available updates from the upstream repository
2. Detects any local modifications you've made to system files
3. Creates a backup before applying changes
4. Fetches and applies system file updates via git
5. Runs any version-specific migrations
6. Regenerates personalized files (CLAUDE.md, coaching.md, settings.json)
7. Reports results and any warnings

## Arguments

- `$ARGUMENTS` - Optional flags:
  - `--check` - Check for available updates without applying
  - `--force` - Skip modification detection warnings
  - `--rollback` - Restore from most recent backup

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      YOUR DATA (PRESERVED)                  │
│  .user/                                                     │
│  ├── identity.yaml      (your personal info)                │
│  ├── integrations.yaml  (your enabled features)             │
│  ├── companies.yaml     (your companies)                    │
│  └── upgrade.yaml       (your upgrade preferences)          │
│                                                             │
│  1-Projects/, 2-Areas/, 4-Daily/, 5-Meetings/, 6-People/    │
│  (all your content is never touched)                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   SYSTEM FILES (UPDATED)                    │
│  (fetched from upstream via git)                            │
│  ├── VERSION                                                │
│  ├── 0-System/           (documentation)                    │
│  ├── .claude/skills/     (AI knowledge modules)             │
│  ├── .claude/commands/   (slash commands)                   │
│  ├── .claude/agents/     (autonomous agents)                │
│  ├── .claude/hooks/      (lifecycle automation)             │
│  ├── .claude/scripts/    (utility scripts)                  │
│  └── CLAUDE.template.md  (template files)                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  GENERATED FILES (REGENERATED)              │
│  (rebuilt from templates + your config)                     │
│  ├── CLAUDE.md                                              │
│  ├── .claude/rules/coaching.md                              │
│  └── .claude/settings.json                                  │
└─────────────────────────────────────────────────────────────┘
```

## Task

Execute the upgrade process based on the provided arguments.

### Step 1: Pre-flight Check

1. Verify `.user/` directory exists
2. Check that `onboarding_complete: true` in `.user/identity.yaml`
3. If prerequisites fail, inform user to run `/setup:onboard` first

### Step 2: Execute Upgrade Script

Run the appropriate command based on arguments:

**Check for updates (--check):**
```bash
python ./.claude/scripts/upgrade_system.py --check
```

**Rollback (--rollback):**
```bash
python ./.claude/scripts/upgrade_system.py --rollback
```

**Full upgrade (default):**
```bash
python ./.claude/scripts/upgrade_system.py
```

**Force upgrade (--force):**
```bash
python ./.claude/scripts/upgrade_system.py --force
```

### Step 3: Handle Local Modifications

If the upgrade script reports locally modified system files:

1. Present options using AskUserQuestion:
   - **Keep local modifications** - Skip upgrade for modified files (recommended if you intentionally customized)
   - **Overwrite with upstream** - Use `--force` flag (your changes will be lost)
   - **Abort and review** - Exit to manually commit or stash changes

2. If user chooses to proceed with force:
   ```bash
   python ./.claude/scripts/upgrade_system.py --force
   ```

### Step 4: Report Results

Present upgrade summary based on script output:

**Success:**
```markdown
## Upgrade Complete

**Version**: v0.5.0 -> v0.6.0

### Updated
- 15 system paths updated from upstream
- Template injection: OK
- Hook configuration: OK

### Preserved
All files in .user/ and content directories were preserved.

### Backup
Created: .claude/backups/2025-01-31_132015/
Use `/system:upgrade --rollback` to restore if needed.

### What's New
[See changelog for what's new]
```

**Check only:**
```markdown
## Update Available

**Current**: v0.5.0
**Available**: v0.6.0

### Locally Modified Files
- .claude/hooks/custom-hook.py (you added this)

Run `/system:upgrade` to apply the update.
Run `/system:upgrade --force` to overwrite local modifications.
```

**Already up to date:**
```markdown
## Already Up To Date

You are running the latest version (v0.5.0).

Last checked: Just now
Upstream: doriancollier/lifeos-starter@main
```

### Step 5: Process Upgrade Notes

The upgrade script outputs any applicable upgrade notes after completion.

When upgrade notes are present in the output (look for "UPGRADE NOTES FOR AI" markers):

1. **Parse the notes** between the markers
2. **Summarize for user**:
   ```markdown
   ## Post-Upgrade Actions

   Based on the upgrade notes, here's what you should know:

   ### Action Items
   - [List any manual actions needed]

   ### New Features
   - [Highlight new capabilities]

   ### Verification
   Run these to confirm the upgrade worked:
   - [Verification steps]
   ```

3. **Offer to help** with any action items:
   - "Would you like me to help you with [action item]?"
   - For new features: "Want me to demonstrate [feature]?"

4. **Track completion** (optional):
   - If action items exist, offer to track them in today's daily note

## Upgrade Configuration

Users can customize upgrade behavior in `.user/upgrade.yaml`:

```yaml
upstream:
  owner: "doriancollier"
  repo: "lifeos-starter"
  branch: "main"

preferences:
  check_frequency_hours: 24  # 0 to disable auto-checks
  auto_backup: true
```

## Safety Features

1. **Automatic backups** - Created before every upgrade in `.claude/backups/`
2. **Modification detection** - Warns about locally modified system files
3. **Content protection** - `.user/`, content directories, and generated files are NEVER overwritten by upgrade
4. **Rollback support** - Restore previous state with `--rollback`
5. **Git-based updates** - Clean diffs, history preserved

## Version Check Hook

The `version-check.py` hook runs on session start and shows a notification when updates are available:

```
[UPDATE AVAILABLE] v0.6.0 is available (you have v0.5.0). Run `/system:upgrade` to update.
```

Checks are cached for 24 hours (configurable) to avoid network overhead.

## When to Use

- When session start shows an update notification
- Periodically to ensure you have the latest features
- After upstream announces new features or fixes
- When troubleshooting - newer versions may fix issues

## Related Commands

- `/system:inject` - Just regenerate templated files (no upstream fetch)
- `/system:configure-hooks` - Just reconfigure hooks (no upstream fetch)
- `/setup:onboard` - Initial vault configuration

## Troubleshooting

**"Could not fetch remote version"**
- Check your network connection
- Verify the upstream repository exists: `https://github.com/doriancollier/lifeos-starter`

**"Locally modified system files detected"**
- Review the listed files - are these intentional changes?
- If intentional: use `--force` but note changes will be lost
- If accidental: run `git checkout -- <file>` to discard changes first
- Consider moving customizations to `.user/` or creating a fork

**"Failed to set up git remote"**
- Ensure git is installed and the vault is a git repository
- Try manually: `git remote add lifeos-upstream https://github.com/doriancollier/lifeos-starter.git`

**"Rollback failed"**
- Check if backups exist: `ls .claude/backups/`
- Backups are gitignored, so they're local-only
