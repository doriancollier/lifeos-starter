#!/usr/bin/env python3
"""
upgrade_system.py - Core upgrade logic for LifeOS

Usage:
    upgrade_system.py [--check] [--force] [--rollback]

Options:
    --check     Show what would change without applying
    --force     Skip modification detection warnings
    --rollback  Restore from most recent backup

Upgrade flow:
1. Fetch latest git tag and compare versions
2. Detect local modifications to system files
3. Create backup in .claude/backups/YYYY-MM-DD_HHMMSS/
4. Add lifeos-upstream git remote (if not exists)
5. Fetch and checkout system files from upstream tag
6. Run migrations (if any)
7. Run inject_placeholders.py
8. Run configure_hooks.py
9. Update system file hashes cache
10. Report results
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# System directories/files that get updated during upgrade
SYSTEM_PATHS = [
    "VERSION",
    "0-System/",
    ".claude/skills/",
    ".claude/commands/",
    ".claude/agents/",
    ".claude/hooks/",
    ".claude/scripts/",
    ".claude/rules/",
    "CLAUDE.template.md",
]

# Paths that should NEVER be modified by upgrade
PROTECTED_PATHS = [
    ".user/",
    "1-Projects/",
    "2-Areas/",
    "3-Resources/",
    "4-Daily/",
    "5-Meetings/",
    "6-People/",
    "7-MOCs/",
    "8-Scratch/",
    "0-Inbox/",
    ".obsidian/",
    "CLAUDE.md",  # Generated file
    ".claude/settings.json",  # Generated file
    ".claude/rules/coaching.md",  # Generated file
]


def get_vault_root() -> Path:
    """Get the vault root directory."""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    return Path(__file__).parent.parent.parent


def parse_version(version_str: str) -> tuple:
    """Parse semantic version string into tuple for comparison."""
    try:
        # Remove 'v' prefix if present
        version_str = version_str.strip().lstrip("v")
        parts = version_str.split(".")
        return tuple(int(p) for p in parts[:3])
    except (ValueError, AttributeError):
        return (0, 0, 0)


def format_version(version_str: str) -> str:
    """Format version string with 'v' prefix for display."""
    version_str = version_str.strip()
    if version_str.startswith("v"):
        return version_str
    return f"v{version_str}"


def load_upgrade_config(vault_root: Path) -> dict:
    """Load upgrade configuration from .user/upgrade.yaml."""
    config_path = vault_root / ".user" / "upgrade.yaml"

    defaults = {
        "upstream": {
            "owner": "doriancollier",
            "repo": "lifeos-starter",
            "branch": "main"
        },
        "preferences": {
            "check_frequency_hours": 24,
            "auto_backup": True
        }
    }

    if not config_path.exists() or not YAML_AVAILABLE:
        return defaults

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
        for key in defaults:
            if key not in config:
                config[key] = defaults[key]
            elif isinstance(defaults[key], dict):
                for subkey in defaults[key]:
                    if subkey not in config[key]:
                        config[key][subkey] = defaults[key][subkey]
        return config
    except Exception:
        return defaults


def get_local_version(vault_root: Path) -> str:
    """Read local VERSION file."""
    version_path = vault_root / "VERSION"
    if not version_path.exists():
        return "0.0.0"
    try:
        with open(version_path, "r") as f:
            return f.read().strip()
    except Exception:
        return "0.0.0"


def fetch_latest_tag(owner: str, repo: str, timeout: float = 10.0) -> Optional[str]:
    """Fetch the latest semver tag from the remote repository using git ls-remote."""
    url = f"https://github.com/{owner}/{repo}.git"

    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "--refs", url],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            return None

        # Parse tags from output
        # Format: <sha>\trefs/tags/<tagname>
        tags = []
        tag_pattern = re.compile(r"refs/tags/(v?\d+\.\d+\.\d+)$")

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                match = tag_pattern.search(parts[1])
                if match:
                    tags.append(match.group(1))

        if not tags:
            return None

        # Find the highest version
        tags_with_versions = [(tag, parse_version(tag)) for tag in tags]
        tags_with_versions.sort(key=lambda x: x[1], reverse=True)

        return tags_with_versions[0][0]

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
        return None


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return ""


def load_system_hashes(vault_root: Path) -> dict:
    """Load cached system file hashes."""
    cache_path = vault_root / ".claude" / "cache" / "system-files.json"
    if not cache_path.exists():
        return {}
    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_system_hashes(vault_root: Path, hashes: dict) -> None:
    """Save system file hashes to cache."""
    cache_dir = vault_root / ".claude" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "system-files.json"
    try:
        with open(cache_path, "w") as f:
            json.dump(hashes, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save system hashes: {e}", file=sys.stderr)


def collect_system_files(vault_root: Path) -> List[Path]:
    """Collect all system files that would be updated."""
    files = []
    for path_str in SYSTEM_PATHS:
        path = vault_root / path_str
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_file() and ".gitkeep" not in file_path.name:
                    files.append(file_path)
    return files


def detect_modifications(vault_root: Path) -> List[str]:
    """Detect locally modified system files."""
    cached_hashes = load_system_hashes(vault_root)
    if not cached_hashes:
        return []  # No cache means first run, no modifications

    modified = []
    system_files = collect_system_files(vault_root)

    for file_path in system_files:
        rel_path = str(file_path.relative_to(vault_root))
        cached_hash = cached_hashes.get(rel_path)
        if cached_hash:
            current_hash = calculate_file_hash(file_path)
            if current_hash and current_hash != cached_hash:
                modified.append(rel_path)

    return modified


def update_system_hashes(vault_root: Path) -> dict:
    """Calculate and save hashes for all system files."""
    hashes = {}
    system_files = collect_system_files(vault_root)

    for file_path in system_files:
        rel_path = str(file_path.relative_to(vault_root))
        file_hash = calculate_file_hash(file_path)
        if file_hash:
            hashes[rel_path] = file_hash

    hashes["_updated_at"] = datetime.now().isoformat()
    save_system_hashes(vault_root, hashes)
    return hashes


def create_backup(vault_root: Path) -> Optional[Path]:
    """Create a backup of system files before upgrade."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = vault_root / ".claude" / "backups" / timestamp

    try:
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup system files
        system_files = collect_system_files(vault_root)
        for file_path in system_files:
            rel_path = file_path.relative_to(vault_root)
            dest_path = backup_dir / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_path)

        # Also backup generated files
        for gen_file in ["CLAUDE.md", ".claude/rules/coaching.md", ".claude/settings.json"]:
            gen_path = vault_root / gen_file
            if gen_path.exists():
                dest_path = backup_dir / gen_file
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(gen_path, dest_path)

        # Save backup metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "local_version": get_local_version(vault_root),
            "file_count": len(system_files)
        }
        with open(backup_dir / "backup-metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        return backup_dir
    except Exception as e:
        print(f"Error creating backup: {e}", file=sys.stderr)
        return None


def get_latest_backup(vault_root: Path) -> Optional[Path]:
    """Get the most recent backup directory."""
    backups_dir = vault_root / ".claude" / "backups"
    if not backups_dir.exists():
        return None

    backups = sorted([d for d in backups_dir.iterdir() if d.is_dir() and d.name != ".gitkeep"],
                     reverse=True)
    return backups[0] if backups else None


def restore_backup(vault_root: Path, backup_dir: Path) -> bool:
    """Restore files from a backup."""
    try:
        for file_path in backup_dir.rglob("*"):
            if file_path.is_file() and file_path.name not in ["backup-metadata.json", ".gitkeep"]:
                rel_path = file_path.relative_to(backup_dir)
                dest_path = vault_root / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
        return True
    except Exception as e:
        print(f"Error restoring backup: {e}", file=sys.stderr)
        return False


def ensure_upstream_remote(vault_root: Path, owner: str, repo: str) -> bool:
    """Ensure the lifeos-upstream git remote exists."""
    remote_url = f"https://github.com/{owner}/{repo}.git"

    try:
        # Check if remote exists
        result = subprocess.run(
            ["git", "remote", "get-url", "lifeos-upstream"],
            cwd=vault_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Remote exists, update URL if needed
            current_url = result.stdout.strip()
            if current_url != remote_url:
                subprocess.run(
                    ["git", "remote", "set-url", "lifeos-upstream", remote_url],
                    cwd=vault_root,
                    check=True
                )
            return True

        # Add remote
        subprocess.run(
            ["git", "remote", "add", "lifeos-upstream", remote_url],
            cwd=vault_root,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting up upstream remote: {e}", file=sys.stderr)
        return False


def fetch_upstream_tag(vault_root: Path, tag: str) -> bool:
    """Fetch a specific tag from the upstream remote."""
    try:
        # Fetch the specific tag
        subprocess.run(
            ["git", "fetch", "lifeos-upstream", f"refs/tags/{tag}:refs/tags/{tag}"],
            cwd=vault_root,
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error fetching upstream tag: {e}", file=sys.stderr)
        return False


def checkout_system_files(vault_root: Path, tag: str) -> List[str]:
    """Checkout system files from upstream tag."""
    updated_files = []

    for path_str in SYSTEM_PATHS:
        try:
            result = subprocess.run(
                ["git", "checkout", tag, "--", path_str],
                cwd=vault_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                updated_files.append(path_str)
        except Exception:
            # Some paths may not exist in upstream, that's OK
            pass

    return updated_files


def run_migrations(vault_root: Path, from_version: str, to_version: str) -> List[str]:
    """Run any migration scripts for versions between from and to."""
    migrations_dir = vault_root / ".claude" / "scripts" / "migrations"
    if not migrations_dir.exists():
        return []

    from_tuple = parse_version(from_version)
    to_tuple = parse_version(to_version)

    ran_migrations = []

    # Find and run applicable migrations
    for migration_file in sorted(migrations_dir.glob("v*.py")):
        # Extract version from filename (e.g., v0.6.0.py -> 0.6.0)
        version_str = migration_file.stem[1:]  # Remove 'v' prefix
        version_tuple = parse_version(version_str)

        # Run if migration version is > from_version and <= to_version
        if from_tuple < version_tuple <= to_tuple:
            print(f"Running migration: {migration_file.name}")
            try:
                result = subprocess.run(
                    [sys.executable, str(migration_file)],
                    cwd=vault_root,
                    capture_output=True,
                    text=True,
                    env={**os.environ, "CLAUDE_PROJECT_DIR": str(vault_root)}
                )
                if result.returncode == 0:
                    ran_migrations.append(migration_file.name)
                else:
                    print(f"Migration failed: {result.stderr}", file=sys.stderr)
            except Exception as e:
                print(f"Error running migration: {e}", file=sys.stderr)

    return ran_migrations


def run_post_upgrade_scripts(vault_root: Path) -> dict:
    """Run inject_placeholders.py and configure_hooks.py."""
    results = {"inject": False, "hooks": False}

    scripts_dir = vault_root / ".claude" / "scripts"
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(vault_root)}

    # Run inject_placeholders.py
    inject_script = scripts_dir / "inject_placeholders.py"
    if inject_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(inject_script)],
                cwd=vault_root,
                capture_output=True,
                text=True,
                env=env
            )
            results["inject"] = result.returncode == 0
            if result.returncode != 0:
                print(f"inject_placeholders.py failed: {result.stderr}", file=sys.stderr)
        except Exception as e:
            print(f"Error running inject_placeholders.py: {e}", file=sys.stderr)

    # Run configure_hooks.py
    hooks_script = scripts_dir / "configure_hooks.py"
    if hooks_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(hooks_script)],
                cwd=vault_root,
                capture_output=True,
                text=True,
                env=env
            )
            results["hooks"] = result.returncode == 0
            if result.returncode != 0:
                print(f"configure_hooks.py failed: {result.stderr}", file=sys.stderr)
        except Exception as e:
            print(f"Error running configure_hooks.py: {e}", file=sys.stderr)

    return results


