---
title: "LifeOS Changelog"
created: "2025-12-02"
status: "active"
---

# LifeOS Changelog

All notable changes to LifeOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added

- Add theme management skill for synchronized VS Code + Obsidian themes

### Changed

### Fixed

- Use relative paths in theme commands instead of $CLAUDE_PROJECT_DIR
- Remove 2.0 suffix from Planning-System path references
---

## [0.7.0] - 2026-01-31

### Added

- **Auto-Changelog System** — Conventional commits now auto-populate the changelog
  - `changelog-populator.py` git post-commit hook parses commit prefixes (feat:, fix:, docs:)
  - `install-git-hooks.sh` setup script for easy installation
  - Updated `/system:release` command to handle empty changelog gracefully
  - Documented conventional commit format in versioning guide
- **YAML Frontmatter** — Added missing frontmatter to 3 command files
  - `project/status.md`, `roadmap/status.md`, `create/song.md`

### Changed

- **Command Reference Consistency** — Renamed `/tasks:due` to `/vault-tasks:due` across all documentation
  - Updated CLAUDE.md, components.md, task-management guide, and related skills
  - Aligns documentation with actual file location (`vault-tasks/due.md`)

### Fixed

- Prevent changelog-populator infinite loop and restore changelog
- **Template Injection** — Regenerated 18 files from templates via `/system:inject`
  - Commands: `update.md`, `daily/plan.md`, `daily/eod.md`, `daily/timebox.md`, `weekly/review.md`, `partner/stateofunion.md`, `board/advise.md`, `context/ab.md`, `context/personal.md`, `annual/plan.md`, `monthly/plan.md`
  - Agents: 5 persona agent files
- **Hardcoded Paths** — Replaced absolute paths with relative paths in 5 command files
  - `annual/plan.md`, `monthly/plan.md`, `weekly/review.md`, `daily/timebox.md`
- **Invalid Tool Declarations** — Fixed `Skill` (invalid) → `AskUserQuestion` in 2 commands
  - `strategic/decide.md`, `premortem/run.md`
- **Orphaned Code** — Removed trailing `$ARGUMENTS` from `skill/create.md` and `skill/audit.md`
- **Missing Frontmatter Fields** — Added `argument-hint` to `goals/status.md` and `goals/review.md`
- **Template Improvements** — Updated `daily/timebox.template.md` to use relative paths and `{{timezone}}` variable

---

## [0.6.1] - 2026-01-31

### Added

- **Skill YAML Frontmatter** — Added `allowed-tools` declarations to 6 skills for explicit tool permissions
  - `personal-insight`, `planning-cadence`, `pre-mortem`, `product-management`, `weekly-aggregator`, `weekly-review`

### Changed

- **Hook Configuration Format** — Updated to Claude Code 2026 format
  - `matcher` now uses regex string or `""` for non-tool hooks (previously object `{}`)
  - Updated `configure_hooks.py` script to generate new format
  - Updated hooks README documentation
- **Agent Documentation** — Enhanced `system-reviewer` command with agent availability section
  - Documented fallback options for different review sizes
  - Added note about session requirements for agent discovery

---

## [0.6.0] - 2026-01-31

### Added

- **Orchestration Patterns Skill** — Model-invoked knowledge for agent delegation and context management
  - Auto-applies when designing new commands or tackling complex tasks
  - Documents 3-tier execution model (SMALL/MEDIUM/LARGE)
  - Provides decision framework for when to delegate vs execute directly
  - Includes structured result patterns, session state for resumption
  - References existing orchestrators: `/system:review`, `/system:release`, `/board:advise`

- **Release System** — Create releases with automated version bumping, changelog updates, and git tagging
  - `/system:release` command for maintainers (orchestrator pattern)
    - **Auto-detects** version bump by spawning analysis agent (keeps main context clean)
    - Agent analyzes changelog sections + commit messages (feat:, fix:, BREAKING markers)
    - Override with explicit: `patch`, `minor`, `major`, or `X.Y.Z`
  - Validation: Working directory clean, on main branch, [Unreleased] has content
  - Shows reasoning and asks for confirmation before proceeding
  - GitHub Release creation support via `gh` CLI
  - `--dry-run` flag to preview without changes

- **Upgrade System** — Fetch updates from upstream repository while preserving user configuration
  - `VERSION` file at repo root for semantic versioning
  - `.user/upgrade.yaml` for upgrade preferences (upstream repo, check frequency)
  - `version-check.py` hook — Checks for updates on session start (cached, < 500ms)
  - `upgrade_system.py` script — Core upgrade logic with backup, rollback, migrations
  - `/system:upgrade` command — Check, apply, or rollback updates
    - `--check` — Show available updates without applying
    - `--force` — Skip modification warnings
    - `--rollback` — Restore from most recent backup
  - Automatic backups in `.claude/backups/` before upgrades
  - Modification detection warns about locally changed system files
  - Migration system in `.claude/scripts/migrations/` for version-specific updates

- **User Configuration Directory** (`.user/`) — Centralized YAML configuration that survives system upgrades
  - `identity.yaml` — Name, timezone, personality, family
  - `companies.yaml` — Company definitions with contacts
  - `coaching.yaml` — Coaching intensity and preferences
  - `integrations.yaml` — Integration on/off flags
  - `health.yaml` — Health export settings
  - `calendars.yaml` — Calendar configuration
- **Template System** — `CLAUDE.template.md` and `coaching.template.md` with `{{placeholder}}` syntax
- **Extended Template System** — Commands and agents now also use templates
  - 11 command templates in `.claude/commands/*.template.md`
  - 5 agent templates in `.claude/agents/persona-*.template.md`
  - New `{{vault_path}}` placeholder for runtime path resolution
- **Configuration Scripts** (`.claude/scripts/`)
  - `inject_placeholders.py` — Generate personalized files from templates
  - `test_inject_placeholders.py` — Unit tests for template injection (23 tests)
  - `configure_hooks.py` — Generate settings.json from integrations
  - `migrate_to_user_dir.py` — Migrate old config to new structure
  - `ensure_dependencies.py` — Auto-install PyYAML if missing
- **New System Commands**
  - `/system:inject` — Regenerate CLAUDE.md from template
  - `/system:configure-hooks` — Regenerate settings.json
  - `/system:upgrade` — Full upgrade workflow

### Changed

- **Onboarding** (`/setup:onboard`) — Now writes to `.user/` and runs configuration scripts
- **Python Hooks** — Now dynamically load company names from `.user/companies.yaml`
  - `frontmatter-validator.py`, `task-format-validator.py`, `reminders-task-detector.py`
- **Shell Scripts** — Now auto-detect vault root from script location
  - `auto-git-backup.sh`, `git-task-sync-detector.sh`
- **Documentation** — Updated README, architecture, personalization guides
- **project-status skill** — Removed hardcoded example paths, made generic

### Fixed

- **update.template.md** — Replaced hardcoded timezone and company names with placeholders
- **personalization.md** — Added missing `{{work_email}}` and `{{current_year}}` placeholders to documentation
- **goal-bingo/SKILL.md** — Clarified config.json file path

### Deprecated

- `0-System/config/user-config.md` — Replaced by `.user/` directory

---

## Upcoming

See [Roadmap](roadmap.md) for planned changes.
