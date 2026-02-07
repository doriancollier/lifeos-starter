# Contributing to LifeOS

This repo is designed to be used with real personal data while keeping the public codebase clean. This guide explains how that works and how to contribute changes back.

## Architecture: System vs Personal Data

LifeOS cleanly separates system code (tracked in git) from personal data (never tracked).

### Tracked (System Code)

These are the files you develop, improve, and commit:

```
.claude/skills/          # AI knowledge modules
.claude/commands/        # Slash commands
.claude/agents/          # Autonomous agents
.claude/hooks/           # Lifecycle hooks
.claude/scripts/         # Utility scripts
.claude/rules/           # Coaching, components, questioning
workspace/0-System/      # Documentation, guides, patterns
workspace/.obsidian/     # Obsidian plugin config
CLAUDE.template.md       # Template (generates CLAUDE.md)
VERSION                  # Current version
integrations/            # Data connectors
tasks/                   # Background tasks
scripts/                 # Build/install scripts
```

### Never Tracked (Personal Data)

These directories exist locally but `.gitignore` excludes them:

```
workspace/1-Projects/    # Active projects
workspace/2-Areas/       # Ongoing responsibilities
workspace/3-Resources/   # Personal resources
workspace/4-Daily/       # Daily notes
workspace/5-Meetings/    # Meeting notes
workspace/6-People/      # Person files
workspace/7-MOCs/        # Maps of content
workspace/8-Scratch/     # Scratch space
.user/identity.yaml      # Personal identity
.user/health.yaml        # Health targets
data/                    # Imported external data
state/                   # Runtime state
```

### Generated Files (Not Tracked)

These are produced from templates + `.user/` config via `/system:inject`:

```
CLAUDE.md                     # From CLAUDE.template.md
.claude/rules/coaching.md     # From coaching.template.md
.claude/settings.json         # From configure_hooks.py
```

**Rule: Edit templates, not generated files.** If you want to change `CLAUDE.md`, edit `CLAUDE.template.md` instead.

## Development Workflow

### Daily Use

1. Use the vault normally -- daily notes, meetings, tasks, etc.
2. Personal data never touches git thanks to `.gitignore`
3. Make system improvements as you go

### Contributing Changes

1. Edit system files (skills, commands, hooks, templates, docs)
2. Test your changes by using them in your vault
3. Commit with conventional commit format:
   - `feat:` -- New feature
   - `fix:` -- Bug fix
   - `docs:` -- Documentation changes
   - `refactor:` -- Code restructuring
   - `chore:` -- Maintenance
4. Push to `origin/main`
5. Cut releases with `/system:release`

### Template Files

Files ending in `.template.md` use placeholder syntax:

```
{{user_name}}           # From .user/identity.yaml
{{partner_name}}        # From .user/identity.yaml
{{company_1_name}}      # From .user/companies.yaml
{{coaching_intensity}}   # From .user/coaching.yaml
```

When editing templates:
- Use `{{placeholder}}` for anything that varies per user
- Run `/system:inject` to regenerate personalized files
- Only commit the `.template.md` files, never the generated output

## Safety Mechanisms

### Pre-Commit Guard

A git pre-commit hook (`pre-commit-guard.sh`) blocks commits containing personal data files. It checks staged files against known personal directories and exits with an error if any match.

Install with:
```bash
.claude/scripts/install-git-hooks.sh
```

If you legitimately need to bypass it (rare):
```bash
git commit --no-verify
```

### .gitignore

The `.gitignore` file excludes all personal content directories, sensitive config files, secrets, and runtime state. If you add a new directory for personal data, add it to `.gitignore` first.

### Directory Guard Hook

The `directory-guard.py` Claude Code hook enforces file placement rules during AI-assisted editing, preventing files from landing in wrong directories.

## Release Process

1. Make changes and commit with conventional commits
2. Run `/system:release` which:
   - Analyzes commits since last tag
   - Determines version bump (patch/minor/major)
   - Updates `VERSION` and changelog
   - Creates a git tag
   - Optionally creates a GitHub Release

## For Fork Users

If you've forked this repo (rather than being the maintainer):

1. Clone your fork
2. Run `/setup:onboard` to personalize
3. Use normally -- personal data stays local
4. Pull upstream updates with `/system:upgrade`
5. The upgrade system preserves your `.user/` config and personal data

To contribute upstream:
1. Create a branch for your change
2. Ensure it only touches system files
3. Open a PR against the main repo
