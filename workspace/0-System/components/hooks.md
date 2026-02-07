---
title: "Hooks"
created: "2025-12-02"
status: "active"
---

# Hooks

> **AI context version**: `.claude/rules/components.md` (summary loaded into CLAUDE.md)

Hooks are scripts that run automatically at specific lifecycle events.

## How Hooks Work

Hooks are **event-triggered** — they run automatically when certain events occur in Claude Code.

```
Event: SessionStart
       ↓
Hook: session-context-loader.py runs
       ↓
Output injected into Claude's context
       ↓
Claude starts with awareness
```

## Key Characteristics

- **Deterministic** — Always run at their trigger event
- **Can block operations** — PreToolUse hooks can prevent actions
- **No Claude involvement** — Run before/after Claude
- **Shell or Python** — Written as scripts

## Hook Events

| Event | When It Fires | Use Case |
|-------|--------------|----------|
| `SessionStart` | Session begins | Load context |
| `UserPromptSubmit` | User sends message | Add timestamp |
| `PreToolUse` | Before tool runs | Validate/block |
| `PostToolUse` | After tool runs | Validate output |
| `Stop` | Session ends | Backup/cleanup |

## Available Hooks

### Context Injection

| Hook | Event | Purpose | Status |
|------|-------|---------|--------|
| `session-context-loader.py` | SessionStart | Load today's tasks, deadlines, inbox, carryover; proactive command suggestions | Active |
| `reminders-session-sync.py` | SessionStart | Pull Reminders completions to daily note | *Not configured* |
| `health-session-sync.py` | SessionStart | Sync health data from Health Auto Export | Active |
| `prompt-timestamp.py` | UserPromptSubmit | Add current time to each prompt | Active |

### Validation

| Hook | Event | Purpose | Status |
|------|-------|---------|--------|
| `frontmatter-validator.py` | PostToolUse (Write/Edit) | Validate YAML frontmatter | Active |
| `task-format-validator.py` | PostToolUse (Write/Edit) | Validate task formatting | Active |
| `table-format-validator.py` | PostToolUse (Write/Edit) | Validate markdown table formatting | Active |
| `task-sync-detector.py` | PostToolUse (Write/Edit) | Detect task changes, queue syncs | Active |
| `reminders-task-detector.py` | PostToolUse (Write/Edit) | Sync tasks to macOS Reminders | *Not configured* |

### External Change Detection

| Hook | Event | Purpose |
|------|-------|---------|
| `git-task-sync-detector.sh` | Git post-commit (manual) | Detect manual/external task changes |

### Protection

| Hook | Event | Purpose |
|------|-------|---------|
| `directory-guard.py` | PreToolUse (Write) | Enforce directory structure |
| `calendar-protection.py` | PreToolUse (Calendar) | Protect calendar events |

### Git Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `pre-commit-guard.sh` | Git pre-commit | Prevents staging personal data |

## Hook Structure

Hooks live in `.claude/hooks/`:

```
.claude/hooks/
├── session-context-loader.py
├── reminders-session-sync.py      # Not currently in settings.json
├── health-session-sync.py
├── prompt-timestamp.py
├── directory-guard.py
├── calendar-protection.py
├── frontmatter-validator.py
├── task-format-validator.py
├── table-format-validator.py
├── task-sync-detector.py
├── reminders-task-detector.py     # Not currently in settings.json
├── git-task-sync-detector.sh      # Manual installation (git hook)
├── pre-commit-guard.sh            # Git pre-commit hook
├── hook_logger.py                 # Utility module (not a hook)
└── README.md
```

## Hook Configuration

Hooks must be configured in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "command": "python3 /path/to/session-context-loader.py",
        "timeout": 5000
      }
    ],
    "PreToolUse": [
      {
        "command": "python3 /path/to/directory-guard.py",
        "tools": ["Write", "Edit"]
      }
    ]
  }
}
```

## Hook Behaviors

### Blocking (PreToolUse)

PreToolUse hooks can block operations:

```python
# directory-guard.py
if file_path.startswith("4-Daily/") and not is_daily_note(file_path):
    print(json.dumps({
        "decision": "block",
        "message": "Daily notes must be named YYYY-MM-DD.md"
    }))
```

### Warning (PostToolUse)

PostToolUse hooks can warn but not block:

```python
# frontmatter-validator.py
if not has_valid_frontmatter(content):
    print(json.dumps({
        "message": "Warning: Missing required frontmatter fields"
    }))
```

### Context Injection (SessionStart/UserPromptSubmit)

Context hooks inject information:

```python
# session-context-loader.py
context = gather_todays_context()
print(json.dumps({
    "additional_context": context
}))
```

## Creating a New Hook

1. **Choose event** — When should it run?
2. **Create script** in `.claude/hooks/`
3. **Handle input** — Parse JSON from stdin
4. **Produce output** — Return JSON to stdout
5. **Configure** in `~/.claude/settings.json`
6. **Document** in CLAUDE.md hooks table

### Template (Python)

```python
#!/usr/bin/env python3
"""
[Hook Name]

Event: [EventName]
Purpose: [What it does]
"""

import json
import sys

def main():
    # Read input from stdin
    input_data = json.loads(sys.stdin.read())

    # Process...

    # Output result
    result = {
        "decision": "allow",  # or "block" for PreToolUse
        "message": "Optional message",
        "additional_context": "Optional context to inject"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

## Dynamic Configuration

Several hooks read user configuration from `.user/` at runtime:

| Hook | Config Used |
|------|-------------|
| `frontmatter-validator.py` | `.user/companies.yaml` — Valid company names for `company:` field |
| `task-format-validator.py` | `.user/companies.yaml` — Valid company contexts for tasks |
| `reminders-task-detector.py` | `.user/companies.yaml` — Company-to-list mapping for Reminders |

This allows hooks to validate against your specific company names without hardcoding values.

## Best Practices

1. **Fast execution** — Hooks run synchronously
2. **Clear messages** — Explain blocks/warnings
3. **Fail gracefully** — Don't crash on edge cases
4. **Minimal scope** — Do one thing well
5. **Test thoroughly** — Hooks affect all operations
6. **Use dynamic config** — Read from `.user/` when company-specific validation is needed
