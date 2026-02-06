#!/bin/bash
# Uninstall LifeOS Heartbeat launchd agent
# Stops the agent and removes the symlink

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_NAME="com.lifeos.heartbeat.plist"
SYMLINK_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"
GENERATED_FILE="$SCRIPT_DIR/com.lifeos.heartbeat.generated.plist"

echo "=== LifeOS Heartbeat Uninstaller ==="

# Unload agent if running
if launchctl list | grep -q "com.lifeos.heartbeat"; then
    echo "Unloading agent..."
    launchctl unload "$SYMLINK_PATH" 2>/dev/null || true
    echo "Agent unloaded"
else
    echo "Agent not currently running"
fi

# Remove symlink
if [[ -L "$SYMLINK_PATH" ]] || [[ -f "$SYMLINK_PATH" ]]; then
    echo "Removing symlink..."
    rm -f "$SYMLINK_PATH"
    echo "Symlink removed"
else
    echo "No symlink found at $SYMLINK_PATH"
fi

# Optionally remove generated plist
if [[ -f "$GENERATED_FILE" ]]; then
    echo "Removing generated plist..."
    rm -f "$GENERATED_FILE"
fi

echo ""
echo "=== Uninstall Complete ==="
echo "Heartbeat agent has been removed."
echo ""
echo "Note: State files preserved in state/heartbeat/"
echo "To reinstall: ./tasks/heartbeat/plist/install.sh"
