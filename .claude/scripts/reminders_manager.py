#!/usr/bin/env python3
"""
Reminders Manager - AppleScript wrapper for macOS Reminders.app

Part of the LifeOS Reminders Integration system.
Provides bidirectional sync between Obsidian daily notes and Reminders app.

Usage:
    # Setup commands
    python reminders_manager.py setup-lists              # Create LifeOS lists
    python reminders_manager.py clear-all                # Remove all LifeOS reminders

    # Read commands
    python reminders_manager.py list-lists               # List all LifeOS lists
    python reminders_manager.py list-reminders <list>    # Get reminders from a list
    python reminders_manager.py get-incomplete           # Get all incomplete reminders
    python reminders_manager.py get <id>                 # Get a specific reminder

    # Write commands
    python reminders_manager.py create --list <list> --name <name> [--priority N] [--body <body>]
    python reminders_manager.py complete <id>            # Mark complete
    python reminders_manager.py uncomplete <id>          # Mark incomplete
    python reminders_manager.py update <id> [--name <name>] [--priority N] [--body <body>]
    python reminders_manager.py delete <id>              # Delete reminder

All functions return JSON for easy parsing.
"""

import subprocess
import json
import sys
import argparse
from datetime import datetime
from typing import Optional

# LifeOS reminder lists - one per company context
LIFEOS_LISTS = ["{{company_1_name}}", "{{company_2_name}}", "EMH", "Personal"]


def run_applescript(script: str, timeout: int = 30) -> str:
    """Run AppleScript and return output."""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode != 0:
            raise Exception(f"AppleScript error: {result.stderr.strip()}")
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise Exception(f"AppleScript timed out after {timeout} seconds")


def output_json(success: bool, data=None, error: str = None):
    """Output standardized JSON response."""
    result = {
        "success": success,
        "data": data,
        "error": error
    }
    print(json.dumps(result, indent=2, default=str))


# =============================================================================
# SETUP COMMANDS
# =============================================================================

def setup_lists() -> dict:
    """Create the 4 LifeOS lists if they don't exist."""
    created = []
    existing = []

    for list_name in LIFEOS_LISTS:
        # Check if list exists
        check_script = f'''
        tell application "Reminders"
            try
                set existingList to list "{list_name}"
                return "exists"
            on error
                return "not_found"
            end try
        end tell
        '''
        result = run_applescript(check_script)

        if result == "not_found":
            # Create the list
            create_script = f'''
            tell application "Reminders"
                make new list with properties {{name:"{list_name}"}}
                return "created"
            end tell
            '''
            run_applescript(create_script)
            created.append(list_name)
        else:
            existing.append(list_name)

    return {
        "created": created,
        "existing": existing,
        "message": f"Created {len(created)} lists, {len(existing)} already existed"
    }


def clear_all() -> dict:
    """Remove all reminders from LifeOS lists (for fresh start)."""
    deleted_count = 0

    for list_name in LIFEOS_LISTS:
        script = f'''
        tell application "Reminders"
            try
                set targetList to list "{list_name}"
                set reminderCount to count of reminders of targetList
                delete every reminder of targetList
                return reminderCount
            on error
                return 0
            end try
        end tell
        '''
        count = run_applescript(script)
        try:
            deleted_count += int(count)
        except ValueError:
            pass

    return {
        "deleted_count": deleted_count,
        "lists_cleared": LIFEOS_LISTS,
        "message": f"Deleted {deleted_count} reminders from LifeOS lists"
    }


# =============================================================================
# READ COMMANDS
# =============================================================================

def list_lists() -> list:
    """List all LifeOS lists with their reminder counts."""
    lists = []

    for list_name in LIFEOS_LISTS:
        script = f'''
        tell application "Reminders"
            try
                set targetList to list "{list_name}"
                set totalCount to count of reminders of targetList
                set incompleteCount to count of (reminders of targetList whose completed is false)
                return totalCount & "," & incompleteCount
            on error
                return "0,0"
            end try
        end tell
        '''
        result = run_applescript(script)
        parts = result.split(",")
        total = int(parts[0].strip()) if parts[0].strip().isdigit() else 0
        incomplete = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip().isdigit() else 0

        lists.append({
            "name": list_name,
            "total_count": total,
            "incomplete_count": incomplete
        })

    return lists


