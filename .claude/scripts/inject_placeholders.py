#!/usr/bin/env python3
"""
inject_placeholders.py - Generate personalized files from templates

Reads user configuration from .user/*.yaml and injects values into
template files (*.template.md) to generate personalized system files.

Usage:
    python inject_placeholders.py [--dry-run] [--verbose]

Templates processed:
    CLAUDE.template.md -> CLAUDE.md
    .claude/rules/coaching.template.md -> .claude/rules/coaching.md
    .claude/commands/*.template.md -> .claude/commands/*.md
    .claude/agents/persona-*.template.md -> .claude/agents/persona-*.md

Placeholders available:
    {{user_name}}, {{user_first_name}}, {{timezone}}, {{user_email}},
    {{partner_name}}, {{child_name}}, {{company_1_name}}, {{company_2_name}},
    {{company_3_name}}, {{coaching_intensity}}, {{vault_path}}, etc.

Dependencies:
    pip install pyyaml
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    print("Or: pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)


def get_vault_root() -> Path:
    """Get the vault root directory."""
    # Check environment variable first
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    # Fall back to script location
    return Path(__file__).parent.parent.parent


def flatten_dict(d: dict, parent_key: str = "", sep: str = "_") -> dict:
    """Flatten a nested dictionary into dot-notation keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        elif isinstance(v, list):
            # Handle lists specially - first item for singular access
            if v and isinstance(v[0], dict):
                items.extend(flatten_dict(v[0], new_key, sep).items())
            elif v:
                items.append((new_key, v[0]))
            else:
                items.append((new_key, ""))
        else:
            items.append((new_key, v if v is not None else ""))
    return dict(items)


def load_user_config(vault_root: Path) -> dict:
    """Load all user configuration from .user/*.yaml files."""
    user_dir = vault_root / ".user"
    config = {}

    yaml_files = [
        "identity.yaml",
        "integrations.yaml",
        "companies.yaml",
        "coaching.yaml",
        "health.yaml",
        "calendars.yaml",
    ]

    for yaml_file in yaml_files:
        file_path = user_dir / yaml_file
        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    data = yaml.safe_load(f) or {}
                    config.update(data)
            except yaml.YAMLError as e:
                print(f"Warning: Failed to parse {yaml_file}: {e}", file=sys.stderr)

    return config


def build_placeholder_map(config: dict) -> dict:
    """Build a map of placeholder names to values."""
    # Flatten the config
    flat = flatten_dict(config)

    # Build the placeholder map with legacy aliases
    placeholders = {}

    # Direct mappings from flat config
    for key, value in flat.items():
        # Convert to placeholder format (snake_case)
        placeholder_key = key.replace(".", "_")
        placeholders[placeholder_key] = str(value) if value else ""

    # Legacy placeholder mappings (for backward compatibility)
    legacy_mappings = {
        # Identity
        "user_name": ["user_name"],
        "user_first_name": ["user_first_name"],
        "user_birthdate": ["user_birthdate"],
        "user_location": ["user_location"],
        "user_email": ["user_email"],
        "work_email": ["user_work_email"],
        "timezone": ["user_timezone"],
        "personality_type": ["user_personality_type"],

        # Family
        "partner_name": ["family_partner_name"],
        "child_name": ["family_children_name"],

        # Companies
        "company_1_name": ["companies_company_1_name"],
        "company_2_name": ["companies_company_2_name"],
        "company_3_name": ["companies_company_3_name"],

        # Coaching
        "coaching_intensity": ["coaching_intensity"],
        "communication_style": ["communication_style"],
    }

    for legacy_key, source_keys in legacy_mappings.items():
        for source_key in source_keys:
            if source_key in placeholders and placeholders[source_key]:
                placeholders[legacy_key] = placeholders[source_key]
                break
        if legacy_key not in placeholders:
            placeholders[legacy_key] = ""

    return placeholders


def add_runtime_placeholders(placeholders: dict, vault_root: Path) -> dict:
    """Add runtime-computed placeholders."""
    # Vault path is needed by many commands/skills
    placeholders["vault_path"] = str(vault_root)

    # Current year for planning files
    placeholders["current_year"] = str(datetime.now().year)

    return placeholders


def inject_placeholders(template_content: str, placeholders: dict) -> str:
    """Replace {{placeholder}} patterns with actual values."""
    def replacer(match):
        placeholder = match.group(1)
        if placeholder in placeholders:
            return placeholders[placeholder]
        # Return original if not found (preserve unknown placeholders)
        return match.group(0)

    # Match {{placeholder_name}} patterns
    pattern = r"\{\{(\w+)\}\}"
    return re.sub(pattern, replacer, template_content)


