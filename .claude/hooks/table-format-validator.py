#!/usr/bin/env python3
"""
Table Format Validator Hook (PostToolUse)

Validates markdown table formatting after Write/Edit operations:
- Tables must have a blank line before them (required for Obsidian rendering)

Returns warnings for issues found (does not block).
"""

import json
import sys
import os
import time
from pathlib import Path

# Add hooks directory to path for hook_logger import
sys.path.insert(0, os.path.dirname(__file__))
from hook_logger import setup_logger, log_hook_execution

# Initialize logger
logger = setup_logger("table-format-validator")

# Vault configuration - uses environment variable or auto-detects from script location
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or os.path.join(PROJECT_ROOT, "workspace")


def find_tables_missing_blank_lines(content):
    """Find tables that are missing a blank line before them."""
    lines = content.split('\n')
    issues = []

    for i, line in enumerate(lines):
        # Check if this line starts with a pipe (potential table row)
        stripped = line.strip()
        if not stripped.startswith('|'):
            continue

        # Check if next line exists and is a separator row (|---|)
        if i + 1 >= len(lines):
            continue

        next_line = lines[i + 1].strip()
        # Separator row patterns: |---| or |:--| or |--:| or |:--:|
        if not ('|---' in next_line or '|:--' in next_line or '|--:' in next_line):
            continue

        # This is a table header row - check the previous line
        if i == 0:
            # First line of file is a table - that's fine
            continue

        prev_line = lines[i - 1]

        # Previous line should be blank or another table row
        if prev_line.strip() == '':
            # Good - there's a blank line
            continue

        if prev_line.strip().startswith('|'):
            # Previous line is also a table row - that's fine (continuation)
            continue

        # Found an issue - table without blank line before it
        context = prev_line.strip()[:50]
        if len(prev_line.strip()) > 50:
            context += "..."
        issues.append((i + 1, context))

    return issues


def validate_tables(file_path, content):
    """Validate table formatting and return issues."""
    warnings = []

    # Skip non-markdown files
    if not file_path.endswith('.md'):
        return warnings

    # Skip template files
    if '/Templates/' in file_path:
        return warnings

    # Find tables missing blank lines
    issues = find_tables_missing_blank_lines(content)

    for line_num, context in issues:
        warnings.append(
            f"Line {line_num}: Table missing blank line before it. "
            f"Preceded by: \"{context}\""
        )

    return warnings


def main():
    """Main hook execution."""
    start = time.time()

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        log_hook_execution(logger, "PostToolUse", status="error",
                          details={"error": "Invalid JSON input"})
        sys.exit(0)

    # Get tool info
    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    # Only process Write/Edit on .md files
    if tool_name not in ['Write', 'Edit']:
        sys.exit(0)

    file_path = tool_input.get('file_path', '')
    if not file_path.endswith('.md'):
        sys.exit(0)

    # Skip if file is outside the vault
    if not file_path.startswith(VAULT_ROOT):
        sys.exit(0)

    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="error",
                          details={"error": "File not found", "file": file_path})
        sys.exit(0)
    except Exception as e:
        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="error",
                          details={"error": str(e), "file": file_path})
        print(json.dumps({"error": f"Could not read file: {e}"}), file=sys.stderr)
        sys.exit(0)

    # Validate tables
    warnings = validate_tables(file_path, content)

    # Output results
    if warnings:
        output_parts = ["Table Format Warnings:"]
        for warning in warnings:
            output_parts.append(f"  - {warning}")

        # Print to stderr for visibility
        print("\n".join(output_parts), file=sys.stderr)

        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="warning",
                          details={"file": os.path.basename(file_path),
                                   "warnings": len(warnings)})
    else:
        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="success",
                          details={"file": os.path.basename(file_path)})

    # Always exit 0 (don't block) - just provide feedback
    sys.exit(0)


if __name__ == "__main__":
    main()
