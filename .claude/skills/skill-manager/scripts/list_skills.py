#!/usr/bin/env python3
"""
List all Claude Code skills with descriptions and metrics.

Usage:
    python list_skills.py [--path <skills-path>]
    python list_skills.py --path .claude/skills
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_SKILLS_PATH = ".claude/skills"


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


def count_words(text: str) -> int:
    """Count words in text, excluding code blocks and frontmatter."""
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            text = parts[2]

    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)

    return len(text.split())


def count_files(skill_path: Path) -> int:
    """Count total files in skill directory."""
    return sum(1 for _ in skill_path.rglob('*') if _.is_file())


def categorize_skill(name: str, description: str) -> str:
    """Attempt to categorize a skill based on name and description."""
    name_lower = name.lower()
    desc_lower = description.lower()

    categories = {
        'Calendar': ['calendar', 'event', 'schedule', 'birthday', 'timebox'],
        'Planning': ['planning', 'strategic', 'pre-mortem', 'energy', 'goals', 'review'],
        'Tasks': ['task', 'todo', 'priority', 'work-log'],
        'People': ['person', 'meeting', 'relationship'],
        'Content': ['writing', 'document', 'product', 'bingo'],
        'System': ['inbox', 'project', 'obsidian', 'context', 'skill'],
        'Advisors': ['advisor'],
        'Core': ['daily', 'note'],
    }

    for category, keywords in categories.items():
        if any(kw in name_lower or kw in desc_lower for kw in keywords):
            return category

    return 'Other'


def get_skill_info(skill_path: Path) -> Optional[Dict]:
    """Get information about a skill."""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return None

    content = skill_md.read_text()
    frontmatter = parse_frontmatter(content)

    name = frontmatter.get('name', skill_path.name)
    description = frontmatter.get('description', 'No description')

    # Truncate description for display
    if len(description) > 80:
        description = description[:77] + '...'

    return {
        'name': name,
        'description': description,
        'full_description': frontmatter.get('description', ''),
        'words': count_words(content),
        'files': count_files(skill_path),
        'category': categorize_skill(name, frontmatter.get('description', '')),
        'path': skill_path,
    }


def list_skills(skills_path: Path) -> List[Dict]:
    """List all skills in the given path."""
    skills = []

    if not skills_path.exists():
        return skills

    for item in sorted(skills_path.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            info = get_skill_info(item)
            if info:
                skills.append(info)

    return skills


def print_skills(skills: List[Dict]):
    """Print skills in a formatted table by category."""
    if not skills:
        print("No skills found.")
        return

    # Group by category
    categories = {}
    for skill in skills:
        cat = skill['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill)

    # Print header
    print(f"\n{'='*80}")
    print(f"Claude Code Skills Inventory")
    print(f"{'='*80}\n")

    # Print by category
    for category in sorted(categories.keys()):
        cat_skills = categories[category]
        print(f"\n### {category} ({len(cat_skills)} skills)\n")
        print(f"| {'Skill':<25} | {'Words':>5} | {'Files':>5} | Description |")
        print(f"|{'-'*27}|{'-'*7}|{'-'*7}|{'-'*40}|")

        for skill in sorted(cat_skills, key=lambda s: s['name']):
            name = skill['name'][:25]
            words = skill['words']
            files = skill['files']
            desc = skill['description'][:38]
            print(f"| {name:<25} | {words:>5} | {files:>5} | {desc} |")

    # Summary
    total = len(skills)
    total_words = sum(s['words'] for s in skills)
    avg_words = total_words // total if total > 0 else 0
    multi_file = sum(1 for s in skills if s['files'] > 1)

    print(f"\n{'-'*80}")
    print(f"Summary:")
    print(f"  Total skills: {total}")
    print(f"  Multi-file skills: {multi_file}")
    print(f"  Average words/skill: {avg_words}")
    print(f"  Categories: {len(categories)}")
    print()

    # Token efficiency warnings
    high_word_skills = [s for s in skills if s['words'] > 500]
    if high_word_skills:
        print("Token efficiency warnings (> 500 words):")
        for skill in high_word_skills:
            print(f"  - {skill['name']}: {skill['words']} words")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="List all Claude Code skills"
    )
    parser.add_argument(
        "--path",
        default=DEFAULT_SKILLS_PATH,
        help=f"Path to skills directory (default: {DEFAULT_SKILLS_PATH})"
    )

    args = parser.parse_args()
    skills_path = Path(args.path)

    skills = list_skills(skills_path)
    print_skills(skills)


if __name__ == "__main__":
    main()
