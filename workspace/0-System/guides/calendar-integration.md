---
title: "Calendar Integration Guide"
created: "2025-12-02"
status: "active"
---

# Calendar Integration Guide

Smart scheduling, timeboxing, and calendar awareness in LifeOS.

## Overview

LifeOS integrates with Google Calendar via MCP to provide:
- Schedule awareness during planning
- Timeboxed focus blocks for tasks
- Birthday and holiday detection
- Event creation and management

## Available Calendars

**Configuration file**: `.user/calendars.yaml`

### Checked for Availability

These calendars are checked before creating any event:

| Calendar | Purpose |
|----------|---------|
| `{{user_email}}` | Primary (timeboxes go here) |
| `{{child_calendar}}` | {{child_name}} schedule |
| `{{work_email}}` | {{company_1_name}} work |
| `{{family_calendar}}` | Family events |
| `{{company_3_email}}` | {{company_3_name}} business |

### Reference Only (not checked for availability)

| Calendar | Purpose |
|----------|---------|
| `en.usa#holiday@group.v.calendar.google.com` | US Holidays |
| Trash Schedule | Utility reminders |

> **Note**: Edit `.user/calendars.yaml` to change which calendars are checked for conflicts.

## Timeboxing

### What is Timeboxing?

Timeboxing creates calendar focus blocks for your tasks, turning your to-do list into a structured schedule.

### Quick Start

```
/daily:timebox
```

Or during morning planning:
```
/daily:plan
```
(Timeboxing happens at the end)

### How It Works

1. **Read tasks** from today's daily note (A + B priority only)
2. **Group by project/company** — All AB tasks together, all 144 tasks together
3. **Estimate durations** — Based on task count and complexity
4. **Check calendar** — Find gaps around real meetings
5. **Match to context windows** — Schedule tasks in appropriate time blocks
6. **Create focus blocks** — As transparent calendar events
7. **Add wellness breaks** — Lunch, afternoon break

### Focus Block Format

```
Summary: [Focus] {{company_1_name}}
Description:
  Tasks:
  - Review PRs
  - Update analytics dashboard
Color: Flamingo (4)
Transparency: Transparent (doesn't block availability)
```

### Color Coding

| Context | Color | Color ID |
|---------|-------|----------|
| {{company_1_name}} | Flamingo | 4 |
| {{company_2_name}} | Banana | 5 |
| Personal | Lavender | 1 |
| {{company_3_name}} | Grape | 3 |
| Breaks/Wellness | Sage | 2 |

### Wellness Blocks

Built-in wellness blocks are **non-negotiable** and always included:

| Block | Default Time | Duration | Notes |
|-------|-------------|----------|-------|
| Lunch | 12:00 PM - 1:00 PM | 1 hour (30 min min) | Shifts around meetings, never skipped |
| Movement | 1:00 PM - 1:20 PM | 20 min | Post-lunch walk, aids digestion |
| Afternoon Reset | 3:00 PM - 3:20 PM | 20 min | Stretch, walk, fresh air |
| Short Breaks | Between blocks | 5-10 min | When back-to-back focus blocks |

**Key rule**: Wellness blocks are scheduled FIRST, then work fills remaining time.

## Context Windows

### What are Context Windows?

Context windows are calendar events YOU create to indicate when you want to focus on specific work. Timeboxes respect these windows when scheduling.

### Creating Context Windows

Create transparent all-day or timed events with these names:

| Event Name | Tasks Scheduled Here |
|------------|---------------------|
| `AB Focus` | {{company_1_name}} tasks |
| `AB Window` | {{company_1_name}} tasks |
| `144 Focus` | {{company_2_name}} tasks |
| `EMC Window` | {{company_3_name}} tasks |
| `Open Focus` | Any tasks (catch-all) |
| `Wind Down` | Light/no scheduling |

### Recognition Rules

An event is a context window if:
1. Name contains `Focus`, `Window`, or `Time`
2. Transparency is `transparent`

### Example Schedule

```
Calendar has:
- 9:30 AM - 1:30 PM: "AB Focus" (transparent)
- 2:00 PM - 4:00 PM: "Open Focus" (transparent)

Tasks:
- [AB] Review PRs
- [AB] Update dashboard
- [Personal] Call doctor
- [144] Write proposal

Scheduled result:
- 9:30-11:00: [Focus] {{company_1_name}} (Review PRs, Update dashboard)
- 12:00-1:00: [Break] Lunch
- 2:00-3:00: [Focus] {{company_2_name}} (Write proposal)
- 3:00-3:30: [Focus] Personal (Call doctor)
```

## Calendar Awareness

### During Daily Planning

When you run `/daily:plan`, the system:

1. **Fetches today's calendar** — All events from all calendars
2. **Surfaces meetings** — Shows time, attendees, location
3. **Checks for birthdays** — All-day events with "birthday"
4. **Checks holidays** — 14-day lookahead on US Holidays calendar
5. **Checks trips/events** — Surfaces approaching trips from projects

