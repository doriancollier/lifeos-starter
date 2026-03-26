#!/bin/bash
# Install LifeOS Heartbeat launchd agent
# Creates symlink in ~/Library/LaunchAgents and loads the agent

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CONFIG_FILE="$VAULT_ROOT/tasks/heartbeat/config.yaml"
TEMPLATE_FILE="$SCRIPT_DIR/com.lifeos.heartbeat.plist"
GENERATED_FILE="$SCRIPT_DIR/com.lifeos.heartbeat.generated.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_NAME="com.lifeos.heartbeat.plist"
SYMLINK_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

echo "=== LifeOS Heartbeat Installer ==="
echo "Vault root: $VAULT_ROOT"

# Ensure LaunchAgents directory exists
mkdir -p "$LAUNCH_AGENTS_DIR"

# Read interval from config (default 30 minutes)
INTERVAL_MINUTES=$(grep -E '^\s*interval_minutes:' "$CONFIG_FILE" 2>/dev/null | sed 's/.*:\s*//' || echo "30")
INTERVAL_SECONDS=$((INTERVAL_MINUTES * 60))
echo "Interval: ${INTERVAL_MINUTES} minutes (${INTERVAL_SECONDS} seconds)"

# Generate plist from template
echo "Generating plist from template..."
sed -e "s|__VAULT_ROOT__|$VAULT_ROOT|g" \
    -e "s|__INTERVAL_SECONDS__|$INTERVAL_SECONDS|g" \
    "$TEMPLATE_FILE" > "$GENERATED_FILE"

# Unload existing agent if present
if launchctl list | grep -q "com.lifeos.heartbeat"; then
    echo "Unloading existing agent..."
    launchctl unload "$SYMLINK_PATH" 2>/dev/null || true
fi

# Remove existing symlink if present
if [[ -L "$SYMLINK_PATH" ]] || [[ -f "$SYMLINK_PATH" ]]; then
    echo "Removing existing plist..."
    rm -f "$SYMLINK_PATH"
fi

# Create symlink
echo "Creating symlink..."
ln -s "$GENERATED_FILE" "$SYMLINK_PATH"

# Load the agent
echo "Loading agent..."
launchctl load "$SYMLINK_PATH"

# Verify
echo ""
echo "=== Verification ==="
if launchctl list | grep -q "com.lifeos.heartbeat"; then
    echo "SUCCESS: Heartbeat agent is running"
    launchctl list | grep "com.lifeos.heartbeat"
else
    echo "WARNING: Agent may not have started correctly"
    echo "Check: launchctl list | grep heartbeat"
fi

echo ""
echo "=== Next Steps ==="
echo "- View logs: tail -f $VAULT_ROOT/state/heartbeat/last-run.log"
echo "- Check status: /heartbeat:status"
echo "- Manual run: $VAULT_ROOT/tasks/heartbeat/runner.sh"
echo "- Uninstall: $SCRIPT_DIR/uninstall.sh"
