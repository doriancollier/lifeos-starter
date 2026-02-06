#!/usr/bin/env python3
"""
Directory Placement Guard Hook (PreToolUse)

Validates that new files are being created in the correct directory based on:
- File naming patterns (YYYY-MM-DD.md → 4-Daily/)
- Content type indicators
- Template patterns

BLOCKS creation of files in wrong directories with guidance on correct location.
"""

import json
import sys
import os
import re
import time
from datetime import datetime
from pathlib import Path

# Add hooks directory to path for hook_logger import
sys.path.insert(0, os.path.dirname(__file__))
from hook_logger import setup_logger, log_hook_execution

# Initialize logger
logger = setup_logger("directory-guard")

# Vault configuration - uses environment variable or auto-detects from script location
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or os.path.join(PROJECT_ROOT, "workspace")

# Directory rules
DIRECTORY_RULES = {
    "4-Daily": {
        "pattern": r"^\d{4}-\d{2}-\d{2}\.md$",
        "description": "Daily notes (YYYY-MM-DD.md format)",
        "examples": ["2025-11-24.md", "2025-12-01.md"]
    },
    "5-Meetings": {
        "pattern": r".*meeting.*\.md$|.*sync.*\.md$|.*standup.*\.md$|.*review.*\.md$",
        "description": "Meeting notes",
        "examples": ["2025-11-24-Product-Sync.md", "Weekly-Sync.md"],
        "subdirs": True  # Allow subdirectories like 5-Meetings/2025/11-November/
    },
    "6-People": {
        "keywords": ["person", "contact", "relationship"],
        "description": "Person/relationship notes",
        "examples": ["alex-smith.md", "sam-taylor.md"],
        "subdirs": True  # Professional/ and Personal/
    },
    "1-Projects": {
        "keywords": ["project", "initiative"],
        "description": "Project documentation",
        "subdirs": True  # Current/, Backlog/, Completed/, Cancelled/
    },
    "2-Areas": {
        "keywords": ["area", "context", "ongoing"],
        "description": "Ongoing area documentation",
        "subdirs": True
    },
    "3-Resources": {
        "keywords": ["template", "guide", "documentation", "reference"],
        "description": "Templates and reference materials",
        "subdirs": True
    },
    "7-MOCs": {
        "keywords": ["moc", "map of content", "index"],
        "description": "Maps of Content for navigation"
    }
}

# Date pattern for daily notes
DATE_FILENAME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}\.md$')

def get_expected_directory(file_path, content=None):
    """Determine the expected directory for a file based on its name and content."""
    filename = os.path.basename(file_path)
    relative_path = file_path.replace(VAULT_ROOT, '').lstrip('/')

    # Allow templates to be created in 3-Resources/Templates/ regardless of naming patterns
    # This exception must come BEFORE pattern checks to allow meeting-related templates
    if relative_path.startswith('3-Resources/Templates/'):
        return None, None

    # Allow 0-System/ documentation files regardless of naming patterns
    # This is the LifeOS product documentation layer
    if relative_path.startswith('0-System/'):
        return None, None

    # Allow 0-Inbox/ as a staging area for files that need processing
    # Files here are triaged and moved to correct locations via /inbox:process
    if relative_path.startswith('0-Inbox/'):
        return None, None

    # Allow 8-Scratch/ as a temporary workspace for any file type
    # This is explicitly designed as a flexible scratch space
    if relative_path.startswith('8-Scratch/'):
        return None, None

    # Check for date-formatted filenames (daily notes)
    if DATE_FILENAME_PATTERN.match(filename):
        return "4-Daily", "Daily notes should use format YYYY-MM-DD.md in 4-Daily/"

    # Check for meeting patterns in filename
    meeting_patterns = ['meeting', 'sync', 'standup', 'review', '1on1', '1-on-1']
    if any(pattern in filename.lower() for pattern in meeting_patterns):
        return "5-Meetings", "Meeting notes should go in 5-Meetings/YYYY/MM-Month/"

    # If we have content, check frontmatter type
    if content:
        type_match = re.search(r'type:\s*["\']?([^"\'\n]+)["\']?', content)
        if type_match:
            note_type = type_match.group(1).strip().lower()

            if note_type == 'daily-note':
                return "4-Daily", "Notes with type: daily-note should go in 4-Daily/"
            elif note_type == 'meeting':
                return "5-Meetings", "Notes with type: meeting should go in 5-Meetings/"
            elif note_type == 'person':
                return "6-People", "Notes with type: person should go in 6-People/Professional/ or 6-People/Personal/"
            elif note_type == 'project':
                return "1-Projects", "Notes with type: project should go in 1-Projects/Current/ or 1-Projects/Backlog/"
            elif note_type == 'moc':
                return "7-MOCs", "Maps of Content should go in 7-MOCs/"

    return None, None

