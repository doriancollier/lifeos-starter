#!/usr/bin/env python3
"""
Session Context Loader Hook (SessionStart)

Loads today's context at the start of each Claude Code session:
- Today's daily note status (A-tasks, blocked tasks)
- Carryover tasks from yesterday (incomplete items)
- Project deadlines (overdue and upcoming within 14 days)
- Unprocessed files in inbox (0-Inbox/)
- Pending task syncs (if any)
- Proactive command suggestions:
  - /system:learn if learning log is stale (30+ days)
  - /board:advise if opportunities await evaluation or decision language detected

This context is injected into the session via additionalContext.
"""

import json
import sys
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add hooks directory to path for hook_logger import
sys.path.insert(0, os.path.dirname(__file__))
from hook_logger import setup_logger, log_hook_execution

# Initialize logger
logger = setup_logger("session-context-loader")

# Vault configuration - uses environment variable or auto-detects from script location
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or os.path.join(PROJECT_ROOT, "workspace")
DAILY_DIR = os.path.join(VAULT_ROOT, "4-Daily")
INBOX_DIR = os.path.join(VAULT_ROOT, "0-Inbox")
PROJECTS_DIR = os.path.join(VAULT_ROOT, "1-Projects", "Current")
SYNC_PENDING_FILE = os.path.join(PROJECT_ROOT, ".claude", "sync-pending")
SYNC_QUEUE_FILE = os.path.join(PROJECT_ROOT, ".claude", "sync-queue.json")
USER_CONFIG_FILE = os.path.join(VAULT_ROOT, "0-System", "config", "user-config.md")
LEARNING_LOG_FILE = os.path.join(VAULT_ROOT, "0-System", "config", "learning-log.md")
OPPORTUNITIES_FILE = os.path.join(VAULT_ROOT, "7-MOCs", "Opportunities-Pipeline.md")


def check_onboarding_status():
    """Check if onboarding has been completed."""
    if not os.path.exists(USER_CONFIG_FILE):
        return False
    try:
        with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check for onboarding_complete: true in frontmatter
            if 'onboarding_complete: true' in content:
                return True
    except Exception:
        pass
    return False


def get_today_date():
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


def get_yesterday_date():
    """Get yesterday's date in YYYY-MM-DD format."""
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def get_daily_note_path(date_str=None):
    """Get the path to a daily note."""
    if date_str is None:
        date_str = get_today_date()
    return os.path.join(DAILY_DIR, f"{date_str}.md")


def extract_tasks(content, pattern):
    """Extract tasks matching a pattern from content."""
    tasks = []
    for line in content.split('\n'):
        if re.search(pattern, line) and '- [ ]' in line:
            task = line.strip()
            tasks.append(task)
    return tasks


def get_inbox_items():
    """Get list of files in the inbox that need processing."""
    if not os.path.exists(INBOX_DIR):
        return []

    items = []
    for item in os.listdir(INBOX_DIR):
        # Skip hidden files and .gitkeep
        if item.startswith('.') or item == '.gitkeep':
            continue
        items.append(item)

    return items


def check_pending_sync():
    """Check if there are pending task syncs from external changes."""
    sync_info = {
        'pending': False,
        'timestamp': None,
        'queue_count': 0
    }

    # Check for sync-pending flag file
    if os.path.exists(SYNC_PENDING_FILE):
        try:
            with open(SYNC_PENDING_FILE, 'r') as f:
                sync_info['timestamp'] = f.read().strip()
            sync_info['pending'] = True
        except Exception:
            pass

    # Check sync queue for items
    if os.path.exists(SYNC_QUEUE_FILE):
        try:
            with open(SYNC_QUEUE_FILE, 'r') as f:
                queue = json.load(f)
                if isinstance(queue, list):
                    unprocessed = [item for item in queue if not item.get('processed', False)]
                    sync_info['queue_count'] = len(unprocessed)
                    if unprocessed:
                        sync_info['pending'] = True
        except (json.JSONDecodeError, Exception):
            pass

    return sync_info