def get_template_mappings(vault_root: Path) -> list[tuple[Path, Path]]:
    """Get list of (template, output) file pairs."""
    mappings = [
        # Core system files
        (
            vault_root / "CLAUDE.template.md",
            vault_root / "CLAUDE.md"
        ),
        (
            vault_root / ".claude" / "rules" / "coaching.template.md",
            vault_root / ".claude" / "rules" / "coaching.md"
        ),
    ]

    # Command templates
    commands_dir = vault_root / ".claude" / "commands"
    command_templates = [
        "update",
        "daily/plan",
        "daily/eod",
        "daily/timebox",
        "weekly/review",
        "partner/stateofunion",
        "board/advise",
        "context/ab",
        "context/personal",
        "annual/plan",
        "monthly/plan",
    ]
    for cmd in command_templates:
        template = commands_dir / f"{cmd}.template.md"
        output = commands_dir / f"{cmd}.md"
        mappings.append((template, output))

    # Agent templates
    agents_dir = vault_root / ".claude" / "agents"
    agent_templates = [
        "persona-board-chair",
        "persona-strategic-operator",
        "persona-relationships-guardian",
        "persona-health-steward",
        "persona-execution-coach",
    ]
    for agent in agent_templates:
        template = agents_dir / f"{agent}.template.md"
        output = agents_dir / f"{agent}.md"
        mappings.append((template, output))

    return mappings


def process_templates(vault_root: Path, placeholders: dict, dry_run: bool = False, verbose: bool = False) -> bool:
    """Process all template files and generate output files."""
    success = True
    mappings = get_template_mappings(vault_root)

    for template_path, output_path in mappings:
        if not template_path.exists():
            if verbose:
                print(f"Skipping: {template_path.name} (not found)")
            continue

        try:
            # Read template
            with open(template_path, "r") as f:
                template_content = f.read()

            # Inject placeholders
            output_content = inject_placeholders(template_content, placeholders)

            # Count replacements
            original_placeholders = set(re.findall(r"\{\{(\w+)\}\}", template_content))
            remaining_placeholders = set(re.findall(r"\{\{(\w+)\}\}", output_content))
            replaced_count = len(original_placeholders) - len(remaining_placeholders)

            if dry_run:
                print(f"Would write: {output_path.name}")
                print(f"  - {replaced_count} placeholders replaced")
                if remaining_placeholders:
                    print(f"  - {len(remaining_placeholders)} placeholders remaining: {remaining_placeholders}")
            else:
                # Write output
                with open(output_path, "w") as f:
                    f.write(output_content)

                if verbose:
                    print(f"Generated: {output_path.name}")
                    print(f"  - {replaced_count} placeholders replaced")
                    if remaining_placeholders:
                        print(f"  - Warning: {len(remaining_placeholders)} placeholders not replaced: {remaining_placeholders}")

        except Exception as e:
            print(f"Error processing {template_path.name}: {e}", file=sys.stderr)
            success = False

    return success


def main():
    parser = argparse.ArgumentParser(
        description="Generate personalized files from templates using .user/ configuration"
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
        "--list-placeholders",
        action="store_true",
        help="List all available placeholders and their values"
    )

    args = parser.parse_args()

    vault_root = get_vault_root()

    # Load configuration
    config = load_user_config(vault_root)
    placeholders = build_placeholder_map(config)
    placeholders = add_runtime_placeholders(placeholders, vault_root)

    if args.list_placeholders:
        print("Available placeholders:")
        for key in sorted(placeholders.keys()):
            value = placeholders[key]
            display_value = str(value)[:50] + "..." if len(str(value)) > 50 else value
            print(f"  {{{{{key}}}}} = {display_value}")
        return 0

    # Check if onboarding is complete
    user_dir = vault_root / ".user"
    identity_file = user_dir / "identity.yaml"

    if not identity_file.exists():
        print("Error: .user/identity.yaml not found. Run /setup:onboard first.", file=sys.stderr)
        return 1

    # Process templates
    if args.verbose or args.dry_run:
        print(f"Vault root: {vault_root}")
        print(f"User config: {user_dir}")
        print()

    success = process_templates(vault_root, placeholders, args.dry_run, args.verbose)

    if success and not args.dry_run:
        print("Template injection complete.")
    elif not success:
        print("Template injection completed with errors.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
