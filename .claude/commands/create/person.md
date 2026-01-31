---
description: Look up or create a person note
argument-hint: [person-name]
allowed-tools: Read, Write, Grep, Glob, Bash
---

# Person Lookup/Create Command

Look up an existing person note or create a new one.

## Arguments

- `$ARGUMENTS` - The person's name to look up or create

## Task

### 1. Search for Existing Person

```bash
# Search in Professional contacts
find "{{vault_path}}/6-People/Professional" -iname "*[name]*" -type f

# Search in Personal contacts
find "{{vault_path}}/6-People/Personal" -iname "*[name]*" -type f
```

### 2. If Person Exists

- Read their profile
- Summarize key information:
  - Role and company
  - Communication preferences
  - Recent interactions
  - Open action items
- Open the note in Obsidian

### 3. If Person Doesn't Exist

Ask user:
- Is this a Professional or Personal contact?
- What company are they with (if professional)?
- What is their role?

Then:
1. Read template from `3-Resources/Templates/person-template.md`
2. Create new file:
   - Professional: `6-People/Professional/[Company]/[name].md`
   - Personal: `6-People/Personal/[name].md`
3. Fill in basic information
4. Open in Obsidian

## Output Format

### For Existing Person
```markdown
## [Person Name]

**Role**: [Title] at [Company]
**Relationship**: [boss/colleague/friend/etc]
**Communication**: Prefers [channel], [style]
**Last Interaction**: [date]

### Recent Activity
- [Recent meeting or interaction]

### Open Items
- [ ] [Any pending action items]

### Quick Context
[Key things to remember about working with this person]
```

### For New Person
```markdown
## Creating New Person: [Name]

I'll create a new person note. Please confirm:
- Type: Professional / Personal
- Company: [if professional]
- Role: [their title]

[Then create and open the note]
```
