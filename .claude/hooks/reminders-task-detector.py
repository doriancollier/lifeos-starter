#!/usr/bin/env python3
"""
Reminders Task Detector - PostToolUse Hook

Detects when task-related changes are made to today's daily note
and synchronizes them to macOS Reminders app.

This hook:
1. Triggers on Write/Edit to today's daily note
2. Parses all tasks from the file
3. Compares with reminders state file
4. Creates/updates/deletes/completes reminders as needed
5. Updates the state file

Hook Event: PostToolUse
Tools: Write, Edit
"""

import json
import os
import re
import sys
import subprocess
import hashlib
import time
from datetime import datetime
from pathlib import Path

# Add hooks directory to path for hook_logger import
sys.path.insert(0, os.path.dirname(__file__))
from hook_logger import setup_logger, log_hook_execution

# Initialize logger
logger = setup_logger("reminders-task-detector")

# Vault configuration - uses environment variable or auto-detects from script location
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or os.path.join(PROJECT_ROOT, "workspace")
DAILY_DIR = os.path.join(VAULT_ROOT, "4-Daily")
STATE_FILE = os.path.join(PROJECT_ROOT, ".claude", "reminders-state.json")
REMINDERS_SCRIPT = os.path.join(PROJECT_ROOT, ".claude", "scripts", "reminders_manager.py")

# Task patterns
TASK_PATTERN = re.compile(r'^(\s*)- \[([ x])\] (.+)$', re.MULTILINE)
SECTION_PATTERN = re.compile(r'^###\s+(.+)$', re.MULTILINE)

# Priority patterns
PRIORITY_PATTERNS = {
    'A': re.compile(r'^🔴(\d)?\.?\s*'),
    'B': re.compile(r'^🟡\s*'),
    'C': re.compile(r'^🟢\s*'),
    'blocked': re.compile(r'^🔵\s*'),
    'scheduled': re.compile(r'^📅\s*'),
}


def load_company_lists():
    """Load company name mappings from .user/companies.yaml dynamically."""
    try:
        import yaml
    except ImportError:
        # Fall back to defaults if PyYAML not installed
        return {"personal": "Personal"}

    companies_file = os.path.join(PROJECT_ROOT, ".user", "companies.yaml")
    company_lists = {"personal": "Personal"}  # Always include Personal

    if os.path.exists(companies_file):
        try:
            with open(companies_file, 'r') as f:
                data = yaml.safe_load(f) or {}

            # Extract company names and create mapping
            companies_data = data.get('companies', {})
            for key in ['company_1', 'company_2', 'company_3']:
                company = companies_data.get(key, {})
                name = company.get('name', '')
                if name:
                    # Map lowercase name to actual name (for Reminders list)
                    company_lists[name.lower()] = name
                    # Also map the short id if available
                    short_id = company.get('id', '')
                    if short_id:
                        company_lists[short_id.lower()] = name
        except Exception:
            pass  # Silently fall back to defaults

    return company_lists


# Company to list mapping - loaded dynamically from user config
COMPANY_LISTS = load_company_lists()


def get_today_date():
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


def get_daily_note_path():
    """Get the path to today's daily note."""
    return os.path.join(DAILY_DIR, f"{get_today_date()}.md")


def is_todays_daily_note(file_path: str) -> bool:
    """Check if the file is today's daily note."""
    today_path = get_daily_note_path()
    return os.path.normpath(file_path) == os.path.normpath(today_path)


def generate_task_hash(task_text: str) -> str:
    """Generate a hash for task matching."""
    # Strip priority emoji and numbers
    normalized = re.sub(r'^[🔴🟡🟢🔵📅]\d*\.?\s*', '', task_text)
    # Strip "Company: X" suffix
    normalized = re.sub(r'\s*-?\s*Company:\s*[\w\s]+$', '', normalized)
    # Strip "Waiting for: X" suffix
    normalized = re.sub(r'\s*-?\s*Waiting for:\s*.+$', '', normalized)
    # Normalize whitespace
    normalized = ' '.join(normalized.split()).lower()
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


