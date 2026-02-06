---
description: Upgrade LifeOS system files from upstream while preserving user configuration
argument-hint: [--check] [--force] [--rollback]
allowed-tools: Bash, Read, Write, Edit, Glob, AskUserQuestion, Task
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

The upgrade script outputs any applicable upgrade notes after completion. Look for content between "UPGRADE NOTES FOR AI" markers.

#### 5.1: Parse and Combine Notes

When upgrading across multiple versions, you may receive multiple upgrade notes files. Parse each one and extract:

- **Summary** - Theme of each version's changes
- **User Action Required** - Checkbox items (combine, deduplicate across versions)
- **Breaking Changes** - Old/new behavior pairs
- **New Features to Explore** - Features with commands to try
- **Configuration Changes** - Config updates needed
- **Verification** - Steps to confirm upgrade worked
- **Notes for AI** - Internal guidance (don't show to user directly)

#### 5.2: Create Task List

Use **TaskCreate** to create trackable tasks for each action item from "User Action Required":

```
For each action item:
  TaskCreate:
    subject: [Action item text without checkbox]
    description: [Any additional context from Breaking Changes or Notes for AI]
    activeForm: [Present participle form, e.g., "Updating Obsidian vault path"]
```

This allows you to track completion and ensures nothing is missed.

#### 5.3: Present Upgrade Summary

Show the user a clear summary:

```markdown
## Upgrade Complete: v{old} → v{new}

### What Changed
[1-2 sentence summary combining all version themes]

### Breaking Changes
[If any - explain what changed and how it affects them]

### Action Items Required
I've created {N} tasks to guide you through the post-upgrade steps:

1. [ ] [Action item 1]
2. [ ] [Action item 2]
...

### New Features
[Highlight 2-3 most interesting new capabilities with commands to try]
```

#### 5.4: Interactive Walkthrough

**Immediately begin helping with the first task.** Don't just list tasks and wait.

For each task:
1. Mark as `in_progress` using TaskUpdate
2. Explain what needs to happen and why
3. If you can help (run a command, check a file), do it
4. If user action required (open Obsidian, enter password), guide them
5. Run any verification steps related to this task
6. Mark as `completed` when done
7. Move to next task

**Example flow:**
```
Let me help you with the first action item: Re-opening Obsidian with the new vault path.

The vault content has moved from the repository root to `workspace/`. You'll need to:
1. Close Obsidian if it's open
2. Open Obsidian
3. Choose "Open folder as vault"
4. Select the `workspace/` folder inside your repository

Once you've done that, let me know and I'll verify it's working correctly.
```

#### 5.5: Verification

After all action items are complete, run the verification steps from the upgrade notes:

```markdown
### Verification Complete

✓ Hook errors: None detected
✓ Daily note path: workspace/4-Daily/ (correct)
✓ New directories: integrations/, tasks/, data/, state/, extensions/ exist
✓ Config files: CLAUDE.md regenerated successfully

All {N} upgrade tasks completed successfully!
```

#### 5.6: Use "Notes for AI" Internally

The "Notes for AI" section contains guidance for future interactions. Remember these hints:
- If user reports specific errors, check the noted causes first
- Remind user about relevant new features when context matches
- Don't show this section to the user directly

#### 5.7: Offer Next Steps

After upgrade is complete:

```markdown
### What's Next?

- Run `/daily:plan` to start your day with the upgraded system
- Try [new feature command] to explore what's new
- If you encounter any issues, the backup is at `.claude/backups/{timestamp}/`
```

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
