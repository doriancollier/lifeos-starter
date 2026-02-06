#!/usr/bin/env python3
"""
Reminders Session Sync - SessionStart Hook

Pulls completion status from macOS Reminders back to Obsidian daily note
at the start of each Claude Code session.

This enables bidirectional sync:
- Obsidian → Reminders: Automatic via reminders-task-detector.py (PostToolUse)
- Reminders → Obsidian: Automatic via this hook (SessionStart)

Hook Event: SessionStart
"""

import json
import os
import re
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Add hooks directory to path for hook_logger import
sys.path.insert(0, os.path.dirname(__file__))
from hook_logger import setup_logger, log_hook_execution

# Initialize logger
logger = setup_logger("reminders-session-sync")

# Vault configuration - uses environment variable or auto-detects from script location
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or os.path.join(PROJECT_ROOT, "workspace")
DAILY_DIR = os.path.join(VAULT_ROOT, "4-Daily")
STATE_FILE = os.path.join(PROJECT_ROOT, ".claude", "reminders-state.json")
REMINDERS_SCRIPT = os.path.join(PROJECT_ROOT, ".claude", "scripts", "reminders_manager.py")


def get_today_date():
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


def get_daily_note_path():
    """Get the path to today's daily note."""
    return os.path.join(DAILY_DIR, f"{get_today_date()}.md")


def load_state() -> dict:
    """Load the reminders state file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "last_refresh": None,
        "daily_note_date": None,
        "mappings": []
    }


def save_state(state: dict):
    """Save the reminders state file."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def run_reminders_command(args: list) -> dict:
    """Run a reminders_manager.py command and return the result."""
    cmd = ["python3", REMINDERS_SCRIPT] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_reminder_status(reminder_id: str) -> dict:
    """Get the current status of a reminder."""
    result = run_reminders_command(["get", reminder_id])
    if result.get("success"):
        return result.get("data", {})
    return {}


def update_daily_note_task(file_path: str, task_text: str, mark_complete: bool) -> bool:
    """Update a task's completion status in the daily note."""
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except IOError:
        return False

    # Build regex to find the task
    # Escape special regex chars in task text but handle emoji specially
    escaped_text = re.escape(task_text)

    if mark_complete:
        # Find uncompleted task and mark it complete
        pattern = rf'^(\s*)- \[ \] ({escaped_text})'
        replacement = r'\1- [x] \2 ✅'
    else:
        # Find completed task and mark it incomplete
        pattern = rf'^(\s*)- \[x\] ({escaped_text})(\s*✅)?'
        replacement = r'\1- [ ] \2'

    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

    if count > 0:
        try:
            with open(file_path, 'w') as f:
                f.write(new_content)
            return True
        except IOError:
            return False

    return False


def sync_completions_from_reminders(state: dict) -> dict:
    """Check Reminders for completions and sync back to Obsidian."""
    summary = {
        "synced_completions": 0,
        "synced_uncomletions": 0,
        "errors": [],
        "tasks_synced": []
    }

    mappings = state.get("mappings", [])
    if not mappings:
        return summary

    daily_note_path = get_daily_note_path()
    today = get_today_date()

    # Only sync if state is for today
    if state.get("daily_note_date") != today:
        return summary

    for mapping in mappings:
        reminder_id = mapping.get("reminder_id")
        if not reminder_id:
            continue

        # Get current reminder status
        reminder = get_reminder_status(reminder_id)
        if not reminder:
            continue

        reminder_completed = reminder.get("completed", False)
        state_completed = mapping.get("completed", False)

        # Check if completion status changed in Reminders
        if reminder_completed and not state_completed:
            # Reminder was completed - sync to Obsidian
            task_text = mapping.get("task_text", "")
            if update_daily_note_task(daily_note_path, task_text, mark_complete=True):
                mapping["completed"] = True
                mapping["last_modified"] = datetime.now().isoformat()
                mapping["synced_from_reminders"] = datetime.now().isoformat()
                summary["synced_completions"] += 1
                summary["tasks_synced"].append(mapping.get("task_text", "")[:50])
            else:
                summary["errors"].append(f"Failed to mark complete: {task_text[:30]}...")

        elif not reminder_completed and state_completed:
            # Reminder was uncompleted - sync to Obsidian
            task_text = mapping.get("task_text", "")
            if update_daily_note_task(daily_note_path, task_text, mark_complete=False):
                mapping["completed"] = False
                mapping["last_modified"] = datetime.now().isoformat()
                mapping["synced_from_reminders"] = datetime.now().isoformat()
                summary["synced_uncomletions"] += 1
                summary["tasks_synced"].append(f"(uncompleted) {mapping.get('task_text', '')[:40]}")
            else:
                summary["errors"].append(f"Failed to mark incomplete: {task_text[:30]}...")

    return summary


def main():
    """Main hook execution."""
    start_time = time.time()

    # Read hook input from stdin (SessionStart provides minimal context)
    try:
        hook_input = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        hook_input = {}

    # Load state
    state = load_state()

    # Check if state is stale (different day)
    today = get_today_date()
    if state.get("daily_note_date") != today:
        # New day - state will be rebuilt when daily note is edited
        # Just report that sync isn't applicable
        elapsed = time.time() - start_time
        log_hook_execution(logger, "SessionStart",
                          duration=elapsed, status="success",
                          details={"skipped": "new day"})
        output = {
            "systemMessage": f"[Reminders] New day - sync will initialize when daily note is updated. ({elapsed:.2f}s)"
        }
        print(json.dumps(output))
        return

    # No mappings yet
    if not state.get("mappings"):
        elapsed = time.time() - start_time
        log_hook_execution(logger, "SessionStart",
                          duration=elapsed, status="success",
                          details={"skipped": "no mappings"})
        print(json.dumps({"status": "success", "timing": f"{elapsed:.2f}s"}))
        return

    # Sync completions from Reminders
    summary = sync_completions_from_reminders(state)

    # Save updated state
    if summary["synced_completions"] > 0 or summary["synced_uncomletions"] > 0:
        state["last_refresh"] = datetime.now().isoformat()
        save_state(state)

    # Calculate elapsed time
    elapsed = time.time() - start_time

    # Build output message
    total_synced = summary["synced_completions"] + summary["synced_uncomletions"]

    if total_synced > 0:
        tasks_list = ", ".join(summary["tasks_synced"][:3])
        if len(summary["tasks_synced"]) > 3:
            tasks_list += f" (+{len(summary['tasks_synced']) - 3} more)"

        message = f"[Reminders] Synced {total_synced} task(s) from Reminders: {tasks_list} ({elapsed:.2f}s)"

        log_hook_execution(logger, "SessionStart",
                          duration=elapsed, status="success",
                          details={"synced_completions": summary["synced_completions"],
                                   "synced_uncompletions": summary["synced_uncomletions"]})
        output = {
            "systemMessage": message
        }
        print(json.dumps(output))
    else:
        log_hook_execution(logger, "SessionStart",
                          duration=elapsed, status="success",
                          details={"synced": 0})
        print(json.dumps({"status": "success", "timing": f"{elapsed:.2f}s"}))


if __name__ == "__main__":
    main()
