---
name: calendar-management
description: Manage calendar events with smart defaults for travel time, attendees, and calendar selection. Use when creating, modifying, or removing calendar events.
allowed-tools: Read, Grep, Glob, AskUserQuestion, Bash, mcp__google-calendar__list-events, mcp__google-calendar__search-events, mcp__google-calendar__create-event, mcp__google-calendar__update-event, mcp__google-calendar__delete-event, mcp__google-calendar__get-freebusy, mcp__google-calendar__list-calendars, mcp__google-calendar__get-event, mcp__google-calendar__get-current-time
---

# Calendar Management Skill

Provides comprehensive calendar management with smart defaults, travel time handling, and contextual attendee suggestions.

## ⚠️ Authentication Recovery (READ FIRST)

**If any calendar MCP tool returns an auth error** (`invalid_grant`, `token expired`, `Authentication token is invalid`):

**Run the calendar auth command** — configure the path to your OAuth credentials:

```bash
GOOGLE_OAUTH_CREDENTIALS="[path-to-your-oauth-credentials.json]" npx -y @cocal/google-calendar-mcp auth
```

This opens a browser for OAuth. Wait for "Authentication completed successfully!" then retry the calendar operation.

**Key details:**

| Item | Value |
|------|-------|
| MCP Package | `@cocal/google-calendar-mcp` |
| OAuth Credentials | [Configure path to your GCP OAuth credentials] |
| Token Storage | `~/.config/google-calendar-mcp/tokens.json` |
| Account Name | `normal` (default) |

**Do NOT:**
- Search for MCP server installation locations
- Read MCP config files to find paths
- Try to refresh tokens manually

**Just run the npx command above.** It handles everything.

---

## 📋 Calendar Configuration (READ THIS)

**Configuration file**: `.user/calendars.yaml`

This file controls which calendars are checked for availability. **Always read this config before creating events.**

### Loading Configuration

```
1. Read: .user/calendars.yaml
2. Extract availability_calendars where check_availability: true
3. Use these calendar IDs for get-freebusy calls
```

### If Config Missing or Empty

If `.user/calendars.yaml` doesn't exist or `availability_calendars` is empty:

```
AskUserQuestion: "No calendar availability configuration found. Which calendars should I check for conflicts?"

Use mcp__google-calendar__list-calendars to show options.

After user selects, create/update .user/calendars.yaml with their choices.
```

### Current Configured Calendars (for reference)

| Name | Check Availability | Purpose |
|------|-------------------|---------|
| Primary | ✅ | Main personal calendar |
| Child | ✅ | Child's schedule - family conflicts |
| Work | ✅ | Work meetings |
| Family | ✅ | Family commitments |
| Business | ✅ | Business events |

