---
description: List all Claude Code skills with descriptions
allowed-tools: Read, Glob, Bash
---

# List Skills Command

Display all Claude Code skills in this vault with their descriptions.

## Context

- **Skills directory**: `.claude/skills/`

## Task

### 1. Find All Skills

```bash
ls -la .claude/skills/
```

### 2. Extract Information

For each skill directory:
- Read SKILL.md
- Extract name from frontmatter
- Extract description from frontmatter
- Note if multi-file (has REFERENCE.md, EXAMPLES.md, etc.)

### 3. Categorize by Function

Group skills by category (infer from name/description):
- **Core Workflow**: daily-note, task-system, work-logging, etc.
- **Calendar**: calendar-awareness, calendar-management, etc.
- **Planning**: planning-cadence, strategic-thinking, etc.
- **People**: person-context, meeting-prep, etc.
- **Content**: writing-voice, document-generator, etc.
- **System**: inbox-processor, project-status, etc.
- **Advisors**: advisor-* skills

### 4. Output Format

```
## Claude Code Skills

### Core Workflow (X skills)

| Skill | Description | Files |
|-------|-------------|-------|
| `skill-name` | Brief description | 1 |
| `other-skill` | Brief description | 3 |

### Calendar (X skills)

| Skill | Description | Files |
|-------|-------------|-------|
| ... | ... | ... |

[Continue for each category]

---

**Total**: X skills
**Multi-file**: Y skills (progressive disclosure)
**Single-file**: Z skills
```

## Output

- Categorized list of all skills
- Brief description for each
- File count indicator
- Summary statistics