def detect_priority(task_text: str) -> tuple:
    """Detect priority from task text. Returns (priority_letter, priority_number, reminders_priority)."""
    for priority, pattern in PRIORITY_PATTERNS.items():
        match = pattern.match(task_text)
        if match:
            if priority == 'A':
                num = match.group(1) if match.group(1) else None
                return ('A', num, 1)  # High priority
            elif priority == 'B':
                return ('B', None, 5)  # Medium priority
            elif priority == 'C':
                return ('C', None, 9)  # Low priority
            elif priority == 'blocked':
                return ('blocked', None, 5)  # Medium priority
            elif priority == 'scheduled':
                return ('scheduled', None, 9)  # Low priority
    return (None, None, 9)  # Default low priority


def detect_company(task_text: str, section_header: str) -> str:
    """Determine which Reminders list a task belongs to."""
    # Check section header first
    if section_header:
        section_lower = section_header.lower()
        for key, list_name in COMPANY_LISTS.items():
            if key in section_lower:
                return list_name

    # Check task text for Company: tag
    company_match = re.search(r'Company:\s*([\w\s]+)', task_text)
    if company_match:
        company = company_match.group(1).strip().lower()
        for key, list_name in COMPANY_LISTS.items():
            if key in company:
                return list_name

    return "Personal"


def extract_blocker(task_text: str) -> str:
    """Extract blocker reason from task text."""
    match = re.search(r'Waiting for:\s*(.+)$', task_text)
    if match:
        return match.group(1).strip()
    return None


def clean_task_name(task_text: str) -> str:
    """Clean task text for reminder name."""
    # Remove priority emoji and numbers
    cleaned = re.sub(r'^[🔴🟡🟢🔵📅]\d*\.?\s*', '', task_text)
    # Remove "Company: X" suffix
    cleaned = re.sub(r'\s*-?\s*Company:\s*[\w\s]+$', '', cleaned)
    return cleaned.strip()


def find_section_for_position(content: str, position: int) -> str:
    """Find which section header a task belongs to based on position."""
    sections = list(SECTION_PATTERN.finditer(content))
    current_section = None

    for section in sections:
        if section.start() <= position:
            current_section = section.group(1)
        else:
            break

    return current_section


def parse_tasks(content: str, file_path: str) -> list:
    """Parse all tasks from file content."""
    tasks = []
    parent_task = None
    parent_section = None
    parent_line = None

    for match in TASK_PATTERN.finditer(content):
        indent = len(match.group(1))
        completed = match.group(2) == 'x'
        task_text = match.group(3).strip()

        current_line = content[:match.start()].count('\n') + 1
        current_section = find_section_for_position(content, match.start())

        # Skip subtasks (indented tasks)
        if indent > 0:
            # Only add as subtask if:
            # 1. There's a parent task
            # 2. Parent is in the same section
            # 3. Parent is within ~10 lines (proximity check)
            if (parent_task and
                parent_section == current_section and
                parent_line is not None and
                current_line - parent_line <= 10):
                parent_task['subtasks'].append({
                    'text': task_text,
                    'completed': completed
                })
            continue

        section = current_section
        priority, priority_num, reminders_priority = detect_priority(task_text)
        company = detect_company(task_text, section)
        blocker = extract_blocker(task_text) if priority == 'blocked' else None

        task = {
            'hash': generate_task_hash(task_text),
            'raw_text': task_text,
            'clean_name': clean_task_name(task_text),
            'completed': completed,
            'priority': priority,
            'priority_number': priority_num,
            'reminders_priority': reminders_priority,
            'list': company,
            'section': section,
            'blocked': priority == 'blocked',
            'blocker_reason': blocker,
            'line_number': current_line,
            'source_file': file_path,
            'subtasks': []
        }

        parent_task = task
        parent_section = section
        parent_line = current_line
        tasks.append(task)

    return tasks


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


def normalize_reminder_name(name: str) -> str:
    """Normalize a reminder name for comparison."""
    # Remove BLOCKED: prefix
    normalized = re.sub(r'^BLOCKED:\s*', '', name, flags=re.IGNORECASE)
    # Remove completion checkmark
    normalized = normalized.replace('✅', '').strip()
    # Normalize whitespace
    normalized = ' '.join(normalized.split()).lower()
    return normalized


