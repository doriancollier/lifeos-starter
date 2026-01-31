---
name: project-structure
description: Standards for organizing project files and folders. Use when creating projects, organizing project content, or when projects become messy. Provides naming conventions, folder structures, and templates.
---

# Project Structure Skill

Defines standards for organizing projects consistently across the vault. Complements `project-status` skill (which handles lifecycle and health tracking).

## Two-Tier Project Structure

### Tier 1: Simple Projects (Single File)

**When to use:**
- < 15 tasks
- No supporting documents needed
- Short duration (days to weeks)
- Solo work

**Structure:**
```
1-Projects/Current/
└── ProjectName.md          ← Single file IS the project
```

**Example:** `AB-Email-Drip-Campaigns.md`

### Tier 2: Complex Projects (Folder)

**When to use:**
- 15+ tasks OR
- Has supporting documents (research, roadmap, specs) OR
- Multi-month timeline OR
- Multiple collaborators OR
- Has assets (images, PDFs, exports)

**Structure:**
```
1-Projects/Current/
└── ProjectName/
    ├── _ProjectName.md     ← Entry point (REQUIRED)
    ├── roadmap.md          ← Optional
    ├── research.md         ← Optional (or research/ folder)
    ├── decisions.md        ← Optional
    ├── archive.md          ← Optional
    └── assets/             ← Optional
```

**Example:** `AssetOps/_AssetOps.md`

---

## Entry File Convention

### Naming: `_ProjectName.md`

The underscore prefix:
- Sorts first alphabetically (always visible at top)
- Signals "this is the entry point"
- Distinguishes from supporting files

