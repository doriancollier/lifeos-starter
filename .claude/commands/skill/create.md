---
description: Create a new Claude Code skill
argument-hint: [skill-name or description]
allowed-tools: Read, Write, Bash, Glob, AskUserQuestion
---

# Create Skill Command

Create a new Claude Code skill with proper structure and documentation.

## Arguments

- `$ARGUMENTS` - Optional skill name or description

## Context

- **Skills directory**: `.claude/skills/`
- **Skill manager skill**: `.claude/skills/skill-manager/SKILL.md`
- **Templates**: `.claude/skills/skill-manager/TEMPLATES.md`

## Task

Use the skill-manager skill to guide skill creation.

### 1. Gather Requirements

If no arguments provided, ask:
- What should this skill do?
- When should it automatically activate?
- What keywords would users naturally say?

If arguments provided, use them as starting point.

### 2. Determine Skill Name

Suggest a name following conventions:
- Lowercase with hyphens
- Descriptive but concise
- 2-4 words typically

Confirm with user before proceeding.

### 3. Assess Complexity

Ask or determine:
- Simple skill (< 300 lines) → single SKILL.md
- Complex skill (> 300 lines) → multi-file with REFERENCE.md

### 4. Create Skill Directory

```bash
mkdir -p .claude/skills/[skill-name]
```

### 5. Create SKILL.md

Use the appropriate template from `.claude/skills/skill-manager/TEMPLATES.md`:
- **Simple Skill**: For focused, single-purpose skills
- **Multi-File Skill**: For complex skills
- **Workflow Skill**: For multi-step processes
- **Domain Knowledge Skill**: For teaching Claude about a domain
- **Integration Skill**: For external system connections

Fill in:
- Name (matching directory)
- Description (keyword-rich, < 1024 chars)
- Allowed tools (if needed)
- Core instructions
- Examples

### 6. Create Supporting Files (if multi-file)

If complex skill:
- Create `REFERENCE.md` for detailed docs
- Create `EXAMPLES.md` for comprehensive examples
- Create `scripts/` directory if utilities needed

### 7. Update CLAUDE.md

Add the new skill to the appropriate table in CLAUDE.md:
```markdown
| `skill-name` | Brief description |
```

### 8. Provide Testing Instructions

Tell user:
```
To test your new skill:
1. Restart Claude Code (exit and restart)
2. Ask: "What skills are available?"
3. Ask a question that should trigger the skill
4. Verify Claude asks to use the skill
```

## Output

- Confirm skill created
- Show file path(s)
- List what was created
- Provide testing instructions
- Remind to restart Claude Code

$ARGUMENTS
