#!/usr/bin/env python3
"""
Sync extensions from extensions/ to .claude/ via symlinks.

This script:
1. Reads extensions/manifest.json for registered extensions
2. Creates symlinks in .claude/ for enabled extensions (prefixed with ext--)
3. Removes symlinks for disabled extensions
4. Updates .claude/settings.json for extension hooks
5. Cleans up orphaned extension symlinks
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).parent.parent
EXTENSIONS_DIR = REPO_ROOT / "extensions"
CLAUDE_DIR = REPO_ROOT / ".claude"
MANIFEST_PATH = EXTENSIONS_DIR / "manifest.json"
SETTINGS_PATH = CLAUDE_DIR / "settings.json"

# Extension prefix to identify extension symlinks
EXT_PREFIX = "ext--"


def load_manifest():
    """Load the extensions manifest."""
    if not MANIFEST_PATH.exists():
        return {"version": "1.0", "extensions": []}

    try:
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {MANIFEST_PATH}: {e}", file=sys.stderr)
        print("Please fix the manifest file or delete it to start fresh.", file=sys.stderr)
        sys.exit(1)


def save_manifest(manifest):
    """Save the extensions manifest."""
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def load_settings():
    """Load Claude settings.json."""
    if not SETTINGS_PATH.exists():
        return {}

    try:
        with open(SETTINGS_PATH) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {SETTINGS_PATH}: {e}", file=sys.stderr)
        print("Returning empty settings. Run /system:configure-hooks to regenerate.", file=sys.stderr)
        return {}


def save_settings(settings):
    """Save Claude settings.json."""
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


def get_extension_symlinks(component_type):
    """Get all extension symlinks for a component type (skills, commands, hooks)."""
    target_dir = CLAUDE_DIR / component_type
    if not target_dir.exists():
        return []

    symlinks = []
    for item in target_dir.iterdir():
        if item.is_symlink() and item.name.startswith(EXT_PREFIX):
            symlinks.append(item)
    return symlinks


def create_symlink(source, target):
    """Create a symlink, removing existing if present."""
    if target.exists() or target.is_symlink():
        target.unlink()

    # Create relative symlink
    rel_source = os.path.relpath(source, target.parent)
    target.symlink_to(rel_source)
    return True


def remove_symlink(target):
    """Remove a symlink if it exists."""
    if target.is_symlink():
        target.unlink()
        return True
    return False


def sync_skills(manifest, verbose=True):
    """Sync skill extensions."""
    synced = []
    removed = []

    # Get enabled skill extensions
    enabled_skills = {}
    for ext in manifest.get("extensions", []):
        if ext.get("enabled", True):
            for skill_name in ext.get("components", {}).get("skills", []):
                skill_path = EXTENSIONS_DIR / ext["path"]
                if skill_path.exists():
                    enabled_skills[skill_name] = skill_path

    # Create symlinks for enabled skills
    target_dir = CLAUDE_DIR / "skills"
    target_dir.mkdir(exist_ok=True)

    for skill_name, skill_path in enabled_skills.items():
        target = target_dir / f"{EXT_PREFIX}{skill_name}"
        if create_symlink(skill_path, target):
            synced.append(skill_name)
            if verbose:
                print(f"  + Linked skill: {skill_name}")

    # Remove orphaned extension symlinks
    for symlink in get_extension_symlinks("skills"):
        skill_name = symlink.name[len(EXT_PREFIX):]
        if skill_name not in enabled_skills:
            remove_symlink(symlink)
            removed.append(skill_name)
            if verbose:
                print(f"  - Removed skill: {skill_name}")

    return synced, removed


def sync_commands(manifest, verbose=True):
    """Sync command extensions."""
    synced = []
    removed = []

    # Get enabled command extensions
    enabled_commands = {}
    for ext in manifest.get("extensions", []):
        if ext.get("enabled", True):
            for cmd_namespace in ext.get("components", {}).get("commands", []):
                cmd_path = EXTENSIONS_DIR / "commands" / cmd_namespace
                if cmd_path.exists():
                    enabled_commands[cmd_namespace] = cmd_path

    # Create symlinks for enabled commands
    target_dir = CLAUDE_DIR / "commands"
    target_dir.mkdir(exist_ok=True)

    for cmd_namespace, cmd_path in enabled_commands.items():
        target = target_dir / f"{EXT_PREFIX}{cmd_namespace}"
        if create_symlink(cmd_path, target):
            synced.append(cmd_namespace)
            if verbose:
                print(f"  + Linked commands: {cmd_namespace}")

    # Remove orphaned extension symlinks
    for symlink in get_extension_symlinks("commands"):
        cmd_namespace = symlink.name[len(EXT_PREFIX):]
        if cmd_namespace not in enabled_commands:
            remove_symlink(symlink)
            removed.append(cmd_namespace)
            if verbose:
                print(f"  - Removed commands: {cmd_namespace}")

    return synced, removed


def sync_hooks(manifest, verbose=True):
    """Sync hook extensions by updating settings.json."""
    settings = load_settings()
    synced = []
    removed = []

    # Track which extension hooks should exist
    enabled_hooks = {}
    for ext in manifest.get("extensions", []):
        if ext.get("enabled", True):
            for hook_name in ext.get("components", {}).get("hooks", []):
                hook_path = EXTENSIONS_DIR / "hooks" / hook_name
                if hook_path.exists():
                    enabled_hooks[hook_name] = {
                        "extension": ext["name"],
                        "path": str(hook_path.relative_to(REPO_ROOT))
                    }

    # Get current hooks from settings
    hooks_config = settings.get("hooks", {})

    # Add extension hooks to appropriate events
    # Extension hooks are identified by having paths starting with extensions/
    for event_type, hooks in hooks_config.items():
        if not isinstance(hooks, list):
            continue

        # Remove old extension hooks
        new_hooks = []
        for hook in hooks:
            command = hook.get("command", "")
            # Keep non-extension hooks
            if "extensions/" not in command:
                new_hooks.append(hook)
            else:
                # Check if this extension hook should still exist
                hook_file = command.split()[-1] if command else ""
                hook_name = Path(hook_file).name if hook_file else ""
                if hook_name in enabled_hooks:
                    new_hooks.append(hook)
                else:
                    removed.append(hook_name)
                    if verbose:
                        print(f"  - Removed hook: {hook_name} from {event_type}")

        hooks_config[event_type] = new_hooks

    # Note: Adding new hooks requires knowing which event they belong to
    # This would typically be specified in the extension's manifest
    # For now, we only handle removal of disabled extension hooks

    settings["hooks"] = hooks_config
    save_settings(settings)

    return synced, removed


def cleanup_orphaned(verbose=True):
    """Remove symlinks pointing to non-existent targets."""
    cleaned = []

    for component_type in ["skills", "commands"]:
        for symlink in get_extension_symlinks(component_type):
            if not symlink.resolve().exists():
                symlink.unlink()
                cleaned.append(f"{component_type}/{symlink.name}")
                if verbose:
                    print(f"  ! Cleaned orphaned: {component_type}/{symlink.name}")

    return cleaned


def sync_all(verbose=True):
    """Run full sync."""
    manifest = load_manifest()

    if verbose:
        print("Syncing extensions...")
        print()

    # Sync each component type
    if verbose:
        print("Skills:")
    skills_synced, skills_removed = sync_skills(manifest, verbose)
    if not skills_synced and not skills_removed and verbose:
        print("  (no changes)")

    if verbose:
        print()
        print("Commands:")
    cmds_synced, cmds_removed = sync_commands(manifest, verbose)
    if not cmds_synced and not cmds_removed and verbose:
        print("  (no changes)")

    if verbose:
        print()
        print("Hooks:")
    hooks_synced, hooks_removed = sync_hooks(manifest, verbose)
    if not hooks_synced and not hooks_removed and verbose:
        print("  (no changes)")

    if verbose:
        print()
        print("Cleanup:")
    cleaned = cleanup_orphaned(verbose)
    if not cleaned and verbose:
        print("  (no orphans)")

    if verbose:
        print()
        total_synced = len(skills_synced) + len(cmds_synced) + len(hooks_synced)
        total_removed = len(skills_removed) + len(cmds_removed) + len(hooks_removed)
        print(f"Done. Synced: {total_synced}, Removed: {total_removed}, Cleaned: {len(cleaned)}")

    return {
        "synced": {
            "skills": skills_synced,
            "commands": cmds_synced,
            "hooks": hooks_synced
        },
        "removed": {
            "skills": skills_removed,
            "commands": cmds_removed,
            "hooks": hooks_removed
        },
        "cleaned": cleaned
    }


def register_extension(name, ext_type, path, components=None):
    """Register a new extension in the manifest."""
    manifest = load_manifest()

    # Check if already registered
    for ext in manifest["extensions"]:
        if ext["name"] == name:
            print(f"Extension '{name}' already registered")
            return False

    # Auto-detect components if not specified
    if components is None:
        components = {"skills": [], "commands": [], "hooks": []}
        ext_path = EXTENSIONS_DIR / path

        if ext_type == "skill":
            if (ext_path / "SKILL.md").exists():
                components["skills"].append(name)
        elif ext_type == "command":
            # Commands are namespaced directories
            if ext_path.is_dir():
                components["commands"].append(ext_path.name)
        elif ext_type == "integration":
            # Integrations can have skills, commands, and hooks
            if (ext_path / "SKILL.md").exists():
                components["skills"].append(name)
            # Check for hooks
            for f in ext_path.glob("*.py"):
                if f.name not in ["__init__.py"]:
                    components["hooks"].append(f.name)

    manifest["extensions"].append({
        "name": name,
        "type": ext_type,
        "path": path,
        "enabled": True,
        "installed": datetime.now().strftime("%Y-%m-%d"),
        "components": components
    })

    save_manifest(manifest)
    print(f"Registered extension: {name}")
    return True


def unregister_extension(name):
    """Unregister an extension from the manifest."""
    manifest = load_manifest()

    original_count = len(manifest["extensions"])
    manifest["extensions"] = [e for e in manifest["extensions"] if e["name"] != name]

    if len(manifest["extensions"]) < original_count:
        save_manifest(manifest)
        print(f"Unregistered extension: {name}")
        return True
    else:
        print(f"Extension '{name}' not found")
        return False


def set_extension_enabled(name, enabled):
    """Enable or disable an extension."""
    manifest = load_manifest()

    for ext in manifest["extensions"]:
        if ext["name"] == name:
            ext["enabled"] = enabled
            save_manifest(manifest)
            status = "enabled" if enabled else "disabled"
            print(f"Extension '{name}' {status}")
            return True

    print(f"Extension '{name}' not found")
    return False


def list_extensions():
    """List all registered extensions."""
    manifest = load_manifest()

    if not manifest["extensions"]:
        print("No extensions registered")
        return []

    print("Registered extensions:")
    print()
    for ext in manifest["extensions"]:
        status = "enabled" if ext.get("enabled", True) else "disabled"
        print(f"  {ext['name']} ({ext['type']}) - {status}")
        print(f"    Path: {ext['path']}")
        components = ext.get("components", {})
        if components.get("skills"):
            print(f"    Skills: {', '.join(components['skills'])}")
        if components.get("commands"):
            print(f"    Commands: {', '.join(components['commands'])}")
        if components.get("hooks"):
            print(f"    Hooks: {', '.join(components['hooks'])}")
        print()

    return manifest["extensions"]


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Sync extensions to Claude Code")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync extensions to .claude/")
    sync_parser.add_argument("-q", "--quiet", action="store_true", help="Quiet output")

    # list command
    subparsers.add_parser("list", help="List registered extensions")

    # register command
    register_parser = subparsers.add_parser("register", help="Register an extension")
    register_parser.add_argument("name", help="Extension name")
    register_parser.add_argument("type", choices=["skill", "command", "integration"], help="Extension type")
    register_parser.add_argument("path", help="Path relative to extensions/")

    # unregister command
    unregister_parser = subparsers.add_parser("unregister", help="Unregister an extension")
    unregister_parser.add_argument("name", help="Extension name")

    # enable command
    enable_parser = subparsers.add_parser("enable", help="Enable an extension")
    enable_parser.add_argument("name", help="Extension name")

    # disable command
    disable_parser = subparsers.add_parser("disable", help="Disable an extension")
    disable_parser.add_argument("name", help="Extension name")

    args = parser.parse_args()

    if args.command == "sync":
        sync_all(verbose=not args.quiet)
    elif args.command == "list":
        list_extensions()
    elif args.command == "register":
        register_extension(args.name, args.type, args.path)
    elif args.command == "unregister":
        unregister_extension(args.name)
    elif args.command == "enable":
        set_extension_enabled(args.name, True)
        sync_all()
    elif args.command == "disable":
        set_extension_enabled(args.name, False)
        sync_all()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
