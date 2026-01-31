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
- **Configuration Scripts** (`.claude/scripts/`)
  - `inject_placeholders.py` — Generate personalized files from templates
  - `configure_hooks.py` — Generate settings.json from integrations
  - `migrate_to_user_dir.py` — Migrate old config to new structure
  - `ensure_dependencies.py` — Auto-install PyYAML if missing
- **New System Commands**
  - `/system:inject` — Regenerate CLAUDE.md from template
  - `/system:configure-hooks` — Regenerate settings.json
  - `/system:upgrade` — Full upgrade workflow

### Changed

- **Onboarding** (`/setup:onboard`) — Now writes to `.user/` and runs configuration scripts
- **Documentation** — Updated README, architecture, personalization guides

### Fixed

### Deprecated

- `0-System/config/user-config.md` — Replaced by `.user/` directory

### Removed

---

## Upcoming

See [Roadmap](roadmap.md) for planned changes.
