---
description: Show a comprehensive view of all current projects with progress, health, and activity status
allowed-tools: Read, Glob, Bash, Grep
---

# Project Portfolio Dashboard

Show a comprehensive view of all current projects with progress, health, and activity status.

## Instructions

### Step 1: Gather All Current Projects

```bash
ls -la "{{vault_path}}/1-Projects/Current/"
```

### Step 2: Read Each Project File

For each project found, read the file and extract:
- `title` - Project name
- `company` - Which company/context
- `status` - Should be "current"
- `created` - When project started
- `deadline` or `target_date` - When due (if set)
- `progress` - Percentage complete (if set)
- `health` - on-track/at-risk/blocked (if set)
- `last_activity` - Last update date (if set)

### Step 3: Calculate Progress (if not explicitly set)

For projects without explicit `progress` field:
1. Count total tasks in the project file (lines matching `- [ ]` or `- [x]`)
2. Count completed tasks (lines matching `- [x]`)
3. Calculate: `progress = completed / total * 100`
4. If no tasks found, mark as "No tasks defined"

### Step 4: Determine Health Status

If `health` not explicitly set, calculate:
- **🟢 On Track**: Has recent activity (within 7 days) OR no deadline set
- **🟡 At Risk**: No activity in 7-14 days OR deadline within 7 days with < 70% progress
- **🔴 Blocked**: No activity in 14+ days OR has `blocked:` field set

### Step 5: Calculate Days Until Deadline

For projects with `deadline` or `target_date`:
- Calculate days remaining
- Flag overdue projects in red

### Step 6: Present Dashboard

**Format:**

```markdown
# 📊 Project Portfolio Dashboard

*Generated: [current date/time]*

## Summary
- **Total Active Projects**: X
- **On Track**: X 🟢
- **At Risk**: X 🟡
- **Blocked**: X 🔴
- **Overdue**: X ⚠️

## By Company

### {{company_1_name}}
| Project | Progress | Health | Deadline | Days Left |
|---------|----------|--------|----------|-----------|
| [[Project Name]] | ██████░░░░ 60% | 🟢 | Dec 8 | 5 |

### {{company_2_name}}
| Project | Progress | Health | Deadline | Days Left |
|---------|----------|--------|----------|-----------|
| [[Project Name]] | ████░░░░░░ 40% | 🟡 | Dec 15 | 12 |

### Personal
...

## Attention Needed

### ⚠️ Overdue
- [[Project]] - X days overdue

### 🔴 Blocked
- [[Project]] - Blocked on: [reason]

### 🟡 At Risk
- [[Project]] - No activity in X days

## Stale Projects (14+ days inactive)
- [[Project]] - Last activity: [date]
```

### Step 7: Offer Actions

After presenting the dashboard, offer:
1. "Would you like me to update any project's progress?"
2. "Should I add tasks from any at-risk projects to today's daily note?"
3. "Any projects that should be moved to Completed or Cancelled?"

## Progress Bar Visualization

Use block characters to show progress:
- `██████████` = 100%
- `█████████░` = 90%
- `████████░░` = 80%
- `███████░░░` = 70%
- `██████░░░░` = 60%
- `█████░░░░░` = 50%
- `████░░░░░░` = 40%
- `███░░░░░░░` = 30%
- `██░░░░░░░░` = 20%
- `█░░░░░░░░░` = 10%
- `░░░░░░░░░░` = 0%

## Example Output

```markdown
# 📊 Project Portfolio Dashboard

*Generated: 2025-12-03 10:30 AM*

## Summary
- **Total Active Projects**: 8
- **On Track**: 5 🟢
- **At Risk**: 2 🟡
- **Blocked**: 1 🔴
- **Overdue**: 0 ⚠️

## By Company

### {{company_1_name}}
| Project | Progress | Health | Deadline | Days Left |
|---------|----------|--------|----------|-----------|
| [[AB-New-Wallet-Reports]] | ░░░░░░░░░░ 0% | 🟢 | Dec 8 | 5 |
| [[AB-Email-Drip-Campaigns]] | ░░░░░░░░░░ 0% | 🟢 | Dec 8 | 5 |
| [[AB-Email-Funnel-Capture]] | ░░░░░░░░░░ 0% | 🟢 | Dec 8 | 5 |
| [[AB-Role-Redefinition-Proposal]] | ░░░░░░░░░░ 0% | 🟢 | Dec 11 | 8 |
| [[AB-Layer-2-Integration]] | ░░░░░░░░░░ 0% | 🟢 | — | — |

### Personal
| Project | Progress | Health | Deadline | Days Left |
|---------|----------|--------|----------|-----------|
| [[{{child_name}}-Passport-Renewal]] | ██░░░░░░░░ 20% | 🟡 | — | — |
```
