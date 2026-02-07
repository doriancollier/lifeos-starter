# Calendar Tagging Convention

This document defines the standard for tagging calendar events created by Claude Code, enabling identification, management, and cleanup of system-generated events.

## Purpose

Calendar tagging allows the system to:

1. **Identify system-created events** - Distinguish from user-created or external events
2. **Enable safe operations** - Delete/update system events without touching real meetings
3. **Feature isolation** - Query events by specific feature (timeboxes, travel, birthdays)
4. **Historical tracking** - Know when and why events were created
5. **Non-destructive rebuilding** - Regenerate planning artifacts while preserving actual commitments

## Technical Implementation

### Extended Properties

Google Calendar supports **extended properties** - metadata invisible to users but accessible programmatically.

| Type | Visibility | Use |
|------|------------|-----|
| `private` | Only visible to creating app | System tracking (use this) |
| `shared` | Visible to all apps | Cross-app coordination (rarely needed) |

### Standard Tags

All Claude Code-created calendar events MUST include these extended properties:

```javascript
extendedProperties: {
  "private": {
    "source": "claude-code",           // REQUIRED: Identifies system origin
    "feature": "[feature-name]",       // REQUIRED: Which feature created it
    "created": "YYYY-MM-DD",           // REQUIRED: Creation date
    "vault_link": "[path]"             // OPTIONAL: Link to source note
  }
}
```

### Feature Values

| Feature | Value | Description |
|---------|-------|-------------|
| Timeboxing | `timebox` | Focus blocks from daily-timebox skill |
| Travel Time | `travel` | Travel time blocks from calendar-management |
| Birthdays | `birthday` | Recurring birthday events |
| Reminders | `reminder` | System-generated reminders |
| Wellness | `wellness` | Break/lunch blocks (subset of timebox) |

### Example: Creating a Tagged Event

```javascript
mcp__google-calendar__create-event with:
- calendarId: "{{user_email}}"
- summary: "[Focus] {{company_1_name}}"
- start: "2025-12-02T09:00:00"
- end: "2025-12-02T11:00:00"
- timeZone: "America/Chicago"
- colorId: "4"
- transparency: "transparent"
- description: "Tasks:\n- Review PRs\n- Update analytics dashboard"
- extendedProperties: {
    "private": {
      "source": "claude-code",
      "feature": "timebox",
      "created": "2025-12-02",
      "vault_link": "4-Daily/2025-12-02.md"
    }
  }
```

## Querying Tagged Events

### Find All System-Created Events

```javascript
mcp__google-calendar__list-events with:
- calendarId: "{{user_email}}"
- privateExtendedProperty: ["source=claude-code"]
```

### Find Specific Feature Events

```javascript
// Find all timeboxes
privateExtendedProperty: ["source=claude-code", "feature=timebox"]

// Find all travel time blocks
privateExtendedProperty: ["source=claude-code", "feature=travel"]

// Find all birthdays
privateExtendedProperty: ["source=claude-code", "feature=birthday"]
```

### Find Events Created on Specific Date

```javascript
privateExtendedProperty: ["source=claude-code", "created=2025-12-02"]
```

## Rules Enabled by Tagging

### Rule 1: Never Delete Untagged Events

```
IF event lacks `private.source=claude-code`:
  → Treat as user-created or external
  → REQUIRE explicit confirmation before any modification
  → NEVER delete without user approval
```

### Rule 2: Safe Rebuild

```
IF user requests "update timeboxes" or "reschedule my day":
  → Query events with `feature=timebox` AND future start time
  → Only delete/update those events
  → Real meetings and external events remain untouched
```

### Rule 3: Historical Preservation

```
IF event start time < current time:
  → Do not delete (it's historical record)
  → Only modify future events when rebuilding
```

### Rule 4: Feature-Specific Cleanup

```
IF user requests "remove all travel time blocks":
  → Query `feature=travel`
  → Delete only matching events
  → Other system events (timeboxes, birthdays) unaffected
```

## Feature-Specific Standards

### Timeboxes (daily-timebox skill)

```javascript
extendedProperties: {
  "private": {
    "source": "claude-code",
    "feature": "timebox",
    "created": "YYYY-MM-DD",
    "vault_link": "4-Daily/YYYY-MM-DD.md"
  }
}
```