def find_existing_reminder(list_name: str, task_name: str) -> dict:
    """Find an existing reminder by name in the specified list.

    Returns the reminder dict if found, None otherwise.
    This prevents duplicate reminders when state is lost.
    """
    result = run_reminders_command(["list-reminders", list_name])
    if not result.get('success'):
        return None

    normalized_task = normalize_reminder_name(task_name)

    for reminder in result.get('data', []):
        normalized_reminder = normalize_reminder_name(reminder.get('name', ''))
        if normalized_task == normalized_reminder:
            return reminder

    return None


def build_reminder_body(task: dict) -> str:
    """Build the body/notes field for a reminder."""
    lines = [
        f"Source: {task['source_file']}",
        f"Company: {task['list']}",
    ]

    if task['priority']:
        priority_str = task['priority']
        if task['priority_number']:
            priority_str += task['priority_number']
        lines.append(f"Priority: {priority_str}")

    if task['blocked']:
        lines.append(f"Blocked: Yes")
        if task['blocker_reason']:
            lines.append(f"Waiting for: {task['blocker_reason']}")
    else:
        lines.append("Blocked: No")

    if task['subtasks']:
        lines.append("---")
        lines.append("Subtasks:")
        for subtask in task['subtasks']:
            check = "[x]" if subtask['completed'] else "[ ]"
            lines.append(f"- {check} {subtask['text']}")

    return "\n".join(lines)


def sync_tasks_to_reminders(tasks: list, state: dict) -> dict:
    """Sync tasks to Reminders app. Returns sync summary."""
    summary = {
        "created": 0,
        "completed": 0,
        "deleted": 0,
        "updated": 0,
        "errors": []
    }

    existing_mappings = {m['task_hash']: m for m in state.get('mappings', [])}
    new_mappings = []
    seen_hashes = set()

    for task in tasks:
        seen_hashes.add(task['hash'])
        existing = existing_mappings.get(task['hash'])

        if existing:
            # Task exists - check for changes
            reminder_id = existing['reminder_id']

            # Check if completion status changed
            if task['completed'] and not existing.get('completed', False):
                result = run_reminders_command(["complete", reminder_id])
                if result.get('success'):
                    summary['completed'] += 1
                    existing['completed'] = True
                else:
                    summary['errors'].append(f"Failed to complete: {result.get('error')}")

            elif not task['completed'] and existing.get('completed', False):
                result = run_reminders_command(["uncomplete", reminder_id])
                if result.get('success'):
                    existing['completed'] = False
                else:
                    summary['errors'].append(f"Failed to uncomplete: {result.get('error')}")

            # Update mapping with current state
            existing['task_text'] = task['raw_text']
            existing['completed'] = task['completed']
            existing['last_modified'] = datetime.now().isoformat()
            new_mappings.append(existing)

        else:
            # New task - check for existing reminder first (prevents duplicates)
            reminder_name = task['clean_name']
            if task['blocked']:
                reminder_name = f"BLOCKED: {reminder_name}"

            # Check if a reminder with this name already exists
            existing_reminder = find_existing_reminder(task['list'], reminder_name)

            if existing_reminder:
                # Reuse existing reminder instead of creating duplicate
                reminder_id = existing_reminder['id']
                summary['updated'] += 1

                # Sync completion status
                if task['completed'] and not existing_reminder.get('completed', False):
                    run_reminders_command(["complete", reminder_id])
                    summary['completed'] += 1
                elif not task['completed'] and existing_reminder.get('completed', False):
                    run_reminders_command(["uncomplete", reminder_id])

                # Update body with current metadata
                body = build_reminder_body(task)
                run_reminders_command(["update", reminder_id, "--body", body])

                new_mappings.append({
                    "reminder_id": reminder_id,
                    "task_hash": task['hash'],
                    "task_text": task['raw_text'],
                    "list": task['list'],
                    "priority": task['priority'],
                    "priority_number": task['priority_number'],
                    "completed": task['completed'],
                    "blocked": task['blocked'],
                    "blocker_reason": task['blocker_reason'],
                    "source_file": task['source_file'],
                    "line_number": task['line_number'],
                    "section": task['section'],
                    "subtasks": task['subtasks'],
                    "created_at": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat(),
                    "source": "obsidian",
                    "recovered_from_orphan": True
                })
            else:
                # Create new reminder
                body = build_reminder_body(task)

                result = run_reminders_command([
                    "create",
                    "--list", task['list'],
                    "--name", reminder_name,
                    "--priority", str(task['reminders_priority']),
                    "--body", body
                ])

                if result.get('success'):
                    summary['created'] += 1
                    reminder_id = result['data']['id']

                    # If task is already completed in Obsidian, complete the reminder too
                    if task['completed']:
                        run_reminders_command(["complete", reminder_id])
                        summary['completed'] += 1

                    new_mappings.append({
                        "reminder_id": reminder_id,
                        "task_hash": task['hash'],
                        "task_text": task['raw_text'],
                        "list": task['list'],
                        "priority": task['priority'],
                        "priority_number": task['priority_number'],
                        "completed": task['completed'],
                        "blocked": task['blocked'],
                        "blocker_reason": task['blocker_reason'],
                        "source_file": task['source_file'],
                        "line_number": task['line_number'],
                        "section": task['section'],
                        "subtasks": task['subtasks'],
                        "created_at": datetime.now().isoformat(),
                        "last_modified": datetime.now().isoformat(),
                        "source": "obsidian"
                    })
                else:
                    summary['errors'].append(f"Failed to create '{reminder_name}': {result.get('error')}")

    # Check for deleted tasks (in state but not in current tasks)
    for task_hash, mapping in existing_mappings.items():
        if task_hash not in seen_hashes:
            # Task was deleted from daily note - delete reminder
            result = run_reminders_command(["delete", mapping['reminder_id']])
            if result.get('success'):
                summary['deleted'] += 1
            else:
                # Reminder might already be deleted - not an error
                pass

    # Update state
    state['mappings'] = new_mappings
    state['last_refresh'] = datetime.now().isoformat()
    state['daily_note_date'] = get_today_date()

    return summary