def cmd_check(vault_root: Path, config: dict) -> int:
    """Check for available updates without applying."""
    upstream = config.get("upstream", {})
    owner = upstream.get("owner", "doriancollier")
    repo = upstream.get("repo", "lifeos-starter")
    branch = upstream.get("branch", "main")

    local_version = get_local_version(vault_root)
    print(f"Local version: {format_version(local_version)}")

    print(f"Checking {owner}/{repo} for latest tag...")
    remote_version = fetch_latest_tag(owner, repo)

    if not remote_version:
        print("Could not fetch remote version. Check your network connection.")
        return 1

    print(f"Remote version: {format_version(remote_version)}")

    local_tuple = parse_version(local_version)
    remote_tuple = parse_version(remote_version)

    if remote_tuple > local_tuple:
        print(f"\nUpdate available: {format_version(local_version)} -> {format_version(remote_version)}")
        print("Run `/system:upgrade` to apply the update.")
    elif remote_tuple == local_tuple:
        print("\nYou are running the latest version.")
    else:
        print("\nYour local version is newer than upstream.")

    # Check for local modifications
    modifications = detect_modifications(vault_root)
    if modifications:
        print(f"\nLocally modified system files ({len(modifications)}):")
        for mod in modifications[:10]:
            print(f"  - {mod}")
        if len(modifications) > 10:
            print(f"  ... and {len(modifications) - 10} more")

    return 0


