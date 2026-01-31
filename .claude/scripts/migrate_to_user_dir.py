#!/usr/bin/env python3
"""
migrate_to_user_dir.py - Migrate configuration to .user/ directory

Reads existing configuration from 0-System/config/ files and migrates
to the new .user/*.yaml structure. This is a one-time migration script.

Usage:
    python migrate_to_user_dir.py [--dry-run] [--verbose]
"""

import os
import re
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


def get_vault_root() -> Path:
    """Get the vault root directory."""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    return Path(__file__).parent.parent.parent


def is_placeholder(value: str) -> bool:
    """Check if a value is still a placeholder (not personalized)."""
    if not isinstance(value, str):
        return False
    return bool(re.match(r"\{\{\w+\}\}", value.strip()))


def extract_from_markdown(content: str, field_pattern: str) -> Optional[str]:
    """Extract a value from markdown config file."""
    # Pattern like "- **Name**: value" or "**Name**: value"
    pattern = rf"\*\*{field_pattern}\*\*:\s*(.+?)(?:\n|$)"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        value = match.group(1).strip()
        if not is_placeholder(value):
            return value
    return None


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown file."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                return yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                pass
    return {}


def load_old_user_config(vault_root: Path) -> dict:
    """Load and parse the old user-config.md file."""
    config_path = vault_root / "0-System" / "config" / "user-config.md"
    if not config_path.exists():
        return {}

    content = config_path.read_text()
    frontmatter = extract_frontmatter(content)

    config = {
        "onboarding_complete": frontmatter.get("onboarding_complete", False),
    }

    # Extract identity fields
    field_mappings = {
        "Name": "user_name",
        "Timezone": "timezone",
        "Personality Type": "personality_type",
        "Birth Date": "birthdate",
        "Location": "location",
        "Partner": "partner_name",
        "Children": "child_name",
        "Primary": "email",
        "Work": "work_email",
        "Intensity Level": "coaching_intensity",
        "Communication Style": "communication_style",
    }

    for field, key in field_mappings.items():
        value = extract_from_markdown(content, field)
        if value:
            config[key] = value

    return config


def load_old_contacts_config(vault_root: Path) -> dict:
    """Load and parse the old contacts-config.json file."""
    config_path = vault_root / "0-System" / "config" / "contacts-config.json"
    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r") as f:
            data = json.load(f)

        # Filter out placeholder values
        companies = {}
        for key, company in data.get("companies", {}).items():
            if isinstance(company, dict):
                name = company.get("name", "")
                if not is_placeholder(name) and name:
                    companies[key] = company

        return {
            "companies": companies,
            "collaborators": data.get("collaborators", []),
            "personal": data.get("personal", {}),
        }
    except (json.JSONDecodeError, Exception) as e:
        print(f"Warning: Failed to parse contacts-config.json: {e}", file=sys.stderr)
        return {}


def load_old_health_config(vault_root: Path) -> dict:
    """Load and parse the old health-config.md file."""
    config_path = vault_root / "0-System" / "config" / "health-config.md"
    if not config_path.exists():
        return {}

    content = config_path.read_text()
    frontmatter = extract_frontmatter(content)

    return {
        "enabled": frontmatter.get("enabled", False),
        "export_path": frontmatter.get("export_path", ""),
    }


def create_identity_yaml(config: dict, user_dir: Path, dry_run: bool) -> None:
    """Create .user/identity.yaml from migrated config."""
    identity = {
        "user": {
            "name": config.get("user_name", ""),
            "first_name": config.get("user_name", "").split()[0] if config.get("user_name") else "",
            "birthdate": config.get("birthdate", ""),
            "location": config.get("location", ""),
            "timezone": config.get("timezone", ""),
            "email": config.get("email", ""),
            "work_email": config.get("work_email", ""),
            "personality_type": config.get("personality_type", ""),
        },
        "family": {
            "partner_name": config.get("partner_name", ""),
            "children": [{"name": config.get("child_name", "")}] if config.get("child_name") else [],
        },
        "communication": {
            "style": config.get("communication_style", "balanced"),
            "writing_voice": {
                "avoid_em_dashes": True,
                "formality": "professional-casual",
            },
        },
        "onboarding": {
            "complete": config.get("onboarding_complete", False),
            "completed_at": datetime.now().isoformat() if config.get("onboarding_complete") else "",
        },
    }

    if dry_run:
        print(f"Would create: {user_dir / 'identity.yaml'}")
        print(yaml.dump(identity, default_flow_style=False, indent=2))
    else:
        with open(user_dir / "identity.yaml", "w") as f:
            yaml.dump(identity, f, default_flow_style=False, indent=2, allow_unicode=True)


