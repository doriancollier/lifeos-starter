#!/bin/bash
#
# Pre-Commit Guard - Prevent personal data from being committed
#
# This git pre-commit hook checks staged files against known personal
# data directories and blocks the commit if any are found. This protects
# against accidentally committing personal vault content to the public repo.
#
# Install: .claude/scripts/install-git-hooks.sh
# Or manually: ln -sf ../../.claude/hooks/pre-commit-guard.sh .git/hooks/pre-commit
#

# Personal data paths that should never be committed.
# These match paths relative to the repo root.
BLOCKED_PATTERNS=(
    "^workspace/1-Projects/"
    "^workspace/2-Areas/"
    "^workspace/3-Resources/"
    "^workspace/4-Daily/"
    "^workspace/5-Meetings/"
    "^workspace/6-People/"
    "^workspace/7-MOCs/"
    "^workspace/8-Scratch/"
    "^workspace/0-Inbox/"
    "^\.user/identity\.yaml$"
    "^\.user/health\.yaml$"
    "^data/"
    "^state/"
    "^\.claude/data/"
)

# Exceptions: these files ARE safe to commit even inside blocked dirs
ALLOWED_PATTERNS=(
    "\.gitkeep$"
)

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Get list of staged files
staged_files=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$staged_files" ]; then
    exit 0
fi

blocked_files=()

while IFS= read -r file; do
    # Check if file matches any blocked pattern
    for pattern in "${BLOCKED_PATTERNS[@]}"; do
        if echo "$file" | grep -qE "$pattern"; then
            # Check if it's in the allowed exceptions
            is_allowed=false
            for allow in "${ALLOWED_PATTERNS[@]}"; do
                if echo "$file" | grep -qE "$allow"; then
                    is_allowed=true
                    break
                fi
            done

            if [ "$is_allowed" = false ]; then
                blocked_files+=("$file")
            fi
            break
        fi
    done
done <<< "$staged_files"

if [ ${#blocked_files[@]} -gt 0 ]; then
    echo -e "${RED}BLOCKED: Personal data detected in staged files${NC}"
    echo ""
    echo "The following files contain personal data and should not be committed:"
    echo ""
    for f in "${blocked_files[@]}"; do
        echo -e "  ${YELLOW}$f${NC}"
    done
    echo ""
    echo "To unstage these files:"
    echo "  git reset HEAD <file>"
    echo ""
    echo "To bypass this check (use with caution):"
    echo "  git commit --no-verify"
    echo ""
    exit 1
fi

exit 0