### Birthday Detection

```
/daily:plan checks 7 days ahead for birthdays

🎂 Birthdays This Week
| Day | Person | Days Away |
|-----|--------|-----------|
| Thu | John Smith | 4 days |
| Sun | Jane Doe | 7 days |
```

### Holiday Awareness

Major holidays (Thanksgiving, Christmas, etc.) get prominent reminders:

```
🦃 Thanksgiving is in 5 days (Thursday, Nov 27)
- Most offices will be closed
- Consider: travel plans, grocery shopping
```

Gift-giving holidays include shopping reminders:
```
🎄 Christmas is in 12 days
- Gift shopping/shipping needed?
```

## Event Management

### Creating Events

The `calendar-management` skill handles event creation with smart defaults:
- Appropriate calendar selection based on context
- Travel time buffers
- Attendee suggestions

### Event Protection

The `calendar-protection` hook prevents accidental damage:

- **Confirms before deleting** any event
- **Extra warning** for recurring events
- **Notes when attendees will be notified**
- **Never deletes** events without confirmation

### Event Tagging

System-created events include tags for identification:

```javascript
extendedProperties: {
  "private": {
    "source": "claude-code",
    "feature": "timebox",  // or "birthday", "travel"
    "created": "2025-12-02"
  }
}
```

This enables:
- Safe cleanup (only affects system events)
- Feature-specific queries
- Protection of real meetings

## Updating Timeboxes

### How Updates Work

When you re-run `/daily:timebox`:

1. **Find existing timeboxes** — Uses system tags
2. **Identify past vs future** — Compares to current time
3. **Leave past untouched** — Historical record preserved
4. **Update future only** — Replaces with new schedule

### Safe Operations

The system only modifies events with `source=claude-code` tag. Real meetings are never touched.

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/daily:timebox` | Create/update focus blocks |
| `/daily:plan` | Full planning (includes timeboxing) |

## Skills Reference

| Skill | Purpose |
|-------|---------|
| `daily-timebox` | Create focus blocks from tasks |
| `calendar-awareness` | Surface schedule during planning |
| `calendar-management` | Create and modify events |
| `birthday-awareness` | Detect and manage birthday events |

## Best Practices

### Do

1. **Create context windows** — Guide where work happens
2. **Keep A-tasks realistic** — Timeboxing reveals overcommitment
3. **Include breaks** — Wellness blocks are there for a reason
4. **Update when tasks change** — Re-run timebox after completing work
5. **Use color coding** — Visual separation helps

### Don't

1. **Don't skip lunch** — Wellness blocks matter
2. **Don't timebox C-tasks** — Only A + B priority
3. **Don't ignore the schedule** — Timeboxes work when followed
4. **Don't manually delete timeboxes** — Let the system manage them

## Integration with Other Features

### Task Management

Timeboxing reads from your daily note's task sections:
- A Priority (🔴) — Gets scheduled first
- B Priority (🟡) — Fills remaining time
- C Priority (🟢) — NOT timeboxed

### Meeting Prep

When calendar shows meetings:
- `/meeting:prep` can prepare context
- Meeting notes can be created with `/meeting:*`

### Daily Planning

Full workflow integration:
```
/daily:plan includes:
├── Calendar check (meetings today)
├── Holiday awareness (14-day)
├── Birthday check (7-day)
├── Task prioritization
└── Timeboxing (at the end)
```

## Troubleshooting

### Timeboxes Not Appearing

1. Check you have tasks in A or B priority
2. Ensure calendar MCP is connected
3. Try `/daily:timebox` directly

### Wrong Calendar

Timeboxes go to primary calendar (`{{user_email}}`). Other calendars are read-only for timeboxing.

### Events Not Deleted

System only deletes events with `source=claude-code` tag. Manually created events are protected.

### Authentication Expired

When you see errors like:
- `invalid_grant`
- `Authentication token is invalid or expired`
- `Please re-run the authentication process`

**To re-authenticate:**

```bash
GOOGLE_OAUTH_CREDENTIALS="{{vault_path}}/gcp-oauth.keys.json" npx -y @cocal/google-calendar-mcp auth
```

This opens a browser for Google OAuth. Complete the flow and the MCP will work again.

> **Note**: The `-y` flag auto-confirms npx installation. Account name is optional (defaults to `normal`).

**Key details:**
| Item | Value |
|------|-------|
| MCP Package | `@cocal/google-calendar-mcp` |
| OAuth Credentials | `{{vault_path}}/gcp-oauth.keys.json` |
| Token Storage | `~/.config/google-calendar-mcp/tokens.json` |
| Account Name | `normal` |

**When to use:**
- After any auth error from calendar MCP
- If tokens haven't been refreshed in a long time
- Don't search for the MCP server location - just run the npx command above

## Related Guides

- [[daily-workflow|Daily Workflow]] — Full planning process
- [[task-management|Task Management]] — Priority system
