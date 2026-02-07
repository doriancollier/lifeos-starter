---
name: birthday-awareness
description: Automatically detect birthday mentions and manage birthday calendar events. Use when birthdays are mentioned, during planning, or when working with person files. Creates recurring yearly events and updates person files.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, mcp__google-calendar__list-events, mcp__google-calendar__search-events, mcp__google-calendar__create-event
---

# Birthday Awareness Skill

Automatically detects birthday mentions in any context and manages birthday calendar events and person file updates.

## When to Use

This skill activates autonomously when:
- Birthdays are mentioned in conversations or notes
- Planning activities that involve checking upcoming birthdays
- Working with person files that might contain birthday information
- Reviewing calendar events to identify birthdays

## Key Calendars

| Calendar ID | Purpose |
|-------------|---------|
| `{{user_email}}` | Primary calendar for birthdays |
| `family07897086865527719823@group.calendar.google.com` | Family birthdays |

**Timezone**: America/Chicago (Central Time)

## Birthday Detection Patterns

### Natural Language Patterns

Detect these phrases and extract birthday information:

| Pattern | Example | Extract |
|---------|---------|---------|
| "[Name]'s birthday is [date]" | "Jane's birthday is December 15th" | Name: Jane, Date: Dec 15 |
| "Happy birthday [Name]" | "Happy birthday John!" | Name: John, Date: Today |
| "[Name] was born on [date]" | "Sarah was born on March 3, 1990" | Name: Sarah, Date: Mar 3, Year: 1990 |
| "[Name] turns [age] [when]" | "Alex turns 30 tomorrow" | Name: Alex, Date: Tomorrow, Age: 30 |
| "Birthday: [Name] - [date]" | "Birthday: Mike - July 4" | Name: Mike, Date: Jul 4 |

### Date Parsing

Parse various date formats:

| Format | Example | Parsed As |
|--------|---------|-----------|
| "Month DD" | "December 15" | 2025-12-15 (current/next year) |
| "Month DDth" | "March 3rd" | 2025-03-03 (current/next year) |
| "MM/DD" | "12/15" | 2025-12-15 (current/next year) |
| "YYYY-MM-DD" | "1990-03-03" | 1990-03-03 (with year) |
| "today" | "today" | Current date |
| "tomorrow" | "tomorrow" | Current date + 1 |
| "next [day]" | "next Monday" | Calculate next occurrence |

**Year handling:**
- If year provided → use exact date and calculate age
- If no year → use current year if future, else next year

## Execution Flow

### Step 1: Detect Birthday Mention

Scan text for birthday patterns (see table above). Extract:
- **Person name**: Full or first name
- **Date**: Parse into YYYY-MM-DD format
- **Year** (optional): If birth year mentioned
- **Age** (optional): If age mentioned

### Step 2: Resolve Person Name

Match the extracted name against known people:

```bash
# Search for person in 6-People/ directory
find "{{vault_path}}/workspace/6-People" -iname "*[person-name]*" -type f
```

**Results:**
- **Single match**: Use that person file
- **Multiple matches**: Ask user which person
- **No match**: Use name as provided (may create person file later)

### Step 3: Check Calendar for Existing Birthday

Search calendar to avoid duplicates:

```
mcp__google-calendar__search-events with:
- calendarId: "{{user_email}}"
- query: "[Person Name] birthday"
- timeMin: [this year]-01-01
- timeMax: [next year]-12-31
- timeZone: "America/Chicago"
```

**Filter results:**
- Must be all-day event (has `date` field, not `dateTime`)
- Summary contains person's name (case-insensitive match)
- Summary contains "birthday" (case-insensitive)

**Results:**
- **Birthday found**: Skip calendar creation (already exists)
- **Birthday not found**: Proceed to Step 4

### Step 4: Ask User About Creating Birthday Event

Use AskUserQuestion to confirm action:

```
AskUserQuestion: "I noticed [[Person Name]]'s birthday is [date]. Should I:

Options:
- "Add recurring birthday event to calendar" - Recommended
- "Update [[Person Name]]'s file with birthday" - If person file exists
- "Do both" - Calendar event + person file
- "Just note it in daily memory" - No automation
```

