# Obsidian Vault Hooks

This directory contains Claude Code hooks for maintaining vault quality and consistency.

## Installation

Add the following configuration to your Claude Code settings file at `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {"type": "command", "command": "{{vault_path}}/.claude/hooks/version-check.py"}
        ]
      },
      {
        "matcher": "",
        "hooks": [
          {"type": "command", "command": "{{vault_path}}/.claude/hooks/session-context-loader.py"}
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {"type": "command", "command": "{{vault_path}}/.claude/hooks/prompt-timestamp.py"}
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {"type": "command", "command": "{{vault_path}}/.claude/hooks/directory-guard.py"}
        ]
      },
      {
        "matcher": "mcp__google-calendar__delete-event",
        "hooks": [
          {"type": "command", "command": "{{vault_path}}/.claude/hooks/calendar-protection.py"}
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "^(Write|Edit)$",
        "hooks": [
          {"type": "command", "command": "{{vault_path}}/.claude/hooks/frontmatter-validator.py"}
        ]
      },
      {
        "matcher": "^(Write|Edit)$",
        "hooks": [
          {"type": "command", "command": "{{vault_path}}/.claude/hooks/task-format-validator.py"}
        ]
      },
      {
        "matcher": "^(Write|Edit)$",
        "hooks": [
          {"type": "command", "command": "{{vault_path}}/.claude/hooks/table-format-validator.py"}
        ]
      },
      {
        "matcher": "^(Write|Edit)$",
        "hooks": [
          {"type": "command", "command": "{{vault_path}}/.claude/hooks/task-sync-detector.py"}
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {"type": "command", "command": "{{vault_path}}/.claude/hooks/auto-git-backup.sh"}
        ]
      }
    ]
  }
}
```

**Note**: The format changed in early 2026. Each hook entry requires:
- `"matcher"`: A regex string for tool filtering, or `""` (empty string) for no filtering
- `"hooks"`: Array of hook definitions

Run `/system:configure-hooks` to regenerate settings.json based on your `.user/integrations.yaml`.

## Hooks Overview

| Hook | Event | Purpose | Behavior |
|------|-------|---------|----------|
| `session-context-loader.py` | SessionStart | Load daily context | Injects today's tasks, meetings, sync status |
| `reminders-session-sync.py` | SessionStart | Sync Reminders completions | Pulls task completions from Reminders to daily note |
| `health-session-sync.py` | SessionStart | Sync health data | Syncs Health Auto Export data, shows daily status |
| `prompt-timestamp.py` | UserPromptSubmit | Inject current time | Adds timestamp to every prompt |
| `directory-guard.py` | PreToolUse (Write) | Enforce directory structure | **BLOCKS** files in wrong directories |
| `calendar-protection.py` | PreToolUse (Calendar) | Protect calendar events | **BLOCKS** deletes/updates without confirmation |
| `frontmatter-validator.py` | PostToolUse (Write/Edit) | Validate YAML frontmatter | Warns on issues |
| `task-format-validator.py` | PostToolUse (Write/Edit) | Validate task formatting | Warns on issues |
| `table-format-validator.py` | PostToolUse (Write/Edit) | Validate table formatting | Warns on missing blank lines |
| `task-sync-detector.py` | PostToolUse (Write/Edit) | Detect task changes | Queues syncs, suggests reconciliation |
| `reminders-task-detector.py` | PostToolUse (Write/Edit) | Sync tasks to Reminders | Creates/updates macOS Reminders |
| `auto-git-backup.sh` | SessionEnd | Auto-commit changes | Creates backup commits with change summary |
| `git-task-sync-detector.sh` | Git post-commit (manual) | Detect external changes | Flags syncs for next session |
| `changelog-populator.py` | Git post-commit | Auto-populate changelog | Adds entries from conventional commits |

## Hook Details

### Session Context Loader (`session-context-loader.py`)

**Event**: SessionStart
**Behavior**: Injects context (does not block)

Loads at session start:
- Today's daily note status
- Uncompleted A-priority tasks (max 5)
- Blocked tasks requiring attention
- Today's meetings
- Energy level and focus areas from frontmatter
- Pending task syncs (from external changes)
- Inbox items waiting for processing
- Weekly review status (Monday/Tuesday detection, prompts for /weekly:reflect)

### Reminders Session Sync (`reminders-session-sync.py`)

**Event**: SessionStart
**Behavior**: Syncs task completions (does not block)

Pulls completion status from macOS Reminders back to Obsidian:
- Checks each mapped reminder's completion status
- If a reminder was completed in Reminders app, marks the task complete in daily note
- If a reminder was uncompleted, marks the task incomplete in daily note
- Reports synced tasks in session context

This enables bidirectional sync:
- **Obsidian → Reminders**: Automatic via `reminders-task-detector.py` (PostToolUse)
- **Reminders → Obsidian**: Automatic via this hook (SessionStart)

### Health Session Sync (`health-session-sync.py`)

**Event**: SessionStart
**Behavior**: Syncs health data (does not block)

