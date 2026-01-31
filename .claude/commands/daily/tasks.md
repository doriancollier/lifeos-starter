---
description: Review open tasks across recent daily notes
allowed-tools: Read, Grep, Glob, Bash
---

# Tasks Review Command

Review all open tasks across recent daily notes, organized by priority and company.

## Context

- **Daily notes directory**: `{{vault_path}}/4-Daily/`
- **Today's date**: !`date +%Y-%m-%d`

## Task

1. **Find recent daily notes** (last 7 days)
2. **Extract all incomplete tasks** (lines matching `- [ ]`)
3. **Organize by priority**:
   - 🔴 A Priority (Critical) - numbered 1-5
   - 🟡 B Priority (Important)
   - 🟢 C Priority (Nice-to-have)
   - 🔵 Blocked - note what's blocking
4. **Group by company** when possible ({{company_1_name}}, {{company_2_name}}, EMC, Personal)
5. **Check for due dates** — Tasks with `📅 YYYY-MM-DD` should be flagged if overdue
6. **Identify patterns**:
   - Tasks that have been carried over multiple days
   - Blocked tasks that might be unblocked now
   - Overdue tasks (due date < today)

## Output Format

```markdown
## Open Tasks Summary

### 🔴 Critical (A Priority)
- [ ] Task 1 - Company - From: [date]
- [ ] Task 2 - Company - From: [date]

### 🟡 Important (B Priority)
- [ ] Task - Company - From: [date]

### 🟢 Nice-to-have (C Priority)
- [ ] Task - Company - From: [date]

### 🔵 Blocked
- [ ] Task - Waiting for: [blocker] - Since: [date]

### 📅 Due Soon / Overdue
- [ ] Task 📅 2025-12-10 - [OVERDUE by X days] or [Due in X days]

### Patterns & Alerts
- [Any tasks carried over 3+ days]
- [Blocked items that may be resolved]
- [Overdue tasks that need immediate attention]
```

## Notes

- Focus on actionable insights
- Highlight tasks that need attention
- Suggest which blocked tasks to follow up on
- For detailed due date analysis, use `/vault-tasks:due` command
