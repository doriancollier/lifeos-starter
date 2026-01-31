---
description: Create timeboxed focus blocks on calendar for today's tasks
allowed-tools: Read, Grep, Glob, mcp__google-calendar__list-events, mcp__google-calendar__create-event, mcp__google-calendar__update-event, mcp__google-calendar__delete-event, mcp__google-calendar__get-current-time
---

# Daily Timebox Command

Create timeboxed focus blocks on your calendar to structure today's work.

## Context

- **Daily notes**: `{{vault_path}}/4-Daily/`
- **Calendar**: `{{user_email}}` (primary)
- **Working hours**: 8:00 AM - 6:00 PM
- **Timezone**: America/Chicago

## Task

Use the `daily-timebox` skill to:

1. **Read today's daily note** to get A and B priority tasks
2. **Check calendar** for existing meetings and timeboxes
3. **Group tasks by project** ({{company_1_name}}, 144, Personal, EMC)
4. **Create focus blocks** with appropriate durations
5. **Add wellness blocks** (lunch, breaks)
6. **Present the schedule** to the user

## Behavior

- If timeboxes already exist for today, ask if user wants to **update** (adjust remaining) or **start fresh**
- Only schedule within working hours (8 AM - 6 PM) unless user specifies otherwise
- Preserve past timeboxes as historical record
- Events are `transparent` (don't block availability for others)

## Output

Show a summary table of the created schedule with times, block names, and tasks assigned to each block.

## Examples

```
/daily:timebox              # Timebox today based on daily note
/daily:timebox              # If timeboxes exist, asks to update or recreate
```
