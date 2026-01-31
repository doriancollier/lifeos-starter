#!/usr/bin/env python3
"""
Task Format Validator Hook (PostToolUse)

Validates task formatting in markdown files after Write/Edit operations:
- A priorities (🔴) should have numbers 1-5
- Maximum 5 A-priority tasks per daily note
- Blocked tasks (🔵) should include "Waiting for:" text
- Due dates (📅) should use ISO format YYYY-MM-DD
- Tasks should have company context

Returns warnings for issues found (does not block).
"""

import json
import sys
import os
import re
import time
from pathlib import Path

# Add hooks directory to path for hook_logger import
sys.path.insert(0, os.path.dirname(__file__))
from hook_logger import setup_logger, log_hook_execution

# Initialize logger
logger = setup_logger("task-format-validator")

# Vault configuration - uses environment variable or auto-detects from script location
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or str(Path(__file__).resolve().parent.parent.parent)

# Task patterns
A_PRIORITY_PATTERN = re.compile(r'- \[[ x]\] 🔴(\d)?\.?\s*(.*)')
B_PRIORITY_PATTERN = re.compile(r'- \[[ x]\] 🟡\s*(.*)')
C_PRIORITY_PATTERN = re.compile(r'- \[[ x]\] 🟢\s*(.*)')
BLOCKED_PATTERN = re.compile(r'- \[[ x]\] 🔵\s*(.*)')
# Due date pattern - matches 📅 YYYY-MM-DD anywhere in the line
DUE_DATE_PATTERN = re.compile(r'📅\s*(\d{4}-\d{2}-\d{2})')
# Old prose format to warn about
OLD_SCHEDULED_PATTERN = re.compile(r'Scheduled:\s*[A-Za-z]+')

# Valid companies for context - configure per vault
VALID_COMPANIES = ["Company 1", "Company 2", "Company 3", "Personal"]

def validate_tasks(file_path, content):
    """Validate task formatting and return issues and warnings."""
    issues = []
    warnings = []

    # Skip non-markdown files
    if not file_path.endswith('.md'):
        return issues, warnings

    # Skip template files
    if '/Templates/' in file_path:
        return issues, warnings

    lines = content.split('\n')

    # Track A-priority tasks
    a_tasks = []
    a_task_numbers = []

    for i, line in enumerate(lines, 1):
        # Check A-priority tasks
        a_match = A_PRIORITY_PATTERN.match(line.strip())
        if a_match:
            number = a_match.group(1)
            task_text = a_match.group(2)
            a_tasks.append((i, number, task_text))

            if number:
                try:
                    num = int(number)
                    if num < 1 or num > 5:
                        warnings.append(f"Line {i}: A-priority number {num} outside range 1-5")
                    a_task_numbers.append(num)
                except ValueError:
                    pass
            else:
                # A-priority without number
                warnings.append(f"Line {i}: A-priority task missing number (should be 🔴1, 🔴2, etc.)")

            # Check for company context
            has_company = any(company.lower() in task_text.lower() for company in VALID_COMPANIES)
            if not has_company and 'Company:' not in task_text:
                pass  # Only warn in daily notes, handled below

        # Check blocked tasks
        blocked_match = BLOCKED_PATTERN.match(line.strip())
        if blocked_match:
            task_text = blocked_match.group(1)
            if 'waiting for' not in task_text.lower() and 'Waiting for:' not in task_text:
                warnings.append(f"Line {i}: Blocked task should include 'Waiting for:' context")

        # Check for due dates - should use ISO format 📅 YYYY-MM-DD
        if '📅' in line:
            has_iso_date = bool(DUE_DATE_PATTERN.search(line))
            has_old_format = bool(OLD_SCHEDULED_PATTERN.search(line))

            if has_old_format:
                warnings.append(f"Line {i}: Due date uses old prose format. Use ISO format: 📅 YYYY-MM-DD")
            elif not has_iso_date:
                warnings.append(f"Line {i}: Due date should use ISO format: 📅 YYYY-MM-DD")

    # Check for daily note specific rules
    if '/4-Daily/' in file_path:
        # Check max 5 A-priority tasks
        uncompleted_a_tasks = [t for t in a_tasks if '- [ ]' in content.split('\n')[t[0]-1]]
        if len(uncompleted_a_tasks) > 5:
            issues.append(f"Too many A-priority tasks ({len(uncompleted_a_tasks)}). Maximum is 5 per day.")

        # Check for duplicate A-priority numbers
        if a_task_numbers:
            duplicates = [n for n in set(a_task_numbers) if a_task_numbers.count(n) > 1]
            if duplicates:
                warnings.append(f"Duplicate A-priority numbers: {duplicates}")

        # Check numbering is sequential
        if a_task_numbers:
            sorted_nums = sorted(a_task_numbers)
            expected = list(range(1, len(sorted_nums) + 1))
            if sorted_nums != expected:
                warnings.append(f"A-priority numbers should be sequential (1, 2, 3...). Found: {sorted_nums}")

        # Check for company context in daily note tasks
        for i, number, task_text in a_tasks:
            has_company = any(company.lower() in task_text.lower() for company in VALID_COMPANIES)
            if not has_company and 'Company:' not in task_text and '[' not in task_text:
                # Check if task text is just a placeholder
                if not task_text.startswith('['):
                    pass  # Don't warn on every task, can be noisy

    return issues, warnings

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

    # Validate tasks
    issues, warnings = validate_tasks(file_path, content)

    # Output results
    if issues or warnings:
        output_parts = []

        if issues:
            output_parts.append("Task Format Issues:")
            for issue in issues:
                output_parts.append(f"  - {issue}")

        if warnings:
            output_parts.append("Task Format Warnings:")
            for warning in warnings:
                output_parts.append(f"  - {warning}")

        # Print to stderr for visibility
        print("\n".join(output_parts), file=sys.stderr)

        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="warning",
                          details={"file": os.path.basename(file_path),
                                   "issues": len(issues), "warnings": len(warnings)})
    else:
        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="success",
                          details={"file": os.path.basename(file_path)})

    # Always exit 0 (don't block) - just provide feedback
    sys.exit(0)

if __name__ == "__main__":
    main()
