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

### Removed

---

## Upcoming

See [Roadmap](roadmap.md) for planned changes.
