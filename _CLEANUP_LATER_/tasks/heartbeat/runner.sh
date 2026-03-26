#!/bin/bash
# LifeOS Heartbeat Runner
# Invoked by launchd to perform periodic vault health checks

set -euo pipefail

# Resolve script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STATE_DIR="$VAULT_ROOT/state/heartbeat"
CONFIG_FILE="$SCRIPT_DIR/config.yaml"
CHECKLIST_FILE="$SCRIPT_DIR/HEARTBEAT.md"
STATE_FILE="$STATE_DIR/state.json"
RUNS_FILE="$STATE_DIR/runs.jsonl"
LOG_FILE="$STATE_DIR/last-run.log"

# Ensure state directory exists
mkdir -p "$STATE_DIR"

# Logging
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Heartbeat starting ==="

# --- Config parsing (simple grep/sed, no external deps) ---

get_config() {
  local key="$1"
  local default="${2:-}"
  local value
  value=$(grep -E "^\s*${key}:" "$CONFIG_FILE" 2>/dev/null | head -1 | sed 's/.*:\s*//' | tr -d '"' || echo "")
  echo "${value:-$default}"
}

get_config_bool() {
  local value
  value=$(get_config "$1" "$2")
  [[ "$value" == "true" ]] && echo "true" || echo "false"
}

# Read configuration
ENABLED=$(get_config_bool "enabled" "true")
MODEL=$(get_config "model" "claude-haiku-4-20250514")
MAX_DAILY_RUNS=$(get_config "max_daily_runs" "24")
ACTIVE_START=$(get_config "start" "07:00")
ACTIVE_END=$(get_config "end" "22:00")
SKIP_WEEKENDS=$(get_config_bool "skip_weekends" "false")
MACOS_NOTIFY=$(get_config_bool "macos_notification" "true")
COOLDOWN_MINUTES=$(get_config "cooldown_minutes" "120")

# --- Pre-flight checks ---

if [[ "$ENABLED" != "true" ]]; then
  log "Heartbeat disabled in config, exiting"
  exit 0
fi

# Check if weekend
DAY_OF_WEEK=$(date +%u)  # 1=Mon, 7=Sun
if [[ "$SKIP_WEEKENDS" == "true" && "$DAY_OF_WEEK" -ge 6 ]]; then
  log "Skipping weekend"
  exit 0
fi

# Check active hours
CURRENT_HOUR_MIN=$(date +%H:%M)
if [[ "$CURRENT_HOUR_MIN" < "$ACTIVE_START" || "$CURRENT_HOUR_MIN" > "$ACTIVE_END" ]]; then
  log "Outside active hours ($ACTIVE_START - $ACTIVE_END), current: $CURRENT_HOUR_MIN"
  exit 0
fi

# Check daily run limit
TODAY=$(date +%Y-%m-%d)
TODAY_RUNS=0
if [[ -f "$RUNS_FILE" ]]; then
  TODAY_RUNS=$(grep -c "\"date\":\"$TODAY\"" "$RUNS_FILE" 2>/dev/null || echo "0")
fi
if [[ "$TODAY_RUNS" -ge "$MAX_DAILY_RUNS" ]]; then
  log "Daily run limit reached ($TODAY_RUNS >= $MAX_DAILY_RUNS)"
  exit 0
fi

# --- Read previous state ---

