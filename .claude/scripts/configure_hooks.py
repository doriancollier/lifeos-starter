#!/usr/bin/env python3
"""
configure_hooks.py - Generate settings.json from integration configuration

Reads .user/integrations.yaml and generates .claude/settings.json with
appropriate hooks enabled or disabled based on user preferences.

Usage:
    python configure_hooks.py [--dry-run] [--verbose]

Core hooks (always enabled):
    - session-context-loader.py
    - prompt-timestamp.py
    - directory-guard.py
    - frontmatter-validator.py
    - task-format-validator.py
    - table-format-validator.py
    - task-sync-detector.py
    - auto-git-backup.sh

Dependencies:
    pip install pyyaml (optional - will use defaults if not available)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def get_vault_root() -> Path:
    """Get the vault root directory."""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    return Path(__file__).parent.parent.parent


# Hook registry: defines all available hooks and their lifecycle events
HOOK_REGISTRY = {
    # Core hooks (always enabled)
    "version-check.py": {
        "event": "SessionStart",
        "core": True,
        "description": "Check for LifeOS updates"
    },
    "session-context-loader.py": {
        "event": "SessionStart",
        "core": True,
        "description": "Load daily context, tasks, meetings"
    },
    "prompt-timestamp.py": {
        "event": "UserPromptSubmit",
        "core": True,
        "description": "Add current timestamp to prompts"
    },
    "directory-guard.py": {
        "event": "PreToolUse",
        "matcher": {"tool_name": "Write"},
        "core": True,
        "description": "Enforce directory structure"
    },
    "calendar-protection.py": {
        "event": "PreToolUse",
        "matcher": {"tool_name": "mcp__google-calendar__delete-event"},
        "core": True,
        "description": "Protect calendar events"
    },
    "frontmatter-validator.py": {
        "event": "PostToolUse",
        "matcher": {"tool_name": ["Write", "Edit"]},
        "core": True,
        "description": "Validate YAML frontmatter"
    },
    "task-format-validator.py": {
        "event": "PostToolUse",
        "matcher": {"tool_name": ["Write", "Edit"]},
        "core": True,
        "description": "Validate task formatting"
    },
    "table-format-validator.py": {
        "event": "PostToolUse",
        "matcher": {"tool_name": ["Write", "Edit"]},
        "core": True,
        "description": "Validate table formatting"
    },
    "task-sync-detector.py": {
        "event": "PostToolUse",
        "matcher": {"tool_name": ["Write", "Edit"]},
        "core": True,
        "description": "Queue task syncs"
    },
    "auto-git-backup.sh": {
        "event": "SessionEnd",
        "core": True,
        "description": "Auto-commit changes"
    },

    # Integration hooks (optional)
    "reminders-session-sync.py": {
        "event": "SessionStart",
        "core": False,
        "integration": "reminders",
        "description": "Sync Reminders completions"
    },
    "reminders-task-detector.py": {
        "event": "PostToolUse",
        "matcher": {"tool_name": ["Write", "Edit"]},
        "core": False,
        "integration": "reminders",
        "description": "Push tasks to Reminders"
    },
    "health-session-sync.py": {
        "event": "SessionStart",
        "core": False,
        "integration": "health",
        "description": "Sync Apple Health data"
    },
}


def load_integrations_config(vault_root: Path) -> dict:
    """Load integrations configuration from .user/integrations.yaml."""
    config_path = vault_root / ".user" / "integrations.yaml"

    if not config_path.exists():
        print("Note: .user/integrations.yaml not found, using defaults (core hooks only)", file=sys.stderr)
        return {"integrations": {}}

    if not YAML_AVAILABLE:
        print("Warning: PyYAML not installed, using defaults. Install with: pip install pyyaml", file=sys.stderr)
        return {"integrations": {}}

    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {"integrations": {}}
    except yaml.YAMLError as e:
        print(f"Warning: Failed to parse integrations.yaml: {e}", file=sys.stderr)
        return {"integrations": {}}


def get_enabled_integrations(config: dict) -> set:
    """Get set of enabled integration names."""
    integrations = config.get("integrations", {})
    enabled = set()

    for name, settings in integrations.items():
        if isinstance(settings, dict) and settings.get("enabled", False):
            enabled.add(name)

    return enabled


def build_hook_config(hook_name: str, hook_info: dict, hooks_dir: str) -> dict:
    """Build a hook configuration entry for settings.json."""
    config = {
        "type": "command",
        "command": f'"{hooks_dir}/{hook_name}"'
    }

    # Add matcher if defined
    if "matcher" in hook_info:
        matcher = hook_info["matcher"]
        if "tool_name" in matcher:
            tool_name = matcher["tool_name"]
            if isinstance(tool_name, list):
                # Multiple tools - use regex pattern
                pattern = "|".join(tool_name)
                config["matcher"] = {"tool_name": f"^({pattern})$"}
            else:
                config["matcher"] = {"tool_name": tool_name}

    return config


def generate_settings(vault_root: Path, enabled_integrations: set, verbose: bool = False) -> dict:
    """Generate the settings.json structure."""
    hooks_dir = "$CLAUDE_PROJECT_DIR/.claude/hooks"

    settings = {
        "hooks": {
            "SessionStart": [],
            "UserPromptSubmit": [],
            "PreToolUse": [],
            "PostToolUse": [],
            "SessionEnd": []
        },
        "_setup_note": "Generated by configure_hooks.py. Uses $CLAUDE_PROJECT_DIR for portable paths.",
        "_generated_at": None  # Will be set when writing
    }

    # Process each hook in registry
    for hook_name, hook_info in HOOK_REGISTRY.items():
        event = hook_info["event"]

        # Check if hook should be included
        if hook_info["core"]:
            include = True
            reason = "core"
        elif "integration" in hook_info:
            include = hook_info["integration"] in enabled_integrations
            reason = f"integration:{hook_info['integration']}"
        else:
            include = False
            reason = "unknown"

        if include:
            hook_config = build_hook_config(hook_name, hook_info, hooks_dir)
            settings["hooks"][event].append(hook_config)

            if verbose:
                print(f"  + {hook_name} ({reason})")
        elif verbose:
            print(f"  - {hook_name} (disabled: {reason})")

    return settings


def write_settings(vault_root: Path, settings: dict, dry_run: bool = False) -> bool:
    """Write settings.json to disk."""
    from datetime import datetime

    settings_path = vault_root / ".claude" / "settings.json"

    # Add generation timestamp
    settings["_generated_at"] = datetime.now().isoformat()

    if dry_run:
        print("\nWould write to:", settings_path)
        print(json.dumps(settings, indent=2))
        return True

    try:
        with open(settings_path, "w") as f:
            json.dump(settings, indent=2, fp=f)
        return True
    except Exception as e:
        print(f"Error writing settings.json: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate settings.json from .user/integrations.yaml"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--list-hooks",
        action="store_true",
        help="List all available hooks and their integrations"
    )

    args = parser.parse_args()

    vault_root = get_vault_root()

    if args.list_hooks:
        print("Available hooks:")
        print("\nCore hooks (always enabled):")
        for name, info in HOOK_REGISTRY.items():
            if info["core"]:
                print(f"  {name} [{info['event']}] - {info['description']}")

        print("\nIntegration hooks:")
        for name, info in HOOK_REGISTRY.items():
            if not info["core"] and "integration" in info:
                print(f"  {name} [{info['event']}] - {info['description']} (requires: {info['integration']})")
        return 0

    # Load configuration
    config = load_integrations_config(vault_root)
    enabled = get_enabled_integrations(config)

    if args.verbose:
        print(f"Vault root: {vault_root}")
        print(f"Enabled integrations: {enabled or '(none)'}")
        print("\nConfiguring hooks:")

    # Generate settings
    settings = generate_settings(vault_root, enabled, args.verbose)

    # Write settings
    success = write_settings(vault_root, settings, args.dry_run)

    if success and not args.dry_run:
        # Count hooks
        total_hooks = sum(len(hooks) for hooks in settings["hooks"].values())
        print(f"Hook configuration complete. {total_hooks} hooks enabled.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