def create_companies_yaml(contacts_config: dict, user_dir: Path, dry_run: bool) -> None:
    """Create .user/companies.yaml from migrated config."""
    companies_data = {
        "companies": {},
        "collaborators": contacts_config.get("collaborators", []),
        "personal": {
            "id": "personal",
            "keywords": ["personal", "family", "home"],
        },
    }

    # Migrate companies
    for key, company in contacts_config.get("companies", {}).items():
        companies_data["companies"][key] = {
            "name": company.get("name", ""),
            "id": company.get("id", ""),
            "keywords": company.get("keywords", []),
            "contacts": company.get("contacts", []),
        }

    # Add empty company slots if needed
    for i in range(1, 4):
        key = f"company_{i}"
        if key not in companies_data["companies"]:
            companies_data["companies"][key] = {
                "name": "",
                "id": "",
                "keywords": [],
                "contacts": [],
            }

    if dry_run:
        print(f"Would create: {user_dir / 'companies.yaml'}")
    else:
        with open(user_dir / "companies.yaml", "w") as f:
            yaml.dump(companies_data, f, default_flow_style=False, indent=2, allow_unicode=True)


def create_coaching_yaml(config: dict, user_dir: Path, dry_run: bool) -> None:
    """Create .user/coaching.yaml from migrated config."""
    intensity = config.get("coaching_intensity", "7")
    try:
        intensity = int(intensity)
    except (ValueError, TypeError):
        intensity = 7

    # Determine style label
    if intensity <= 3:
        style_label = "Supportive"
    elif intensity <= 6:
        style_label = "Balanced"
    elif intensity <= 8:
        style_label = "Challenging"
    else:
        style_label = "Relentless"

    coaching = {
        "coaching": {
            "intensity": intensity,
            "style_label": style_label,
        },
        "role_priorities": {
            "emergency": ["child", "partner", "work"],
            "default": "balance",
            "biases": ["Over-prioritizes professional work"],
        },
        "personality_coaching": {
            "notes": [],
        },
        "question_emphasis": ["planning", "decision-making", "energy"],
        "integration_points": {
            "before_meetings": True,
            "before_a_priorities": True,
            "before_skipping_tasks": True,
            "after_interactions": False,
        },
    }

    if dry_run:
        print(f"Would create: {user_dir / 'coaching.yaml'}")
    else:
        with open(user_dir / "coaching.yaml", "w") as f:
            yaml.dump(coaching, f, default_flow_style=False, indent=2, allow_unicode=True)


def create_integrations_yaml(health_config: dict, user_dir: Path, dry_run: bool) -> None:
    """Create .user/integrations.yaml with default settings."""
    integrations = {
        "integrations": {
            "reminders": {
                "enabled": False,
                "description": "Bidirectional sync with macOS Reminders",
                "hooks": ["reminders-session-sync.py", "reminders-task-detector.py"],
                "requirements": ["macOS with Reminders app"],
            },
            "health": {
                "enabled": health_config.get("enabled", False),
                "description": "Sync health metrics from Apple Health",
                "hooks": ["health-session-sync.py"],
                "requirements": ["Health Auto Export iOS app"],
            },
            "calendar": {
                "enabled": True,
                "description": "Google Calendar integration via MCP",
                "hooks": [],
                "requirements": ["Google Calendar MCP server"],
            },
            "email": {
                "enabled": False,
                "description": "Read emails from Mail.app",
                "hooks": [],
                "requirements": ["macOS with Mail.app"],
            },
            "supernormal": {
                "enabled": False,
                "description": "Import meeting transcripts",
                "hooks": [],
                "requirements": ["SuperNormal account"],
            },
        },
        "core_hooks": [
            "session-context-loader.py",
            "prompt-timestamp.py",
            "directory-guard.py",
            "frontmatter-validator.py",
            "task-format-validator.py",
            "table-format-validator.py",
            "task-sync-detector.py",
            "auto-git-backup.sh",
        ],
    }

    if dry_run:
        print(f"Would create: {user_dir / 'integrations.yaml'}")
    else:
        with open(user_dir / "integrations.yaml", "w") as f:
            yaml.dump(integrations, f, default_flow_style=False, indent=2, allow_unicode=True)