def main():
    """Main hook execution."""
    start = time.time()

    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        log_hook_execution(logger, "PostToolUse", status="error",
                          details={"error": "Invalid JSON input"})
        print(json.dumps({"status": "success"}))
        return

    tool_name = hook_input.get('tool_name', '')
    tool_input = hook_input.get('tool_input', {})

    # Only process Write and Edit tools
    if tool_name not in ['Write', 'Edit']:
        print(json.dumps({"status": "success"}))
        return

    file_path = tool_input.get('file_path', '')

    # Only process today's daily note
    if not is_todays_daily_note(file_path):
        print(json.dumps({"status": "success"}))
        return

    # Read the file content
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except IOError as e:
        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="error",
                          details={"error": str(e), "file": file_path})
        print(json.dumps({"status": "success"}))
        return

    # Parse tasks
    tasks = parse_tasks(content, file_path)

    # Load state
    state = load_state()

    # Check if this is a new day
    if state.get('daily_note_date') != get_today_date():
        # New day - clear mappings (will be rebuilt from scratch)
        state['mappings'] = []
        state['daily_note_date'] = get_today_date()

    # Sync tasks to Reminders
    summary = sync_tasks_to_reminders(tasks, state)

    # Save updated state
    save_state(state)

    # Report summary if any changes
    total_changes = summary['created'] + summary['completed'] + summary['deleted'] + summary['updated']
    if total_changes > 0:
        parts = []
        if summary['created'] > 0:
            parts.append(f"{summary['created']} created")
        if summary['updated'] > 0:
            parts.append(f"{summary['updated']} recovered")
        if summary['completed'] > 0:
            parts.append(f"{summary['completed']} completed")
        if summary['deleted'] > 0:
            parts.append(f"{summary['deleted']} deleted")

        message = f"Reminders synced: {', '.join(parts)}"
        if summary['errors']:
            message += f" ({len(summary['errors'])} errors)"

        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="success",
                          details={"created": summary['created'],
                                   "completed": summary['completed'],
                                   "deleted": summary['deleted'],
                                   "errors": len(summary['errors'])})
        print(json.dumps({
            "status": "success",
            "message": message
        }))
    else:
        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="success",
                          details={"changes": 0})
        print(json.dumps({"status": "success"}))


if __name__ == "__main__":
    main()
