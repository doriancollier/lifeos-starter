---
title: "Task Management Guide"
created: "2025-12-02"
status: "active"
---

# Task Management Guide

The A/B/C priority system and task patterns in LifeOS.

## The Priority System

LifeOS uses emoji-based priority indicators for visual scanning:

| Priority | Symbol | Meaning | Daily Limit | Numbering |
|----------|--------|---------|-------------|-----------|
| **A** | 🔴 | Must complete today | Max 5 | Numbered 1-5 by urgency |
| **B** | 🟡 | Should complete today | No limit | None |
| **C** | 🟢 | Nice to have | No limit | None |
| **Blocked** | 🔵 | Waiting on external | N/A | None |
| **Due Date** | 📅 | Has deadline | N/A | ISO format |

### Why This System?

1. **Visual Priority** — Emoji scanning is instant
2. **Forced Constraint** — Max 5 A-tasks prevents overcommitment
3. **Numbered Urgency** — A1 > A2 > A3 creates clear order
4. **Company Context** — Every task tied to a company for context switching

## Task Format

### Standard Task Syntax

```markdown
- [ ] 🔴1. Task description - Company: {{company_1_name}}
- [ ] 🔴2. Second priority task - Company: {{company_2_name}}
- [ ] 🟡 Important but not critical - Company: Personal
- [ ] 🟢 Nice to have task
- [ ] 🔵 Blocked task - Waiting for: Alex's feedback
- [ ] 🟡 Future task 📅 2025-12-15
```

### Completed Tasks

```markdown
- [x] 🔴1. Completed critical task - Company: {{company_1_name}}
- [x] 🟡 Completed important task - Company: Personal
```

### With Subtasks

```markdown
- [ ] 🔴1. Main task - Company: Personal
  - [x] Subtask completed
  - [x] Another subtask done
  - [ ] Subtask remaining
```

## Company Context

**Every work task should identify its company**:

| Company | Tag | Context |
|---------|-----|---------|
| {{company_1_name}} | `Company: {{company_1_name}}` | Configure during onboarding |
| {{company_2_name}} | `Company: {{company_2_name}}` | Configure during onboarding |
| {{company_3_name}} | `Company: {{company_3_name}}` | Configure during onboarding |
| Personal | `Company: Personal` | Family, health, personal |

### Why Context Matters

1. **Context Switching** — Know what hat you're wearing
2. **Filtering** — Find all tasks for a specific company
3. **Timeboxing** — Tasks get scheduled to appropriate focus windows
4. **Reporting** — See time allocation across companies

## Task Lifecycle

```
┌─────────────┐
│  New Task   │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  A/B/C Priority Set  │
└──────┬───────────────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌──────────────┐  ┌───────────┐
│  In Progress │  │  Blocked  │
└──────┬───────┘  │    🔵     │
       │          └─────┬─────┘
       │                │
       │          (blocker resolved)
       │                │
       ▼                ▼
┌──────────────────────────┐
│       Completed ✓        │
└──────────────────────────┘
       │
       │ (if not completed)
       ▼
┌──────────────────────────┐
│   Moved to Tomorrow      │
└──────────────────────────┘
```

## Daily Task Sections

Tasks appear in multiple sections of daily notes:

### 1. Today's Task Overview

The main task list organized by priority:

```markdown
## Today's Task Overview

### A Priority (Must Do)
- [ ] 🔴1. First priority - Company: {{company_1_name}}
- [ ] 🔴2. Second priority - Company: {{company_2_name}}

### B Priority (Should Do)
- [ ] 🟡 Important task - Company: Personal
- [ ] 🟡 Another important one - Company: {{company_1_name}}

### C Priority (Nice to Have)
- [ ] 🟢 Optional task
- [ ] 🟢 If time permits

### Blocked
- [ ] 🔵 Waiting on Alex - Company: {{company_1_name}}

### Due This Week
- [ ] 🟡 Call insurance 📅 2025-12-10
- [ ] 🔴1. Submit proposal 📅 2025-12-15
```

### 2. Company Context Sections

Priority tasks by company for focused work:

```markdown
## Company: {{company_1_name}}
- **Active projects**: [[Project-1]], [[Project-2]]
- **Priority tasks**:
  - [ ] 🔴1. Finish feature review
  - [ ] 🟡 Review PR comments
```

### 3. Task Review (End of Day)

Summarizes what happened:

```markdown
## Task Review

### Completed
- [x] 🔴1. Analytics review
- [x] 🟡 Team sync prep

### Moved to Tomorrow
- [ ] 🔴2. Documentation update

### Still Blocked
- [ ] 🔵 API integration - Waiting for: Matt
```

## Setting A-Priority Tasks

### The Morning Decision

During `/daily:plan`, you'll choose your A-priorities:

1. **Review carryovers** — What didn't get done yesterday?
2. **Check calendar** — What meetings constrain your time?
3. **Energy check** — High energy = more A-tasks
4. **Select 3-5 tasks** — The truly critical ones
5. **Number by urgency** — A1 is THE most important

### Signs of Too Many A-Tasks

- More than 5 A-tasks
- Most days with incomplete A-tasks
- Everything feels "critical"
- Unable to finish A1 before lunch

### Right-Sizing Your Day

| Energy Level | Suggested A-Tasks | B-Tasks |
|--------------|-------------------|---------|
| High | 4-5 | 5-7 |
| Medium | 3-4 | 3-5 |
| Low | 2-3 | 2-3 |

## Blocked Tasks

### When to Mark Blocked

Use 🔵 when you literally cannot proceed:
- Waiting for someone's input
- Waiting for an external event
- Waiting for a dependency

