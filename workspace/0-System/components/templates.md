---
title: "Templates"
created: "2025-12-02"
status: "active"
---

# Templates

Templates provide consistent structure for different note types.

## How Templates Work

Templates live in `3-Resources/Templates/` and are used when creating new notes of specific types.

> **Planning Templates**: 50+ new templates have been added for planning, decisions, retrospectives, roles, productivity, strategic thinking, and work-life integration. See [[3-Resources/Templates/_Template-Index|Template Index]] for the complete list organized by domain and context.

## Planning Templates

| Domain | Count | Purpose |
|--------|-------|---------|
| Planning/ | 8 | Annual, quarterly, monthly, weekly planning |
| Decisions/ | 10 | First principles, pre-mortems, strategic decisions |
| Retrospectives/ | 5 | Weekly, monthly, quarterly, annual, project retros |
| Roles/ | 8 | Provider, father, partner role reviews |
| Productivity/ | 5 | Pareto audits, leverage audits, priority filters |
| Strategic/ | 9 | Systems thinking, personal SWOT, barbell audits |
| Work-Life/ | 5 | Energy assessment, burnout prevention, boundaries |

**Template Index**: `3-Resources/Templates/_Template-Index.md`

## Legacy Template Categories

### Daily Notes

| Template | Purpose |
|----------|---------|
| `daily-enhanced.md` | Daily note with task sections, company contexts, captures |

### Meeting Notes

| Template | Purpose |
|----------|---------|
| `meeting.md` | Generic meeting template (works for all companies via `{{company}}` placeholder) |
| `personal-meeting.md` | Personal/family meeting notes |
| `recurring-meeting-*.md` | Recurring meeting templates (e.g., `recurring-meeting-engineering-sync.md`) |

### People

| Template | Purpose |
|----------|---------|
| `person-template.md` | Person file (professional or personal) |

### Projects

| Template | Purpose |
|----------|---------|
| `trip-planning.md` | Trip/travel planning |
| `gift-planning.md` | Gift occasion planning |
| `product-roadmap.md` | Product roadmap structure |

### Personal Documents (Owner Profile)

Templates for vault owner's personal profile documents in `3-Resources/Templates/personal/`:

| Template | Purpose |
|----------|---------|
| `resume-template.md` | Professional summary |
| `work-history-template.md` | Detailed role breakdowns |
| `education-template.md` | Schools, degrees, certifications |
| `skills-template.md` | Technical and soft skills inventory |
| `assets-template.md` | Ownership stakes, investments |
| `legal-entities-template.md` | LLCs, business structures |
| `medical-history-template.md` | Personal health records |
| `emergency-contacts-template.md` | POA, emergency info |
| `insurance-template.md` | Policy details |

See `0-System/guides/personal-documents.md` for full documentation.

### Documents

| Template | Purpose |
|----------|---------|
| `3-Resources/Documents/Templates/*.html` | Printable document templates |
| `.claude/skills/goal-bingo/bingo-card-template.html` | Goal Bingo card template (in skill folder) |

## Template Structure

### Frontmatter

Every template starts with YAML frontmatter:

```yaml
---
title: "{{title}}"
created: "{{date}}"
type: "template-type"
---
```

### Placeholders

Common placeholders:

| Placeholder | Meaning |
|-------------|---------|
| `{{title}}` | Note title |
| `{{date}}` | Current date (YYYY-MM-DD) |
| `{{time}}` | Current time (HH:MM) |
| `{{company}}` | Company context |

## Example Templates

### Daily Note Template

```markdown
---
title: "{{date}}"
date: "{{date}}"
energy_level: ""
focus_areas: []
---

# {{date}}

## Today's Focus

### A Priority (Must Do)

### B Priority (Should Do)

### C Priority (Nice to Have)

### Blocked

### Scheduled

---

## Company: {{company_1_name}}

## Company: {{company_2_name}}

## Company: Personal

---

## Random Captures

### Daily Memories

### Quick Notes

---

## End of Day
```

### Person Template

```markdown
---
name: "{{name}}"
company: ""
role: ""
relationship: ""
last_contact: "{{date}}"
---

# {{name}}

## Context

How I know this person.

## Role & Responsibilities

What they do.

## Communication Style

How they prefer to communicate.

## Current Projects Together

- [[Project 1]]

## Notes

Additional context.
```

### Project Template

```markdown
---
title: "{{title}}"
status: "backlog"
company: ""
created: "{{date}}"
supports_goal: ""
goal_alignment: ""
---

# {{title}}

## Context

Why this project exists.

## Objective

What we're trying to achieve.

## Success Criteria

How we'll know we've succeeded.

## Tasks

- [ ] Task 1
- [ ] Task 2

## Notes

Additional notes.

## Related

- [[YYYY]] - Goal X: [Goal Name from supports_goal]
- [[Other-Related-Notes]]
```

## Creating a New Template

1. **Identify the note type** needing consistency
2. **Create template** in `3-Resources/Templates/`
3. **Include frontmatter** with type-appropriate fields
4. **Add placeholders** for dynamic content
5. **Document** the template's purpose

## Template Naming

| Type | Pattern | Example |
|------|---------|---------|
| General | `[type].md` | `person-template.md`, `meeting.md` |
| Recurring meetings | `recurring-meeting-[name].md` | `recurring-meeting-engineering-sync.md` |
| Special projects | `[type]-planning.md` | `trip-planning.md`, `gift-planning.md` |
| Printable | `[type].html` | `poster-wall.html`, `checklist-routine.html` |

## Best Practices

1. **Minimal but complete** — Include required fields, not everything possible
2. **Clear placeholders** — Use consistent `{{placeholder}}` syntax
3. **Type-specific frontmatter** — Each template type has appropriate fields
4. **Instructions** — Include comments for how to fill sections
5. **Consistent structure** — Similar templates should have similar layouts