PREVIOUS_STATE=""
if [[ -f "$STATE_FILE" ]]; then
  # Format state.json as readable text for Claude
  PREVIOUS_STATE=$(cat <<EOF
PREVIOUS STATE (from last heartbeat):
$(cat "$STATE_FILE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"- Last check: {data.get('last_updated', 'unknown')}\")
if 'last_check' in data:
  lc = data['last_check']
  print(f\"- Daily note exists: {lc.get('daily_note_exists', 'unknown')}\")
  print(f\"- A-tasks: {lc.get('a_tasks', 'unknown')}\")
  print(f\"- Inbox count: {lc.get('inbox_count', 'unknown')}\")
  print(f\"- Overdue projects: {lc.get('overdue_projects', 'unknown')}\")
  if lc.get('next_meeting'):
    print(f\"- Next meeting: {lc.get('next_meeting')} (has prep: {lc.get('next_meeting_has_prep', 'unknown')})\")
if data.get('alerts'):
  print('- Recent alerts:')
  for a in data['alerts'][:3]:
    print(f\"  - {a.get('type')}: sent {a.get('count', 1)}x, last at {a.get('last_sent', 'unknown')}\")
if data.get('suppressed'):
  print('- Suppressed:')
  for s in data['suppressed']:
    print(f\"  - {s.get('type')} until {s.get('until')}\")
" 2>/dev/null || echo "- (Could not parse previous state)")
EOF
)
else
  PREVIOUS_STATE="PREVIOUS STATE: First run - no previous state available."
fi

# --- Build prompt ---

CHECKLIST=$(cat "$CHECKLIST_FILE")
PROMPT=$(cat <<EOF
$CHECKLIST

---
$PREVIOUS_STATE
---

Current date/time: $(date '+%Y-%m-%d %H:%M:%S')
Vault root: $VAULT_ROOT

Perform the heartbeat check now. Be concise.
EOF
)

log "Invoking Claude with model: $MODEL"

# --- Invoke Claude ---

cd "$VAULT_ROOT"

# Run Claude and capture output
CLAUDE_OUTPUT=$(claude --print \
  --model "$MODEL" \
  --no-session-persistence \
  --dangerously-skip-permissions \
  "$PROMPT" 2>&1) || {
  log "ERROR: Claude invocation failed"
  echo "$CLAUDE_OUTPUT" >> "$LOG_FILE"
  exit 1
}

echo "$CLAUDE_OUTPUT" >> "$LOG_FILE"
log "Claude response received"

# --- Parse response ---

# Extract STATUS line
STATUS=$(echo "$CLAUDE_OUTPUT" | grep -E "^STATUS:" | head -1 | sed 's/STATUS:\s*//' | tr -d ' ')
log "Status: $STATUS"

# Extract ALERTS section
ALERTS=""
IN_ALERTS=false
while IFS= read -r line; do
  if [[ "$line" =~ ^ALERTS: ]]; then
    IN_ALERTS=true
    continue
  fi
  if [[ "$line" =~ ^STATE_CHANGES: ]] || [[ "$line" =~ ^\`\`\` ]]; then
    IN_ALERTS=false
  fi
  if [[ "$IN_ALERTS" == "true" && -n "$line" ]]; then
    ALERTS+="$line"$'\n'
  fi
done <<< "$CLAUDE_OUTPUT"

# --- Update state.json ---

# This is a simplified update - a more robust version would parse all fields
NOW=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
if [[ ! -f "$STATE_FILE" ]]; then
  echo '{"last_updated":"'"$NOW"'","alerts":[],"suppressed":[],"last_check":{}}' > "$STATE_FILE"
fi

# Update last_updated timestamp using Python for safe JSON manipulation
python3 -c "
import json
from datetime import datetime

with open('$STATE_FILE', 'r') as f:
    data = json.load(f)

data['last_updated'] = '$NOW'
data['last_status'] = '$STATUS'

with open('$STATE_FILE', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null || log "WARNING: Could not update state.json"

# --- Append to runs.jsonl ---

echo "{\"date\":\"$TODAY\",\"time\":\"$(date '+%H:%M:%S')\",\"status\":\"$STATUS\"}" >> "$RUNS_FILE"

# --- Send notification if ALERT ---

if [[ "$STATUS" == "ALERT" && "$MACOS_NOTIFY" == "true" ]]; then
  # Check cooldown - don't spam notifications
  LAST_NOTIFIED=""
  if [[ -f "$STATE_FILE" ]]; then
    LAST_NOTIFIED=$(python3 -c "
import json
from datetime import datetime, timedelta

with open('$STATE_FILE', 'r') as f:
    data = json.load(f)

last = data.get('last_notification')
if last:
    last_dt = datetime.fromisoformat(last.replace('Z', '+00:00'))
    cooldown = timedelta(minutes=$COOLDOWN_MINUTES)
    if datetime.now(last_dt.tzinfo) - last_dt < cooldown:
        print('cooldown')
" 2>/dev/null || echo "")
  fi

  if [[ "$LAST_NOTIFIED" != "cooldown" ]]; then
    # Format first alert for notification
    FIRST_ALERT=$(echo "$ALERTS" | head -1 | sed 's/^- //')
    if [[ -n "$FIRST_ALERT" ]]; then
      osascript -e "display notification \"$FIRST_ALERT\" with title \"LifeOS Heartbeat\" sound name \"Ping\""
      log "Sent macOS notification"

      # Update last_notification timestamp
      python3 -c "
import json
from datetime import datetime

with open('$STATE_FILE', 'r') as f:
    data = json.load(f)

data['last_notification'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open('$STATE_FILE', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null
    fi
  else
    log "Notification suppressed (cooldown active)"
  fi
fi

log "=== Heartbeat complete: $STATUS ==="
exit 0
