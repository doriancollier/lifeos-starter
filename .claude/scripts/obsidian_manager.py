#!/usr/bin/env python3
"""
Obsidian Manager - Vault registration and file opening utility.

Part of the LifeOS system. Manages Obsidian vault registration using Obsidian's
native registry at ~/Library/Application Support/obsidian/obsidian.json.

Usage:
    # Check if vault is registered
    python obsidian_manager.py check [--vault-path /path/to/vault]

    # Register vault if not already (idempotent)
    python obsidian_manager.py register [--vault-path /path/to/vault]

    # Open file (auto-registers vault if needed) - THE MAIN COMMAND
    python obsidian_manager.py open "/absolute/path/to/file.md"

All functions return JSON for easy parsing.
"""

import subprocess
import json
import sys
import argparse
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

# Obsidian config location on macOS
OBSIDIAN_CONFIG_PATH = Path.home() / "Library" / "Application Support" / "obsidian" / "obsidian.json"


def output_json(success: bool, data=None, error: str = None):
    """Output standardized JSON response."""
    result = {
        "success": success,
        "data": data,
        "error": error
    }
    print(json.dumps(result, indent=2, default=str))


def get_vault_path() -> Path:
    """Get the vault path from the script's location (two levels up from .claude/scripts/)."""
    script_dir = Path(__file__).resolve().parent
    # Script is at .claude/scripts/, vault is two levels up
    vault_path = script_dir.parent.parent
    return vault_path


def read_obsidian_config() -> dict:
    """Read Obsidian's configuration file."""
    if not OBSIDIAN_CONFIG_PATH.exists():
        return {}

    try:
        with open(OBSIDIAN_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return {}


def write_obsidian_config(config: dict) -> bool:
    """Write Obsidian's configuration file."""
    try:
        # Ensure parent directory exists
        OBSIDIAN_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(OBSIDIAN_CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError as e:
        return False


def is_vault_registered(vault_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Check if a vault is registered in Obsidian's config.

    Returns:
        Tuple of (is_registered, vault_id or None)
    """
    config = read_obsidian_config()
    vaults = config.get("vaults", {})

    vault_path_str = str(vault_path.resolve())

    for vault_id, vault_info in vaults.items():
        if vault_info.get("path") == vault_path_str:
            return True, vault_id

    return False, None


def register_vault(vault_path: Path) -> dict:
    """
    Register a vault in Obsidian's config. Idempotent.

    Returns:
        dict with registration result
    """
    # Check if already registered
    registered, existing_id = is_vault_registered(vault_path)
    if registered:
        return {
            "registered": False,
            "already_existed": True,
            "vault_id": existing_id,
            "vault_path": str(vault_path.resolve()),
            "message": "Vault was already registered"
        }

    # Generate a new vault ID (Obsidian uses random hex strings)
    vault_id = uuid.uuid4().hex[:16]

    # Read current config
    config = read_obsidian_config()

    # Initialize vaults dict if needed
    if "vaults" not in config:
        config["vaults"] = {}

    # Add the vault
    config["vaults"][vault_id] = {
        "path": str(vault_path.resolve()),
        "ts": int(os.path.getmtime(vault_path) * 1000) if vault_path.exists() else 0
    }

    # Write config
    if not write_obsidian_config(config):
        return {
            "registered": False,
            "error": "Failed to write Obsidian config"
        }

    return {
        "registered": True,
        "already_existed": False,
        "vault_id": vault_id,
        "vault_path": str(vault_path.resolve()),
        "message": f"Vault registered with ID {vault_id}"
    }


def open_file(file_path: str, vault_path: Optional[Path] = None) -> dict:
    """
    Open a file in Obsidian, auto-registering the vault if needed.

    Args:
        file_path: Absolute path to the file to open
        vault_path: Optional vault path (auto-detected if not provided)

    Returns:
        dict with result
    """
    file_path = Path(file_path).resolve()

    # Auto-detect vault path if not provided
    if vault_path is None:
        vault_path = get_vault_path()

    # Verify the file is within the vault
    try:
        file_path.relative_to(vault_path)
    except ValueError:
        return {
            "opened": False,
            "error": f"File {file_path} is not within vault {vault_path}"
        }

    # Check if Obsidian config exists (indicates Obsidian is installed)
    if not OBSIDIAN_CONFIG_PATH.parent.exists():
        return {
            "opened": False,
            "error": "Obsidian config not found. Is Obsidian installed? Expected config at: " + str(OBSIDIAN_CONFIG_PATH)
        }

    # Auto-register vault if needed
    registered, vault_id = is_vault_registered(vault_path)
    registration_info = None

    if not registered:
        reg_result = register_vault(vault_path)
        if reg_result.get("error"):
            return {
                "opened": False,
                "error": f"Failed to register vault: {reg_result['error']}"
            }
        registration_info = reg_result

    # Build the obsidian:// URI
    obsidian_uri = f"obsidian://{file_path}"

    # Open in Obsidian using macOS open command
    try:
        result = subprocess.run(
            ["open", obsidian_uri],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return {
                "opened": False,
                "error": f"Failed to open Obsidian: {result.stderr.strip()}"
            }
    except subprocess.TimeoutExpired:
        return {
            "opened": False,
            "error": "Timed out waiting for Obsidian to open"
        }
    except Exception as e:
        return {
            "opened": False,
            "error": str(e)
        }

    result = {
        "opened": True,
        "file_path": str(file_path),
        "vault_path": str(vault_path),
        "uri": obsidian_uri,
        "message": f"Opened {file_path.name} in Obsidian"
    }

    if registration_info:
        result["registration"] = registration_info

    return result


def check_vault(vault_path: Optional[Path] = None) -> dict:
    """
    Check if a vault is registered in Obsidian.

    Returns:
        dict with status information
    """
    if vault_path is None:
        vault_path = get_vault_path()

    registered, vault_id = is_vault_registered(vault_path)

    return {
        "registered": registered,
        "vault_id": vault_id,
        "vault_path": str(vault_path.resolve()),
        "obsidian_config_exists": OBSIDIAN_CONFIG_PATH.exists()
    }


# =============================================================================
# MAIN CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Obsidian Manager - Vault registration and file opening utility"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check if vault is registered")
    check_parser.add_argument(
        "--vault-path",
        type=Path,
        help="Path to vault (auto-detected if not provided)"
    )

    # Register command
    register_parser = subparsers.add_parser("register", help="Register vault (idempotent)")
    register_parser.add_argument(
        "--vault-path",
        type=Path,
        help="Path to vault (auto-detected if not provided)"
    )

    # Open command - THE MAIN COMMAND
    open_parser = subparsers.add_parser("open", help="Open file in Obsidian (auto-registers vault)")
    open_parser.add_argument(
        "file_path",
        help="Absolute path to the file to open"
    )
    open_parser.add_argument(
        "--vault-path",
        type=Path,
        help="Path to vault (auto-detected if not provided)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "check":
            result = check_vault(args.vault_path)
            output_json(True, result)

        elif args.command == "register":
            result = register_vault(args.vault_path or get_vault_path())
            if result.get("error"):
                output_json(False, error=result["error"])
            else:
                output_json(True, result)

        elif args.command == "open":
            result = open_file(args.file_path, args.vault_path)
            if result.get("opened"):
                output_json(True, result)
            else:
                output_json(False, error=result.get("error", "Unknown error"))

        else:
            output_json(False, error=f"Unknown command: {args.command}")
            sys.exit(1)

    except Exception as e:
        output_json(False, error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
