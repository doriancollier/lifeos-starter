---
title: "Versioning & Upgrades"
created: "2026-01-31"
status: "active"
---

# Versioning & Upgrades

How LifeOS versions work and how to upgrade safely.

## Version Sources

| Purpose | Source | Example |
|---------|--------|---------|
| **Local version** (what you have) | `VERSION` file | `0.5.0` |
| **Remote versions** (what's available) | Git tags | `v0.5.0`, `v0.6.0` |

The `VERSION` file is the source of truth for your installed version. Git tags are the source of truth for available versions.

## How Version Checking Works

On session start, the `version-check.py` hook:

1. Reads your local `VERSION` file
2. Fetches available tags from upstream via `git ls-remote --tags`
3. Compares versions using semantic versioning
4. Notifies you if an update is available:
   ```
   [UPDATE AVAILABLE] v0.6.0 is available (you have v0.5.0). Run `/system:upgrade` to update.
   ```

Results are cached for 24 hours (configurable in `.user/upgrade.yaml`).

## How Upgrades Work

When you run `/system:upgrade`:

1. **Version check**: Fetches latest tag, compares to local VERSION
2. **Modification detection**: Warns if you've modified system files
3. **Backup**: Creates backup in `.claude/backups/YYYY-MM-DD_HHMMSS/`
4. **Fetch tag**: Downloads the specific version tag from upstream
5. **Checkout**: Updates system files from the tag (including VERSION file)
6. **Migrations**: Runs any version-specific migration scripts
7. **Regenerate**: Runs `inject_placeholders.py` and `configure_hooks.py`
8. **Upgrade notes**: Outputs AI guidance for post-upgrade actions
9. **Interactive walkthrough**: Creates tasks and guides you through action items
10. **Verification**: Confirms upgrade completed successfully

Your `.user/` configuration and all content directories are never touched.

### Upgrade Notes

Each release may include upgrade notes (`.claude/upgrade-notes/v{version}.md`) that provide:
- **User Action Required**: Manual steps the AI will guide you through
- **Breaking Changes**: What changed and how to adapt
- **New Features**: Highlights of what's new to explore
- **Verification**: Steps to confirm the upgrade worked

During upgrade, the AI creates a task list from the action items and walks you through each one interactively.

## Upgrade Commands

```bash
/system:upgrade           # Apply available updates
/system:upgrade --check   # Check without applying
/system:upgrade --force   # Skip modification warnings
/system:upgrade --rollback # Restore from latest backup
```

## Configuration

Create `.user/upgrade.yaml` to customize (optional):

```yaml
upstream:
  owner: "doriancollier"      # GitHub owner
  repo: "lifeos-starter"       # Repository name
  branch: "main"               # Not used for version check, but for reference

preferences:
  check_frequency_hours: 24    # How often to check (0 = disable)
  auto_backup: true            # Backup before upgrading
```

## For Maintainers: Creating Releases

### Quick Release (Recommended)

Use the `/system:release` command to automate the entire process:

```bash
/system:release         # Auto-detect version from changelog & commits
/system:release patch   # Force patch: 0.5.0 → 0.5.1
/system:release minor   # Force minor: 0.5.0 → 0.6.0
/system:release major   # Force major: 0.5.0 → 1.0.0

/system:release --dry-run  # Preview without changes
```

**Auto-detection** spawns an analysis agent to recommend the right version (keeps main context clean):
- **MAJOR**: Breaking changes, removed features, significant rewrites
- **MINOR**: New features added (looks for "### Added" in changelog, "feat:" commits)
- **PATCH**: Bug fixes only (looks for "### Fixed" in changelog, "fix:" commits)

The agent reads the changelog and commits, then returns a structured recommendation with reasoning.

The command:
1. Validates working directory is clean and on `main`
2. Checks changelog has content in `[Unreleased]`
3. Auto-detects version bump (or uses your override)
4. Generates upgrade notes draft (if breaking changes or new features)
5. Shows reasoning and asks for confirmation
6. Updates VERSION file and changelog
7. Saves upgrade notes (if approved)
8. Commits with "Release vX.Y.Z"
9. Creates annotated git tag
10. Pushes to origin
11. Optionally creates GitHub Release

### Manual Release Process

If you prefer manual steps:

```bash
# 1. Update VERSION file
echo "0.6.0" > VERSION

# 2. Update changelog
# Edit 0-System/changelog.md

# 3. Commit changes
git add VERSION 0-System/changelog.md
git commit -m "Release v0.6.0"

# 4. Create and push tag
git tag -a v0.6.0 -m "Version 0.6.0: Description"
git push origin main
git push origin v0.6.0

# 5. Create GitHub Release
gh release create v0.6.0 --title "v0.6.0" --notes "Release notes..."
```

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes to user config or workflows
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, documentation updates

## Conventional Commits

LifeOS uses [Conventional Commits](https://www.conventionalcommits.org/) to automatically populate the changelog.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

### Commit Types and Changelog Mapping

| Type | Changelog Section | Example |
|------|-------------------|---------|
| `feat:` | ### Added | `feat: Add calendar awareness skill` |
| `fix:` | ### Fixed | `fix: Task sync not detecting changes` |
| `docs:` | ### Changed | `docs: Update meeting workflow guide` |
| `refactor:` | ### Changed | `refactor: Simplify hook registration` |
| `perf:` | ### Changed | `perf: Speed up session context loading` |
| `chore:` | *(skipped)* | `chore: Update dependencies` |

### Breaking Changes

Mark breaking changes with `!` after the type or include `BREAKING CHANGE:` in the footer:

```bash
# Using ! marker
feat!: Change config format

# Using footer
feat: Change config format

BREAKING CHANGE: The .user/ directory structure has changed.
```

### Scopes (Optional)

Add context with scopes:

```bash
feat(calendar): Add recurring event support
fix(hooks): Correct directory detection
docs(guides): Update task management guide
```

### What Gets Tracked

Only commits affecting **system files** are added to the changelog:
- `.claude/skills/`, `.claude/commands/`, `.claude/agents/`, `.claude/hooks/`
- `.claude/scripts/`, `.claude/rules/`
- `0-System/`
- `CLAUDE.template.md`, `VERSION`

User content (`1-Projects/` through `8-Scratch/`, `.user/`, `.obsidian/`) is ignored.

### Git Hook Setup

To enable auto-changelog:

```bash
# Install the git hook
.claude/scripts/install-git-hooks.sh

# Check status
.claude/scripts/install-git-hooks.sh --status

# Uninstall
.claude/scripts/install-git-hooks.sh --uninstall
```

Once installed, conventional commits automatically update `0-System/changelog.md`.

---

### What Gets Updated

During upgrade, these paths are updated from the tag:

- `VERSION`
- `workspace/0-System/`
- `.claude/skills/`
- `.claude/commands/`
- `.claude/agents/`
- `.claude/hooks/`
- `.claude/scripts/`
- `.claude/rules/`
- `.claude/upgrade-notes/`
- `CLAUDE.template.md`
- `integrations/`
- `tasks/`
- `scripts/`

### What's Protected

These are never modified by upgrade:

- `.user/` (user configuration)
- `workspace/1-Projects/` through `workspace/8-Scratch/` (user content)
- `workspace/.obsidian/` (Obsidian settings)
- `extensions/` (user plugins and customizations)
- `data/` (imported external data)
- Generated files (`CLAUDE.md`, `coaching.md`, `settings.json`) - regenerated after upgrade

## Migrations

For breaking changes, create migration scripts in `.claude/scripts/migrations/`:

```
v0.6.0.py  # Runs when upgrading TO 0.6.0
v0.7.0.py  # Runs when upgrading TO 0.7.0
```

Migrations run automatically in version order. See `.claude/scripts/migrations/README.md` for details.

## Troubleshooting

### "Could not fetch remote version"

- Check network connection
- Verify upstream repo exists: `gh repo view doriancollier/lifeos-starter`

### "Locally modified system files detected"

You've edited files in system directories. Options:
- `--force` to overwrite (your changes will be lost)
- Commit your changes to a branch first
- Move customizations to `.user/` directory

### Version shows as 0.0.0

The `VERSION` file is missing or unreadable. Create it:
```bash
echo "0.5.0" > VERSION
```