Additional settings:
- `transparency: "transparent"` (doesn't block availability)
- Summary format: `[Focus] Project Name` or `[Break] Type`
- Color coding by project context

### Travel Time (calendar-management skill)

```javascript
extendedProperties: {
  "private": {
    "source": "claude-code",
    "feature": "travel",
    "created": "YYYY-MM-DD",
    "linked_event": "[event-id]"  // Optional: links to the event being traveled to
  }
}
```

Additional settings:
- `colorId: "7"` (Peacock)
- Summary format: `Travel to [Event]` or `Return from [Event]`

### Birthdays (birthday-awareness skill)

```javascript
extendedProperties: {
  "private": {
    "source": "claude-code",
    "feature": "birthday",
    "created": "YYYY-MM-DD",
    "person_file": "6-People/[path]/[name].md"  // Optional: links to person file
  }
}
```

Additional settings:
- `colorId: "9"` (Blueberry)
- `recurrence: ["RRULE:FREQ=YEARLY"]`
- All-day event format
- Summary format: `🎂 [Person Name]'s Birthday`

## Context Windows (User-Created Guidance Events)

Context windows are **user-created** calendar events that guide timeboxing behavior. Unlike system-created events (which use extended properties), context windows are identified by their **name and transparency setting**.

### Identifying Context Windows

An event is a context window if it meets BOTH criteria:

1. **Name contains a keyword**: `Focus`, `Window`, or `Time` (case-insensitive)
2. **Transparency is `transparent`**: Event doesn't block availability

### Why Name-Based (Not Property-Based)?

Extended properties can only be set via API, not the Google Calendar web interface. Since users create context windows manually, we use a naming convention they can easily apply.

### Context Window Behavior

| Event Name Pattern | Extracted Company | Timebox Behavior |
|-------------------|-------------------|------------------|
| `AB Focus` / `AB Window` / `AB Time` | {{company_1_name}} | AB tasks scheduled HERE |
| `144 Focus` / `144 Window` / `144 Time` | {{company_2_name}} | 144 tasks scheduled HERE |
| `EMC Focus` / `EMC Window` / `EMC Time` | {{company_3_name}} | EMC tasks scheduled HERE |
| `Personal Focus` / `Personal Time` | Personal | Personal tasks scheduled HERE |
| `Open Focus` / `Open Window` / `Open Time` | Any/Flexible | Catch-all for any work |
| `Wind Down` | Special | Light/no scheduling |

### Parsing Logic

1. Check if event summary contains "Focus", "Window", or "Time"
2. Verify event has `transparency: transparent`
3. Extract prefix before the keyword (e.g., "AB" from "AB Focus")
4. Map prefix to company context

### Scheduling Rules

| Task Company | Scheduling Behavior |
|--------------|---------------------|
| {{company_1_name}} | Schedule WITHIN `AB Focus/Window/Time` |
| {{company_2_name}} | Schedule WITHIN `144 Focus/Window/Time` or `Open Focus` |
| EMC | Schedule WITHIN `EMC Focus/Window/Time` or `Open Focus` |
| Personal | Schedule in `Open Focus` or gaps, avoid company windows |
| Wellness | Can overlay ANY window (lunch, breaks are exceptions) |

### Example

```
User's Calendar:
- 9:30 AM - 1:30 PM: "AB Focus" (transparency: transparent)
- 2:00 PM - 4:00 PM: "Open Focus" (transparency: transparent)

Tasks to timebox:
- [AB] Review PRs
- [AB] Update dashboard
- [144] Write proposal

Result:
- AB tasks → scheduled within AB Focus (9:30-1:30)
- 144 tasks → scheduled within Open Focus (2:00-4:00)
- Lunch break → can overlay AB Focus at 12:00
```

---

## Migration Notes

### Existing Timeboxes

The daily-timebox skill previously used only `timebox=true`. Events with this legacy tag should still be recognized:

```javascript
// Query that catches both old and new format
privateExtendedProperty: ["timebox=true"]
// OR
privateExtendedProperty: ["feature=timebox"]
```

New timeboxes should use the full standard. Legacy events will be updated over time.

## Maintenance

### Cleanup Stale System Events

To remove all system-created events older than N days:

1. Query: `privateExtendedProperty: ["source=claude-code"]`
2. Filter: `created < (today - N days)`
3. Delete matching events

### Audit System Events

Periodically review system-created events:

1. Query all `source=claude-code` events
2. Group by `feature`
3. Identify orphaned events (linked vault files deleted, etc.)

## Related Documentation

- [Calendar Management Skill](.claude/skills/calendar-management/SKILL.md)
- [Daily Timebox Skill](.claude/skills/daily-timebox/SKILL.md)
- [Birthday Awareness Skill](.claude/skills/birthday-awareness/SKILL.md)
- [CLAUDE.md Calendar Integration Section](../../../CLAUDE.md#calendar-integration)
