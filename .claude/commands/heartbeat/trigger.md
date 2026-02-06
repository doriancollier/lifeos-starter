---
description: Run heartbeat check manually
argument-hint:
allowed-tools: Read, Bash
---

# Heartbeat Trigger Command

Manually triggers a heartbeat check outside the normal schedule.

## When to Use

- Testing heartbeat configuration
- Checking vault health immediately
- After making changes you want to verify
- Debugging heartbeat issues

## Steps

### 1. Show Current State

```bash
cat "{{vault_path}}/state/heartbeat/state.json" 2>/dev/null || echo "No previous state"
```

### 2. Run Heartbeat

```bash
"{{vault_path}}/tasks/heartbeat/runner.sh"
```

### 3. Show Results

```bash
# Show the latest run result
tail -50 "{{vault_path}}/state/heartbeat/last-run.log"
```

### 4. Show Updated State

```bash
cat "{{vault_path}}/state/heartbeat/state.json"
```

## Output

Report what the heartbeat found:

```markdown
## Manual Heartbeat Complete

**Status**: OK / ALERT / CHANGED

### Checks Performed
- [ ] Daily note exists
- [ ] No overdue A-tasks
- [ ] Upcoming meetings have prep
- [ ] Inbox under threshold
- [ ] No stalled projects

### Alerts Found
- [List any issues detected]

### State Changes
- [List what changed since last run]

### Next Scheduled Run
- launchd will run again at approximately HH:MM
```

## Notes

- Manual runs count toward the daily limit
- Notifications respect the cooldown period
- This bypasses active hours check (intentional for manual runs)
