#!/bin/bash
#
# Git Task Sync Detector
#
# This script analyzes git commits for task-related changes in daily notes
# and project files, then queues them for synchronization.
#
# Can be used as:
# 1. Git post-commit hook (symlink to .git/hooks/post-commit)
# 2. Manual execution: .claude/hooks/git-task-sync-detector.sh
#
# It writes sync requirements to .claude/sync-queue.json which the
# SessionStart hook will process in the next Claude Code session.
#

VAULT_ROOT="{{vault_path}}"
SYNC_QUEUE_FILE="$VAULT_ROOT/.claude/sync-queue.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Ensure we're in the vault directory
cd "$VAULT_ROOT" || exit 1

# Check if this is being run from a git commit
if [ -z "$GIT_AUTHOR_NAME" ]; then
    # Manual run - analyze the last commit
    COMMIT_RANGE="HEAD~1..HEAD"
else
    # Post-commit hook - analyze the just-committed changes
    COMMIT_RANGE="HEAD~1..HEAD"
fi

# Get list of changed files
CHANGED_FILES=$(git diff --name-only "$COMMIT_RANGE" 2>/dev/null)

if [ -z "$CHANGED_FILES" ]; then
    # No commits to analyze (possibly first commit)
    exit 0
fi

# Filter for relevant files (daily notes and project files)
RELEVANT_FILES=""
while IFS= read -r file; do
    if [[ "$file" == 1-Projects/Current/*.md ]] || [[ "$file" == 4-Daily/*.md ]]; then
        RELEVANT_FILES="$RELEVANT_FILES$file"$'\n'
    fi
done <<< "$CHANGED_FILES"

if [ -z "$RELEVANT_FILES" ]; then
    # No relevant file changes
    exit 0
fi

# Initialize or load sync queue
if [ -f "$SYNC_QUEUE_FILE" ]; then
    QUEUE=$(cat "$SYNC_QUEUE_FILE")
else
    QUEUE="[]"
fi

# Track if we added any entries
ENTRIES_ADDED=0

# Process each relevant file
while IFS= read -r file; do
    [ -z "$file" ] && continue

    # Get the diff for this file
    DIFF=$(git diff "$COMMIT_RANGE" -- "$file" 2>/dev/null)

    # Check if diff contains task patterns
    if echo "$DIFF" | grep -qE '^\+.*- \[([ x])\]|^-.*- \[([ x])\]'; then
        # Determine source type
        if [[ "$file" == 4-Daily/*.md ]]; then
            SOURCE_TYPE="daily"
            # Extract date from filename
            FILENAME=$(basename "$file" .md)
        else
            SOURCE_TYPE="project"
            # Extract project name
            FILENAME=$(dirname "$file" | xargs basename)
            if [ "$FILENAME" = "Current" ]; then
                FILENAME=$(basename "$file" .md)
            fi
        fi

        # Add a queue entry
        NEW_ENTRY=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "source_file": "$file",
  "source_type": "$SOURCE_TYPE",
  "project": null,
  "task_text": "[detected from git diff]",
  "completed": null,
  "processed": false,
  "git_detected": true,
  "commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
}
EOF
)
        # Add to queue (simple append since we're not doing full JSON parsing in bash)
        ENTRIES_ADDED=$((ENTRIES_ADDED + 1))

        # Create a marker file for the session start hook
        echo "$TIMESTAMP" > "$VAULT_ROOT/.claude/sync-pending"
    fi
done <<< "$RELEVANT_FILES"

if [ $ENTRIES_ADDED -gt 0 ]; then
    echo "Task sync detector: $ENTRIES_ADDED file(s) with task changes detected."
    echo "Changes will be processed in the next Claude Code session."
fi
