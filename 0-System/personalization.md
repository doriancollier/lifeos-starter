---
title: "LifeOS Personalization"
created: "2025-12-02"
updated: "2026-01-31"
status: "active"
---

# LifeOS Personalization

How to customize LifeOS for your context.

## Architecture

LifeOS separates **your configuration** from **system files**:

```
.user/ (YOUR DATA - preserved during upgrades)
    ├── identity.yaml
    ├── companies.yaml
    ├── coaching.yaml
    └── integrations.yaml
              │
              ▼
    Template Files (updated during upgrades)
    ├── CLAUDE.template.md
    └── .claude/rules/coaching.template.md
              │
              ▼
    Generated Files (regenerated from templates)
    ├── CLAUDE.md
    ├── .claude/rules/coaching.md
    └── .claude/settings.json
```

**Key benefit:** System upgrades update templates, then regenerate files using your config. Your data is never lost.

## Configuration Files

All user configuration lives in `.user/`:

| File | Purpose |
|------|---------|
| `identity.yaml` | Name, timezone, personality, family members |
| `companies.yaml` | Company definitions with IDs, keywords, contacts |
| `coaching.yaml` | Coaching intensity (1-10), style preferences |
| `integrations.yaml` | Which integrations are enabled |
| `health.yaml` | Health export path and targets |
| `calendars.yaml` | Calendar configuration and defaults |

### identity.yaml

```yaml
user:
  name: "Your Name"
  first_name: "Your"
  timezone: "America/Chicago"
  email: "you@example.com"
  personality_type: "INTJ"  # Optional

family:
  partner_name: "Partner"
  children:
    - name: "Child"

onboarding:
  complete: true
```

### companies.yaml

```yaml
companies:
  company_1:
    name: "Acme Corp"
    id: "acme"  # Short ID for commands
    keywords: ["acme", "project-x"]  # For meeting detection
    contacts:
      - name: "Alex Smith"
        role: "CTO"
        communication_preference: "slack"

  company_2:
    name: "Side Project"
    id: "sp"
    keywords: []
    contacts: []
```

### coaching.yaml

```yaml
coaching:
  intensity: 7  # 1-10 scale
  style_label: "Challenging"

# Intensity levels:
# 1-3: Supportive - gentle reminders
# 4-6: Balanced - moderate accountability
# 7-8: Challenging - pushes limits
# 9-10: Relentless - maximum accountability
```

### integrations.yaml

```yaml
integrations:
  reminders:
    enabled: true  # Sync with macOS Reminders
  health:
    enabled: false  # Sync Apple Health data
  calendar:
    enabled: true  # Google Calendar (MCP-based)
  email:
    enabled: false  # Read from Mail.app
```

## Modifying Configuration

### Method 1: Edit YAML Files Directly

1. Open files in `.user/` directory
2. Make changes (valid YAML required)
3. Run regeneration commands:

```bash
/system:inject           # Regenerate CLAUDE.md
/system:configure-hooks  # Regenerate settings.json
```

### Method 2: Re-run Onboarding

```bash
/setup:onboard
```

This walks through all configuration interactively.

## System Commands

| Command | Purpose |
|---------|---------|
| `/system:inject` | Regenerate CLAUDE.md and coaching.md from templates |
| `/system:configure-hooks` | Regenerate settings.json from integrations.yaml |
| `/system:upgrade` | Full upgrade workflow (both of the above) |
| `/setup:onboard` | Interactive configuration wizard |

## Template System

Templates use `{{placeholder}}` syntax:

```markdown
# From CLAUDE.template.md
You are a **Level {{coaching_intensity}} Relentless Challenger** coach,
helping {{user_first_name}} bridge the gap between philosophy and daily action.
```

The `inject_placeholders.py` script reads `.user/*.yaml` and replaces placeholders.

### Available Placeholders

| Placeholder | Source |
|-------------|--------|
| `{{user_name}}` | identity.yaml → user.name |
| `{{user_first_name}}` | identity.yaml → user.first_name |
| `{{timezone}}` | identity.yaml → user.timezone |
| `{{partner_name}}` | identity.yaml → family.partner_name |
| `{{child_name}}` | identity.yaml → family.children[0].name |
| `{{company_1_name}}` | companies.yaml → companies.company_1.name |
| `{{coaching_intensity}}` | coaching.yaml → coaching.intensity |

## Integrations

### Enabling an Integration

1. Edit `.user/integrations.yaml`
2. Set `enabled: true` for the integration
3. Run `/system:configure-hooks`

This regenerates `.claude/settings.json` with the appropriate hooks.

### Available Integrations

| Integration | Hooks Added | Requirements |
|-------------|-------------|--------------|
| `reminders` | reminders-session-sync.py, reminders-task-detector.py | macOS |
| `health` | health-session-sync.py | Health Auto Export app |
| `calendar` | (none - MCP-based) | Google Calendar MCP |
| `email` | (none - on-demand) | macOS Mail.app |

## System Upgrades

When you upgrade LifeOS:

1. **Templates may change** — New features, bug fixes
2. **Your `.user/` is preserved** — Your config stays intact
3. **Run `/system:upgrade`** — Regenerates files from new templates

```bash
# After updating LifeOS files
/system:upgrade
```

This runs both `/system:inject` and `/system:configure-hooks`.

## Backup Recommendations

- `.user/identity.yaml` contains personal info — consider excluding from git
- `.user/health.yaml` contains health targets — consider excluding from git
- Other `.user/` files are generally safe to commit

See `.gitignore` for current exclusions.

## Migration from Old Config

If you have existing config in `0-System/config/`:

```bash
python3 .claude/scripts/migrate_to_user_dir.py
```

This reads old config files and creates new `.user/` YAML files.
