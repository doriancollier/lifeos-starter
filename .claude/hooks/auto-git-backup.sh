#!/bin/bash
#
# Auto Git Backup Hook (SessionEnd)
#
# Automatically commits vault changes when a Claude Code session ends.
# Includes a summary of what changed in the commit message.
#
# This hook:
# - Checks if there are uncommitted changes
# - Stages all changes
# - Generates a summary of changes
# - Creates a commit with timestamp and change summary
# - Does NOT push (manual push is safer)
#

# Consume stdin (hook receives JSON input that we don't need)
cat > /dev/null

# Configuration - auto-detect vault root from script location
# Script is in .claude/hooks/, so vault root is 2 directories up
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to vault directory
cd "$VAULT_ROOT" || exit 0

# Check if this is a git repository
if [ ! -d ".git" ]; then
    exit 0
fi

# Check if there are any changes
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    # No changes to commit
    exit 0
fi

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Stage all changes
git add -A

# Check again after staging
if git diff --cached --quiet; then
    # Nothing staged
    exit 0
fi

# Generate change summary
generate_summary() {
    local summary=""

    # Get file statistics
    local stats=$(git diff --cached --stat | tail -1)

    # Count files by type/directory
    local daily_notes=$(git diff --cached --name-only | grep -c "^4-Daily/" || echo "0")
    local meetings=$(git diff --cached --name-only | grep -c "^5-Meetings/" || echo "0")
    local projects=$(git diff --cached --name-only | grep -c "^1-Projects/" || echo "0")
    local people=$(git diff --cached --name-only | grep -c "^6-People/" || echo "0")
    local system=$(git diff --cached --name-only | grep -c "^0-System/\|^\.claude/" || echo "0")
    local areas=$(git diff --cached --name-only | grep -c "^2-Areas/" || echo "0")

    # Build summary line
    local parts=()
    [ "$daily_notes" -gt 0 ] && parts+=("${daily_notes} daily")
    [ "$meetings" -gt 0 ] && parts+=("${meetings} meetings")
    [ "$projects" -gt 0 ] && parts+=("${projects} projects")
    [ "$people" -gt 0 ] && parts+=("${people} people")
    [ "$areas" -gt 0 ] && parts+=("${areas} areas")
    [ "$system" -gt 0 ] && parts+=("${system} system")

    if [ ${#parts[@]} -gt 0 ]; then
        summary=$(IFS=', '; echo "${parts[*]}")
    else
        # Fallback to just file count
        local file_count=$(git diff --cached --name-only | wc -l | tr -d ' ')
        summary="${file_count} files"
    fi

    echo "$summary"
}

# Get list of changed files (abbreviated)
get_changed_files() {
    git diff --cached --name-only | head -10 | while read -r file; do
        # Shorten paths for readability
        echo "  - ${file}"
    done

    local total=$(git diff --cached --name-only | wc -l | tr -d ' ')
    if [ "$total" -gt 10 ]; then
        echo "  ... and $((total - 10)) more files"
    fi
}

# Generate the summary
SUMMARY=$(generate_summary)
CHANGED_FILES=$(get_changed_files)

# Create commit message with summary
COMMIT_MSG="vault backup: $TIMESTAMP ($SUMMARY)

Changed files:
$CHANGED_FILES

Auto-committed by Claude Code session hook"

# Commit changes
git commit -m "$COMMIT_MSG" --quiet

# Output confirmation (will appear in Claude Code output)
echo "Auto-backup committed: $TIMESTAMP ($SUMMARY)" >&2

exit 0
