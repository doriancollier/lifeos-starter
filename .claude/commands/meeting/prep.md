---
description: Prepare context for a meeting or person interaction
argument-hint: [meeting-title or person-name]
allowed-tools: Read, Grep, Glob, Bash
---

# Prepare Context Command

Gather all relevant context before a meeting or interaction with someone.

## Arguments

- `$ARGUMENTS` - Either a meeting title, person name, or topic to prepare for

## Task

### 1. Identify What We're Preparing For

Determine if the argument is:
- A **person's name** → Focus on that person's profile and interaction history
- A **meeting title** → Focus on the meeting topic and likely attendees
- A **company/project** → Focus on that context area

### 1.5. Check for Recurring Meeting Template

Search for a matching recurring meeting template:

```bash
# List all recurring meeting templates
find "{{vault_path}}/3-Resources/Templates" -name "recurring-meeting-*.md" -type f
```

**Template Matching:**
- Normalize the meeting name (lowercase, replace spaces with hyphens)
- Look for templates containing key words from the meeting name
- Example: "Engineering Sync" → matches `recurring-meeting-engineering-sync.md`

If a template is found:
1. Read the template to get the pre-meeting checklist
2. Surface the checklist items in the prep output
3. Note the expected agenda structure

### 2. Gather Person Context

For each relevant person:
- Search `{{vault_path}}/6-People/Professional/` and `{{vault_path}}/6-People/Personal/` for their profile
- Note their role, communication style, preferences
- Find recent interactions and meetings

```bash
# Find person file
find "{{vault_path}}/6-People" -name "*[name]*" -type f
```

### 3. Find Previous Meetings

```bash
# Search meeting notes for the person or topic
grep -r "[search term]" "{{vault_path}}/5-Meetings/" --include="*.md" -l
```

### 4. Find Related Projects

```bash
# Search projects
grep -r "[topic]" "{{vault_path}}/1-Projects/" --include="*.md" -l
```

### 5. Find Open Action Items

```bash
# Find action items related to the person/topic
grep -r "- \[ \].*[name/topic]" "{{vault_path}}/5-Meetings/" --include="*.md"
```

### 6. Check Daily Notes for Recent Context

```bash
# Recent mentions in daily notes
grep -r "[name/topic]" "{{vault_path}}/4-Daily/" --include="*.md" | tail -20
```

## Output Format

```markdown
## Prep Summary: [Topic/Person/Meeting]

### Recurring Meeting Template (if found)
- **Template**: `[template filename]`
- **Pre-Meeting Checklist**:
  - [ ] [Checklist item from template]
  - [ ] [Checklist item from template]
- **Expected Agenda**: [Brief summary of agenda structure]

### Key People
- **[Name]**: [Role] at [Company]
  - Communication style: [style]
  - Last interaction: [date] - [brief summary]
  - Open items with them: [list]

### Recent History
- [Date]: [What happened]
- [Date]: [What happened]

### Open Action Items
- [ ] [Action] - Owner: [who] - Due: [date]

### Related Projects/Context
- [[Project]]: [Status/relevance]

### Suggested Talking Points
1. Follow up on [previous item]
2. Discuss [relevant topic]
3. Decide on [pending decision]

### Things to Remember
- [Important context point]
- [Communication preference to keep in mind]
```

## Integration

This command uses knowledge from:
- **meeting-prep** skill for meeting-specific preparation
- **person-context** skill for people-specific context
- **task-system** skill for finding related tasks