def list_reminders(list_name: str, include_completed: bool = True) -> list:
    """Get all reminders from a specific list."""
    filter_clause = "" if include_completed else "whose completed is false"

    script = f'''
    tell application "Reminders"
        set reminderData to {{}}
        try
            set targetList to list "{list_name}"
            set reminderList to every reminder of targetList {filter_clause}

            repeat with r in reminderList
                set rId to id of r
                set rName to name of r
                set rBody to body of r
                set rCompleted to completed of r
                set rPriority to priority of r
                set rCreated to creation date of r
                set rModified to modification date of r

                -- Build delimited string for each reminder
                set reminderStr to "ID:" & rId & "|NAME:" & rName & "|COMPLETED:" & rCompleted & "|PRIORITY:" & rPriority & "|CREATED:" & (rCreated as string) & "|MODIFIED:" & (rModified as string) & "|BODY:" & rBody
                set end of reminderData to reminderStr
            end repeat
        end try
        return reminderData
    end tell
    '''
    output = run_applescript(script, timeout=60)

    reminders = []
    if output:
        for line in output.split(", ID:"):
            line = line.replace("ID:", "")
            if "|NAME:" in line:
                reminder = parse_reminder_line(line, list_name)
                if reminder:
                    reminders.append(reminder)

    return reminders


def parse_reminder_line(line: str, list_name: str) -> dict:
    """Parse a delimited reminder string into a dict."""
    reminder = {"list": list_name}

    # Split by known delimiters
    parts = line.split("|")
    for part in parts:
        if part.startswith("NAME:"):
            reminder["name"] = part[5:]
        elif part.startswith("COMPLETED:"):
            reminder["completed"] = part[10:].lower() == "true"
        elif part.startswith("PRIORITY:"):
            try:
                reminder["priority"] = int(part[9:])
            except ValueError:
                reminder["priority"] = 0
        elif part.startswith("CREATED:"):
            reminder["created"] = part[8:]
        elif part.startswith("MODIFIED:"):
            reminder["modified"] = part[9:]
        elif part.startswith("BODY:"):
            reminder["body"] = part[5:]
        elif not ":" in part:
            # First part is the ID
            reminder["id"] = f"x-apple-reminder://{part}" if not part.startswith("x-apple") else part

    # Handle ID at the start of line
    if "id" not in reminder:
        first_part = parts[0].split("|")[0] if parts else ""
        if first_part:
            reminder["id"] = f"x-apple-reminder://{first_part}" if not first_part.startswith("x-apple") else first_part

    return reminder


def get_incomplete() -> list:
    """Get all incomplete reminders across all LifeOS lists."""
    all_reminders = []

    for list_name in LIFEOS_LISTS:
        reminders = list_reminders(list_name, include_completed=False)
        all_reminders.extend(reminders)

    return all_reminders


def get_reminder(reminder_id: str) -> dict:
    """Get a specific reminder by ID."""
    # Extract UUID from full ID format
    uuid = reminder_id.replace("x-apple-reminder://", "")

    script = f'''
    tell application "Reminders"
        try
            set r to reminder id "x-apple-reminder://{uuid}"
            set rId to id of r
            set rName to name of r
            set rBody to body of r
            set rCompleted to completed of r
            set rPriority to priority of r
            set rCreated to creation date of r
            set rModified to modification date of r
            set rContainer to name of container of r

            return "ID:" & rId & "|NAME:" & rName & "|COMPLETED:" & rCompleted & "|PRIORITY:" & rPriority & "|LIST:" & rContainer & "|CREATED:" & (rCreated as string) & "|MODIFIED:" & (rModified as string) & "|BODY:" & rBody
        on error errMsg
            return "ERROR:" & errMsg
        end try
    end tell
    '''
    output = run_applescript(script)

    if output.startswith("ERROR:"):
        return {"error": output[6:]}

    reminder = {}
    parts = output.split("|")
    for part in parts:
        if part.startswith("ID:"):
            reminder["id"] = part[3:]
        elif part.startswith("NAME:"):
            reminder["name"] = part[5:]
        elif part.startswith("COMPLETED:"):
            reminder["completed"] = part[10:].lower() == "true"
        elif part.startswith("PRIORITY:"):
            try:
                reminder["priority"] = int(part[9:])
            except ValueError:
                reminder["priority"] = 0
        elif part.startswith("LIST:"):
            reminder["list"] = part[5:]
        elif part.startswith("CREATED:"):
            reminder["created"] = part[8:]
        elif part.startswith("MODIFIED:"):
            reminder["modified"] = part[9:]
        elif part.startswith("BODY:"):
            reminder["body"] = part[5:]

    return reminder


