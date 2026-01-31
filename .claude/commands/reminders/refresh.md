---
description: Bidirectional sync between Obsidian tasks and macOS Reminders
argument-hint:
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Reminders Refresh Command

Performs a full bidirectional synchronization between today's daily note tasks and macOS Reminders app.

## When to Use

- At session start when prompted about new reminders from Siri/mobile
- When you want to ensure daily note and Reminders are in sync
- After making bulk changes to tasks
- To pull in tasks created via Siri, iPhone, or Apple Watch

## Architecture

```
Daily Note Tasks ←→ reminders_manager.py ←→ macOS Reminders.app
                           ↓
                    reminders-state.json
```

## Context

- **Script**: `.claude/scripts/reminders_manager.py`
- **State file**: `.claude/reminders-state.json`
- **Daily notes**: `4-Daily/YYYY-MM-DD.md`
- **Reminder lists**: {{company_1_name}}, {{company_2_name}}, EMC, Personal

## Task Priority Mapping

| Daily Note | Reminders Priority |
|------------|-------------------|
| 🔴 A-Priority | 1 (High) |
| 🟡 B-Priority | 5 (Medium) |
| 🟢 C-Priority | 9 (Low) |
| 🔵 Blocked | 9 (Low) + "BLOCKED:" prefix |

## Company → List Mapping

| Company Context | Reminders List |
|-----------------|----------------|
| {{company_1_name}} | {{company_1_name}} |
| {{company_2_name}} | {{company_2_name}} |
| EMC | EMC |
| Personal / Other | Personal |

## Order of Operations

Execute these steps sequentially:

### 1. Load Current State

```bash
# Get current state
cat "{{vault_path}}/.claude/reminders-state.json"
```

Read existing mappings between tasks and reminders.

### 2. Get Today's Daily Note

```bash
# Today's date
date +%Y-%m-%d
```

Read today's daily note at `4-Daily/YYYY-MM-DD.md`.

### 3. Extract All Tasks from Daily Note

Parse the daily note Work section to find all tasks:
- Look for `- [ ]` (incomplete) and `- [x]` (complete) patterns
- Extract priority emoji (🔴, 🟡, 🟢, 🔵)
- Identify company context from parent header (e.g., "### {{company_1_name}}")
- Extract task text and any subtasks

### 4. Get All Reminders from Reminders.app

```bash
python3 "{{vault_path}}/.claude/scripts/reminders_manager.py" list-reminders "{{company_1_name}}"
python3 "{{vault_path}}/.claude/scripts/reminders_manager.py" list-reminders "{{company_2_name}}"
python3 "{{vault_path}}/.claude/scripts/reminders_manager.py" list-reminders "EMC"
python3 "{{vault_path}}/.claude/scripts/reminders_manager.py" list-reminders "Personal"
```

### 5. Sync: Reminders → Daily Note (Pull)

For each reminder NOT in state mappings:
1. This is a new reminder created via Siri/mobile
2. Determine which section based on the list name
3. Add to daily note under appropriate company header
4. Create mapping entry

For each reminder that's completed but task isn't:
1. Mark the task as complete in daily note (`- [x]`)

For each reminder that's deleted (in mappings but not in Reminders):
1. Remove the task from daily note
2. Remove mapping entry

### 6. Sync: Daily Note → Reminders (Push)

For each task NOT in state mappings:
1. Create a new reminder
2. Set list based on company context
3. Set priority based on emoji
4. Add subtasks to body/notes field
5. Create mapping entry

For each completed task where reminder isn't complete:
1. Mark reminder as complete

For each deleted task (in mappings but not in daily note):
1. Delete the reminder
2. Remove mapping entry

### 7. Handle Updates

For tasks/reminders that both exist:
- Compare task text - if different, use last-modified wins
- Compare priority - sync if changed
- Compare completion status - sync if changed

### 8. Save Updated State

Write updated state file with new mappings:

```json
{
  "last_refresh": "2025-01-15T10:30:00",
  "daily_note_date": "2025-01-15",
  "mappings": [
    {
      "task_hash": "abc123...",
      "reminder_id": "x-apple-reminder://...",
      "task_text": "Call mom",
      "company": "Personal",
      "priority": "B",
      "last_synced": "2025-01-15T10:30:00"
    }
  ]
}
```

### 9. Day Transition Handling

If `daily_note_date` in state differs from today:
1. This is a new day
2. For each incomplete reminder from yesterday:
   - Add to today's daily note as carryover task
   - Update mapping to point to today's task

## Output Format

```markdown
## Reminders Sync Complete

### Summary
- **Pulled from Reminders**: X new tasks
- **Pushed to Reminders**: Y new reminders
- **Completed synced**: Z tasks
- **Deleted synced**: W items

### New from Siri/Mobile
- [List any tasks that came from Reminders]

### Pushed to Reminders
- [List any tasks that were synced to Reminders]

### Completions
- [List any completion status changes]

### Issues (if any)
- [Any errors or conflicts that need attention]
```

## reminders_manager.py Commands Reference

| Command | Description |
|---------|-------------|
| `list-reminders <list>` | Get all reminders in a list |
| `get-incomplete` | Get all incomplete reminders across all lists |
| `get <list> <id>` | Get specific reminder details |
| `create --list <list> --name <name> [--priority N] [--body text]` | Create reminder |
| `complete <id>` | Mark reminder complete |
| `uncomplete <id>` | Mark reminder incomplete |
| `update <id> [--name X] [--priority N] [--body X]` | Update reminder |
| `delete <id>` | Delete reminder |

## Task Hash Generation

To match tasks between systems, generate a hash from:
- Normalized task text (lowercase, trimmed, no timestamps)
- Company context
- Priority level

This allows matching even if minor formatting changes occur.

## Error Handling

- If Reminders.app is inaccessible, report error and skip sync
- If daily note doesn't exist, create it first using daily-note skill
- If mapping is orphaned (task/reminder deleted externally), clean up
- Log all sync operations for debugging
