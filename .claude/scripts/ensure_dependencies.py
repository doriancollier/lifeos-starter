#!/usr/bin/env python3
"""
ensure_dependencies.py - Ensure required Python packages are installed

Run this before other scripts to install missing dependencies.
Safe to run multiple times.

Usage:
    python ensure_dependencies.py
"""

import subprocess
import sys


REQUIRED_PACKAGES = [
    "pyyaml",  # For YAML config file parsing
]


def check_package(package_name: str) -> bool:
    """Check if a package is installed."""
    try:
        __import__(package_name.replace("-", "_").split("[")[0])
        return True
    except ImportError:
        return False


def install_package(package_name: str) -> bool:
    """Install a package using pip."""
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    missing = []
    installed = []
    failed = []

    for package in REQUIRED_PACKAGES:
        # Map package name to import name
        import_name = package.replace("-", "_").replace("pyyaml", "yaml")

        if check_package(import_name):
            continue

        missing.append(package)
        print(f"Installing {package}...", end=" ", flush=True)

        if install_package(package):
            print("done")
            installed.append(package)
        else:
            print("FAILED")
            failed.append(package)

    if not missing:
        print("All dependencies already installed.")
        return 0

    if installed:
        print(f"\nInstalled: {', '.join(installed)}")

    if failed:
        print(f"\nFailed to install: {', '.join(failed)}")
        print("\nTry manually:")
        for pkg in failed:
            print(f"  pip install {pkg}")
            print(f"  # or: pip3 install {pkg}")
            print(f"  # or: python3 -m pip install {pkg}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