def check_project_deadlines():
    """Scan current projects for overdue and upcoming deadlines."""
    deadline_info = {
        'overdue': [],
        'upcoming': [],  # Within 14 days
        'this_week': []  # Within 7 days
    }

    today = datetime.now().date()

    if not os.path.exists(PROJECTS_DIR):
        return deadline_info

    # Walk through project directories looking for entry point files
    for root, dirs, files in os.walk(PROJECTS_DIR):
        for file in files:
            if not file.endswith('.md'):
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(2000)  # Only read first 2KB for frontmatter
            except Exception:
                continue

            # Check if this is an entry point file (main project file)
            if 'entry_point: true' not in content:
                # Also check for files starting with _ (convention for main files)
                if not file.startswith('_'):
                    continue

            # Extract frontmatter
            if not content.startswith('---'):
                continue

            try:
                frontmatter_end = content.index('---', 3)
                frontmatter = content[3:frontmatter_end]
            except ValueError:
                continue

            # Extract title
            title_match = re.search(r'title:\s*["\']?([^"\'\n]+)["\']?', frontmatter)
            title = title_match.group(1) if title_match else file.replace('.md', '').replace('_', '')

            # Extract deadline or target_date
            deadline_match = re.search(r'deadline:\s*["\']?(\d{4}-\d{2}-\d{2})["\']?', frontmatter)
            target_match = re.search(r'target_date:\s*["\']?(\d{4}-\d{2}-\d{2})["\']?', frontmatter)

            date_str = None
            date_type = None
            if deadline_match:
                date_str = deadline_match.group(1)
                date_type = 'deadline'
            elif target_match:
                date_str = target_match.group(1)
                date_type = 'target'

            if not date_str:
                continue

            try:
                due_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                continue

            days_until = (due_date - today).days

            project_info = {
                'title': title,
                'date': date_str,
                'date_type': date_type,
                'days_until': days_until
            }

            if days_until < 0:
                project_info['days_overdue'] = abs(days_until)
                deadline_info['overdue'].append(project_info)
            elif days_until <= 7:
                deadline_info['this_week'].append(project_info)
            elif days_until <= 14:
                deadline_info['upcoming'].append(project_info)

    # Sort by urgency
    deadline_info['overdue'].sort(key=lambda x: x['days_overdue'], reverse=True)
    deadline_info['this_week'].sort(key=lambda x: x['days_until'])
    deadline_info['upcoming'].sort(key=lambda x: x['days_until'])

    return deadline_info