**Excluded** (don't check): Holidays, inactive/legacy calendars

---

## When to Activate

This skill activates autonomously when:
- Creating, modifying, or removing calendar events
- User mentions scheduling, appointments, or meetings
- Events involve specific people ({{child_name}}, {{partner_name}}, etc.)
- In-person events that may need travel time
- Managing recurring event schedules

## Key Calendars (Quick Reference)

Configure your calendars in `.user/calendars.yaml`. Example structure:

| Calendar ID | Name | Use For |
|-------------|------|---------|
| `{{user_email}}` | Primary | Default for personal events |
| [work-calendar-id] | Work | Work meetings and events |
| [family-calendar-id] | Family | Family-wide events |
| [child-calendar-id] | {{child_name}} | Child's schedule, school, activities |

> **Note**: Full calendar list and availability settings are in `.user/calendars.yaml`

## Key Reference Information

**Home Address** (for travel calculations):
```
[Configure your home address]
```

**Timezone**: {{timezone}}

**Key People Email Lookup**:
- Look up attendee emails in `workspace/6-People/` directory
- Configure key contacts in `.user/calendars.yaml` or person files

## Color Coding Standards

| Color ID | Color | Use For |
|----------|-------|---------|
| 1 | Lavender | Personal events |
| 2 | Sage | Family/child events |
| 3 | Grape | {{company_3_name}} business |
| 4 | Flamingo | {{company_1_name}} |
| 5 | Banana | {{company_2_name}} |
| 7 | Peacock | Travel time blocks |
| 9 | Blueberry | Birthdays |
| 11 | Tomato | Important/Urgent |

---

## Core Rules

### Rule 1: Ending Recurring Events (NOT Deleting)

**NEVER delete recurring events.** Instead, set an end date using UNTIL.

**When user says "remove" or "delete" a recurring event:**

1. Get the current recurrence rule:
   ```
   mcp__google-calendar__get-event to retrieve current RRULE
   ```

2. Modify the RRULE to add UNTIL:
   ```
   Original: RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
   Modified: RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;UNTIL=20251201T235959Z
   ```

3. If no end date specified by user, use **today's date**

4. Update the event with new recurrence rule:
   ```
   mcp__google-calendar__update-event with:
   - recurrence: ["RRULE:...;UNTIL=YYYYMMDDTHHMMSSZ"]
   ```

**Example:**
```
User: "Stop the Provan school events"
Action: Update recurrence to end today, not delete
Result: Events stop appearing after today but history preserved
```

### Rule 2: Child-Related Events - Calendar Selection

When creating events related to {{child_name}} (school, activities, appointments):

**Always ask:**
```
AskUserQuestion: "This event is related to {{child_name}}. Which calendar should I add it to?"

Options:
- "{{child_name}} calendar" - Their dedicated schedule calendar
- "Primary calendar" - Your main personal calendar
- "Both calendars" - Add to both for visibility
```

**Child calendar ID**: [Configure in .user/calendars.yaml]

### Rule 3: Events Involving Partner - Attendee Invitation

When creating events that involve {{partner_name}}:

**Always ask (never auto-invite):**
```
AskUserQuestion: "This event involves {{partner_name}}. Should I add them as an attendee?"

Options:
- "Yes, invite {{partner_name}}" - They'll receive a calendar invitation
- "No, don't invite" - Event is just for your awareness
```

**Partner's email**: [Configure in person file or .user/calendars.yaml]

**If inviting:**
```
mcp__google-calendar__create-event with:
- attendees: [{ "email": "[partner-email]" }]
```

### Rule 4: In-Person Meetups - Attendee Suggestion

When creating events to meet someone in person:

**Always ask:**
```
AskUserQuestion: "You're meeting with [Person Name] in person. Should I add them to the calendar invite?"

Options:
- "Yes, invite [Person Name]" - They'll receive the invitation
- "No, just for my calendar" - No invitation sent
```

**To find their email:**
```bash
# Search person files
find "{{vault_path}}/workspace/6-People" -iname "*[person-name]*" -type f
```

Then read the file and extract email from Contact Information section.

### Rule 5: Addresses for In-Person Events

**Always add location/address** to in-person events.

**If address not provided:**
1. Check if it's a known location (home, office, etc.)
2. Ask user for address if unknown
3. Include full address in the `location` field

**Format:**
```
mcp__google-calendar__create-event with:
- location: "1401-A West Pecan, Pflugerville, TX 78660"
```

### Rule 6: Google Meet for Online Meetings

**For online/virtual meetings:** Always add Google Meet conferencing.

**For in-person meetings:** Do NOT add Google Meet.

**Detecting meeting type:**
- Keywords suggesting online: "call", "video call", "zoom", "virtual", "remote", "online meeting"
- Keywords suggesting in-person: "lunch", "dinner", "coffee", "meet at", "visit", address mentioned

**If unclear, ask:**
```
AskUserQuestion: "Is this an online meeting or in-person?"

Options:
- "Online meeting" - I'll add Google Meet
- "In-person" - No video conferencing needed
```

**Adding Google Meet:**
```
mcp__google-calendar__create-event with:
- conferenceData: {
    createRequest: {
      requestId: "[unique-id]",
      conferenceSolutionKey: { type: "hangoutsMeet" }
    }
  }
```

**Note:** The `requestId` should be a unique string (use timestamp or UUID).

### Rule 7: Travel Time Events

For in-person events, offer to add travel time:

**Step 1: Ask about travel time:**
```
AskUserQuestion: "This is an in-person event. Would you like me to add travel time blocks?"

Options:
- "Yes, add travel time" - I'll calculate and add travel events
- "No travel time needed" - Skip travel blocks
```

**Step 2: If yes, confirm locations:**
```
AskUserQuestion: "For travel time calculation:"

Questions:
1. "Leaving from home ({{home_address}})?" - Yes / Different location
2. "Returning home after?" - Yes / Going somewhere else
```

**Step 3: Calculate travel time:**
- Use estimated drive times based on Austin area knowledge
- Default estimates if unsure: 30-45 min for local Austin, 1 hour for suburbs

**Step 4: Check for excessive travel:**
```
IF travel_time > 2 hours:
  AskUserQuestion: "The calculated travel time is over 2 hours. Please confirm:"

  Options:
  - "Locations are correct" - Proceed with long travel time
  - "Let me fix the addresses" - User will provide correct info
```

**Step 5: Create travel events:**
```
# Before event
mcp__google-calendar__create-event with:
- summary: "Travel to [Event Name]"
- start: [event_start - travel_time]
- end: [event_start]
- colorId: "7"  # Peacock for travel
- location: "From: [start_address] To: [destination]"
- extendedProperties: {
    "private": {
      "source": "claude-code",
      "feature": "travel",
      "created": "YYYY-MM-DD",
      "linked_event": "[main-event-id]"
    }
  }

# After event
mcp__google-calendar__create-event with:
- summary: "Return from [Event Name]"
- start: [event_end]
- end: [event_end + return_travel_time]
- colorId: "7"
- location: "From: [destination] To: [end_address]"
- extendedProperties: {
    "private": {
      "source": "claude-code",
      "feature": "travel",
      "created": "YYYY-MM-DD",
      "linked_event": "[main-event-id]"
    }
  }
```

**Note:** The `linked_event` property allows cleanup of travel blocks when the main event is cancelled.

### Rule 8: Conflict Detection (MANDATORY)

**⚠️ ALWAYS check availability before creating ANY event. This is not optional.**

**Step 1: Load configured calendars**
```
Read: .claude/skills/calendar-management/.user/calendars.yaml
Extract all calendar IDs where check_availability: true
```

**Step 2: Check for conflicts across ALL configured calendars**
```
mcp__google-calendar__get-freebusy with:
- calendars: [
    { id: "[primary-calendar-id]" },
    { id: "[child-calendar-id]" },
    { id: "[work-calendar-id]" },
    { id: "[family-calendar-id]" },
    { id: "[business-calendar-id]" }
  ]
- timeMin: event start
- timeMax: event end
- timeZone: {{timezone}}
```

**Step 3: If ANY calendar has a conflict**
```
AskUserQuestion: "Scheduling conflict detected:"

Show which calendar(s) have conflicts:
- "Primary: Meeting with X (3:00-4:00 PM)"
- "Child: School pickup (3:30 PM)"

Options:
- "Create anyway" - Double-book (you'll manage it)
- "Suggest alternative time" - I'll find a free slot
- "Cancel" - Don't create the event
```

**Step 4: If "Suggest alternative time"**
- Query get-freebusy for a 4-hour window around requested time
- Find 30-min slots where ALL configured calendars are free
- Present top 3 options

**Why this matters**: Child calendars can be overlooked, causing family time conflicts. Now ALL configured calendars are checked every time

### Rule 9: Recurring Event Modification Scope

When modifying a recurring event:

**Always ask:**
```
AskUserQuestion: "This is a recurring event. Should this change apply to:"

Options:
- "This event only" - Just this one instance
- "This and all future events" - From this date forward
- "All events in the series" - Past and future
```

**Implementation:**
- "This event only" → Use instance ID, not recurring event ID
- "This and future" → Use `modificationScope: "thisAndFollowing"`
- "All events" → Use `modificationScope: "all"`

### Rule 10: Attendee Email Lookup

When adding attendees:

1. Search for person in vault:
   ```bash
   find "workspace/6-People" -iname "*[name]*" -type f
   ```

2. Read person file and extract email from Contact Information

3. If no email found:
   ```
   AskUserQuestion: "I couldn't find an email for [Person Name]. Would you like to:"

   Options:
   - "Provide the email" - I'll add them with the email you give
   - "Skip this attendee" - Don't add them to the invite
   - "Add without email" - Just note their name (won't receive invite)
   ```

### Rule 11: Attendee Notification Warning

**Before modifying or deleting events WITH attendees:**

```
AskUserQuestion: "This event has attendees who will be notified of changes. Proceed?"

Options:
- "Yes, notify attendees" - They'll receive update/cancellation
- "No, cancel this change" - Don't modify the event
```

### Rule 12: Event Descriptions

**Always include relevant info in descriptions:**

For meetings:
```
Meeting with [Person]
Contact: [phone/email if available]
Notes: [any context]
```

For appointments:
```
[Appointment type]
Address: [full address]
Phone: [if available]
Notes: [prep needed, bring items, etc.]
```

For child events:
```
[Event description]
School: [school name if relevant]
Contact: [school phone if relevant]
```

### Rule 13: Calendar Selection by Context

Suggest appropriate calendar based on event context:

| Event Type | Suggested Calendar |
|------------|-------------------|
| {{company_1_name}} meetings/work | Work calendar |
| {{company_2_name}} work | Primary or dedicated if exists |
| {{company_3_name}} business | Business calendar |
| {{child_name}} (school, activities) | Child calendar (ask per Rule 2) |
| Family events (multiple people) | Family calendar |
| Personal appointments | Primary |
| {{partner_name}}-specific events | Primary (ask about invite per Rule 3) |

---

## Execution Examples

### Example 1: Adding School Event for Child

**Input:** "Add {{child_name}}'s parent-teacher conference on Dec 15 at 3pm"

**Execution:**
1. Detect: Child-related event
2. **Rule 2**: Ask which calendar (Child or Primary)
3. **Rule 5**: Ask for school address if not known
4. **Rule 7**: Ask about travel time (it's in-person)
5. **Rule 8**: Check for conflicts at 3pm Dec 15
6. Create event with address and description
7. If travel requested, create travel blocks

### Example 2: Dinner with Partner

**Input:** "Schedule dinner with {{partner_name}} at [restaurant] on Friday at 7pm"

**Execution:**
1. Detect: Event involving partner, in-person
2. **Rule 3**: Ask if {{partner_name}} should be invited
3. **Rule 5**: Add restaurant address (look up or ask)
4. **Rule 7**: Ask about travel time
5. **Rule 8**: Check for conflicts
6. Create event with location and description
7. Add attendee if approved, travel if requested

### Example 3: Stopping Recurring Events

**Input:** "Stop the school events after this Friday"

**Execution:**
1. Detect: Ending recurring events
2. **Rule 1**: DO NOT DELETE
3. Get current RRULE from events
4. Add UNTIL=YYYYMMDD (Friday's date) to RRULE
5. Update events with modified recurrence
6. Confirm: "Updated recurring events to end after Friday"

### Example 4: Work Meeting

**Input:** "Add a meeting with [colleague] tomorrow at 2pm"

**Execution:**
1. Detect: Work meeting
2. **Rule 12**: Suggest appropriate work calendar
3. **Rule 4**: Ask if colleague should be invited (look up email from person file)
4. **Rule 7**: Check for conflicts
5. Create event on work calendar

---

## Calendar Tagging Standard

All system-created events MUST include extended properties for identification:

```javascript
extendedProperties: {
  "private": {
    "source": "claude-code",    // REQUIRED: Identifies system origin
    "feature": "[feature]",     // REQUIRED: travel, birthday, etc.
    "created": "YYYY-MM-DD"     // REQUIRED: Creation date
  }
}
```

**Benefits:**
- Safe operations: Can delete/modify system events without touching real meetings
- Feature isolation: Query only travel blocks, only birthdays, etc.
- Cleanup: Remove old system-generated events easily

**To find system-created events:**
```
privateExtendedProperty: ["source=claude-code"]
```

**To find specific feature events:**
```
privateExtendedProperty: ["source=claude-code", "feature=travel"]
```

See [Calendar Tagging Convention](/workspace/3-Resources/Documentation/calendar-tagging-convention.md) for full specification.

---

## Integration with Other Skills

- **`calendar-awareness`**: Reads calendar for planning; this skill writes/modifies
- **`birthday-awareness`**: Creates birthday events; follows color coding from this skill
- **`daily-timebox`**: Creates focus blocks; follows same tagging standard
- **`person-context`**: Provides attendee info; this skill looks up emails
- **`meeting-prep`**: Uses calendar data; this skill manages the events

## MCP Tools Reference

| Tool | Purpose |
|------|---------|
| `mcp__google-calendar__list-events` | List events in date range |
| `mcp__google-calendar__get-event` | Get single event details |
| `mcp__google-calendar__create-event` | Create new event |
| `mcp__google-calendar__update-event` | Modify existing event |
| `mcp__google-calendar__delete-event` | Delete event (avoid for recurring!) |
| `mcp__google-calendar__get-freebusy` | Check for conflicts |
| `mcp__google-calendar__search-events` | Search by text query |

## Edge Cases

### Multiple People with Same Name
If attendee name matches multiple person files, ask user to clarify which person.

### Unknown Locations
If user doesn't provide address for in-person event, ask before creating.

### Very Early/Late Events
For events before 7am or after 10pm, confirm the time is intentional.

### Cross-Timezone Events
If event involves someone in a different timezone, note this in description.

### Recurring Event Exceptions
When modifying single instance of recurring event, use the instance-specific event ID.

---

## Enhancements

These scheduling concepts integrate with [[planning-horizons]] and [[decision-frameworks]] to ensure calendar management supports strategic priorities.

### Protected Time Concepts

**Big Rocks First**: The Big Rock metaphor applies to calendar management. If you put sand (meetings, interruptions) in the jar first, rocks (deep work, strategic priorities) won't fit.

**Identifying Big Rock Time:**
- Quarterly rocks from [[planning-horizons]] need dedicated calendar blocks
- A-priority tasks require protected focus time
- Weekly Big 3 items should be scheduled BEFORE accepting meeting requests

**Protection Behaviors:**
1. When a meeting request arrives during a Big Rock block:
   ```
   AskUserQuestion: "This meeting request conflicts with your [Focus Block Name] which supports your quarterly rock on [Rock Name]. Proceed?"

   Options:
   - "Keep focus block, decline meeting"
   - "Reschedule focus block, accept meeting"
   - "Suggest alternative meeting time"
   ```

2. When scheduling new events, check for Big Rock conflicts:
   - Look for events tagged `feature: timebox` or containing "Focus" in summary
   - Warn before double-booking over focus blocks
   - Suggest moving focus blocks rather than deleting

### Seasonal Priorities

**Life Season Awareness**: Calendar priorities should shift based on current life season.

| Season Indicator | Calendar Adjustment |
|-----------------|---------------------|
| High-intensity work phase | Protect more deep work blocks, fewer meetings |
| Family milestone (birthday, school event) | Block family time first, work fits around |
| Quarterly planning week | Block retreat/review time |
| Recovery needed (post-deadline) | More buffer time, lighter scheduling |

**Seasonal Detection:**
- Check year file (`workspace/2-Areas/Personal/Years/YYYY.md`) for current theme
- Check quarterly rocks for priority signals
- Look for recent high-intensity periods (many late meetings, weekend work)

**When creating events during sensitive periods:**
```
Note: "This is [birthday week / Quarterly planning time / etc.].
Consider whether this meeting is essential."
```

### Buffer Time Requirements

**Buffer Rule**: Schedule minimum 30 minutes between meetings for mental transition.

**Why this matters:**
- Transition time helps shift mental contexts
- Back-to-back meetings cause cognitive fatigue
- Buffer time prevents chronic rushing and stress

**Implementation:**

1. **When creating meetings**, check for buffer:
   - If previous event ends at new event start time → warn
   - If less than 30 min gap → suggest adjustment

2. **Buffer warning prompt:**
   ```
   AskUserQuestion: "This meeting starts immediately after [Previous Event].
   You generally need 30 min between meetings for mental reset. Options:"

   - "Create with buffer" - Move to 30 min later
   - "Create anyway" - Accept back-to-back
   - "Suggest alternative" - Find a better slot
   ```

3. **Buffer check for in-person events:**
   - Add travel time PLUS buffer (e.g., 45 min travel + 15 min buffer = 1 hour before)

### Renewal Blocks

**Strategic Renewal**: Schedule intentional recovery time, not just "free time."

**Types of Renewal Blocks:**

| Block Type | Purpose | Suggested Duration | When to Schedule |
|------------|---------|-------------------|------------------|
| Weekly Renewal | Recharge for next week | 2-4 hours | Sunday afternoon |
| Post-Intensity Recovery | Recover from sprint | Half-day to full day | After major deadline |
| Quarterly Retreat | Strategic reflection | 1-2 days | End of quarter |
| Monthly Personal Day | Relationship investment | Full day | Once per month |

**Renewal vs. Avoidance Check:**
- Strategic renewal: Planned in advance, connects to recovery need
- Avoidance: Reactive, triggered by overwhelm, not scheduled

**When scheduling renewal:**
```
mcp__google-calendar__create-event with:
- summary: "[Renewal] Weekly Reset" or "[Renewal] Recovery Day"
- colorId: "2"  # Sage for wellness
- transparency: "opaque"  # This blocks availability
- description: "Protected renewal time. Not negotiable."
- extendedProperties: {
    "private": {
      "source": "claude-code",
      "feature": "renewal",
      "created": "YYYY-MM-DD"
    }
  }
```

**Coaching Integration:**
When user tries to schedule over renewal blocks:
```
AskUserQuestion: "This would eliminate your [Renewal Block].
Are you treating this as strategic renewal or was it just placeholder time?"

Options:
- "Protect this renewal time"
- "Reschedule renewal to [suggest alternative]"
- "Skip renewal this week" (warn about pattern if repeated)
```

See [[planning-horizons]] for the complete planning rhythm and [[decision-frameworks]] for strategic time protection.
