# Reminders Integration Skill

Bidirectional synchronization between Obsidian daily note tasks and macOS Reminders app, enabling mobile access via iPhone/Apple Watch and voice capture via Siri.

## Activation

Activate this skill when:
- User mentions Reminders, Siri tasks, or mobile task access
- Session context shows new reminders from Siri/mobile
- Session context shows incomplete carryover tasks from yesterday
- User wants to sync tasks with their phone/watch
- User asks about task availability on mobile devices
- Daily planning involves reminders check

## Architecture

```
Daily Note Tasks <--> reminders_manager.py <--> macOS Reminders.app
                             |                        |
                      reminders-state.json        iCloud Sync
                                                      |
                                              iPhone/Apple Watch
```

## Available Lists

| List Name | Company Context | Notes |
|-----------|-----------------|-------|
| {{company_1_name}} | {{company_1_name}} | Work tasks for {{company_1_name}} |
| {{company_2_name}} | {{company_2_name}} | Joint venture tasks |
| EMC | {{company_3_name}} | EMC business tasks |
| Personal | Personal / Default | Personal tasks, default for untagged |

## Priority Mapping

| Daily Note | Reminders Priority | Notes |
|------------|-------------------|-------|
| 🔴 A-priority | 1 (High) | A1-A5 numbering preserved in notes |
| 🟡 B-priority | 5 (Medium) | |
| 🟢 C-priority | 9 (Low) | |
| 🔵 Blocked | 5 (Medium) | "BLOCKED:" prefix in name |

## Usage

### Via Python Script

The `reminders_manager.py` script provides all Reminders operations:

```bash
# ═══════════════════════════════════════════════════════════════════
# SETUP COMMANDS
# ═══════════════════════════════════════════════════════════════════

# Create the 4 LifeOS lists if they don't exist
python3 .claude/scripts/reminders_manager.py setup-lists

# Remove all existing reminders from LifeOS lists (fresh start)
python3 .claude/scripts/reminders_manager.py clear-all

# ═══════════════════════════════════════════════════════════════════
# READ COMMANDS
# ═══════════════════════════════════════════════════════════════════

# List all LifeOS lists
python3 .claude/scripts/reminders_manager.py list-lists

# Get all reminders from a specific list
python3 .claude/scripts/reminders_manager.py list-reminders "Personal"

# Get all incomplete reminders across all LifeOS lists
python3 .claude/scripts/reminders_manager.py get-incomplete

# Get a specific reminder by ID
python3 .claude/scripts/reminders_manager.py get "Personal" "x-apple-reminder://UUID"

# ═══════════════════════════════════════════════════════════════════
# CREATE/UPDATE COMMANDS
# ═══════════════════════════════════════════════════════════════════

# Create a new reminder
python3 .claude/scripts/reminders_manager.py create --list "Personal" --name "Call Texas Diabetes" \
  --priority 1 \
  --body "Source: 4-Daily/2025-12-05.md"

# Mark reminder as complete
python3 .claude/scripts/reminders_manager.py complete "x-apple-reminder://UUID"

# Mark reminder as incomplete (uncomplete)
python3 .claude/scripts/reminders_manager.py uncomplete "x-apple-reminder://UUID"

# Update reminder properties
python3 .claude/scripts/reminders_manager.py update "x-apple-reminder://UUID" \
  --name "New name" \
  --priority 5 \
  --body "Updated body"

# ═══════════════════════════════════════════════════════════════════
# DELETE COMMANDS
# ═══════════════════════════════════════════════════════════════════

# Delete a specific reminder
python3 .claude/scripts/reminders_manager.py delete "x-apple-reminder://UUID"

# Delete all reminders from a list
python3 .claude/scripts/reminders_manager.py delete-list-reminders "Personal"
```

### Slash Command

```bash
# Manual bidirectional sync
/reminders:refresh
```

This performs a full sync between today's daily note and Reminders app.

## Synchronization Behavior

### Automatic (Push): Obsidian -> Reminders

