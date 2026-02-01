---
description: Create or open today's daily note
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Daily Note Command

Create or open today's daily note.

## Context

- **Today's date**: !`date +%Y-%m-%d`
- **Daily notes directory**: `{{vault_path}}/4-Daily/`
- **Template**: `{{vault_path}}/3-Resources/Templates/daily-enhanced.md`

## Task

1. Check if today's daily note exists at `4-Daily/YYYY-MM-DD.md`
2. If it exists:
   - Read and summarize the current state (tasks, meetings, energy level)
   - Open it in Obsidian using: `python3 {{vault_path}}/.claude/scripts/obsidian_manager.py open "{{vault_path}}/4-Daily/YYYY-MM-DD.md"`
3. If it doesn't exist:
   - Read the template from `3-Resources/Templates/daily-enhanced.md`
   - Create the new daily note with today's date
   - Replace template variables: `{{date:YYYY-MM-DD}}` with actual date, `{{date:dddd}}` with day of week
   - Open it in Obsidian

## Output

Provide a brief summary:
- Whether the note was created or already existed
- Current A-priority tasks (if any)
- Scheduled meetings (if any)
- Energy level setting
