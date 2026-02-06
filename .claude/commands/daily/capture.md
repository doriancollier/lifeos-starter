---
description: Quick capture to today's daily note
argument-hint: [text to capture]
allowed-tools: Read, Write, Edit, Bash
---

# Quick Capture Command

Quickly add a note, idea, or task to today's daily note.

## Arguments

- `$ARGUMENTS` - The text to capture (idea, note, task, link, etc.)

## Context

- **Daily notes**: `{{vault_path}}/4-Daily/`
- **Today's note**: `workspace/4-Daily/YYYY-MM-DD.md`

## Task

### 1. Find Today's Daily Note

```bash
ls "{{vault_path}}/4-Daily/$(date +%Y-%m-%d).md"
```

Note: The `daily-note` skill will automatically create today's note if it doesn't exist.

### 2. Determine Capture Type

Analyze the input to categorize:

| If input contains... | Capture to section |
|---------------------|-------------------|
| `- [ ]` or "task:" or "todo:" | Tasks (determine priority) |
| URL or "http" | Links to Explore Later |
| "idea:" or "thought:" | Ideas |
| "meeting" or calendar reference | Meetings & Events |
| Default | Quick Notes |

### 3. Append to Appropriate Section

**For Tasks**: Add to appropriate priority section
```markdown
### [A/B/C] Priority Tasks
- [ ] [emoji] [Task text] - Company: [if specified]
```

**For Ideas**: Add to Ideas section
```markdown
### Ideas
- [Captured idea text]
```

**For Links**: Add to Links section
```markdown
### Links to Explore Later
- [URL or link text]
```

**For Quick Notes**: Add to Quick Notes section
```markdown
### Quick Notes
- [Captured text]
```

### 4. Add Timestamp

Prefix capture with time if it seems time-sensitive:
```markdown
- [HH:MM] [Captured content]
```

## Output

```markdown
## Captured!

Added to today's daily note (`YYYY-MM-DD.md`):

**Section**: [Quick Notes / Ideas / Links / Tasks]
**Content**: [what was captured]

[Optional: Open in Obsidian? y/n]
```

## Examples

| Input | Result |
|-------|--------|
| `/capture Call mom about dinner` | Quick Notes: "- Call mom about dinner" |
| `/capture task: Review PR for analytics` | B Priority: "- [ ] 🟡 Review PR for analytics" |
| `/capture idea: What if we added gamification?` | Ideas: "- What if we added gamification?" |
| `/capture https://example.com/article` | Links: "- https://example.com/article" |
| `/capture 🔴 Urgent: Fix production bug` | A Priority: "- [ ] 🔴 Urgent: Fix production bug" |
