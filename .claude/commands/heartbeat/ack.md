---
description: Acknowledge and suppress a heartbeat alert temporarily
argument-hint: <alert_type> <duration>
allowed-tools: Read, Write, Edit, Bash
---

# Heartbeat Acknowledge Command

Suppresses a specific alert type until the specified time, preventing repeated notifications.

## Usage

```
/heartbeat:ack <alert_type> <duration>
```

### Duration Formats

- `until tomorrow` - Until midnight tonight
- `for 4 hours` - For the next 4 hours
- `until 2026-02-07` - Until specific date
- `for 30 minutes` - Short suppression

### Alert Types

Common alert types (from heartbeat checks):

| Type | Description |
|------|-------------|
| `overdue_tasks` | Overdue A-priority tasks |
| `inbox_overflow` | Inbox has too many items |
| `no_daily_note` | Missing today's daily note |
| `meeting_no_prep` | Upcoming meeting without prep |
| `stalled_projects` | Projects with no recent activity |
| `project_deadline` | Project past its deadline |

## Steps

### 1. Parse Arguments

Extract from `$ARGUMENTS`:
- `alert_type`: The type of alert to suppress
- `duration`: How long to suppress

### 2. Read Current State

```bash
cat "{{vault_path}}/state/heartbeat/state.json"
```

### 3. Calculate Expiry Time

Based on the duration format:
- "until tomorrow" → midnight tonight
- "for N hours" → now + N hours
- "until YYYY-MM-DD" → that date at midnight
- "for N minutes" → now + N minutes

### 4. Update Suppressed Array

Add or update the suppression entry:

```python
# Example state.json update
{
  "suppressed": [
    {
      "type": "inbox_overflow",
      "until": "2026-02-07T00:00:00Z",
      "reason": "Acknowledged via /heartbeat:ack"
    }
  ]
}
```

### 5. Confirm

```markdown
## Alert Suppressed

**Type**: {alert_type}
**Until**: {formatted_expiry}

The heartbeat will not alert for `{alert_type}` until {formatted_expiry}.

To remove suppression early, edit `state/heartbeat/state.json` and remove the entry from the `suppressed` array.
```

## Examples

```
/heartbeat:ack inbox_overflow until tomorrow
→ Suppresses inbox overflow alerts until midnight

/heartbeat:ack overdue_tasks for 4 hours
→ Suppresses overdue task alerts for 4 hours

/heartbeat:ack meeting_no_prep until 2026-02-10
→ Suppresses meeting prep alerts until Feb 10
```

## Notes

- Suppressed alerts are still logged, just not notified
- Expired suppressions are automatically cleaned up
- Multiple suppressions can be active simultaneously
- Use `/heartbeat:status` to see active suppressions