When tasks are edited in today's daily note (via PostToolUse hook):
1. New tasks are created as reminders
2. Completed tasks mark reminders complete
3. Deleted tasks remove reminders
4. Modified tasks update reminders

**Duplicate Detection**: Before creating a new reminder, the hook:
1. Normalizes the task name (removes "BLOCKED:" prefix, ✅ checkmarks, normalizes whitespace)
2. Searches for existing reminders with matching names in the target list
3. If found, reuses the existing reminder instead of creating a duplicate
4. Marks recovered reminders with `recovered_from_orphan: true` in state

### On Session Start (Pull): Reminders -> Obsidian

When a Claude Code session starts (via `reminders-session-sync.py` hook):
1. Checks each mapped reminder's completion status
2. If a reminder was completed in the app, marks the task complete in daily note
3. If a reminder was uncompleted, marks the task incomplete
4. Reports synced tasks in session context

### Manual: /reminders:refresh

Performs bidirectional sync on demand:
1. Pushes all daily note tasks to Reminders
2. Pulls all Reminders changes to daily note
3. Reports sync status

## Orphan Recovery

### What Are Orphaned Reminders?

When the state file (`state/reminders-state.json`) is reset or lost, existing reminders in the Reminders app become "orphaned" - they still exist but have no mapping to Obsidian tasks.

### How Recovery Works

The push hook automatically recovers orphaned reminders:

1. **Name Matching**: When syncing a task without an existing mapping, the hook searches for reminders with matching names
2. **Normalization**: Names are normalized for comparison (ignoring "BLOCKED:" prefix, checkmarks, whitespace differences)
3. **Reuse**: If a matching reminder is found, it's linked to the task instead of creating a duplicate
4. **State Update**: The mapping is recreated with `recovered_from_orphan: true`

### Why This Matters

- **State resets are safe**: You can delete the state file without creating duplicates
- **Bug fixes are easier**: When fixing sync issues, you won't orphan existing reminders
- **No manual cleanup**: The system self-heals by reconnecting orphans

## State File

Location: `state/reminders-state.json`

```json
{
  "last_refresh": "2025-12-05T09:30:00",
  "daily_note_date": "2025-12-05",
  "mappings": [
    {
      "task_hash": "abc123...",
      "reminder_id": "x-apple-reminder://UUID",
      "task_text": "Call Texas Diabetes",
      "company": "Personal",
      "priority": "A",
      "completed": false,
      "last_synced": "2025-12-05T09:30:00"
    }
  ]
}
```

## Company Detection

How tasks are assigned to Reminders lists:

1. **Primary**: Section header the task is under
   - `### {{company_1_name}}` -> {{company_1_name}} list
   - `### {{company_2_name}}` -> {{company_2_name}} list
   - `### EMC` or `### {{company_3_name}}` -> EMC list
   - `### Personal` -> Personal list

2. **Fallback**: "Company: X" tag in task text
   - `- [ ] Review PR - Company: {{company_1_name}}` -> {{company_1_name}} list

3. **Default**: Personal list

## Common Use Cases

### Morning Planning with Reminders Check

When session starts with pending reminders:

```
Session context shows:
[Reminders] 3 new reminder(s) from Siri/mobile:
  - Call passport office (Personal)
  - Review quarterly report ({{company_1_name}})
  - Order printer ink (Personal)

Action: Run /reminders:refresh to add these to today's daily note
```

### Creating Tasks for Mobile Access

Tasks added to daily note automatically sync:

```markdown
### Personal
- [ ] 🔴1. Pick up prescription - Company: Personal
- [ ] 🟡 Buy groceries
```

These appear in the Personal Reminders list within seconds.

### Day Transition Handling

When starting a new day with incomplete tasks:

```
Session context shows:
[Reminders] New day detected - 2 incomplete task(s) from yesterday:
  - Call Texas Diabetes (Personal)
  - Review PR ({{company_1_name}})

Consider running /reminders:refresh to handle carryover
```

### Siri Task Capture

User says: "Hey Siri, remind me to call Alex about the roadmap"

Next session start detects this and prompts to add to daily note.

## Reminder Notes Field Format

