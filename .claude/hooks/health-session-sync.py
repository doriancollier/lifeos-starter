#!/usr/bin/env python3
"""
Health Session Sync - SessionStart Hook

Syncs health data from Health Auto Export at the start of each Claude Code session
and provides a quick health summary in the session context.

Hook Event: SessionStart
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Add hooks directory to path for hook_logger import
sys.path.insert(0, os.path.dirname(__file__))
from hook_logger import setup_logger, log_hook_execution

# Initialize logger
logger = setup_logger("health-session-sync")

# Vault configuration - uses environment variable or auto-detects from script location
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or str(Path(__file__).resolve().parent.parent.parent)
HEALTH_SYNC_SCRIPT = os.path.join(VAULT_ROOT, ".claude", "scripts", "health_sync.py")


def run_health_command(args: list, timeout: int = 30) -> dict:
    """Run a health_sync.py command and return the result."""
    cmd = ["python3", HEALTH_SYNC_SCRIPT] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return {"success": True, "output": result.stdout}
        else:
            return {"success": False, "error": result.stderr or result.stdout}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def sync_health_data() -> dict:
    """Sync latest health data and return summary."""
    summary = {
        "synced": False,
        "files_processed": 0,
        "quick_status": None,
        "error": None
    }

    # Run sync command (syncs last 3 days by default for recent data)
    sync_result = run_health_command(["sync", "--days", "3"])

    if sync_result.get("success"):
        output = sync_result.get("output", "")
        # Parse number of days synced
        if "Synced" in output:
            try:
                # Look for "Synced N day(s)"
                import re
                match = re.search(r"Synced (\d+) day", output)
                if match:
                    summary["files_processed"] = int(match.group(1))
                    summary["synced"] = True
            except:
                pass
    else:
        summary["error"] = sync_result.get("error", "Unknown error")

    # Get quick status for yesterday (most relevant for morning planning)
    status_result = run_health_command(["status", "--format", "compact"])

    if status_result.get("success"):
        summary["quick_status"] = status_result.get("output", "").strip()

    return summary


def format_session_message(summary: dict) -> str:
    """Format the health summary for session context."""
    parts = ["[Health]"]

    if summary.get("error"):
        parts.append(f"Sync error: {summary['error']}")
    elif summary.get("synced"):
        parts.append(f"Synced {summary['files_processed']} day(s)")

    if summary.get("quick_status"):
        # Add the compact status (already formatted by the script)
        parts.append(summary["quick_status"])

    return " | ".join(parts)


def main():
    """Main hook execution."""
    start_time = time.time()

    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        hook_input = {}

    # Check if health sync script exists
    if not os.path.exists(HEALTH_SYNC_SCRIPT):
        elapsed = time.time() - start_time
        log_hook_execution(logger, "SessionStart",
                          duration=elapsed, status="warning",
                          details={"skipped": "script not found"})
        print(json.dumps({"status": "skipped", "reason": "health_sync.py not found"}))
        return

    # Sync health data
    summary = sync_health_data()

    # Calculate elapsed time
    elapsed = time.time() - start_time

    # Build output
    if summary.get("quick_status") or summary.get("synced"):
        message = format_session_message(summary)

        log_hook_execution(logger, "SessionStart",
                          duration=elapsed, status="success",
                          details={"synced": summary.get("synced", False),
                                   "files_processed": summary.get("files_processed", 0)})
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": message
            }
        }
        print(json.dumps(output))
    else:
        # No data to report
        log_hook_execution(logger, "SessionStart",
                          duration=elapsed, status="success",
                          details={"synced": False})
        print(json.dumps({"status": "success", "timing": f"{elapsed:.2f}s"}))


if __name__ == "__main__":
    main()