Syncs Apple Health data via Health Auto Export and provides quick status:
- Syncs last 3 days of health data from JSON files
- Provides compact status summary for today's metrics
- Shows ring closure status (Move, Exercise, Stand)
- Displays sleep hours with goal progress

Example session context output:
```
[Health] | Synced 3 day(s) | 2026-01-11: Move 🟨 | Exercise 🟨 | Stand 🟨 | Sleep 5.7h 🟩
```

Requires:
- Health Auto Export app exporting to iCloud Drive
- `.claude/scripts/health_sync.py` script
- `.claude/data/health.db` database

### Prompt Timestamp (`prompt-timestamp.py`)

**Event**: UserPromptSubmit
**Behavior**: Injects context (does not block)

Adds the current date and time to every prompt, including:
- Full timestamp (YYYY-MM-DD HH:MM:SS)
- Day of week
- Timezone

Example output: `Current time: Tuesday, 2025-11-25 14:32:15 CST`

### Calendar Protection (`calendar-protection.py`)

**Event**: PreToolUse (Calendar modification tools)
**Behavior**: BLOCKS without confirmation

Protects against accidental calendar modifications:

| Operation | Behavior |
|-----------|----------|
| Delete any event | **BLOCKS** - requires user confirmation |
| Update with attendees | **BLOCKS** - warns about notification emails |
| Update recurring (thisAndFollowing/all) | **BLOCKS** - warns about multiple instances |
| Update time | **BLOCKS** - confirms time change |
| Other updates | Allows |

This prevents accidental deletion of important events and ensures users are aware when their actions will send emails to attendees.

### Directory Guard (`directory-guard.py`)

**Event**: PreToolUse (Write only)
**Behavior**: BLOCKS invalid operations

Enforces directory placement rules:

| File Pattern | Required Directory |
|--------------|-------------------|
| `YYYY-MM-DD.md` | `4-Daily/` |
| `*meeting*.md`, `*sync*.md` | `5-Meetings/` |
| `type: daily-note` | `4-Daily/` |
| `type: meeting` | `5-Meetings/` |
| `type: person` | `6-People/` |
| `type: project` | `1-Projects/` |
| `type: moc` | `7-MOCs/` |

**Note**: Only blocks NEW file creation. Existing files can be edited anywhere.

### Frontmatter Validator (`frontmatter-validator.py`)

**Event**: PostToolUse (Write/Edit)
**Behavior**: Warns (does not block)

Validates:
- Required fields by note type
- Date format (YYYY-MM-DD)
- Valid company values
- Valid note types
- Daily note date matches filename
- Day of week matches date

Required fields by type:

| Type | Required Fields |
|------|-----------------|
| `daily-note` | date, day_of_week, type, tags |
| `meeting` | title, date, type, company, attendees, tags |
| `person` | name, type, relationship |
| `project` | title, type, status |

### Task Format Validator (`task-format-validator.py`)

**Event**: PostToolUse (Write/Edit)
**Behavior**: Warns (does not block)

Validates:
- A-priority tasks (🔴) have numbers 1-5
- No more than 5 A-priority tasks per daily note
- A-priority numbers are sequential (1, 2, 3...)
- No duplicate A-priority numbers
- Blocked tasks (🔵) include "Waiting for:" context

### Table Format Validator (`table-format-validator.py`)

**Event**: PostToolUse (Write/Edit)
**Behavior**: Warns (does not block)

Validates markdown table formatting for Obsidian compatibility:
- Tables must have a blank line before the header row
- Without a blank line, Obsidian won't render the table correctly

Example warning:
```
Table Format Warnings:
  - Line 42: Table missing blank line before it. Preceded by: "**Quarterly Milestones**:"
```

### Task Sync Detector (`task-sync-detector.py`)

**Event**: PostToolUse (Write/Edit)
**Behavior**: Queues syncs, suggests action

Detects task changes in daily notes and project files:
- Triggers on Write/Edit to `1-Projects/` or `4-Daily/`
- Parses content for task patterns (checkboxes, priority emojis)
- Determines project context from section headers
- Writes sync requirements to `.claude/sync-queue.json`
- Suggests using the `task-sync` skill to reconcile

### Git Task Sync Detector (`git-task-sync-detector.sh`)

**Event**: Git post-commit (or manual execution)
**Behavior**: Flags external changes for next session

Detects external/manual changes to task files:
- Analyzes git diffs for task-related changes
- Creates `.claude/sync-pending` flag file
- Next Claude Code session's SessionStart hook detects this
- User is prompted to run task-sync skill

**Setup as Git Hook** (optional):
```bash
ln -s {{vault_path}}/.claude/hooks/git-task-sync-detector.sh \
      {{vault_path}}/.git/hooks/post-commit
chmod +x {{vault_path}}/.git/hooks/post-commit
```

### Changelog Populator (`changelog-populator.py`)

**Event**: Git post-commit
**Behavior**: Auto-updates changelog (does not block)

Automatically populates `0-System/changelog.md` from conventional commit messages:
- Parses commit message prefix (feat:, fix:, docs:, etc.)
- Only processes commits that modify system files
- Ignores user content directories
- Amends the commit to include the changelog update

