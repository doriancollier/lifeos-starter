#!/usr/bin/env python3
"""
Initialize a new Claude Code skill with standard directory structure.

Usage:
    python init_skill.py <skill-name> [--path <path>]

Examples:
    python init_skill.py my-new-skill
    python init_skill.py data-analysis --path .claude/skills
"""

import argparse
import re
import sys
from pathlib import Path

# Default skills directory (relative to repo root)
DEFAULT_SKILLS_PATH = ".claude/skills"

# SKILL.md template
SKILL_TEMPLATE = '''---
name: {name}
description: [REPLACE: Clear description of what this skill does. Include trigger keywords users would naturally say. Use "Use when..." format.]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# {title}

Brief overview of what this skill does and why it exists.

## When to Use

This skill activates when:
- [Trigger context 1]
- [Trigger context 2]
- User mentions [keywords]

## Core Instructions

### Main Operation

Step-by-step guidance for the primary use case.

1. First step
2. Second step
3. Third step

### Common Patterns

**Pattern 1:**
```
Example code or format
```

## Examples

### Example 1: [Scenario]

**User says**: "Help me with [scenario]"

**Claude does**: [Expected behavior]

### Example 2: [Another Scenario]

**User says**: "[Another scenario]"

**Claude does**: [Expected behavior]

## Integration with Other Skills

- Use **related-skill** for [purpose]

## Utility Scripts

To run validation:
```bash
python scripts/example.py input
```
'''

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example utility script for {title}.

This script is executed by Claude, not read into context.
Only the output consumes tokens.
"""

import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python example.py <input>")
        sys.exit(1)

    input_arg = sys.argv[1]
    print(f"Processing: {{input_arg}}")
    # Add your logic here
    print("Done!")

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = '''# API Reference

Detailed documentation for {title}.

## Functions/Formats

### Item 1

**Purpose**: What this does

**Syntax**:
```
format or syntax here
```

**Example**:
```
concrete example
```

## Configuration

### Option 1

- **Default**: value
- **Description**: What this controls
'''

EXAMPLE_ASSET = '''# {title} Template

This is a template file that can be used as output.

Replace this content with actual template material.
'''


def validate_name(name: str) -> bool:
    """Validate skill name format: lowercase, hyphens, max 64 chars."""
    if len(name) > 64:
        return False
    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        return False
    if '--' in name:  # No double hyphens
        return False
    return True


def create_skill(name: str, base_path: Path) -> Path:
    """Create skill directory with standard structure."""
    skill_path = base_path / name

    if skill_path.exists():
        raise FileExistsError(f"Skill directory already exists: {skill_path}")

    # Create directories
    skill_path.mkdir(parents=True)
    (skill_path / "scripts").mkdir()
    (skill_path / "references").mkdir()
    (skill_path / "assets").mkdir()

    # Create title from name
    title = name.replace('-', ' ').title()

    # Create SKILL.md
    skill_md = SKILL_TEMPLATE.format(name=name, title=title)
    (skill_path / "SKILL.md").write_text(skill_md)

    # Create example script
    example_py = EXAMPLE_SCRIPT.format(title=title)
    (skill_path / "scripts" / "example.py").write_text(example_py)

    # Create example reference
    example_ref = EXAMPLE_REFERENCE.format(title=title)
    (skill_path / "references" / "api_reference.md").write_text(example_ref)

    # Create example asset
    example_asset = EXAMPLE_ASSET.format(title=title)
    (skill_path / "assets" / "template.md").write_text(example_asset)

    return skill_path


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new Claude Code skill"
    )
    parser.add_argument(
        "name",
        help="Skill name (lowercase, hyphens, e.g., 'my-new-skill')"
    )
    parser.add_argument(
        "--path",
        default=DEFAULT_SKILLS_PATH,
        help=f"Base path for skills (default: {DEFAULT_SKILLS_PATH})"
    )

    args = parser.parse_args()

    # Validate name
    if not validate_name(args.name):
        print(f"Error: Invalid skill name '{args.name}'")
        print("Requirements:")
        print("  - Lowercase letters, numbers, and hyphens only")
        print("  - Must start with a letter")
        print("  - No double hyphens")
        print("  - Maximum 64 characters")
        sys.exit(1)

    # Resolve path
    base_path = Path(args.path)

    try:
        skill_path = create_skill(args.name, base_path)
        print(f"Created skill: {skill_path}")
        print()
        print("Directory structure:")
        print(f"  {skill_path}/")
        print(f"  ├── SKILL.md")
        print(f"  ├── scripts/")
        print(f"  │   └── example.py")
        print(f"  ├── references/")
        print(f"  │   └── api_reference.md")
        print(f"  └── assets/")
        print(f"      └── template.md")
        print()
        print("Next steps:")
        print("  1. Edit SKILL.md with your skill's instructions")
        print("  2. Update the description (critical for activation)")
        print("  3. Add examples and integration notes")
        print("  4. Restart Claude Code to load the skill")
        print("  5. Test with a question that should trigger it")

    except FileExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
