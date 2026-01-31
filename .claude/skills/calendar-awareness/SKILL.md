---
name: calendar-awareness
description: Proactive calendar awareness for holidays and schedule overview. Use at week start, during planning, or when user asks about schedule. For birthday-specific queries, delegate to birthday-awareness skill.
allowed-tools: Read, Grep, Glob, Bash, mcp__google-calendar__list-events, mcp__google-calendar__search-events, mcp__google-calendar__get-current-time
---

# Calendar Awareness Skill

Provides proactive awareness of calendar events, holidays, and schedule overview.

## ⚠️ Authentication Recovery

**If any calendar MCP tool returns an auth error** (`invalid_grant`, `token expired`, `Authentication token is invalid`):

**Immediately run this command** — do NOT search for MCP locations:

```bash
GOOGLE_OAUTH_CREDENTIALS="{{vault_path}}/gcp-oauth.keys.json" npx -y @cocal/google-calendar-mcp auth
```

This opens a browser for OAuth. Wait for completion, then retry.

---

## Skill Boundaries

| Responsibility | This Skill | Other Skill |
|----------------|------------|-------------|
| Holiday awareness | ✅ | - |
| Schedule overview | ✅ | - |
| Weekly calendar view | ✅ | - |
| Birthday detection | ❌ | `birthday-awareness` |
| Birthday event creation | ❌ | `birthday-awareness` |
| Event CRUD operations | ❌ | `calendar-management` |
| Timeboxed focus blocks | ❌ | `daily-timebox` |

> **Note**: For birthday-related queries, delegate to the `birthday-awareness` skill which handles detection, event creation, and person file updates.

## When to Activate

- **Monday sessions**: Check upcoming week for holidays and important dates
- **Daily planning**: Surface today's calendar events
- **User asks about schedule**: Query relevant calendars
- **Meeting prep**: Check for calendar event details

## Key Calendars

| Calendar ID | Purpose |
|-------------|---------|
| `{{user_email}}` | Primary personal calendar |
| `{{work_email}}` | {{company_1_name}} work |
| `{{family_calendar}}` | Family events |
| `{{child_calendar}}` | {{child_name}} schedule |
| `{{company_3_email}}` | {{company_3_name}} business |
| `en.usa#holiday@group.v.calendar.google.com` | US Holidays |

## Birthday Handling

> **Delegated**: Birthday detection and management is handled by the `birthday-awareness` skill.
>
> If birthdays come up during schedule queries, note them but delegate detailed birthday work (event creation, person file updates) to that skill.

When birthdays appear in calendar results, simply include them in the schedule summary:

```markdown
### Thursday - Also 🎂 Mom's Birthday
```

## Holiday Awareness

US Holidays are in calendar: `en.usa#holiday@group.v.calendar.google.com`

### Checking for Holidays

```
Use mcp__google-calendar__list-events with:
- calendarId: en.usa#holiday@group.v.calendar.google.com
- timeMin: today
- timeMax: 14 days from today
- timeZone: America/Chicago
```

### Major Holidays (Require 14-Day Advance Notice)

| Holiday | Type | Considerations |
|---------|------|----------------|
| **Thanksgiving** | Public + Family | Offices closed, travel, groceries, family coordination |
| **Christmas Day** | Public + Gift | Offices closed, gifts, shipping deadlines, family |
| **New Year's Day** | Public | Offices closed, plans for NYE |
| **Independence Day** | Public | Offices closed, fireworks, BBQ plans |
| **Memorial Day** | Public | Offices closed, unofficial start of summer |
| **Labor Day** | Public | Offices closed, end of summer |
| **Christmas Eve** | Observance + Gift | Many leave early, last-minute prep |
| **New Year's Eve** | Observance | Plans, reservations |

### Gift-Giving Holidays

These require extra lead time for shopping/shipping:
- **Christmas** (Dec 25) - Remind 2-3 weeks ahead
- **Valentine's Day** (Feb 14) - Remind 1-2 weeks ahead
- **Mother's Day** (2nd Sunday May) - Remind 2 weeks ahead
- **Father's Day** (3rd Sunday June) - Remind 2 weeks ahead

### Holiday Alert Format

**Major holiday within 3 days:**
```
🦃 **REMINDER: Thanksgiving is THURSDAY**
- Most offices closed Thu-Fri
- Do you have everything ready?
```

**Major holiday within 14 days:**
```
🎄 Christmas is in 12 days (Thursday, Dec 25)
- Gift shopping/shipping status?
- Travel plans confirmed?
```

**Observance:**
```
📅 Also upcoming: Black Friday (Nov 28)
```

### Holiday Planning Considerations

When a holiday is upcoming:
- Note if it's a bank holiday (offices closed)
- Consider impact on meetings (people may be off)
- Remind about gift-giving holidays (Christmas, etc.)
- Flag shipping deadlines for gifts (usually ~1 week before)

## Weekly Calendar Overview

On Mondays or when asked, provide a week-at-a-glance:

```markdown
## 📅 Week of November 25, 2025

### Today (Monday)
- 9:30 AM - 1:30 PM: Focus Block
- 2:30 PM: Sync with collaborator

### Tuesday
- No meetings scheduled

### Wednesday
- 10:00 AM: Team Standup

### Thursday - Thanksgiving 🦃
- US Holiday - Most offices closed

### Friday
- No meetings scheduled

---

**🎂 Birthdays**: Alex (Mon), Mom (Thu)
**🎉 Holidays**: Thanksgiving (Thu)
```

## Integration with Other Skills

- **daily-note**: Add calendar events to daily note during planning
- **meeting-prep**: Pull calendar event details for meeting context
- **person-context**: Cross-reference birthdays with People notes