# =============================================================================
# WRITE COMMANDS
# =============================================================================

def create_reminder(list_name: str, name: str, priority: int = 0, body: str = "") -> dict:
    """Create a new reminder in the specified list."""
    # Escape special characters for AppleScript
    escaped_name = name.replace('"', '\\"').replace('\n', '\\n')
    escaped_body = body.replace('"', '\\"').replace('\n', '\\n')

    script = f'''
    tell application "Reminders"
        try
            set targetList to list "{list_name}"
            set newReminder to make new reminder at end of targetList with properties {{name:"{escaped_name}", body:"{escaped_body}", priority:{priority}}}
            return id of newReminder
        on error errMsg
            return "ERROR:" & errMsg
        end try
    end tell
    '''
    result = run_applescript(script)

    if result.startswith("ERROR:"):
        return {"error": result[6:]}

    return {
        "id": result,
        "name": name,
        "list": list_name,
        "priority": priority,
        "message": f"Created reminder '{name}' in {list_name}"
    }


def complete_reminder(reminder_id: str) -> dict:
    """Mark a reminder as complete."""
    uuid = reminder_id.replace("x-apple-reminder://", "")

    script = f'''
    tell application "Reminders"
        try
            set r to reminder id "x-apple-reminder://{uuid}"
            set rName to name of r
            set completed of r to true
            return "Completed: " & rName
        on error errMsg
            return "ERROR:" & errMsg
        end try
    end tell
    '''
    result = run_applescript(script)

    if result.startswith("ERROR:"):
        return {"error": result[6:]}

    return {
        "id": reminder_id,
        "completed": True,
        "message": result
    }


def uncomplete_reminder(reminder_id: str) -> dict:
    """Mark a reminder as incomplete."""
    uuid = reminder_id.replace("x-apple-reminder://", "")

    script = f'''
    tell application "Reminders"
        try
            set r to reminder id "x-apple-reminder://{uuid}"
            set rName to name of r
            set completed of r to false
            return "Uncompleted: " & rName
        on error errMsg
            return "ERROR:" & errMsg
        end try
    end tell
    '''
    result = run_applescript(script)

    if result.startswith("ERROR:"):
        return {"error": result[6:]}

    return {
        "id": reminder_id,
        "completed": False,
        "message": result
    }


def update_reminder(reminder_id: str, name: str = None, priority: int = None, body: str = None) -> dict:
    """Update reminder properties."""
    uuid = reminder_id.replace("x-apple-reminder://", "")

    # Build property updates
    updates = []
    if name is not None:
        escaped_name = name.replace('"', '\\"').replace('\n', '\\n')
        updates.append(f'set name of r to "{escaped_name}"')
    if priority is not None:
        updates.append(f'set priority of r to {priority}')
    if body is not None:
        escaped_body = body.replace('"', '\\"').replace('\n', '\\n')
        updates.append(f'set body of r to "{escaped_body}"')

    if not updates:
        return {"error": "No properties to update"}

    updates_str = '\n            '.join(updates)

    script = f'''
    tell application "Reminders"
        try
            set r to reminder id "x-apple-reminder://{uuid}"
            {updates_str}
            return "Updated: " & (name of r)
        on error errMsg
            return "ERROR:" & errMsg
        end try
    end tell
    '''
    result = run_applescript(script)

    if result.startswith("ERROR:"):
        return {"error": result[6:]}

    return {
        "id": reminder_id,
        "updated": True,
        "message": result
    }


def delete_reminder(reminder_id: str) -> dict:
    """Delete a reminder."""
    uuid = reminder_id.replace("x-apple-reminder://", "")

    script = f'''
    tell application "Reminders"
        try
            set r to reminder id "x-apple-reminder://{uuid}"
            set rName to name of r
            delete r
            return "Deleted: " & rName
        on error errMsg
            return "ERROR:" & errMsg
        end try
    end tell
    '''
    result = run_applescript(script)

    if result.startswith("ERROR:"):
        return {"error": result[6:]}

    return {
        "id": reminder_id,
        "deleted": True,
        "message": result
    }