### Format

```markdown
- [ ] 🔵 Task description - Waiting for: [specific blocker]
```

### Unblocking

During `/daily:plan`, blocked tasks are reviewed:
- Is the blocker resolved?
- Should this become an A-task today?
- Is there a workaround?

## Due Dates

### When to Use Due Dates

Add `📅 YYYY-MM-DD` to any task with a deadline:
- Hard deadlines
- Appointments (also create calendar event)
- Future follow-ups

### Format

```markdown
# Due date annotation (can combine with any priority)
- [ ] 🟡 Call insurance about prescription 📅 2025-12-10
- [ ] 🔴1. Submit proposal to client 📅 2025-12-15
- [ ] 🔵 Wait for callback - Waiting: Texas Diabetes 📅 2025-12-10
```

### Why ISO Format?

The `📅 YYYY-MM-DD` format is:
1. **Machine-parseable** — grep and Python can query without external libraries
2. **Sortable** — alphabetically = chronologically
3. **Unambiguous** — no "Dec 5" vs "5 Dec" confusion
4. **Obsidian Tasks compatible** — works with popular plugins

### Querying Due Dates

Use `/vault-tasks:due` to see all tasks organized by due date, or query directly:

```bash
# Tasks due today
grep -rn "📅 $(date +%Y-%m-%d)" 4-Daily/*.md | grep "\- \[ \]"

# All tasks with due dates
grep -rEn "📅 [0-9]{4}-[0-9]{2}-[0-9]{2}" 4-Daily/*.md
```

## Finding Tasks

### Common Searches

| Find | Command |
|------|---------|
| All incomplete today | `grep "^- \[ \]" 4-Daily/$(date +%Y-%m-%d).md` |
| All A-priority tasks | `grep "^- \[ \] 🔴" 4-Daily/*.md` |
| All blocked tasks | `grep "^- \[ \] 🔵" 4-Daily/*.md` |
| Tasks with due dates | `grep -E "📅 [0-9]{4}-[0-9]{2}-[0-9]{2}" 4-Daily/*.md` |
| Tasks for {{company_1_name}} | `grep "Company: {{company_1_name}}" 4-Daily/*.md` |
| Completed today | `grep "^- \[x\]" 4-Daily/$(date +%Y-%m-%d).md` |

### Using `/daily:tasks`

The command shows open tasks across recent daily notes:
```
/daily:tasks
```

## Best Practices

### Do

1. **Set A-priorities each morning** — Use `/daily:plan`
2. **Work A1 first** — Most important gets done first
3. **Include company context** — Know what context you're in
4. **Use subtasks** — Break down large tasks
5. **Move incomplete tasks** — Don't leave them orphaned
6. **Specify blockers** — "Waiting for X" not just "blocked"

### Don't

1. **Don't have 10 A-tasks** — Max 5, ideally 3-4
2. **Don't leave tasks without context** — Add `Company: X`
3. **Don't hoard blocked tasks** — Actively unblock or drop them
4. **Don't overuse due dates** — Only truly date-specific items need 📅
5. **Don't number B/C tasks** — Only A-tasks get numbers

## Integration with Other Features

### Timeboxing

A and B priority tasks get scheduled as focus blocks via `/daily:timebox`:
- Tasks grouped by company/project
- Placed in appropriate focus windows
- C-priority tasks are not timeboxed

### Work Logging

As you complete work, the `work-logging` skill:
- Adds subtasks under parent tasks
- Checks off completed items
- Logs progress to Quick Notes

### Meeting Prep

Tasks involving people can reference person files:
```markdown
- [ ] 🔴1. Review analytics with [[Alex Smith]] - Company: {{company_1_name}}
```

### Task Cross-Linking

Tasks can exist in multiple locations with cross-references to maintain traceability.

#### When to Cross-Link

| Source | Also Track In | Cross-Link Pattern |
|--------|---------------|-------------------|
| Meeting → Daily | Task needs active tracking | `[[meeting#Action Items\|from Meeting Name]]` |
| Meeting → Project | Project-specific work | `Source: [[meeting-note]]` |
| Daily → Project | Long-running task | `[[project#Tasks]]` |

#### Cross-Link Syntax

**In daily note** (task from meeting):
```markdown
- [ ] 🟡 Create dashboards - Company: {{company_1_name}} - [[meeting#Action Items|from Product Sync]]
```

**In project file** (task from meeting):
```markdown
- [ ] Create dashboards - Source: [[2025-12-03-product-sync/meeting]]
```

**In meeting note** (task already tracked):
```markdown
### Already Tracked Elsewhere
- Push scheduling updates → [[2025-12-03#🔴2]]
```

#### Deduplication Rule

**Don't duplicate tasks** — When a task already exists:
1. Reference the existing task with `→ Tracked in [[location]]`
2. Don't create a new checkbox
3. If context is needed, add a Quick Note instead

## Task Sync

When tasks are edited in either daily notes or project files, the **Task Sync System** ensures consistency between both locations.

### How It Works

1. **Real-time detection** — PostToolUse hook detects task changes
2. **Queue for processing** — Changes written to sync queue
3. **Reconciliation** — task-sync skill matches and updates both files

### When to Sync

- After editing tasks in projects or daily notes
- When session start shows pending syncs
- Proactively: "sync my tasks"

See [[task-sync|Task Sync Guide]] for full documentation.

## Related Guides

- [[daily-workflow|Daily Workflow]] — Full day-to-day process
- [[calendar-integration|Calendar Integration]] — Timeboxing tasks
- [[task-sync|Task Sync Guide]] — Bidirectional task synchronization
