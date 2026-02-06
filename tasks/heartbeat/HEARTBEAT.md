# LifeOS Heartbeat Checklist

This document defines the checks performed during each heartbeat cycle.
Claude evaluates this checklist against current vault state.

## Instructions

You are performing a periodic heartbeat check of the LifeOS vault.
Your task is to quickly assess the current state and report any issues.

**Evaluation Rules:**
1. Only report NEW or WORSENED conditions compared to previous state
2. Don't alert on suppressed items (check suppressed list)
3. Be concise - this runs frequently and should be fast
4. Focus on actionable issues, not general observations

---

## Checklist

### 1. Daily Note Status
- [ ] Daily note exists for today
- [ ] No overdue A-priority tasks (🔴 tasks from previous days)

**Check:** `workspace/4-Daily/YYYY-MM-DD.md`

### 2. Upcoming Meetings
- [ ] Meetings in next 30 minutes have prep notes or context gathered
- [ ] No calendar conflicts in next 2 hours

**Check:** Query calendar for upcoming events, check `workspace/5-Meetings/` for prep

### 3. Project Health
- [ ] No projects past their deadline
- [ ] No stalled projects (no activity in 14+ days)

**Check:** `workspace/1-Projects/Current/` for deadline and last-modified

### 4. Inbox Status
- [ ] Inbox has fewer than 10 items awaiting processing

**Check:** Count files in `workspace/0-Inbox/`

### 5. Task Sync
- [ ] No pending task syncs between daily notes and projects

**Check:** `state/task-sync-pending.json` or equivalent state file

### 6. Energy Check (if health integration enabled)
- [ ] No critically low energy indicators from recent health data

**Check:** `data/health/` for recent imports

---

## Output Format

Respond with this exact structure:

```
STATUS: OK | ALERT | CHANGED

ALERTS:
- [Issue description with severity]
- [Another issue if any]

STATE_CHANGES:
- field_name: old_value -> new_value
```

**STATUS values:**
- `OK` - All checks passed, no changes
- `ALERT` - One or more issues require attention
- `CHANGED` - No alerts, but state changed (for tracking)

**Example output:**

```
STATUS: ALERT

ALERTS:
- 2 overdue A-tasks from yesterday (high priority)
- Meeting with John in 25 min has no prep notes

STATE_CHANGES:
- a_tasks: 3 -> 5
- inbox_count: 8 -> 12
```