def delete_list_reminders(list_name: str) -> dict:
    """Delete all reminders from a specific list."""
    script = f'''
    tell application "Reminders"
        try
            set targetList to list "{list_name}"
            set reminderCount to count of reminders of targetList
            delete every reminder of targetList
            return reminderCount
        on error errMsg
            return "ERROR:" & errMsg
        end try
    end tell
    '''
    result = run_applescript(script)

    if result.startswith("ERROR:"):
        return {"error": result[6:]}

    try:
        count = int(result)
    except ValueError:
        count = 0

    return {
        "list": list_name,
        "deleted_count": count,
        "message": f"Deleted {count} reminders from {list_name}"
    }


# =============================================================================
# MAIN CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Reminders Manager - AppleScript wrapper for macOS Reminders")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup commands
    subparsers.add_parser("setup-lists", help="Create LifeOS reminder lists")
    subparsers.add_parser("clear-all", help="Remove all reminders from LifeOS lists")

    # Read commands
    subparsers.add_parser("list-lists", help="List all LifeOS lists")

    list_reminders_parser = subparsers.add_parser("list-reminders", help="Get reminders from a list")
    list_reminders_parser.add_argument("list_name", help="Name of the list")
    list_reminders_parser.add_argument("--include-completed", action="store_true", default=True)

    subparsers.add_parser("get-incomplete", help="Get all incomplete reminders")

    get_parser = subparsers.add_parser("get", help="Get a specific reminder")
    get_parser.add_argument("id", help="Reminder ID")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new reminder")
    create_parser.add_argument("--list", required=True, dest="list_name", help="List name")
    create_parser.add_argument("--name", required=True, help="Reminder name")
    create_parser.add_argument("--priority", type=int, default=0, help="Priority (0-9)")
    create_parser.add_argument("--body", default="", help="Body/notes")

    # Complete/uncomplete commands
    complete_parser = subparsers.add_parser("complete", help="Mark reminder as complete")
    complete_parser.add_argument("id", help="Reminder ID")

    uncomplete_parser = subparsers.add_parser("uncomplete", help="Mark reminder as incomplete")
    uncomplete_parser.add_argument("id", help="Reminder ID")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update reminder properties")
    update_parser.add_argument("id", help="Reminder ID")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--priority", type=int, help="New priority (0-9)")
    update_parser.add_argument("--body", help="New body/notes")

    # Delete commands
    delete_parser = subparsers.add_parser("delete", help="Delete a reminder")
    delete_parser.add_argument("id", help="Reminder ID")

    delete_list_parser = subparsers.add_parser("delete-list-reminders", help="Delete all reminders from a list")
    delete_list_parser.add_argument("list_name", help="Name of the list")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "setup-lists":
            result = setup_lists()
            output_json(True, result)

        elif args.command == "clear-all":
            result = clear_all()
            output_json(True, result)

        elif args.command == "list-lists":
            result = list_lists()
            output_json(True, result)

        elif args.command == "list-reminders":
            result = list_reminders(args.list_name, args.include_completed)
            output_json(True, result)

        elif args.command == "get-incomplete":
            result = get_incomplete()
            output_json(True, result)

        elif args.command == "get":
            result = get_reminder(args.id)
            if "error" in result:
                output_json(False, error=result["error"])
            else:
                output_json(True, result)

        elif args.command == "create":
            result = create_reminder(args.list_name, args.name, args.priority, args.body)
            if "error" in result:
                output_json(False, error=result["error"])
            else:
                output_json(True, result)

        elif args.command == "complete":
            result = complete_reminder(args.id)
            if "error" in result:
                output_json(False, error=result["error"])
            else:
                output_json(True, result)

        elif args.command == "uncomplete":
            result = uncomplete_reminder(args.id)
            if "error" in result:
                output_json(False, error=result["error"])
            else:
                output_json(True, result)

        elif args.command == "update":
            result = update_reminder(args.id, args.name, args.priority, args.body)
            if "error" in result:
                output_json(False, error=result["error"])
            else:
                output_json(True, result)

        elif args.command == "delete":
            result = delete_reminder(args.id)
            if "error" in result:
                output_json(False, error=result["error"])
            else:
                output_json(True, result)

        elif args.command == "delete-list-reminders":
            result = delete_list_reminders(args.list_name)
            if "error" in result:
                output_json(False, error=result["error"])
            else:
                output_json(True, result)

        else:
            output_json(False, error=f"Unknown command: {args.command}")
            sys.exit(1)

    except Exception as e:
        output_json(False, error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