**For simple projects:** The file is just `ProjectName.md` (no underscore needed since it's the only file)

### Required Sections

Every entry file MUST have:

```markdown
---
[Frontmatter]
---

# Project Name

## Overview
**Objective**: [One sentence]
**Success Criteria**: [2-3 bullets]
**Company Context**: [{{company_1_name}} | {{company_2_name}} | EMC | Personal]

## Current Status
### Active Tasks
- [ ] Task 1
- [ ] Task 2

### Blocked
- [ ] 🔵 Task - Waiting for: [reason]

## Tasks
[All project tasks - active and completed]

## Notes
[Running log of decisions, progress, context]

## Related
- [[Goal this supports]]
- [[Key people involved]]
```

### Optional Sections

Add as needed:

```markdown
## Background
[Why this project exists, problem being solved]

## Scope
### In Scope
### Out of Scope

## Supporting Files
| File | Purpose |
|------|---------|
| [[roadmap]] | Detailed phases |

## Timeline
| Milestone | Target | Status |
|-----------|--------|--------|

## Retrospective
[Post-completion reflection]
```

---

## Frontmatter Standard

### Required Fields

```yaml
---
title: "Project Name"
type: "project"
status: "backlog|current|on-hold|completed|cancelled"
company: "{{company_1_name}}|{{company_2_name}}|EMC|Personal"
created: "YYYY-MM-DD"
tags: ["project"]
---
```

### Recommended Fields

```yaml
---
# Core (required above)

# Planning
target_date: "YYYY-MM-DD"           # Soft target
deadline: "YYYY-MM-DD"              # Hard deadline
next_steps: "Brief next action"     # Quick glance

# Progress (auto-calculated if not set)
progress: 0                          # 0-100
health: "on-track"                   # on-track|at-risk|blocked
last_activity: "YYYY-MM-DD"

# Context
supports_goal: "Goal name"           # Links to annual goal
goal_alignment: "high|medium|low"
collaborators: ["[[Person]]"]

# For on-hold projects
hold_reason: "Why paused"
revisit_date: "YYYY-MM-DD"

# For complex projects
entry_point: true                    # Signals this is the main file
---
```

---

## Supporting File Standards

### Standard File Names

| Purpose | File Name | When to Create |
|---------|-----------|----------------|
| Detailed roadmap | `roadmap.md` | Multi-phase projects |
| Research notes | `research.md` | Investigation needed |
| Decision log | `decisions.md` | Major choices to track |
| Archived items | `archive.md` | Long-running projects |
| Transition notes | `YYYY-MM-DD-transition-*.md` | Handoffs |
| Implementation plan | `implementation-plan.md` | Technical projects |
| PRD | `prd.md` | Product features |

### Standard Folder Names

| Purpose | Folder Name | When to Create |
|---------|-------------|----------------|
| Images, PDFs, exports | `assets/` | Has media files |
| Research documents | `research/` | Multiple research files |
| Meeting notes | `meetings/` | Project-specific meetings (rare) |
| Version history | `versions/` | Iterative deliverables |
| Drafts | `drafts/` | Document iterations |

### File Naming Patterns

| Type | Pattern | Example |
|------|---------|---------|
| Dated notes | `YYYY-MM-DD-description.md` | `2026-01-05-kickoff-notes.md` |
| Versioned files | `v1-description.md` | `v1-implementation-plan.md` |
| Person-related | `transition-to-[name].md` | `transition-to-alex.md` |

---

## Auto-Reorganization Triggers

### When to Suggest Restructuring

Suggest converting simple → complex when:
- **> 5 files** in project root
- **> 20 tasks** in single file
- **File exceeds 300 lines**
- **Multiple file types** (md + images + PDFs)

### Reorganization Process

1. Create project folder: `ProjectName/`
2. Rename entry file: `ProjectName.md` → `_ProjectName.md`
3. Move into folder
4. Group related files:
   - Research files → `research/`
   - Assets → `assets/`
   - Old versions → `versions/` or `archive.md`

### Suggested Message

When detecting a messy project:

```
This project has grown to [X files / Y lines]. Consider reorganizing:

1. Create folder: `1-Projects/Current/ProjectName/`
2. Move files into it
3. Rename entry file to `_ProjectName.md`
4. Group: research/ for research, assets/ for media

Would you like me to reorganize this project?
```

---

## Project Type Conventions

### Product/Feature Projects

```
FeatureName/
├── _FeatureName.md         # Overview, tasks
├── prd.md                  # Product requirements
├── implementation-plan.md  # Technical approach
└── assets/                 # Mockups, diagrams
```

### Research Projects

```
ResearchTopic/
├── _ResearchTopic.md       # Summary, findings
├── research/
│   ├── source-1.md
│   ├── source-2.md
│   └── synthesis.md
└── assets/                 # PDFs, exports
```

### Event/Trip Projects

Use existing `trip-planning.md` template in `3-Resources/Templates/`

### Administrative Projects

```
AdminProject/
├── _AdminProject.md        # Checklist, status
├── documents/              # Forms, applications
└── correspondence/         # Emails, letters
```

---

## Meeting Notes Location

**Standard:** Meeting notes stay in `5-Meetings/YYYY/MM-Month/`

**In project file:** Link to meetings, don't embed:

```markdown
## Related Meetings
- [[5-Meetings/2026/01-January/2026-01-05-Project-Kickoff]]
- [[5-Meetings/2026/01-January/2026-01-10-Design-Review]]
```

**Exception:** If a project needs dedicated meeting tracking, use:
```
ProjectName/
├── _ProjectName.md
└── meetings/               # Only for project-specific meetings
    └── YYYY-MM-DD-topic.md
```

---

## Templates Reference

| Template | Location | Purpose |
|----------|----------|---------|
| Simple project | `3-Resources/Templates/Projects/project-simple.md` | Single-file projects |
| Complex entry | `3-Resources/Templates/Projects/project-complex.md` | Folder entry file |
| Roadmap | `3-Resources/Templates/Projects/project-roadmap.md` | Phase planning |
| Retrospective | `3-Resources/Templates/Retrospectives/project-retro.md` | Post-completion review |

---

## Decision Tree: Simple vs Complex

```
Is this project expected to have:
├── 15+ tasks? → Complex (folder)
├── Supporting documents? → Complex (folder)
├── Multiple phases? → Complex (folder)
├── Assets (images, PDFs)? → Complex (folder)
├── Multi-month timeline? → Complex (folder)
├── Multiple collaborators? → Complex (folder)
└── None of the above → Simple (single file)
```

---

## Migration Checklist

When converting existing projects to this standard:

### Simple → Complex Migration
- [ ] Create folder: `ProjectName/`
- [ ] Rename file: `ProjectName.md` → `_ProjectName.md`
- [ ] Move file into folder
- [ ] Update any links in daily notes
- [ ] Add `entry_point: true` to frontmatter

### Standardizing Existing Complex Projects
- [ ] Rename entry file to `_ProjectName.md`
- [ ] Ensure entry file has all required sections
- [ ] Standardize supporting file names
- [ ] Move assets to `assets/` folder
- [ ] Archive old content to `archive.md`
- [ ] Update frontmatter to match standard

---

## Integration with Other Skills

- **project-status**: Handles lifecycle (backlog → current → completed)
- **project-structure** (this): Handles organization and conventions
- **task-system**: Handles task priorities (A/B/C) and due dates
- **task-sync**: Syncs tasks between projects and daily notes

---

## Quick Reference

| Decision | Standard |
|----------|----------|
| Entry file name (folder) | `_ProjectName.md` |
| Entry file name (simple) | `ProjectName.md` |
| Roadmap file | `roadmap.md` |
| Research folder | `research/` |
| Assets folder | `assets/` |
| Date format | `YYYY-MM-DD` |
| Meeting location | `5-Meetings/` (link from project) |
| Reorganize trigger | > 5 files or > 300 lines |
