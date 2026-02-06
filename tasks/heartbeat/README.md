# LifeOS Heartbeat

Periodic background checks of vault health, running via macOS launchd.

## Overview

The heartbeat system performs automated health checks of your LifeOS vault:
- Detects overdue tasks and missed deadlines
- Alerts for upcoming meetings without prep notes
- Monitors inbox overflow
- Tracks project health

## Architecture

```
launchd (every 30 min) → runner.sh → claude --print → ALERT or OK
         ↓                    ↓              ↓
~/Library/LaunchAgents/    config.yaml    state.json
```

## Files

| File | Purpose |
|------|---------|
| `config.yaml` | All settings (interval, model, limits, checks) |
| `HEARTBEAT.md` | Checklist Claude evaluates each run |
| `runner.sh` | Main shell script invoked by launchd |
| `plist/` | launchd plist and install/uninstall scripts |

## State Files

Located in `state/heartbeat/`:

| File | Purpose |
|------|---------|
| `state.json` | Structured state (alerts, suppressed, last check values) |
| `runs.jsonl` | Run history (append-only, one JSON per run) |
| `last-run.log` | Raw Claude output (debugging) |

## Installation

```bash
# Install launchd agent
./plist/install.sh

# Verify installation
launchctl list | grep heartbeat

# Or use the command
/heartbeat:install
```

## Commands

| Command | Purpose |
|---------|---------|
| `/heartbeat:install` | Install and start the launchd agent |
| `/heartbeat:status` | Check status, show recent runs |
| `/heartbeat:trigger` | Run heartbeat manually |
| `/heartbeat:ack [type] [until]` | Suppress an alert temporarily |

## Configuration

Edit `config.yaml` to customize:

```yaml
heartbeat:
  interval_minutes: 30      # Check frequency
  model: "claude-haiku-4-20250514"  # Cheaper for routine checks
  max_daily_runs: 24        # Cost control
  active_hours:
    start: "07:00"
    end: "22:00"
  skip_weekends: false

alerts:
  macos_notification: true
  cooldown_minutes: 120     # Don't repeat same alert within 2 hours
```

## Cost Considerations

- Haiku model: ~$0.25-0.50 per run
- 24 runs/day = ~$6-12/day at maximum
- `max_daily_runs` provides hard limit
- Active hours reduce unnecessary runs
- Consider longer intervals (60 min) for cost reduction

## Troubleshooting

### Check if running
```bash
launchctl list | grep heartbeat
```

### View recent output
```bash
tail -50 state/heartbeat/last-run.log
```

### View run history
```bash
tail -20 state/heartbeat/runs.jsonl | jq .
```

### Manual test run
```bash
./tasks/heartbeat/runner.sh
```

### Stop temporarily
```bash
launchctl unload ~/Library/LaunchAgents/com.lifeos.heartbeat.plist
```

### Reinstall
```bash
./tasks/heartbeat/plist/uninstall.sh
./tasks/heartbeat/plist/install.sh
```

## How It Works

1. **launchd** triggers `runner.sh` at configured interval
2. **runner.sh** checks:
   - Is heartbeat enabled?
   - Is it within active hours?
   - Have we exceeded daily run limit?
   - Is it a weekend (if skip_weekends enabled)?
3. **runner.sh** reads previous state from `state.json`
4. **runner.sh** invokes Claude with:
   - The HEARTBEAT.md checklist
   - Previous state for comparison
   - Current timestamp
5. **Claude** checks the vault and outputs:
   - STATUS: OK, ALERT, or CHANGED
   - ALERTS: List of issues found
   - STATE_CHANGES: What changed since last check
6. **runner.sh** parses the response:
   - Updates `state.json` with new values
   - Appends to `runs.jsonl` for history
   - Sends macOS notification if ALERT (respecting cooldown)

## State Schema

```json
{
  "last_updated": "2026-02-06T14:00:00Z",
  "last_status": "OK",
  "last_notification": "2026-02-06T10:00:00Z",
  "alerts": [
    {
      "type": "overdue_tasks",
      "message": "2 overdue A-tasks",
      "first_sent": "2026-02-06T10:00:00Z",
      "last_sent": "2026-02-06T12:00:00Z",
      "count": 3
    }
  ],
  "suppressed": [
    {"type": "inbox_overflow", "until": "2026-02-07"}
  ],
  "last_check": {
    "daily_note_exists": true,
    "a_tasks": 3,
    "inbox_count": 12,
    "overdue_projects": 1
  }
}
```

## Acknowledging Alerts

To temporarily suppress a recurring alert:

```
/heartbeat:ack inbox_overflow until tomorrow
/heartbeat:ack overdue_tasks for 4 hours
```

This updates the `suppressed` array in `state.json`. The heartbeat will skip these alerts until the specified time.