def get_carryover_tasks():
    """Get incomplete tasks from yesterday's daily note."""
    carryover = []

    yesterday_path = get_daily_note_path(get_yesterday_date())
    if not os.path.exists(yesterday_path):
        return carryover

    try:
        with open(yesterday_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return carryover

    # Find incomplete A-priority and B-priority tasks
    for line in content.split('\n'):
        if '- [ ]' in line:
            # Check for A-priority (🔴) or B-priority (🟡)
            if re.search(r'🔴\d?', line) or re.search(r'🟡', line):
                task = line.strip()
                # Skip template placeholders
                if '[Task]' in task or 'Task' == task.split()[-1]:
                    continue
                carryover.append(task)

    return carryover


def load_daily_note_context():
    """Load context from today's daily note."""
    daily_note_path = get_daily_note_path()
    context_parts = []

    # Check if daily note exists
    if not os.path.exists(daily_note_path):
        context_parts.append(f"[Daily Note] No daily note found for {get_today_date()}. The daily-note skill will auto-create it when needed.")
        return context_parts

    try:
        with open(daily_note_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        context_parts.append(f"[Daily Note] Error reading daily note: {e}")
        return context_parts

    # Extract A-priority tasks (uncompleted)
    a_tasks = extract_tasks(content, r'🔴\d?')
    if a_tasks:
        context_parts.append(f"[A-Priority Tasks] {len(a_tasks)} critical tasks today:")
        for task in a_tasks[:5]:  # Limit to 5
            context_parts.append(f"  {task}")

    # Extract blocked tasks
    blocked_tasks = extract_tasks(content, r'🔵')
    if blocked_tasks:
        context_parts.append(f"[Blocked Tasks] {len(blocked_tasks)} tasks waiting on dependencies:")
        for task in blocked_tasks[:3]:  # Limit to 3
            context_parts.append(f"  {task}")

    if not context_parts:
        context_parts.append(f"[Daily Note] Daily note exists for {get_today_date()} but no actionable items found.")

    return context_parts


def detect_learning_opportunities():
    """Detect if /system:learn should be suggested based on learning log staleness."""
    suggestions = []

    if not os.path.exists(LEARNING_LOG_FILE):
        # No learning log yet - that's fine for new vaults
        return suggestions

    try:
        stat = os.stat(LEARNING_LOG_FILE)
        days_since_learning = (time.time() - stat.st_mtime) / 86400

        if days_since_learning > 30:
            suggestions.append(
                f"[SYSTEM LEARNING] No new capabilities learned in {int(days_since_learning)} days. "
                "If you've discovered working patterns, consider `/system:learn codify [what worked]`"
            )
    except Exception:
        pass

    return suggestions


def detect_board_opportunities():
    """Detect if /board:advise should be suggested based on opportunities or decision language."""
    suggestions = []

    # Check Opportunities-Pipeline for unprocessed items
    if os.path.exists(OPPORTUNITIES_FILE):
        try:
            with open(OPPORTUNITIES_FILE, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for items under "Awaiting Evaluation" section
            if "Awaiting Evaluation" in content:
                # Split on the section header and get content until next section
                parts = re.split(r'##?#? ?🔴? ?Awaiting Evaluation', content, maxsplit=1)
                if len(parts) > 1:
                    # Get content until next heading (## or ---)
                    awaiting_section = re.split(r'\n##|\n---', parts[1])[0]

                    # Count items - support both list format (- item) and table format (| item |)
                    items = []

                    # Check for list items
                    list_items = [
                        l.strip() for l in awaiting_section.split('\n')
                        if l.strip().startswith('-') and len(l.strip()) > 3
                        and '[Opportunity]' not in l and 'template' not in l.lower()
                    ]
                    items.extend(list_items)

                    # Check for table rows (lines starting with | that aren't headers)
                    table_rows = [
                        l.strip() for l in awaiting_section.split('\n')
                        if l.strip().startswith('|') and '|' in l[1:]
                        and '---' not in l  # Skip separator rows
                        and 'Opportunity' not in l.split('|')[1][:20]  # Skip header row
                        and len(l.strip()) > 5
                    ]
                    items.extend(table_rows)

                    if len(items) >= 1:
                        suggestions.append(
                            f"[BOARD ADVISE] {len(items)} opportunity(ies) awaiting evaluation in pipeline. "
                            "For significant decisions, consider `/board:advise`"
                        )
        except Exception:
            pass

    # Check today's daily note for decision-related language
    today_note = get_daily_note_path()
    if os.path.exists(today_note):
        try:
            with open(today_note, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            # Decision keywords that suggest deliberation might help
            decision_keywords = [
                'should i', 'deciding', 'torn between', 'weighing options',
                'major decision', 'not sure whether', 'thinking about whether',
                'pros and cons', 'trade-off', 'tradeoff'
            ]

            matches = [kw for kw in decision_keywords if kw in content]
            if matches:
                suggestions.append(
                    "[BOARD ADVISE] Decision-related language detected in daily note. "
                    "For significant decisions, `/board:advise` provides multi-perspective deliberation"
                )
        except Exception:
            pass

    return suggestions


def main():
    """Main hook execution."""
    start_time = time.time()
    timings = {}  # Track per-function timings

    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    context_parts = []

    # Check onboarding status first
    t0 = time.time()
    onboarding_complete = check_onboarding_status()
    timings['onboarding_check'] = time.time() - t0
    if not onboarding_complete:
        context_parts.append("[FIRST-RUN DETECTED] This vault has not been personalized yet.")
        context_parts.append("[ACTION REQUIRED] You MUST immediately invoke the Skill tool with skill='setup:onboard' before doing anything else.")
        context_parts.append("[INSTRUCTION] Do not wait for user input. Auto-start the onboarding wizard now.")

    # Load daily note context
    t0 = time.time()
    daily_context = load_daily_note_context()
    context_parts.extend(daily_context)
    timings['daily_note'] = time.time() - t0

    # Check for carryover tasks from yesterday
    t0 = time.time()
    carryover = get_carryover_tasks()
    timings['carryover'] = time.time() - t0
    if carryover:
        context_parts.append(f"[Carryover] {len(carryover)} incomplete task(s) from yesterday:")
        for task in carryover[:5]:  # Limit to 5
            context_parts.append(f"  {task}")
        if len(carryover) > 5:
            context_parts.append(f"  ... and {len(carryover) - 5} more")

    # Check project deadlines
    t0 = time.time()
    deadlines = check_project_deadlines()
    timings['deadlines'] = time.time() - t0

    if deadlines['overdue']:
        context_parts.append(f"[OVERDUE] {len(deadlines['overdue'])} project(s) past deadline:")
        for proj in deadlines['overdue'][:3]:
            context_parts.append(f"  ⚠️ {proj['title']} - {proj['days_overdue']} days overdue ({proj['date']})")

    if deadlines['this_week']:
        context_parts.append(f"[Due This Week] {len(deadlines['this_week'])} project(s):")
        for proj in deadlines['this_week'][:3]:
            days_label = "today" if proj['days_until'] == 0 else f"in {proj['days_until']} days"
            context_parts.append(f"  📅 {proj['title']} - {days_label} ({proj['date']})")

    if deadlines['upcoming']:
        context_parts.append(f"[Upcoming] {len(deadlines['upcoming'])} project(s) due in 8-14 days:")
        for proj in deadlines['upcoming'][:2]:
            context_parts.append(f"  📆 {proj['title']} - in {proj['days_until']} days ({proj['date']})")

    # Check inbox for unprocessed items
    t0 = time.time()
    inbox_items = get_inbox_items()
    timings['inbox'] = time.time() - t0
    if inbox_items:
        context_parts.append(f"[Inbox] {len(inbox_items)} file(s) waiting to be processed:")
        for item in inbox_items[:5]:  # Limit to 5
            context_parts.append(f"  - {item}")
        if len(inbox_items) > 5:
            context_parts.append(f"  ... and {len(inbox_items) - 5} more")
        context_parts.append("  Use /inbox:process to triage these files")

    # Check for pending task syncs (from external/manual changes)
    t0 = time.time()
    sync_info = check_pending_sync()
    timings['sync_check'] = time.time() - t0
    if sync_info['pending']:
        if sync_info['queue_count'] > 0:
            context_parts.append(f"[Task Sync] {sync_info['queue_count']} task change(s) detected from external edits")
            context_parts.append("  Use the task-sync skill to reconcile daily notes with project files")
        else:
            context_parts.append("[Task Sync] External changes detected - consider running task-sync skill")

    # Proactive command suggestions
    t0 = time.time()
    learning_suggestions = detect_learning_opportunities()
    board_suggestions = detect_board_opportunities()
    timings['proactive_suggestions'] = time.time() - t0

    context_parts.extend(learning_suggestions)
    context_parts.extend(board_suggestions)

    # Add session info
    today = get_today_date()
    day_of_week = datetime.now().strftime("%A")

    # Calculate elapsed time
    elapsed = time.time() - start_time

    header = f"=== Obsidian Vault Session Context ({day_of_week}, {today}) ==="

    # Build detailed timing breakdown
    timing_breakdown = " | ".join([f"{k}: {v:.2f}s" for k, v in timings.items()])
    timing_note = f"[Hook Timing] session-context-loader.py: {elapsed:.2f}s ({timing_breakdown})"

    # Build additional context
    additional_context = header + "\n" + "\n".join(context_parts) + "\n" + timing_note

    # Output for SessionStart hook
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context
        }
    }

    # Log execution
    log_hook_execution(logger, "SessionStart",
                      duration=elapsed, status="success",
                      details={"context_parts": len(context_parts)})

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