**Note**: If person file doesn't exist, don't offer "Update person file" option unless it's significant enough to create one.

### Step 5: Create Recurring Birthday Event

If user approves calendar event:

```
mcp__google-calendar__create-event with:
- summary: "🎂 [Person Name]'s Birthday"
- start: { date: "YYYY-MM-DD" }  # All-day event
- end: { date: "YYYY-MM-DD+1" }  # Next day (all-day events use exclusive end)
- recurrence: ["RRULE:FREQ=YEARLY"]  # Repeats every year
- colorId: "9"  # Blueberry color for birthdays
- calendarId: "{{user_email}}"
- extendedProperties: {
    "private": {
      "source": "claude-code",
      "feature": "birthday",
      "created": "YYYY-MM-DD",
      "person_file": "workspace/6-People/[path]/[person-name].md"
    }
  }
```

**Important details:**
- **All-day event**: Use `date` field (not `dateTime`)
- **End date**: Must be day after start for all-day events
- **Recurrence**: YEARLY ensures it repeats automatically
- **No reminders**: `/daily:plan` handles birthday awareness
- **Emoji**: 🎂 makes birthdays easy to spot
- **Tagging**: Extended properties enable system identification and person file linking

**Confirm to user**: "Created recurring birthday event for [[Person Name]] on [date]"

### Step 6: Update Person File (if approved)

If user approves person file update and file exists:

1. **Read person file** from 6-People/
2. **Add birthday to appropriate section**:

   **Option A: Frontmatter field** (if template supports it):
   ```yaml
   ---
   birthday: "MM-DD" or "YYYY-MM-DD"
   ---
   ```

   **Option B: Important Dates section**:
   ```markdown
   ## Important Dates & Events

   - **Birthday**: [Month Day] (captured from [[YYYY-MM-DD daily note]])
   ```

3. **Update modified date**:
   ```yaml
   ---
   modified: "YYYY-MM-DD"
   ---
   ```

4. **Confirm**: "Updated [[Person Name]]'s file with birthday"

### Step 7: Calculate and Store Age (if year known)

If birth year was provided:

1. Calculate current age: `current_year - birth_year`
2. Add to person file:
   ```markdown
   - **Birthday**: [Month Day, Year] (age [X])
   ```

**Example**: "Birthday: March 3, 1990 (age 35)"

## Integration with Other Processes

- **`/update` command**: Automatically uses this skill when birthdays mentioned
- **`/daily:plan` command**: Explicitly checks for upcoming birthdays
- **`calendar-awareness` skill**: Works together to surface birthdays during planning
- **`calendar-management` skill**: Provides CRUD operations and color coding standards
- **`person-file-management` skill**: Coordinates person file updates

## Examples

### Example 1: Birthday Mentioned with Date

**Input:** "Jane Doe's birthday is December 15th"

**Actions:**
1. ✅ Detect pattern: "[Name]'s birthday is [date]"
2. ✅ Extract: Name = "Jane Doe", Date = "December 15" → 2025-12-15
3. ✅ Search person files: Find `workspace/6-People/Personal/jane-doe.md`
4. ✅ Check calendar for existing birthday
5. ❌ Not found in calendar
6. ❓ AskUserQuestion:
   ```
   "I noticed [[Jane Doe]]'s birthday is December 15th. Should I:

   Options:
   - Add recurring birthday event to calendar
   - Update [[Jane Doe]]'s file with birthday
   - Do both
   - Just note it in daily memory"
   ```
7. **User selects: "Do both"**
8. ✅ Create calendar event:
   ```
   Summary: "🎂 Jane Doe's Birthday"
   Date: 2025-12-15 (all-day, recurring yearly)
   Color: Blue
   ```
9. ✅ Update person file:
   ```markdown
   ## Important Dates & Events

   - **Birthday**: December 15th (from [[2025-11-28 daily note]])
   ```
