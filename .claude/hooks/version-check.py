#!/usr/bin/env python3
"""
version-check.py - Check for LifeOS updates on session start

Hook: SessionStart
Performance target: < 500ms (uses cache, 3-second network timeout)

Checks git tags from the configured upstream repository
and notifies the user if a newer version is available.
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List

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


def parse_version(version_str: str) -> tuple:
    """Parse semantic version string into tuple for comparison."""
    try:
        # Remove 'v' prefix if present
        version_str = version_str.strip().lstrip("v")
        parts = version_str.split(".")
        return tuple(int(p) for p in parts[:3])
    except (ValueError, AttributeError):
        return (0, 0, 0)


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
        # Merge with defaults
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


def load_cache(vault_root: Path) -> dict:
    """Load version check cache."""
    cache_path = vault_root / ".claude" / "cache" / "version-check.json"

    if not cache_path.exists():
        return {}

    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(vault_root: Path, cache: dict) -> None:
    """Save version check cache."""
    cache_dir = vault_root / ".claude" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "version-check.json"

    try:
        with open(cache_path, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass  # Non-critical, ignore errors


def fetch_latest_tag(owner: str, repo: str, timeout: float = 3.0) -> Optional[str]:
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


def should_check(cache: dict, check_frequency_hours: int) -> bool:
    """Determine if we should check for updates based on cache."""
    if check_frequency_hours <= 0:
        return False  # Checks disabled

    last_check = cache.get("last_check_timestamp")
    if not last_check:
        return True

    try:
        elapsed_hours = (time.time() - last_check) / 3600
        return elapsed_hours >= check_frequency_hours
    except Exception:
        return True


def main():
    vault_root = get_vault_root()

    # Load configuration
    config = load_upgrade_config(vault_root)
    upstream = config.get("upstream", {})
    prefs = config.get("preferences", {})
    check_frequency = prefs.get("check_frequency_hours", 24)

    # Load cache
    cache = load_cache(vault_root)

    # Get local version
    local_version = get_local_version(vault_root)

    # Check if we should fetch remote version
    remote_version = cache.get("remote_version")

    if should_check(cache, check_frequency):
        owner = upstream.get("owner", "doriancollier")
        repo = upstream.get("repo", "lifeos-starter")

        fetched = fetch_latest_tag(owner, repo)
        if fetched:
            remote_version = fetched
            cache["remote_version"] = remote_version
            cache["last_check_timestamp"] = time.time()
            cache["last_check_date"] = datetime.now().isoformat()
            save_cache(vault_root, cache)

    # Compare versions
    if remote_version:
        local_tuple = parse_version(local_version)
        remote_tuple = parse_version(remote_version)

        if remote_tuple > local_tuple:
            # Update available!
            # Normalize version display (ensure 'v' prefix)
            remote_display = remote_version if remote_version.startswith("v") else f"v{remote_version}"
            local_display = f"v{local_version}" if not local_version.startswith("v") else local_version
            print(f"[UPDATE AVAILABLE] {remote_display} is available (you have {local_display}). Run `/system:upgrade` to update.")

    # Always exit successfully - this hook should never block
    return 0


if __name__ == "__main__":
    sys.exit(main())
