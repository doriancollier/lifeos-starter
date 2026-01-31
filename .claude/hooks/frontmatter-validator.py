#!/usr/bin/env python3
"""
Frontmatter Validator Hook (PostToolUse)

Validates YAML frontmatter in markdown files after Write/Edit operations:
- Checks required fields based on note type
- Validates date formats
- Ensures company field uses valid values
- Verifies type field matches known types

Returns warnings for issues found (does not block by default).
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
logger = setup_logger("frontmatter-validator")

# Vault configuration - uses environment variable or auto-detects from script location
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or str(Path(__file__).resolve().parent.parent.parent)


def load_company_names():
    """Load company names from .user/companies.yaml dynamically."""
    try:
        import yaml
    except ImportError:
        # Fall back to defaults if PyYAML not installed
        return ["Personal", ""]

    companies_file = os.path.join(VAULT_ROOT, ".user", "companies.yaml")
    companies = ["Personal", ""]  # Always include Personal and empty

    if os.path.exists(companies_file):
        try:
            with open(companies_file, 'r') as f:
                data = yaml.safe_load(f) or {}

            # Extract company names from structure
            companies_data = data.get('companies', {})
            for key in ['company_1', 'company_2', 'company_3']:
                company = companies_data.get(key, {})
                name = company.get('name', '')
                if name and name not in companies:
                    companies.append(name)
        except Exception:
            pass  # Silently fall back to defaults

    return companies


# Valid values - loaded dynamically from user config
VALID_COMPANIES = load_company_names()
VALID_NOTE_TYPES = ["daily-note", "meeting", "person", "project", "moc", "area", "resource", ""]
VALID_RELATIONSHIPS = ["boss", "colleague", "friend", "family", "client", "partner", "mentor", "report", "vendor", ""]

# Required fields by note type
REQUIRED_FIELDS = {
    "daily-note": ["date", "day_of_week", "type", "tags"],
    "meeting": ["title", "date", "type", "company", "attendees", "tags"],
    "person": ["name", "type", "relationship"],
    "project": ["title", "type", "status"],
}

# Date pattern
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return None

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    frontmatter_text = parts[1].strip()
    frontmatter = {}

    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            # Handle arrays
            if value.startswith('['):
                # Simple array parsing
                value = value.strip('[]')
                value = [v.strip().strip('"').strip("'") for v in value.split(',') if v.strip()]

            frontmatter[key] = value

    return frontmatter

def validate_frontmatter(file_path, content):
    """Validate frontmatter and return list of issues."""
    issues = []
    warnings = []

    # Skip non-markdown files
    if not file_path.endswith('.md'):
        return issues, warnings

    # Skip template files
    if '/Templates/' in file_path:
        return issues, warnings

    # Extract frontmatter
    frontmatter = extract_frontmatter(content)

    if frontmatter is None:
        # Check if this is a file that should have frontmatter
        if any(dir_name in file_path for dir_name in ['4-Daily', '5-Meetings', '6-People', '1-Projects']):
            warnings.append(f"Missing YAML frontmatter in {os.path.basename(file_path)}")
        return issues, warnings

    # Get note type
    note_type = frontmatter.get('type', '')

    # Validate required fields for known types
    if note_type in REQUIRED_FIELDS:
        for field in REQUIRED_FIELDS[note_type]:
            if field not in frontmatter or not frontmatter[field]:
                issues.append(f"Missing required field '{field}' for {note_type}")

    # Validate date format
    date_value = frontmatter.get('date', '')
    if date_value and not DATE_PATTERN.match(date_value):
        issues.append(f"Invalid date format '{date_value}' - expected YYYY-MM-DD")

    # Validate company field
    company = frontmatter.get('company', '')
    if company and company not in VALID_COMPANIES:
        warnings.append(f"Unknown company '{company}' - expected one of: {', '.join([c for c in VALID_COMPANIES if c])}")

    # Validate type field
    if note_type and note_type not in VALID_NOTE_TYPES:
        warnings.append(f"Unknown note type '{note_type}' - expected one of: {', '.join([t for t in VALID_NOTE_TYPES if t])}")

    # Validate relationship field for person notes
    if note_type == 'person':
        relationship = frontmatter.get('relationship', '')
        if relationship and relationship not in VALID_RELATIONSHIPS:
            warnings.append(f"Unknown relationship '{relationship}'")

    # Validate daily note date matches filename
    if note_type == 'daily-note' and '/4-Daily/' in file_path:
        filename = os.path.basename(file_path).replace('.md', '')
        if date_value and date_value != filename and filename != 'today':
            issues.append(f"Date in frontmatter ({date_value}) doesn't match filename ({filename})")

    # Validate day_of_week matches date
    if note_type == 'daily-note':
        day_of_week = frontmatter.get('day_of_week', '')
        if date_value and day_of_week and DATE_PATTERN.match(date_value):
            try:
                actual_day = datetime.strptime(date_value, '%Y-%m-%d').strftime('%A')
                if day_of_week != actual_day:
                    warnings.append(f"day_of_week '{day_of_week}' doesn't match date (should be '{actual_day}')")
            except ValueError:
                pass

    # Validate attendees is a list for meetings
    if note_type == 'meeting':
        attendees = frontmatter.get('attendees', '')
        if attendees and not isinstance(attendees, list):
            warnings.append("'attendees' should be an array")

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

    # Validate frontmatter
    issues, warnings = validate_frontmatter(file_path, content)

    # Output results
    if issues or warnings:
        output_parts = []

        if issues:
            output_parts.append("Frontmatter Issues:")
            for issue in issues:
                output_parts.append(f"  - {issue}")

        if warnings:
            output_parts.append("Frontmatter Warnings:")
            for warning in warnings:
                output_parts.append(f"  - {warning}")

        # Print to stderr for visibility (doesn't block)
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