## Proactive Behaviors

1. **Monday Morning**: If it's Monday, automatically check for:
   - Birthdays this week
   - Holidays this week
   - Heavy meeting days

2. **Meeting Conflicts**: When creating events, check for conflicts

3. **Prep Time**: When surfacing meetings with attendees, suggest prep time if none exists

## Example Queries

**User**: "What's my week look like?"
→ Query all calendars for next 7 days, summarize by day

**User**: "Any birthdays coming up?"
→ Query for all-day events containing "birthday" in next 14 days

**User**: "When is Thanksgiving?"
→ Query US Holidays calendar for "Thanksgiving"

**User**: "Do I have anything with Alex this week?"
→ Search events with "Alex" in summary or attendees

---

## Enhancements

These planning rhythm features integrate with [[planning-horizons]] and [[quarterly-planning-extraction]] to ensure proactive awareness of strategic planning needs.

### Quarterly Retreat Scheduling

**The 90-Day Sweet Spot**: Quarterly planning is the critical bridge between annual vision and daily execution. The quarterly retreat should be scheduled proactively.

**Quarterly Retreat Cadence:**
- Every ~12 weeks (end of March, June, September, December)
- Duration: 1-2 days for full retreat, minimum 2-3 hours for abbreviated review
- Location: Different from usual workspace (within 2 hours, avoid airport stress)

**Proactive Prompts:**

1. **Week 10-11 of Quarter** (2-3 weeks before quarter end):
   ```
   📅 Quarterly Retreat Reminder

   Q[X] ends in [X] weeks. Your quarterly planning retreat should be scheduled.

   Suggested dates: [Last weekend of quarter month]
   - Full retreat (recommended): 1-2 days away
   - Abbreviated: 3-4 hour block at home

   Would you like me to check your calendar for available slots?
   ```

2. **If no retreat scheduled by Week 11**:
   ```
   ⚠️ No quarterly retreat scheduled

   Q[X] ends [date]. Organizations with quarterly reviews achieve 70-80% goal completion
   vs. 30% without. At minimum, block 2-3 hours for review and planning.

   Options:
   - "Schedule 3-hour block" - Add to primary calendar
   - "Schedule full retreat" - Block 1-2 days
   - "I'll handle it manually"
   ```

**Retreat Dates for 2025-2026:**
| Quarter End | Retreat Window |
|-------------|---------------|
| Q1 2025 (Mar 31) | Mar 28-30 |
| Q2 2025 (Jun 30) | Jun 27-29 |
| Q3 2025 (Sep 30) | Sep 26-28 |
| Q4 2025 (Dec 31) | Dec 26-28 |
| Q1 2026 (Mar 31) | Mar 27-29 |

### Planning Rhythm Awareness

**Planning Cadence Monitoring**: Track when reviews are due and prompt appropriately.

| Review Type | Frequency | Duration | Prompt Timing |
|-------------|-----------|----------|---------------|
| Daily | Daily | 10-15 min | Morning (via `/daily:plan`) |
| Weekly | Weekly | 60-90 min | Friday afternoon |
| Monthly | Monthly | 2-3 hours | Last Sunday of month |
| Quarterly | Every 12 weeks | 2-4 hours | Week 10-11 of quarter |
| Annual | Yearly | 4-8 hours | December/early January |

**Weekly Review Detection:**
```
If today is Friday:
  Check: Is there a "Weekly Review" or "Planning" event scheduled for today/weekend?
  If not → Surface reminder: "📋 Weekly review not scheduled. Block 60-90 min this weekend?"
```

**Monthly Review Detection:**
```
If within last 3 days of month:
  Check: Has monthly review happened? (Look for event or daily note section)
  If not → Surface reminder: "📊 Monthly review due. This takes 2-3 hours and covers [month] progress."
```

**Mid-Quarter Check-in (Week 6-7):**
```
If in week 6-7 of quarter:
  Surface reminder: "📈 Mid-quarter check-in due.

  Key questions:
  - Are your 30-day milestones being hit?
  - Do any quarterly rocks need adjustment?
  - What's your biggest blocker right now?"
```

### Annual Planning Trigger

**December/January Planning Window**: Annual planning requires dedicated time for reflection and direction-setting.

**December Prompts (Starting Dec 1):**

```
Week 1 of December:
  "🎯 Annual Planning Reminder

  December is annual planning month. Key activities:
  - Year-end reflection on [current year]
  - Goal completion assessment
  - [Next year] theme and goal setting

  Have you blocked time for your annual review? (Recommended: 4-8 hours)"
```

```
Week 2-3 of December (if no annual planning time scheduled):
  "⚠️ Annual Review Not Scheduled

  [Current year] ends in [X] days. Annual planning includes:
  1. Year-end retrospective (what worked, what didn't)
  2. Foundation check (mission, vision, values still aligned?)
  3. [Next year] theme selection
  4. 3-5 annual goals

  This typically takes 4-8 hours. Schedule this week?"
```

**January Prompts (if planning not completed in December):**

```
First week of January:
  "🗓️ New Year Planning

  If you haven't completed annual planning yet:
  - Review [previous year] year file for reflection
  - Check foundation.md for alignment
  - Set [current year] theme and 3-5 goals

  Would you like to start the annual planning workflow?"
```

**Key Questions for Annual Planning:**
- "What did I learn about what really matters this year?"
- "When did I feel most aligned? What values were present?"
- "Does my mission still feel true? Am I living it daily?"
- "What would I do differently if I could repeat the year?"
- "What am I putting down to pick this up?" (for every new goal)

See [[planning-horizons]] for the complete planning cascade and [[quarterly-planning-extraction]] for 90-day planning details.
