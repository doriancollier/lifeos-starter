---
name: project-status
description: Track project lifecycle and status across the vault. Use when checking on projects, moving them between stages, or getting an overview of all active work.
---

# Project Status Skill

Manages project lifecycle and provides visibility into project portfolio.

## Project Locations

- **Current**: `1-Projects/Current/` - Active projects being worked on
- **Backlog**: `1-Projects/Backlog/` - Future projects waiting to start
- **Completed**: `1-Projects/Completed/` - Finished projects
- **Cancelled**: `1-Projects/Cancelled/` - Abandoned projects

## Project Lifecycle

```
Backlog → Current → Completed
            ↓
        Cancelled
```

## Finding Projects

### List all current projects
```bash
ls -la "{{vault_path}}/1-Projects/Current/"
```

### List backlog
```bash
ls -la "{{vault_path}}/1-Projects/Backlog/"
```

### Find projects by company
```bash
grep -r "company:.*{{company_1_name}}" "{{vault_path}}/1-Projects/" --include="*.md" -l
```

### Find projects by status
```bash
grep -r "status:.*current" "{{vault_path}}/1-Projects/" --include="*.md" -l
```

## Project Note Structure

```yaml
---
title: "Project Name"
status: "backlog|current|completed|cancelled"
company: "{{company_1_name}}|{{company_2_name}}|EMC|Personal"
created: "YYYY-MM-DD"
target_date: "YYYY-MM-DD"
deadline: "YYYY-MM-DD"          # Hard deadline (if different from target)
completed_date: ""
progress: 0                      # 0-100 percentage (optional, auto-calculated if not set)
health: "on-track"               # on-track|at-risk|blocked (optional, auto-calculated)
last_activity: "YYYY-MM-DD"      # Last meaningful update (optional)
blocked_on: ""                   # Description of blocker (if blocked)
tags: ["project"]
type: "project"
---
```

### Progress Tracking Fields

| Field | Required | Description |
|-------|----------|-------------|
| `progress` | No | 0-100 percentage. Auto-calculated from tasks if not set. |
| `health` | No | `on-track`, `at-risk`, or `blocked`. Auto-calculated if not set. |
| `last_activity` | No | Date of last meaningful progress. Helps detect stale projects. |
| `blocked_on` | No | Description of what's blocking progress. |
| `deadline` | No | Hard deadline date. Use instead of/with `target_date` for firm deadlines. |

### Auto-Calculated Progress

When `progress` is not explicitly set, calculate from tasks in the project file:

```
progress = (completed_tasks / total_tasks) * 100
```

Where:
- `completed_tasks` = count of lines matching `- [x]`
- `total_tasks` = count of lines matching `- [ ]` or `- [x]`

### Auto-Calculated Health

When `health` is not explicitly set:

| Condition | Health |
|-----------|--------|
| `blocked_on` is set | 🔴 Blocked |
| No activity in 14+ days | 🔴 Blocked (stale) |
| No activity in 7-14 days | 🟡 At Risk |
| Deadline within 7 days AND progress < 70% | 🟡 At Risk |
| Recent activity OR no deadline | 🟢 On Track |

## Key Project Directories

### {{company_1_name}} Analytics
Main active project: `1-Projects/Current/Art-Blocks-Analytics/`

Contains:
- `draft-1/` - First draft materials
- `draft-2/` - Second draft materials
- `misc/` - Supporting documents

## Project Status Report Template

```markdown
# Project Portfolio Status

## Current Projects (Active)

| Project | Company | Target | Progress |
|---------|---------|--------|----------|
| [Name] | [Company] | [Date] | [Status] |

## Backlog (Planned)

| Project | Company | Priority |
|---------|---------|----------|
| [Name] | [Company] | [H/M/L] |

## Recently Completed

| Project | Company | Completed |
|---------|---------|-----------|
| [Name] | [Company] | [Date] |

## At Risk

| Project | Issue | Action Needed |
|---------|-------|---------------|
| [Name] | [Blocker] | [Next step] |
```

## Moving Projects

### Start a project (Backlog → Current)
1. Move file from `Backlog/` to `Current/`
2. Update `status: current` in frontmatter
3. Add initial tasks
4. Reference in today's daily note

### Complete a project (Current → Completed)
1. Move file from `Current/` to `Completed/`
2. Update `status: completed` in frontmatter
3. Add `completed_date: YYYY-MM-DD`
4. Write completion notes

### Cancel a project (→ Cancelled)
1. Move file to `Cancelled/`
2. Update `status: cancelled`
3. Document reason for cancellation

## Project Health Checks

### Questions to ask:
- When was the project last touched?
- Are there tasks being completed?
- Is it blocked on something?
- Does target date need adjustment?

### Warning signs:
- No activity in 2+ weeks
- Tasks keep getting carried over
- No clear next action
- Missing target date

## Single Project Query

When asked about a specific project by name:

### 1. Find the Project

```bash
# Search for project file or folder
find "{{vault_path}}/1-Projects" -iname "*[project-name]*" -type f -o -iname "*[project-name]*" -type d
```

### 2. Identify Entry Point

For found project:
- **Simple project** (single file): Read the `.md` file directly
- **Complex project** (folder): Look for `_ProjectName.md` or `README.md` at folder root

```bash
# For folder projects, find entry point
ls "{{vault_path}}/1-Projects/Current/[ProjectName]/" | grep -E "^_.*\.md$|^README\.md$"
```

### 3. Extract Status Information

From the entry file, extract:
- **Frontmatter**: status, company, progress, health, deadline, target_date
- **Tasks**: Count `- [ ]` (open) and `- [x]` (complete)
- **Blockers**: Tasks with 🔵 or "Waiting for:"
- **Last activity**: `last_activity` field or file modification date

### 4. Search Recent Activity

```bash
# Find mentions in last 7 daily notes
grep -l "[ProjectName]" {{vault_path}}/4-Daily/*.md | tail -7
```

### 5. Format Single Project Report

```markdown
# Project: [Name]

**Status**: [status] | **Health**: [health emoji + text] | **Progress**: [X]%
**Company**: [company] | **Deadline**: [date or "None"]

## Current Tasks
- [ ] Task 1
- [ ] Task 2

## Blocked (X items)
- 🔵 Task - Waiting for: [reason]

## Recent Activity
- [Date]: [Activity from daily note]
- [Date]: [Activity from daily note]

## Quick Stats
- Open tasks: X
- Completed tasks: Y
- Days since last activity: Z
- Days until deadline: N (or "No deadline")

## Files
- Entry: [[path/to/entry]]
- Supporting: [list of other files in project folder]
```

### 6. Offer Actions

After displaying status, offer:
1. "Open project in Obsidian?"
2. "Add tasks to today's daily note?"
3. "Update project status?"

---

## Integration

- Projects link to daily notes where work happens
- Projects link to meetings where decisions are made
- Projects link to people involved
- MOCs provide navigation: `7-MOCs/Art-Blocks-Projects.md`, `7-MOCs/144-Projects.md`
- See `project-structure` skill for organization conventions
