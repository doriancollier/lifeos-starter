---
name: skill-manager
description: Create, review, and maintain Claude Code skills. Use when creating new skills, auditing existing skills, understanding skill vs command vs agent patterns, or when the user mentions skill development, SKILL.md files, or skill best practices.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# Skill Manager

Create and maintain Claude Code skills. Skills are model-invoked knowledge modules that auto-activate when context matches.

> **Core Principle**: "The context window is a public good." Keep skills concise.

## Quick Start

### Create a Skill

```bash
# Option 1: Use init script
python .claude/skills/skill-manager/scripts/init_skill.py my-skill

# Option 2: Manual
mkdir -p .claude/skills/my-skill
# Create SKILL.md with frontmatter
```

### Directory Structure

```
my-skill/
├── SKILL.md          # Required (< 500 words)
├── scripts/          # Utility scripts (executed, not read)
├── references/       # Detailed docs (read when needed)
└── assets/           # Templates, output files
```

### Minimal SKILL.md

```markdown
---
name: my-skill
description: [What it does]. Use when [trigger 1], [trigger 2], or when user mentions [keywords].
---

# My Skill

## When to Use
- Trigger context 1
- Trigger context 2

## Instructions
Step-by-step guidance.

## Examples
**User says**: "..."
**Claude does**: ...
```

## Creation Workflow

1. **Assess**: Does Claude need this repeatedly? Too large for CLAUDE.md?
2. **Define**: Domain, trigger keywords, tools needed
3. **Create**: Use init script or manual setup
4. **Write**: Frontmatter + instructions + examples
5. **Test**: Restart Claude Code, test activation
6. **Document**: Add to CLAUDE.md skills table
7. **Iterate**: Improve based on usage

## Utility Scripts

```bash
# Initialize new skill with full structure
python .claude/skills/skill-manager/scripts/init_skill.py my-skill

# Validate skill quality
python .claude/skills/skill-manager/scripts/validate_skill.py .claude/skills/my-skill

# List all skills with metrics
python .claude/skills/skill-manager/scripts/list_skills.py
```

## Key Rules

| Rule | Details |
|------|---------|
| **Description is critical** | Triggers activation; use keywords, "Use when..." |
| **< 500 words** | Use progressive disclosure for complex skills |
| **Name = directory** | `name:` frontmatter must match folder name |
| **CSO** | Description = triggers only, not workflow summary |

## When to Use What

| Component | Use When |
|-----------|----------|
| **Skill** | Auto-activation, domain knowledge, multi-file |
| **Command** | Explicit `/invoke`, single file, user control |
| **Agent** | Isolated context, heavy processing, parallel work |

## Additional Resources

- **[REFERENCE.md](REFERENCE.md)** — Detailed docs: TDD, CSO, troubleshooting, advanced patterns
- **[TEMPLATES.md](TEMPLATES.md)** — Ready-to-use skill templates (6 types)

## Skill Locations

- **Project**: `.claude/skills/` (this repo)
- **Personal**: `~/.claude/skills/` (all projects)