Each reminder's notes/body contains metadata:

```
Source: 4-Daily/2025-12-05.md
Company: {{company_1_name}}
Priority: A1
---
Subtasks:
- [x] Find phone number
- [ ] Prepare questions
```

## Error Handling

### Reminders App Not Accessible

If AppleScript can't access Reminders:
1. System Preferences -> Privacy & Security -> Automation
2. Enable Terminal/IDE access to Reminders

### State File Issues

If `state/reminders-state.json` is corrupted or needs reset:
1. Delete the file (this is safe - orphan recovery will reconnect existing reminders)
2. Edit the daily note or run `/reminders:refresh`
3. The hook will recover existing reminders by name matching
4. Check the state file - recovered reminders have `recovered_from_orphan: true`

**Note**: State resets no longer cause duplicates thanks to orphan recovery.

### iCloud Sync Delays

Mobile-created reminders may take a few seconds to sync:
- Wait briefly before expecting new items
- Run `/reminders:refresh` if items seem missing

## Limitations

1. **No tag support**: AppleScript doesn't expose Reminders tags
2. **No recurring reminders**: Out of scope for v1
3. **Single device at a time**: Concurrent edits may cause brief inconsistencies
4. **iCloud required**: Mobile access requires iCloud sync
5. **No due dates in v1**: Tasks don't sync due times

## Integration Points

### With daily-note skill
Tasks created/modified in daily notes automatically sync to Reminders.

### With task-system skill
Respects A/B/C priority system. Blocked tasks (🔵) sync with BLOCKED: prefix.

### With /daily:plan command
Morning planning can check for new reminders and carryover tasks.

### With /daily:eod command
End-of-day can report reminders sync status.

## Separate from task-sync

**Important**: Reminders integration is separate from task-sync:
- **task-sync**: Daily notes <-> Project files (within Obsidian)
- **reminders-integration**: Daily notes <-> Reminders app (external)

These systems operate independently.

## Debugging

### Common Issues and Solutions

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Duplicates appearing | Old orphaned reminders + new ones created | Delete state file, edit daily note to trigger recovery |
| Completions not syncing back | Session sync hook not running | Check `.claude/settings.json` has `reminders-session-sync.py` in SessionStart |
| Wrong list assignment | Task in wrong section | Check the `### Section` header the task is under |
| Reminder has wrong metadata | Stale body text | Run `/reminders:refresh` to update all bodies |

### Debugging Commands

```bash
# Check current reminders in each list
python3 .claude/scripts/reminders_manager.py list-reminders "Personal"
python3 .claude/scripts/reminders_manager.py list-reminders "{{company_1_name}}"
python3 .claude/scripts/reminders_manager.py list-reminders "{{company_2_name}}"

# Check state file for mappings
cat state/reminders-state.json | python3 -m json.tool

# Check for recovered orphans (look for recovered_from_orphan: true)
grep "recovered_from_orphan" state/reminders-state.json

# Test the push hook manually
echo '{"tool_name": "Write", "tool_input": {"file_path": "/path/to/daily/note.md"}}' | \
  python3 .claude/hooks/reminders-task-detector.py

# Test the session sync hook manually
echo '{}' | python3 .claude/hooks/reminders-session-sync.py
```

### Clean Slate Recovery

If things are very broken:

1. Clear all LifeOS reminders:
   ```bash
   python3 .claude/scripts/reminders_manager.py clear-all
   ```

2. Delete state file:
   ```bash
   rm state/reminders-state.json
   ```

3. Trigger fresh sync by editing daily note or running `/reminders:refresh`

## File Locations

| Component | Path |
|-----------|------|
| Python Script | `.claude/scripts/reminders_manager.py` |
| State File | `state/reminders-state.json` |
| Push Hook (PostToolUse) | `.claude/hooks/reminders-task-detector.py` |
| Pull Hook (SessionStart) | `.claude/hooks/reminders-session-sync.py` |
| Refresh Command | `.claude/commands/reminders/refresh.md` |
| This Skill | `.claude/skills/reminders-integration/SKILL.md` |