Commit prefix to changelog section mapping:

| Prefix | Changelog Section |
|--------|-------------------|
| `feat:` | ### Added |
| `fix:` | ### Fixed |
| `docs:` | ### Changed |
| `refactor:` | ### Changed |
| `chore:` | *(skipped)* |

Skipped commit types:
- `chore:` - Maintenance tasks
- `vault backup:` - Auto-backup commits
- Merge commits
- Revert commits

System files tracked:
- `.claude/skills/`, `.claude/commands/`, `.claude/agents/`, `.claude/hooks/`
- `.claude/scripts/`, `.claude/rules/`
- `0-System/`
- `CLAUDE.template.md`, `VERSION`

**Installation**:
```bash
.claude/scripts/install-git-hooks.sh
```

See `0-System/guides/versioning.md` for conventional commit format details.

### Auto Git Backup (`auto-git-backup.sh`)

**Event**: SessionEnd
**Behavior**: Commits if changes exist (once per session)

Actions:
- Checks for uncommitted changes
- Stages all changes (`git add -A`)
- Generates a summary of changes by directory (daily notes, meetings, projects, etc.)
- Creates commit with message including timestamp and change summary
- Does NOT push automatically (safety)

Commit message format:
```
vault backup: 2025-12-30 14:30:00 (1 daily, 2 system)

Changed files:
  - 4-Daily/2025-12-30.md
  - .claude/hooks/auto-git-backup.sh
  - .claude/hooks/README.md

Auto-committed by Claude Code session hook
```

**Note**: Uses `SessionEnd` (not `Stop`) to commit only once when you exit the session, not after every Claude response.

## Customization

### Making a Hook Block Operations

Change the exit code and output format:

```python
# To block an operation
output = {
    "decision": "block",
    "reason": "Explanation of why blocked"
}
print(json.dumps(output))
sys.exit(2)  # Exit code 2 = block
```

### Adding Custom Validation Rules

Edit the respective hook file to add new rules:

**Frontmatter**: Add to `REQUIRED_FIELDS` dict or validation functions
**Tasks**: Add new regex patterns and validation in `validate_tasks()`
**Directories**: Add to `DIRECTORY_RULES` or `get_expected_directory()`

## Hook Logging

All Python hooks use a centralized logging system for debugging and error visibility.

### Log Location

```
.claude/hooks/logs/hooks.log
```

The log file rotates automatically at 1MB with 3 backup files retained.

### Viewing Logs

```bash
# View recent log entries
tail -50 .claude/hooks/logs/hooks.log

# Watch logs in real-time
tail -f .claude/hooks/logs/hooks.log

# Search for errors
grep '"status": "error"' .claude/hooks/logs/hooks.log

# Search for a specific hook
grep 'directory-guard' .claude/hooks/logs/hooks.log
```

### Log Format

Each entry is a structured JSON object:

```json
{
  "timestamp": "2026-01-31T10:55:45",
  "event": "PostToolUse",
  "tool": "Edit",
  "duration_ms": 45,
  "status": "success",
  "details": {"file": "2026-01-31.md"}
}
```

Fields:
- `event`: Hook event type (SessionStart, PreToolUse, PostToolUse, UserPromptSubmit)
- `tool`: Tool name if applicable (Write, Edit, etc.)
- `duration_ms`: Execution time in milliseconds
- `status`: "success", "warning", or "error"
- `details`: Hook-specific context (file paths, counts, error messages)

### Claude Code Debug Mode

For real-time hook visibility during sessions:

```bash
# Run with verbose mode to see hook execution
claude --verbose

# Run with debug mode for detailed output
claude --debug "hooks"
```

In-session: Press `Ctrl+O` to toggle verbose mode.

### Exit Code Meanings

| Exit Code | Behavior |
|-----------|----------|
| 0 | Success (non-blocking) |
| 2 | Blocking error (stderr shown to Claude as error message) |
| Other | Non-blocking error (stderr shown in verbose mode) |

## Troubleshooting

### Hooks Not Running

1. Check settings.json is correctly formatted (valid JSON)
2. Ensure hook files are executable: `chmod +x *.py *.sh`
3. Test hooks manually: `echo '{}' | ./hook-name.py`
4. Restart Claude Code after settings changes

### Session Context Not Loading

1. Verify today's daily note exists in `4-Daily/YYYY-MM-DD.md`
2. Check daily note has valid YAML frontmatter
3. Run manually to see output: `echo '{}' | ./session-context-loader.py`

### Directory Guard Too Strict

The guard only blocks NEW file creation. If you need to create a file in a non-standard location:
1. Create it in the correct location and move it, or
2. Temporarily disable the hook in settings.json

## Development

All hooks receive JSON input via stdin with session and tool context:

```json
{
  "session_id": "abc123",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.md",
    "content": "file contents..."
  }
}
```

Hooks can output JSON to stdout for specific behaviors:
- SessionStart: `{"hookSpecificOutput": {"additionalContext": "..."}}`
- Pre/PostToolUse: `{"decision": "block|approve", "reason": "..."}`