10. ✅ Confirm: "Created birthday event and updated [[Jane Doe]]'s file"

### Example 2: Birthday Mentioned Today

**Input:** "Happy birthday John!"

**Actions:**
1. ✅ Detect pattern: "Happy birthday [Name]"
2. ✅ Extract: Name = "John", Date = "today" → 2025-11-28
3. ✅ Search person files: Find `workspace/6-People/Professional/{{company_1_name}}/john-smith.md`
4. ✅ Check calendar for existing birthday
5. ❌ Not found
6. ❓ AskUserQuestion:
   ```
   "I noticed today is [[John Smith]]'s birthday (November 28th). Should I:

   Options:
   - Add recurring birthday event to calendar
   - Update [[John Smith]]'s file with birthday
   - Do both
   - Just note it in daily memory"
   ```
7. **User selects: "Add recurring birthday event"**
8. ✅ Create calendar event for Nov 28, recurring yearly
9. ✅ Confirm: "Created recurring birthday event for [[John Smith]]"

### Example 3: Birthday with Birth Year

**Input:** "Sarah Miller was born on March 3, 1990"

**Actions:**
1. ✅ Detect pattern: "[Name] was born on [date]"
2. ✅ Extract: Name = "Sarah Miller", Date = "March 3, 1990" → 1990-03-03
3. ✅ Calculate age: 2025 - 1990 = 35 years old
4. ✅ Search person files: Find `workspace/6-People/Professional/{{company_2_name}}/sarah-miller.md`
5. ✅ Check calendar for existing birthday
6. ❌ Not found
7. ❓ AskUserQuestion: [offers both options]
8. **User selects: "Do both"**
9. ✅ Create calendar event (March 3, recurring yearly)
10. ✅ Update person file:
    ```markdown
    ## Important Dates & Events

    - **Birthday**: March 3, 1990 (age 35) (from [[2025-11-28 daily note]])
    ```
11. ✅ Confirm: "Created birthday event and updated file with birthday and age"

### Example 4: Birthday Already in Calendar

**Input:** "Alex Johnson's birthday is July 15th"

**Actions:**
1. ✅ Detect pattern: "[Name]'s birthday is [date]"
2. ✅ Extract: Name = "Alex Johnson", Date = "July 15" → 2025-07-15
3. ✅ Search person files: Find `workspace/6-People/Personal/alex-johnson.md`
4. ✅ Check calendar for existing birthday
5. ✅ **Found**: "🎂 Alex Johnson's Birthday" on July 15 (recurring)
6. ℹ️ Notify: "[[Alex Johnson]]'s birthday is already in your calendar (July 15th, recurring yearly)"
7. ❓ Optional ask: "Should I update [[Alex Johnson]]'s file with the birthday if it's not already there?"
8. **User selects: "Yes"**
9. ✅ Check person file for birthday field
10. ❌ Not found in file
11. ✅ Add to person file
12. ✅ Confirm: "Updated [[Alex Johnson]]'s file with birthday"

### Example 5: Tomorrow's Birthday

**Input:** "Reminder: Robert Chen turns 30 tomorrow"

**Actions:**
1. ✅ Detect pattern: "[Name] turns [age] [when]"
2. ✅ Extract: Name = "Robert Chen", Age = 30, Date = "tomorrow" → 2025-11-29
3. ✅ Calculate birth year: 2025 - 30 = 1995
4. ✅ Search person files: Find `workspace/6-People/Professional/AustinDiabetesCenter/robert-chen.md`
5. ✅ Check calendar
6. ❌ Not found
7. ❓ AskUserQuestion: [offers both options]
8. **User selects: "Do both"**
9. ✅ Create calendar event (Nov 29, recurring yearly)
10. ✅ Update person file with birthday and calculated birth year (1995)
11. ✅ Confirm: "Created birthday event and updated file (calculated birth year: 1995)"

### Example 6: Multiple People with Same Name

**Input:** "John's birthday is April 5th"

