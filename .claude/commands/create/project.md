---
description: Create a new project in the backlog
argument-hint: [project-name]
allowed-tools: Read, Write, Bash, Glob, AskUserQuestion
---

# Create Project Command

Create a new project note in the backlog using standardized structure.

## Arguments

- `$ARGUMENTS` - The project name

## Context

- **Projects directory**: `{{vault_path}}/1-Projects/`
- **Backlog**: `{{vault_path}}/1-Projects/Backlog/`
- **Current**: `{{vault_path}}/1-Projects/Current/`
- **Templates**: `{{vault_path}}/3-Resources/Templates/Projects/`
- **Structure Guide**: See `project-structure` skill for conventions

## Task

### 1. Check if Project Exists

```bash
find "{{vault_path}}/1-Projects" -iname "*[project-name]*" -type f
find "{{vault_path}}/1-Projects" -iname "*[project-name]*" -type d
```

### 2. If Project Exists
- Show where it is (Backlog, Current, Completed, Cancelled)
- Offer to open it

### 3. If Project Doesn't Exist - Determine Complexity

Use AskUserQuestion to determine project type:

**Question**: "What type of project is this?"
**Options**:
- **Simple (Recommended for most)**: Single file, < 15 tasks, no supporting docs
- **Complex**: Folder with entry file, 15+ tasks, has roadmap/research/assets

### 4a. Create Simple Project (Single File)

Create file: `{{vault_path}}/1-Projects/Backlog/[Project-Name].md`

Use template from `{{vault_path}}/3-Resources/Templates/Projects/project-simple.md`:

```markdown
---
title: "[Project Name]"
type: "project"
status: "backlog"
company: ""
created: "YYYY-MM-DD"
tags: ["project"]

# Planning
target_date: ""
deadline: ""
next_steps: ""

# Context
supports_goal: ""
goal_alignment: ""
collaborators: []
---

# [Project Name]

## Overview

**Objective**: [One sentence describing what this project achieves]

**Success Criteria**:
- [ ] [How we know it's done - measurable outcome]
- [ ] [Second criterion]

**Company Context**: [{{company_1_name}} | {{company_2_name}} | EMC | Personal]

## Current Status

### Active Tasks
- [ ] [Next task to do]

### Blocked
<!-- - [ ] 🔵 Task - Waiting for: [reason] -->

## Tasks

### To Do
- [ ] Task 1
- [ ] Task 2

### Done
<!-- - [x] Completed task ✅ YYYY-MM-DD -->

## Notes

### YYYY-MM-DD
Project created.

## Related

- [[Goal or area this supports]]
```

### 4b. Create Complex Project (Folder)

1. Create folder: `{{vault_path}}/1-Projects/Backlog/[Project-Name]/`
2. Create entry file: `{{vault_path}}/1-Projects/Backlog/[Project-Name]/_[Project-Name].md`

Use template from `{{vault_path}}/3-Resources/Templates/Projects/project-complex.md`:

```markdown
---
title: "[Project Name]"
type: "project"
status: "backlog"
company: ""
created: "YYYY-MM-DD"
tags: ["project"]
entry_point: true

# Planning
target_date: ""
deadline: ""
next_steps: ""

# Progress (auto-calculated if not set)
progress: 0
health: "on-track"
last_activity: "YYYY-MM-DD"

# Context
supports_goal: ""
goal_alignment: ""
collaborators: []
---

# [Project Name]

## Overview

**Objective**: [One sentence describing what this project achieves]

**Success Criteria**:
- [ ] [How we know it's done - measurable outcome]
- [ ] [Second criterion]
- [ ] [Third criterion]

**Company Context**: [{{company_1_name}} | {{company_2_name}} | EMC | Personal]

## Background

[Why this project exists. What problem does it solve?]

## Scope

### In Scope
- [What's included]

### Out of Scope
- [What's explicitly not included]

## Current Status

### Active Tasks
- [ ] [Next task to do]

### Blocked
<!-- - [ ] 🔵 Task - Waiting for: [reason] -->

## Tasks

### Phase 1: [Name]
- [ ] Task 1
- [ ] Task 2

### Done
<!-- Move completed tasks here -->

## Supporting Files

| File | Purpose |
|------|---------|
| [[roadmap]] | Detailed phase planning |

## Notes

### YYYY-MM-DD
Project created.

## Related

- [[Goal this supports]]
```

### 5. Ask Company Context

If company not obvious from name, ask:

**Question**: "Which company/area is this for?"
**Options**:
- {{company_1_name}}
- {{company_2_name}}
- EMC ({{company_3_name}})
- Personal

Update the `company:` field in frontmatter.

### 6. Save and Open

- Save file(s) to appropriate location
- Open entry file in Obsidian using `obsidian-open` skill

## Output

- Confirm project created
- Show file path
- Indicate structure type (simple or complex)
- Remind about moving to Current when ready to start

## Naming Convention

- Use kebab-case for file/folder names: `My-Project-Name`
- Entry files for complex projects: `_My-Project-Name.md` (underscore prefix)
- Simple projects: `My-Project-Name.md` (no underscore)

## Next Steps Suggestion

After creation, suggest:
1. Fill in Overview section with objective and success criteria
2. Add initial tasks
3. Link to relevant goal in `supports_goal` field
4. When ready to start, move to `{{vault_path}}/1-Projects/Current/`