def cmd_rollback(vault_root: Path) -> int:
    """Restore from the most recent backup."""
    backup_dir = get_latest_backup(vault_root)

    if not backup_dir:
        print("No backups found.")
        return 1

    # Load backup metadata
    metadata_path = backup_dir / "backup-metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        print(f"Restoring backup from {metadata.get('created_at', 'unknown')}")
        print(f"Original version: v{metadata.get('local_version', 'unknown')}")
    else:
        print(f"Restoring backup: {backup_dir.name}")

    if restore_backup(vault_root, backup_dir):
        print("Backup restored successfully.")

        # Re-run post-upgrade scripts to ensure consistency
        print("Running post-restore scripts...")
        run_post_upgrade_scripts(vault_root)

        print("Rollback complete.")
        return 0
    else:
        print("Failed to restore backup.")
        return 1


def cmd_upgrade(vault_root: Path, config: dict, force: bool = False) -> int:
    """Perform the upgrade."""
    upstream = config.get("upstream", {})
    prefs = config.get("preferences", {})
    owner = upstream.get("owner", "doriancollier")
    repo = upstream.get("repo", "lifeos-starter")
    branch = upstream.get("branch", "main")

    # Step 1: Version check
    local_version = get_local_version(vault_root)
    print(f"Current version: {format_version(local_version)}")

    print(f"Fetching latest tag from {owner}/{repo}...")
    remote_version = fetch_latest_tag(owner, repo)

    if not remote_version:
        print("Could not fetch remote version. Check your network connection.")
        return 1

    local_tuple = parse_version(local_version)
    remote_tuple = parse_version(remote_version)

    if remote_tuple <= local_tuple:
        print(f"Already up to date ({format_version(local_version)}).")
        return 0

    print(f"Upgrading: {format_version(local_version)} -> {format_version(remote_version)}")

    # Step 2: Check for modifications
    if not force:
        modifications = detect_modifications(vault_root)
        if modifications:
            print(f"\nWarning: {len(modifications)} locally modified system files detected:")
            for mod in modifications[:5]:
                print(f"  - {mod}")
            if len(modifications) > 5:
                print(f"  ... and {len(modifications) - 5} more")
            print("\nThese files will be overwritten. Use --force to proceed anyway.")
            print("Or manually review and commit your changes first.")
            return 1

    # Step 3: Create backup
    if prefs.get("auto_backup", True):
        print("Creating backup...")
        backup_dir = create_backup(vault_root)
        if backup_dir:
            print(f"Backup created: {backup_dir.name}")
        else:
            print("Warning: Backup failed, proceeding anyway.")

    # Step 4: Set up git remote
    print("Setting up upstream remote...")
    if not ensure_upstream_remote(vault_root, owner, repo):
        print("Failed to set up git remote.")
        return 1

    # Step 5: Fetch tag from upstream
    # Normalize tag format (ensure 'v' prefix for git tag)
    tag = format_version(remote_version)
    print(f"Fetching tag {tag}...")
    if not fetch_upstream_tag(vault_root, tag):
        print("Failed to fetch tag from upstream.")
        return 1

    # Step 6: Checkout system files from tag
    print("Updating system files...")
    updated = checkout_system_files(vault_root, tag)
    print(f"Updated {len(updated)} paths")

    # Step 7: Run migrations
    migrations = run_migrations(vault_root, local_version, remote_version)
    if migrations:
        print(f"Ran {len(migrations)} migration(s)")

    # Step 8: Run post-upgrade scripts
    print("Regenerating configuration...")
    post_results = run_post_upgrade_scripts(vault_root)

    # Step 9: Update system file hashes
    print("Updating file hashes...")
    update_system_hashes(vault_root)

    # Step 10: Report
    print("\n" + "=" * 50)
    print("UPGRADE COMPLETE")
    print("=" * 50)
    print(f"Version: {format_version(local_version)} -> {format_version(remote_version)}")
    print(f"System paths updated: {len(updated)}")
    if migrations:
        print(f"Migrations run: {', '.join(migrations)}")
    print(f"Template injection: {'OK' if post_results['inject'] else 'FAILED'}")
    print(f"Hook configuration: {'OK' if post_results['hooks'] else 'FAILED'}")
    print()
    print("Your .user/ configuration was preserved.")
    print()

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Upgrade LifeOS system files from upstream"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Show what would change without applying"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip modification detection warnings"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Restore from most recent backup"
    )

    args = parser.parse_args()
    vault_root = get_vault_root()
    config = load_upgrade_config(vault_root)

    if args.rollback:
        return cmd_rollback(vault_root)
    elif args.check:
        return cmd_check(vault_root, config)
    else:
        return cmd_upgrade(vault_root, config, args.force)


if __name__ == "__main__":
    sys.exit(main())
