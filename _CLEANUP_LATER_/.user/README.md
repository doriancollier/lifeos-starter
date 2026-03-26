# User Configuration Directory

This directory contains **user-specific configuration** that personalizes the LifeOS experience. These files are:

- **Never modified by system upgrades** - Your data is preserved
- **Used to generate personalized system files** - CLAUDE.md, coaching.md, settings.json
- **The single source of truth** - All user preferences live here

## Files

| File | Purpose |
|------|---------|
| `identity.yaml` | Name, timezone, personality, family members |
| `integrations.yaml` | Which integrations are enabled (Reminders, Health, etc.) |
| `companies.yaml` | Company definitions with IDs, keywords, and contacts |
| `coaching.yaml` | Coaching intensity and preferences |
| `health.yaml` | Health export path and targets |
| `calendars.yaml` | Calendar configuration and defaults |

## How It Works

1. **Onboarding** (`/setup:onboard`) populates these files based on your answers
2. **Template injection** (`/system:inject`) reads these files and generates:
   - `CLAUDE.md` from `CLAUDE.template.md`
   - `.claude/rules/coaching.md` from `.claude/rules/coaching.template.md`
3. **Hook configuration** (`/system:configure-hooks`) generates:
   - `.claude/settings.json` based on enabled integrations

## Modifying Configuration

You can edit these YAML files directly. After making changes:

```bash
# Regenerate personalized files
/system:inject

# Regenerate hook configuration (if you changed integrations.yaml)
/system:configure-hooks
```

## System Upgrades

When you upgrade the LifeOS system:

1. Template files may be updated with new features
2. Run `/system:inject` to regenerate personalized files
3. Your `.user/` configuration is preserved
4. New template placeholders use sensible defaults

## Backup

Consider backing up this directory separately from the vault, as it contains personalized configuration that would need to be recreated after a fresh install.

## Privacy

Some files contain sensitive information. The `.gitignore` excludes:
- `.user/identity.yaml` (personal details)
- `.user/health.yaml` (health targets)

Company and integration configuration is typically safe to commit.