**Actions:**
1. ✅ Detect pattern: "[Name]'s birthday is [date]"
2. ✅ Extract: Name = "John", Date = "April 5" → 2025-04-05
3. ✅ Search person files
4. ⚠️ **Multiple matches found**:
   - `workspace/6-People/Professional/{{company_1_name}}/john-smith.md`
   - `workspace/6-People/Personal/john-doe.md`
5. ❓ AskUserQuestion:
   ```
   "Which John did you mean?

   Options:
   - [[John Smith]] - {{company_1_name}} colleague
   - [[John Doe]] - Personal contact
   - Someone else - I'll specify
   ```
6. **User selects: "John Smith"**
7. ✅ Proceed with John Smith's file
8. ✅ Check calendar, create event, update file
9. ✅ Confirm: "Created birthday event for [[John Smith]] (April 5th)"

## Birthday Event Format

### Standard Format

All birthday events follow this consistent format:

```
Summary: 🎂 [Person Name]'s Birthday
Start: YYYY-MM-DD (all-day)
End: YYYY-MM-DD+1 (all-day exclusive end)
Recurrence: RRULE:FREQ=YEARLY
Color: Blue (colorId: 9)
Calendar: {{user_email}}
Reminders: None (handled by /daily:plan)
Extended Properties:
  private.source: "claude-code"
  private.feature: "birthday"
  private.created: "YYYY-MM-DD"
  private.person_file: "workspace/6-People/[path]/[name].md" (optional)
```

### Why This Format?

- **🎂 Emoji**: Visual indicator, easy to spot in calendar views
- **All-day event**: Birthdays aren't time-specific
- **Recurring yearly**: Automatically appears every year
- **Blueberry color**: Consistent categorization (colorId: 9)
- **No reminders**: `/daily:plan` surfaces upcoming birthdays during morning planning
- **Tagging**: `source=claude-code` enables identification and bulk operations

### Querying Birthday Events

To find all system-created birthday events:
```
privateExtendedProperty: ["source=claude-code", "feature=birthday"]
```

See [Calendar Tagging Convention](/workspace/0-System/guides/calendar-tagging-convention.md) for full specification.

## Person File Birthday Format

When adding birthdays to person files, use one of these formats:

### Option 1: Frontmatter (if template supports)

```yaml
---
birthday: "MM-DD"  # or "YYYY-MM-DD" if year known
---
```

### Option 2: Important Dates Section

```markdown
## Important Dates & Events

- **Birthday**: [Month Day] (from [[YYYY-MM-DD daily note]])
```

### Option 3: With Birth Year and Age

```markdown
## Important Dates & Events

- **Birthday**: [Month Day, Year] (age [X]) (from [[YYYY-MM-DD daily note]])
```

**Always include source reference** to track where the information came from.

## Best Practices

1. **Always check calendar first**: Avoid creating duplicate birthday events
2. **Preserve birth year if mentioned**: Helps calculate age automatically
3. **Link to source**: Note where birthday info was captured
4. **Use consistent format**: Makes birthdays easy to find and parse
5. **Cross-reference person files**: Birthday in calendar should match person file
6. **Ask before creating**: User might already have this information elsewhere

## Edge Cases

### Ambiguous Dates

If date is unclear:
- "sometime in December" → Ask for specific date
- "early March" → Ask for specific date
- "I think it's the 15th" → Confirm before creating

### Already in Calendar but Different Format

If birthday exists but format differs:
- Different name ("Jane" vs "Jane Doe")
- Missing emoji
- Not recurring

**Action**: Notify user, ask if they want to update/standardize the existing event

### Birthday Passed This Year

If current date is after the birthday date in the current year:
- Create event with this year's date
- Recurring rule will show it next year automatically
- Event is already "in the past" for this year, which is fine

### Family Calendar vs Personal Calendar

If unclear which calendar to use:
- Default to personal calendar (`{{user_email}}`)
- Family members could optionally go to family calendar
- Use AskUserQuestion if context suggests family calendar

**Example**:
```
"Should this go in your personal calendar or family calendar?

Options:
- Personal calendar
- Family calendar
```