def create_health_yaml(health_config: dict, user_dir: Path, dry_run: bool) -> None:
    """Create .user/health.yaml with settings from old config."""
    health = {
        "health": {
            "enabled": health_config.get("enabled", False),
            "export_path": health_config.get("export_path", ""),
            "sync_days": 7,
        },
        "targets": {
            "steps": 10000,
            "sleep_hours": 7.5,
            "active_calories": 500,
            "exercise_minutes": 30,
            "stand_hours": 12,
        },
        "metrics": {
            "activity": ["steps", "active_energy_burned", "exercise_time", "stand_time"],
            "vitals": ["heart_rate", "resting_heart_rate", "heart_rate_variability"],
            "body": ["weight", "body_fat_percentage"],
            "sleep": ["sleep_analysis", "time_in_bed"],
        },
        "display": {
            "show_in_daily_plan": True,
            "show_in_session": True,
            "alert_on_missed_targets": True,
        },
    }

    if dry_run:
        print(f"Would create: {user_dir / 'health.yaml'}")
    else:
        with open(user_dir / "health.yaml", "w") as f:
            yaml.dump(health, f, default_flow_style=False, indent=2, allow_unicode=True)


def create_calendars_yaml(config: dict, user_dir: Path, dry_run: bool) -> None:
    """Create .user/calendars.yaml with default settings."""
    calendars = {
        "calendars": {
            "primary": {
                "email": config.get("email", ""),
                "name": "Primary",
                "color": "#4285f4",
            },
            "additional": [],
        },
        "default_calendar": config.get("email", ""),
        "defaults": {
            "duration_minutes": 60,
            "reminder_minutes": 15,
            "travel_buffer_minutes": 15,
            "source_tag": "claude-code",
        },
        "awareness": {
            "check_during_planning": True,
            "protect_events_with_attendees": True,
            "planning_horizon_days": 7,
            "show_holidays": True,
        },
        "working_hours": {
            "start": "09:00",
            "end": "18:00",
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        },
    }

    if dry_run:
        print(f"Would create: {user_dir / 'calendars.yaml'}")
    else:
        with open(user_dir / "calendars.yaml", "w") as f:
            yaml.dump(calendars, f, default_flow_style=False, indent=2, allow_unicode=True)


def add_deprecation_notice(vault_root: Path, dry_run: bool) -> None:
    """Add deprecation notice to old config files."""
    notice = """
<!--
  DEPRECATED: This file is no longer used.

  Configuration has been migrated to .user/ directory.
  See .user/README.md for the new structure.

  You can safely delete this file.
-->

"""

    files_to_update = [
        vault_root / "0-System" / "config" / "user-config.md",
    ]

    for file_path in files_to_update:
        if file_path.exists():
            content = file_path.read_text()
            if "DEPRECATED" not in content:
                if dry_run:
                    print(f"Would add deprecation notice to: {file_path}")
                else:
                    with open(file_path, "w") as f:
                        f.write(notice + content)


def main():
    parser = argparse.ArgumentParser(
        description="Migrate configuration to .user/ directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .user/ files"
    )

    args = parser.parse_args()

    vault_root = get_vault_root()
    user_dir = vault_root / ".user"

    # Check if already migrated
    if user_dir.exists() and any(user_dir.iterdir()) and not args.force:
        print(f".user/ directory already exists with files.")
        print("Use --force to overwrite existing configuration.")
        return 1

    print(f"Vault root: {vault_root}")
    print(f"User dir: {user_dir}")
    print()

    # Load old configuration
    print("Loading old configuration...")
    user_config = load_old_user_config(vault_root)
    contacts_config = load_old_contacts_config(vault_root)
    health_config = load_old_health_config(vault_root)

    if args.verbose:
        print(f"  User config: {user_config}")
        print(f"  Contacts config: {len(contacts_config.get('companies', {}))} companies")
        print(f"  Health config: {health_config}")
        print()

    # Create .user/ directory
    if not args.dry_run:
        user_dir.mkdir(parents=True, exist_ok=True)

    # Create new YAML files
    print("Creating .user/ configuration files...")
    create_identity_yaml(user_config, user_dir, args.dry_run)
    create_companies_yaml(contacts_config, user_dir, args.dry_run)
    create_coaching_yaml(user_config, user_dir, args.dry_run)
    create_integrations_yaml(health_config, user_dir, args.dry_run)
    create_health_yaml(health_config, user_dir, args.dry_run)
    create_calendars_yaml(user_config, user_dir, args.dry_run)

    # Create README
    if not args.dry_run:
        readme_src = vault_root / ".user" / "README.md"
        # README already created by earlier step, skip if exists

    # Add deprecation notices to old files
    print("Adding deprecation notices...")
    add_deprecation_notice(vault_root, args.dry_run)

    if not args.dry_run:
        print()
        print("Migration complete!")
        print()
        print("Next steps:")
        print("  1. Run: python .claude/scripts/inject_placeholders.py")
        print("  2. Run: python .claude/scripts/configure_hooks.py")
        print("  3. Review .user/*.yaml files and edit as needed")
    else:
        print()
        print("Dry run complete. Use without --dry-run to apply changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
