---
description: Check heartbeat status and show recent run history
argument-hint:
allowed-tools: Read, Bash
---

# Heartbeat Status Command

Shows the current status of the LifeOS heartbeat system including launchd status, recent runs, and any active alerts.

## Steps

### 1. Check launchd Agent Status

```bash
# Check if agent is registered and running
launchctl list | grep heartbeat || echo "Agent not running"

# Check plist symlink
ls -la ~/Library/LaunchAgents/com.lifeos.heartbeat.plist 2>/dev/null || echo "Plist not installed"
```

### 2. Read Current State

```bash
cat "{{vault_path}}/state/heartbeat/state.json" 2>/dev/null || echo "No state file yet"
```

### 3. Show Recent Runs

```bash
# Last 10 runs
tail -10 "{{vault_path}}/state/heartbeat/runs.jsonl" 2>/dev/null | while read line; do
  echo "$line" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{d[\"date\"]} {d[\"time\"]} - {d[\"status\"]}')"
done || echo "No run history yet"
```

### 4. Show Last Run Details

```bash
# Last 20 lines of log
tail -20 "{{vault_path}}/state/heartbeat/last-run.log" 2>/dev/null || echo "No logs yet"
```

### 5. Read Configuration

```bash
cat "{{vault_path}}/tasks/heartbeat/config.yaml"
```

## Output Format

```markdown
## Heartbeat Status

### Agent
| Status | Value |
|--------|-------|
| launchd | Running / Not Running |
| Enabled | true / false |
| Interval | X minutes |
| Active Hours | HH:MM - HH:MM |

### Last Run
- **Time**: YYYY-MM-DD HH:MM:SS
- **Status**: OK / ALERT / CHANGED
- **Duration**: Xs

### Recent History (last 10 runs)
| Time | Status |
|------|--------|
| ... | ... |

### Active Alerts
- [List any active alerts from state.json]

### Suppressed Alerts
- [List any suppressed alerts with expiry]

### Statistics (Today)
- Runs: X of Y max
- Alerts sent: N
- Last notification: HH:MM
```

## Quick Actions

Based on status, suggest relevant actions:

- If not installed: "Run `/heartbeat:install` to set up"
- If alerts active: "Run `/heartbeat:ack [type]` to suppress"
- If not running: "Check launchd logs in `state/heartbeat/launchd-stderr.log`"
