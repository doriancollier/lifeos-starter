#!/usr/bin/env python3
"""
Validate a Claude Code skill for quality and best practices.

Usage:
    python validate_skill.py <skill-path>
    python validate_skill.py .claude/skills/my-skill
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Validation thresholds
MAX_DESCRIPTION_CHARS = 1024
MAX_NAME_CHARS = 64
MAX_SKILL_LINES = 500
TOKEN_TARGETS = {
    "getting-started": 150,
    "frequent": 200,
    "standard": 500,
}


def count_words(text: str) -> int:
    """Count words in text, excluding code blocks and frontmatter."""
    # Remove frontmatter
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            text = parts[2]

    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)

    # Count words
    words = text.split()
    return len(words)


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md."""
    if not content.startswith('---'):
        return {}

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}

    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"\'')

    return frontmatter


def validate_skill(skill_path: Path) -> List[Tuple[str, str, str]]:
    """
    Validate a skill and return list of (level, check, message) tuples.
    Levels: 'pass', 'warn', 'fail'
    """
    results = []

    # Check directory exists
    if not skill_path.exists():
        results.append(('fail', 'Directory', f"Skill path does not exist: {skill_path}"))
        return results

    if not skill_path.is_dir():
        results.append(('fail', 'Directory', f"Path is not a directory: {skill_path}"))
        return results

    results.append(('pass', 'Directory', 'Skill directory exists'))

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        results.append(('fail', 'SKILL.md', 'SKILL.md file not found'))
        return results

    results.append(('pass', 'SKILL.md', 'SKILL.md file exists'))

    # Read content
    content = skill_md.read_text()
    lines = content.split('\n')

    # Parse frontmatter
    frontmatter = parse_frontmatter(content)

    # Check name field
    if 'name' not in frontmatter:
        results.append(('fail', 'Name', 'Missing "name" field in frontmatter'))
    else:
        name = frontmatter['name']
        dir_name = skill_path.name

        if name != dir_name:
            results.append(('fail', 'Name', f"Name '{name}' does not match directory '{dir_name}'"))
        elif len(name) > MAX_NAME_CHARS:
            results.append(('fail', 'Name', f"Name exceeds {MAX_NAME_CHARS} characters"))
        elif not re.match(r'^[a-z][a-z0-9-]*$', name):
            results.append(('fail', 'Name', 'Name must be lowercase with hyphens only'))
        else:
            results.append(('pass', 'Name', f"Name '{name}' is valid"))

    # Check description field
    if 'description' not in frontmatter:
        results.append(('fail', 'Description', 'Missing "description" field in frontmatter'))
    else:
        desc = frontmatter['description']

        if len(desc) > MAX_DESCRIPTION_CHARS:
            results.append(('fail', 'Description', f"Description exceeds {MAX_DESCRIPTION_CHARS} characters ({len(desc)} chars)"))
        elif len(desc) < 20:
            results.append(('fail', 'Description', 'Description is too short (< 20 chars)'))
        elif '[REPLACE' in desc or 'TODO' in desc.upper():
            results.append(('warn', 'Description', 'Description contains placeholder text'))
        else:
            # Check for trigger keywords
            has_trigger = any(phrase in desc.lower() for phrase in ['use when', 'activates when', 'use for'])
            if not has_trigger:
                results.append(('warn', 'Description', 'Description missing trigger phrase ("Use when...", "Activates when...")'))
            else:
                results.append(('pass', 'Description', f"Description is valid ({len(desc)} chars)"))

    # Check line count
    line_count = len(lines)
    if line_count > MAX_SKILL_LINES:
        results.append(('warn', 'Size', f"SKILL.md exceeds {MAX_SKILL_LINES} lines ({line_count} lines). Consider progressive disclosure."))
    else:
        results.append(('pass', 'Size', f"SKILL.md is {line_count} lines"))

    # Check word count
    word_count = count_words(content)
    if word_count > TOKEN_TARGETS["standard"]:
        results.append(('warn', 'Token Efficiency', f"Body has {word_count} words (target: < {TOKEN_TARGETS['standard']})"))
    else:
        results.append(('pass', 'Token Efficiency', f"Body has {word_count} words"))

    # Check for required sections
    required_sections = ['When to Use', 'Example']
    for section in required_sections:
        if section.lower() in content.lower():
            results.append(('pass', f'Section: {section}', f"'{section}' section found"))
        else:
            results.append(('warn', f'Section: {section}', f"Missing '{section}' section"))

    # Check for scripts directory
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists() and any(scripts_dir.iterdir()):
        results.append(('pass', 'Scripts', 'Scripts directory with files'))
    else:
        results.append(('pass', 'Scripts', 'No scripts (optional)'))

    # Check for references directory
    refs_dir = skill_path / "references"
    if refs_dir.exists() and any(refs_dir.iterdir()):
        results.append(('pass', 'References', 'References directory with files'))

    return results


def print_results(results: List[Tuple[str, str, str]], skill_name: str):
    """Print validation results in a formatted way."""
    print(f"\n{'='*60}")
    print(f"Skill Validation: {skill_name}")
    print(f"{'='*60}\n")

    pass_count = sum(1 for r in results if r[0] == 'pass')
    warn_count = sum(1 for r in results if r[0] == 'warn')
    fail_count = sum(1 for r in results if r[0] == 'fail')

    # Print results by level
    for level, icon in [('fail', ''), ('warn', ''), ('pass', '')]:
        level_results = [r for r in results if r[0] == level]
        for _, check, message in level_results:
            print(f"  {icon} [{check}] {message}")

    # Summary
    print(f"\n{'-'*60}")
    if fail_count > 0:
        print(f"  Status: FAILED ({fail_count} errors, {warn_count} warnings)")
    elif warn_count > 0:
        print(f"  Status: PASSED with warnings ({warn_count} warnings)")
    else:
        print(f"  Status: PASSED ({pass_count} checks)")
    print()

    return fail_count == 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Claude Code skill"
    )
    parser.add_argument(
        "path",
        help="Path to skill directory"
    )

    args = parser.parse_args()
    skill_path = Path(args.path)

    results = validate_skill(skill_path)
    success = print_results(results, skill_path.name)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
