---
description: Install and start the heartbeat launchd agent
argument-hint:
allowed-tools: Read, Bash
---

# Heartbeat Install Command

Installs the LifeOS heartbeat background task as a macOS launchd agent.

## What This Does

1. Generates a launchd plist from template
2. Creates symlink in `~/Library/LaunchAgents/`
3. Loads the agent with `launchctl`
4. Verifies the agent is running

## Prerequisites

- Claude Code CLI installed and in PATH
- macOS with launchd
- Heartbeat enabled in config

## Steps

### 1. Check Current Status

```bash
launchctl list | grep -E "heartbeat|com.lifeos" || echo "No heartbeat agent currently running"
```

### 2. Verify Configuration

Read the heartbeat configuration:

```bash
cat "{{vault_path}}/tasks/heartbeat/config.yaml"
```

Confirm heartbeat is enabled.

### 3. Run Install Script

```bash
"{{vault_path}}/tasks/heartbeat/plist/install.sh"
```

### 4. Verify Installation

```bash
# Check launchd
launchctl list | grep heartbeat

# Check symlink exists
ls -la ~/Library/LaunchAgents/com.lifeos.heartbeat.plist
```

### 5. Test Run (Optional)

Offer to run a test heartbeat:

```bash
"{{vault_path}}/tasks/heartbeat/runner.sh"
```

## Output

Report installation status:

```markdown
## Heartbeat Installation Complete

**Status**: Running / Failed
**Interval**: X minutes
**Active Hours**: HH:MM - HH:MM
**Model**: claude-haiku-4-20250514

### Next Steps
- View logs: `tail -f state/heartbeat/last-run.log`
- Check status: `/heartbeat:status`
- Manual run: `/heartbeat:trigger`
- Uninstall: `./tasks/heartbeat/plist/uninstall.sh`
```

## Troubleshooting

If installation fails:

1. Check for existing conflicting agent
2. Verify PATH includes claude CLI
3. Check ~/Library/LaunchAgents permissions
4. Review launchd stderr log