def is_valid_location(file_path, expected_dir):
    """Check if the file is being created in a valid location."""
    relative_path = file_path.replace(VAULT_ROOT, '').lstrip('/')

    # Get the top-level directory
    parts = relative_path.split('/')
    if not parts:
        return False

    top_dir = parts[0]

    # Check if it matches expected directory
    if expected_dir and not relative_path.startswith(expected_dir):
        return False

    return True

def validate_directory_placement(file_path, content=None):
    """Validate that a file is being created in the correct directory."""
    # Skip if outside vault
    if not file_path.startswith(VAULT_ROOT):
        return None, None

    # Skip .claude directory
    if '/.claude/' in file_path:
        return None, None

    # Skip .obsidian directory
    if '/.obsidian/' in file_path:
        return None, None

    # Skip hidden files
    filename = os.path.basename(file_path)
    if filename.startswith('.'):
        return None, None

    # Get expected directory
    expected_dir, reason = get_expected_directory(file_path, content)

    if expected_dir:
        relative_path = file_path.replace(VAULT_ROOT, '').lstrip('/')

        if not relative_path.startswith(expected_dir):
            return expected_dir, reason

    return None, None

def main():
    """Main hook execution."""
    start = time.time()

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        log_hook_execution(logger, "PreToolUse", tool="Write",
                          duration=time.time()-start, status="error",
                          details={"error": "Invalid JSON input"})
        sys.exit(0)

    # Get tool info
    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    # Only process Write operations (new file creation)
    if tool_name != 'Write':
        sys.exit(0)

    file_path = tool_input.get('file_path', '')
    content = tool_input.get('content', '')

    # Skip non-markdown files
    if not file_path.endswith('.md'):
        log_hook_execution(logger, "PreToolUse", tool="Write",
                          duration=time.time()-start, status="success",
                          details={"skipped": "non-markdown"})
        sys.exit(0)

    # Check if file already exists (edit vs create)
    if os.path.exists(file_path):
        # File exists, this is an overwrite, not a new creation
        # Be more lenient with existing files
        log_hook_execution(logger, "PreToolUse", tool="Write",
                          duration=time.time()-start, status="success",
                          details={"skipped": "existing file"})
        sys.exit(0)

    # Validate directory placement
    expected_dir, reason = validate_directory_placement(file_path, content)

    if expected_dir:
        # Wrong directory - BLOCK the operation
        current_dir = os.path.dirname(file_path.replace(VAULT_ROOT, '').lstrip('/'))
        filename = os.path.basename(file_path)

        error_message = f"""
Directory Placement Error:
  File: {filename}
  Current location: {current_dir}/
  Expected location: {expected_dir}/

  Reason: {reason}

  Correct path would be: {VAULT_ROOT}/{expected_dir}/{filename}

To proceed, please use the correct directory path.
"""
        # Output blocking response
        output = {
            "decision": "block",
            "reason": error_message.strip()
        }
        print(json.dumps(output))

        log_hook_execution(logger, "PreToolUse", tool="Write",
                          duration=time.time()-start, status="warning",
                          details={"blocked": True, "file": filename,
                                   "current_dir": current_dir, "expected_dir": expected_dir})
        sys.exit(2)  # Exit code 2 blocks the operation

    # All good - allow the operation
    log_hook_execution(logger, "PreToolUse", tool="Write",
                      duration=time.time()-start, status="success",
                      details={"file": os.path.basename(file_path)})
    sys.exit(0)

if __name__ == "__main__":
    main()
