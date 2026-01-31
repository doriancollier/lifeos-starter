---
description: Smart capture - parses updates into tasks, calendar events, mood notes, narrative memories, and cross-references. Auto-detects birthdays, suggests calendar attendees, and manages person files.
argument-hint: [[date]] [freeform update text]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, mcp__google-calendar__list-events, mcp__google-calendar__create-event, mcp__google-calendar__get-freebusy, mcp__google-calendar__search-events
---

# Smart Update Command

A universal capture command that intelligently parses freeform natural language into multiple actions: tasks, calendar events, mood notes, narrative memories, person/project updates, and cross-references. Supports updating any day's note (today, yesterday, or specific dates).

## Arguments

- `$ARGUMENTS` - Optional date followed by freeform text
  - **With date**: `/update 2025-11-26 [text]` or `/update yesterday [text]`
  - **Without date** (default to today): `/update [text]`

## Core Principle

**Always update something.** Every invocation should result in at least one change to the vault or calendar. Your job is to figure out what needs updating and WHERE (which day's note, which sections).

## Context

- **Daily notes**: `{{vault_path}}/4-Daily/`
- **Today's note**: `4-Daily/YYYY-MM-DD.md`
- **People**: `{{vault_path}}/6-People/`
- **Projects**: `{{vault_path}}/1-Projects/`
- **Primary calendar**: `{{user_email}}`
- **User timezone**: {{timezone}}

## Date Parameter Parsing

### Step 0: Extract Date (if present)

Check if `$ARGUMENTS` starts with a date reference:

| Date Format | Example | Resolves To |
|-------------|---------|-------------|
| `YYYY-MM-DD` | `2025-11-26` | That specific date |
| `yesterday` | `yesterday` | Previous day |
| `last [day]` | `last Tuesday` | Most recent occurrence of that weekday |
| *(no date)* | *(text only)* | Today (current behavior) |

**Implementation:**
```bash
# Get today's date
TODAY=$(date +%Y-%m-%d)

# Parse date argument
if [[ "$ARGUMENTS" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then
  TARGET_DATE="${BASH_REMATCH[0]}"
  TEXT="${ARGUMENTS#$TARGET_DATE }"
elif [[ "$ARGUMENTS" =~ ^yesterday ]]; then
  TARGET_DATE=$(date -v-1d +%Y-%m-%d)  # macOS syntax
  TEXT="${ARGUMENTS#yesterday }"
elif [[ "$ARGUMENTS" =~ ^last\ (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) ]]; then
  # Calculate most recent occurrence of that weekday
  # (Implementation varies by platform)
  TEXT="${ARGUMENTS#last * }"
else
  TARGET_DATE="$TODAY"
  TEXT="$ARGUMENTS"
fi
```

**After parsing:**
- `TARGET_DATE` = which day's note to update
- `TODAY` = today's date (for cross-references)
- `TEXT` = the actual content to parse

## Parsing Strategy

### Step 1: Identify All Action Types

Scan `TEXT` for signals that indicate different action types:

| Signal Pattern | Action Type | Example |
|----------------|-------------|---------|
| Past tense storytelling: "made", "went", "had", "was", "saw" | **Narrative** | "{{child_name}} made deviled eggs" |
| Dreams: "dream", "dreamed", "dreamt", "had a dream" | **Narrative** | "Had a vivid dream about flying" |
| Detailed descriptions, emotions, sensory details | **Narrative** | "it was so fun watching him carefully spoon the filling" |
| "need to", "should", "want to", "go to", "have to", action verbs | **Task** | "need to call the pharmacy" |
| Time words: "this afternoon", "tomorrow", "at 3pm", "tonight", specific times | **Calendar Event** | "this afternoon" → create event |
| Feeling words: "feeling", "frustrated", "happy", "tired", "bad", "stressed" | **Mood Note** | "feeling bad" → mood log |
| Person names (fuzzy match against 6-People/) | **Person Reference** | "talked to Alex" → link [[Alex Smith]] |
| Project keywords or names | **Project Reference** | "working on analytics" → link [[Analytics]] |
| Company names: "{{company_1_name}}", "{{company_2_name}}", "{{company_3_name}}", "personal" | **Company Context** | Sets task company |
| "update on", "finished", "completed", "done with", "progress on" | **Task Update** | Update existing task status |
| Urgency: "urgent", "asap", "critical", "important" | **Priority Elevation** | 🟡 → 🔴 |
| URLs | **Link Capture** | Add to Links section |
| Major events: "trip to", "traveling to", "wedding", "birthday party" | **Life Event** | Add to Life Events Timeline |

**Important:** Content can be BOTH narrative AND task/work. Example:
- "finished the AssetOps work AND {{child_name}} helped me test it - made it a learning moment"
  - Task/Work: "finished AssetOps work" → Quick Notes
  - Narrative: "{{child_name}} helped me test it - made it a learning moment" → Daily Memories

### Step 2: Classify Content Type

Determine if content is **Narrative**, **Work**, or **Hybrid**:

**Narrative indicators:**
- Past tense verbs describing events ("made", "went", "had", "saw", "was")
- Story-like structure with details
- Emotional or sensory language
- Dreams, memories, reflections
- Family moments, personal experiences

**Work indicators:**
- Task keywords ("need to", "should", "finished", "completed")
- Progress reports ("done with", "working on")
- Project/company references
- Action-oriented language

**Hybrid detection:**
- Contains BOTH narrative AND work elements
- Example: "finished X AND [personal detail]"
- Example: "working on Y with [person] - [story about the interaction]"

### Step 3: Handle Cross-Temporal Scenarios

When updating a **past day's note** with content that has **future implications**:

**Example:** `/update yesterday {{partner_name}} asked to take her car to the shop next week`

This requires updating **multiple notes**:

| Date | Section | Entry | Purpose |
|------|---------|-------|---------|
| **Yesterday** | Daily Memories | `[~HH:MM] 📖 [[{{partner_name}}]] asked about taking her car to the shop next week ^block-id` | Record the conversation |
| **Today** | Quick Notes | `[HH:MM] Captured from yesterday: [[YYYY-MM-DD#^block-id\|description]] - added task` | Audit trail |
| **Today** | Tasks | `[ ] 🟡 Take [[{{partner_name}}]]'s car to shop 📅 2025-12-15 - Origin: [[YYYY-MM-DD#^block-id]]` | Actionable item |

**Block Reference Syntax:**
- End narrative entry with `^block-id` (lowercase, hyphens, descriptive)
- Link to it with `[[note-name#^block-id|display text]]`
- Tasks reference origin with `Origin: [[date#^block-id]]`

### Step 4: Determine Priority

Default priority is **🟡 B (Important)**. Adjust based on:

| If input contains... | Priority |
|---------------------|----------|
| "urgent", "asap", "critical", "emergency", "must" | 🔴 A Priority |
| "important", "need to", "should" | 🟡 B Priority (default) |
| "maybe", "could", "nice to", "would like" | 🟢 C Priority |
| "someday", "eventually", "when I have time" | 🟢 C Priority |

**Note**: Context matters for "want to":
- "want to go to the store" → 🟡 B (actionable errand)
- "want to learn guitar someday" → 🟢 C (aspirational)

**Important**: If you assign a priority other than 🟡, mention it in your response.

### Step 5: Fuzzy Match People and Projects

**For People:**
```bash
# Search for person names in 6-People/
find "{{vault_path}}/6-People" -name "*.md" -type f
```

- Match first names, last names, or partial names
- If multiple matches and context doesn't disambiguate, ask the user
- Create links using `[[Person Name]]` format

**For Projects:**
```bash
# Search for projects
find "{{vault_path}}/1-Projects/Current" -name "*.md" -type f
```

### Step 6: Handle Time References

When time references are detected:

1. **Parse the time reference**:
   - "this afternoon" → Today 14:00-15:00 (1 hour default for errands)
   - "tomorrow morning" → Tomorrow 09:00-10:00
   - "at 3pm" → Today 15:00-16:00
   - "tonight" → Today 19:00-20:00
   - "next week" → Scheduled task, not calendar event
   - "later" → Ambiguous, ask for clarification

2. **Check calendar for conflicts** (only if creating event):
   ```
   Use mcp__google-calendar__get-freebusy for {{user_email}}
   ```

3. **If conflict detected**: Ask user how to proceed with specific options

4. **Duration defaults**:
   - Errands (store, pickup, drop off): 1 hour
   - Calls/quick meetings: 30 minutes
   - Meetings/appointments: 1 hour
   - Open-ended activities: 1 hour

### Step 6.5: Ask About Calendar Attendees

When creating a calendar event that involves another person:

1. **Detect person involvement** from event context:
   - Event mentions a specific person's name: "Jane's surgery", "meeting with John"
   - Appointment for someone else: "take Sarah to the doctor"
   - Event belongs to another person: "Robert's recital"

2. **Extract person name and match against known people**:
   ```bash
   # Search for person in 6-People/ directory
   find "{{vault_path}}/6-People" -iname "*[person-name]*" -type f
   ```

3. **Use AskUserQuestion with context-based suggestions**:

   If person file found:
   ```
   AskUserQuestion: "I'm creating '[Event Name]' on [date] at [time]. Should I add attendees?

   Options:
   - "Add [[Person Name]]" - They should receive the invite
   - "No attendees" - Just for my calendar awareness
   - "Let me add manually" - I'll specify who to invite
   ```

   If multiple people found, include all as options:
   ```
   AskUserQuestion: "I'm creating '[Event Name]'. Should I add attendees?

   Options:
   - "Add [[Person Name]]" - Primary person
   - "Add [[Other Person]]" - If multiple people detected
   - "Add both" - If 2 people detected
   - "No attendees" - Just for my awareness
   - "Let me add manually" - I'll specify
   ```

4. **Create event with attendees** (if selected):
   ```
   mcp__google-calendar__create-event with:
   - summary: "[Event Name]"
   - start: { dateTime: "YYYY-MM-DDTHH:MM:SS", timeZone: "America/Chicago" }
   - end: { dateTime: "YYYY-MM-DDTHH:MM:SS", timeZone: "America/Chicago" }
   - attendees: [{ email: "person@email.com", responseStatus: "needsAction" }]
   ```

**Note**: Email addresses should be extracted from person files if available. If not available in person file, ask user for email or skip attendee.

## Integration with Skills

This command leverages two specialized skills for automatic capability:

### `birthday-awareness` Skill (Model-Invoked)

Automatically activates when birthdays are mentioned. Handles:
- Detecting birthday patterns in natural language
- Checking calendar for existing birthday events
- Creating recurring yearly birthday events
- Updating person files with birthday information

**You don't need to explicitly invoke this skill** - it activates autonomously when appropriate.

### `person-file-management` Skill (Model-Invoked)

Automatically activates when significant person information is mentioned. Handles:
- Auto-creating person files for new people with significant context
- Auto-updating existing files for health info, major life events, contact changes
- Asking user for middle-ground cases and learning from feedback
- Managing Professional vs Personal categorization

**You don't need to explicitly invoke this skill** - it activates autonomously when appropriate.

**Important**: These skills work in the background. You simply process the update normally, and the skills will automatically handle birthday detection and person file management based on their decision criteria.

## Execution Flow

### 1. Parse Date and Content

```
Input: "/update yesterday {{child_name}} made the deviled eggs for Thanksgiving"

Parse:
- TARGET_DATE = 2025-11-26 (yesterday)
- TODAY = 2025-11-27
- TEXT = "{{child_name}} made the deviled eggs for Thanksgiving"
```

### 2. Find or Create Target Daily Note

```bash
TARGET_NOTE="{{vault_path}}/4-Daily/${TARGET_DATE}.md"

# Note: If daily note doesn't exist, the `daily-note` skill will automatically create it
# The skill also handles offering /daily:plan if the note appears unplanned
```

### 3. Classify Content Type

Analyze `TEXT` to determine: **Narrative**, **Work**, or **Hybrid**

### 4. Ensure Journal Section Exists

If updating with narrative content and target note doesn't have the Journal section:

```markdown
## Journal

### Reflections

*Thoughts, observations, feelings*

### Daily Memories

*Narrative moments worth remembering*

- [HH:MM] 📖

### Quick Notes

*Work progress, project updates, misc*

- [HH:MM]
```

**Section order:** Journal contains Reflections, Daily Memories, then Quick Notes

### 5. Execute Each Action Type

#### For Narrative Content

**If TARGET_DATE = TODAY:**
```markdown
### Daily Memories
- [HH:MM] 📖 [Narrative entry with [[person/project links]]]
```

**If TARGET_DATE ≠ TODAY (retroactive entry):**
```markdown
### Daily Memories
- [~HH:MM] 📖 [Narrative entry with [[person/project links]]] ^block-id
```

**AND add to TODAY's Quick Notes:**
```markdown
### Quick Notes
- [HH:MM] Captured from [date]: [[TARGET_DATE#^block-id|brief description]]
```

**Block ID format:** Lowercase, hyphens, descriptive. Examples:
- `^{{child_name}}-deviled-eggs`
- `^partner-car-shop`
- `^dream-flying`

#### For Task Content

**If TARGET_DATE = TODAY:**
- Add to appropriate project section in Work area
- If no clear project, add to Quick Hits section
- Include person/project links if detected
- Format: `- [ ] [emoji] [Task with [[links]]]`

**If TARGET_DATE ≠ TODAY but task is for FUTURE:**
- Create a calendar event for the future date instead
- Add task to relevant project section with note about future timing
- Format: `- [ ] [emoji] [Task] - Due: [date]`

**If TARGET_DATE ≠ TODAY and task was for THAT DAY (completed):**
- Don't create task, just note in Daily Memories

#### For Hybrid Content (Both Narrative + Work)

Update **BOTH** sections:

1. **Daily Memories** (narrative portion):
   ```markdown
   - [~HH:MM] 📖 [[{{child_name}}]] helped me test AssetOps - turned it into a learning moment for him ^assetops-{{child_name}}-test
   ```

2. **Quick Notes** (work portion):
   ```markdown
   - [HH:MM] AssetOps: Finished Vendor Claiming/Scheduling features - [[2025-11-26#^assetops-{{child_name}}-test|{{child_name}} helped test]]
   ```

3. **Task update** (if applicable):
   - Mark existing task complete
   - Add subtask for completion

#### For Calendar Events

- Check for conflicts first
- If clear, create event on primary calendar
- Also create a task (tasks can exist alongside calendar events)
- If conflict, present options to user

#### For Mood Notes

- Add to Quick Notes section with timestamp and 🎭 emoji
- Format: `- [HH:MM] 🎭 Mood: [feeling] - [context if provided]`

#### For Task Updates (progress reports)

- Find matching task in daily note
- Add subtask or mark complete as appropriate
- Add timestamped log entry
- Follow work-logging skill patterns

#### For Person References

- Always link with `[[Person Name]]`
- If notable interaction, consider adding note to person's file

#### For Links/URLs

- Add to "Links to Explore Later" section

#### For Life Events

- Detect major life events (trips, weddings, holidays, birthdays, vacations)
- Read `/7-MOCs/Life-Events-Timeline.md`
- Add entry to appropriate timeframe section
- Update "Last Updated" date in timeline

### 6. Smart Confirmation Rules

**Ask the user when:**
- Calendar conflict detected
- Time reference is ambiguous ("later", "soon", "when I can")
- Multiple people match a name and context doesn't help
- Input could be interpreted multiple ways
- Updating an existing task and multiple tasks match
- Cross-temporal scenario is complex (affects 3+ notes)

**Proceed without asking when:**
- Actions are clear and unambiguous
- No calendar conflicts
- Single matching person/project
- Creating new items (not updating existing)
- Standard retroactive memory capture

### 7. Report What Was Done

Always output a detailed summary showing ALL updates:

```markdown
## Updated

**Daily Memories (2025-11-26):**
- Added: "{{child_name}} made the deviled eggs for Thanksgiving" (block: ^{{child_name}}-deviled-eggs)

**Quick Notes (2025-11-27):**
- Cross-reference to yesterday's memory

**Tasks:**
- Added: [task description] (🟡 B Priority, Personal)

**Calendar:**
- Created: "[Event name]" today 3:00-4:00 PM

**Links:**
- [[{{child_name}}]] referenced in memory
```

## Examples

### Example 1: Simple Narrative (Yesterday)

**Input:** `/update yesterday {{child_name}} made the deviled eggs for Thanksgiving - it was so fun watching him carefully spoon the filling`

**Actions:**
1. ✅ Parse date: yesterday = 2025-11-26
2. ✅ Classify: Pure narrative (past tense, descriptive detail, family moment)
3. ✅ Add to 2025-11-26 Daily Memories:
   ```
   - [~12:32] 📖 [[{{child_name}}]] made the deviled eggs for Thanksgiving - it was so fun watching him carefully spoon the filling ^{{child_name}}-deviled-eggs
   ```
4. ✅ Add to TODAY (2025-11-27) Quick Notes:
   ```
   - [12:32] Captured from yesterday: [[2025-11-26#^{{child_name}}-deviled-eggs|{{child_name}} made deviled eggs]]
   ```

### Example 2: Dream (Specific Date)

**Input:** `/update 2025-11-25 Had a vivid dream about flying over Austin`

**Actions:**
1. ✅ Parse date: 2025-11-25
2. ✅ Classify: Narrative (dream)
3. ✅ Add to 2025-11-25 Daily Memories:
   ```
   - [~12:32] 📖 Had a vivid dream about flying over Austin ^dream-flying
   ```
4. ✅ Add to TODAY Quick Notes:
   ```
   - [12:32] Captured dream from 2025-11-25: [[2025-11-25#^dream-flying|flying over Austin]]
   ```

### Example 3: Cross-Temporal with Future Task

**Input:** `/update yesterday {{partner_name}} asked to take her car to the shop next week`

**Actions:**
1. ✅ Parse date: yesterday = 2025-11-26
2. ✅ Classify: Hybrid (narrative conversation + future task)
3. ✅ Add to 2025-11-26 Daily Memories:
   ```
   - [~12:32] 📖 [[{{partner_name}}]] asked about taking her car to the shop next week ^partner-car-shop
   ```
4. ✅ Add to TODAY (2025-11-27) Quick Notes:
   ```
   - [12:32] Captured from yesterday: [[2025-11-26#^partner-car-shop|{{partner_name}}'s car shop request]] - created calendar event
   ```
5. ✅ Create calendar event for next week:
   ```
   Summary: "Take {{partner_name}}'s car to shop"
   Date: Next week (pick a day)
   ```
6. ✅ Add to Personal Quick Hits section:
   ```
   - [ ] Take [[{{partner_name}}]]'s car to the shop - Due: Next week
   ```

### Example 4: Hybrid Work + Narrative

**Input:** `/update finished the AssetOps work AND {{child_name}} helped me test it - made it a learning moment for him`

**Actions:**
1. ✅ Parse date: (none) = TODAY
2. ✅ Classify: Hybrid (work completion + narrative moment)
3. ✅ Add to Daily Memories:
   ```
   - [12:32] 📖 [[{{child_name}}]] helped me test AssetOps - turned it into a learning moment, showing him how vendor workflows work ^assetops-{{child_name}}-test
   ```
4. ✅ Add to Quick Notes:
   ```
   - [12:32] AssetOps: Finished Vendor Claiming/Scheduling features - [[#^assetops-{{child_name}}-test|{{child_name}} helped test]]
   ```
5. ✅ Update task (if exists):
   ```
   - [x] 🔴4. Get Vendor Claiming working - Company: AssetOps
   - [x] 🔴5. Get Vendor Scheduling working - Company: AssetOps
   ```

### Example 5: Multi-part Update (Today)

**Input:** `/update I want to go to the store this afternoon to pickup ice cream because I'm feeling bad`

**Actions:**
1. ✅ Task: `- [ ] 🟡 Go to the store to pickup ice cream - Company: Personal`
2. ✅ Check calendar 2-5 PM for conflicts
3. ✅ Calendar event: "Store - pickup ice cream" (1 hour, suggest 3-4 PM if free)
4. ✅ Mood note: `- [17:15] 🎭 Mood: Not feeling great, want comfort food`

### Example 6: Person Reference with Task

**Input:** `/update need to follow up with Alex about the analytics dashboard`

**Actions:**
1. ✅ Search 6-People/ for "Alex" → matches [[Alex Smith]]
2. ✅ Task: `- [ ] 🟡 Follow up with [[Alex Smith]] about the analytics dashboard - Company: {{company_1_name}}`

### Example 7: Urgent Task

**Input:** `/update urgent - call the pharmacy about my prescription asap`

**Actions:**
1. ✅ Detect urgency → 🔴 A Priority
2. ✅ Task: `- [ ] 🔴 Call the pharmacy about prescription - Company: Personal`
3. ✅ Report: "Added as A Priority due to urgency"

### Example 8: Task Update/Progress

**Input:** `/update just finished the prescription call, pickup is ready tomorrow`

**Actions:**
1. ✅ Find task matching "prescription" in today's note
2. ✅ Add subtask: `  - [x] Call pharmacy`
3. ✅ Add subtask: `  - [ ] Pickup prescription tomorrow`
4. ✅ Quick note: `- [17:20] Prescription: Called pharmacy, pickup ready tomorrow`

### Example 9: Calendar Conflict

**Input:** `/update meeting with Matt at 2pm tomorrow`

**Actions:**
1. ✅ Check calendar for 2pm tomorrow → CONFLICT with "Product Sync"
2. ❓ Ask user: "You have 'Product Sync' at 2pm tomorrow. Would you like to: (a) Schedule before at 1pm, (b) Schedule after at 3pm, (c) Replace the existing event, (d) Skip calendar and just add as task?"

### Example 10: Ambiguous Time

**Input:** `/update should call mom later`

**Actions:**
1. ✅ Task: `- [ ] 🟡 Call mom - Company: Personal`
2. ❓ Ask: "Would you like me to add this to your calendar? If so, what time works?"

### Example 11: Just Mood

**Input:** `/update feeling really good today, got a lot done`

**Actions:**
1. ✅ Mood note: `- [17:25] 🎭 Mood: Feeling really good, got a lot done`
2. ✅ Report: "Logged your mood to today's Quick Notes"

### Example 12: Link Capture

**Input:** `/update check out this article later https://example.com/article`

**Actions:**
1. ✅ Add to Links: `- https://example.com/article`
2. ✅ Optionally task: `- [ ] 🟢 Read article from example.com - Company: Personal`

### Example 13: Calendar Event with Attendee Suggestion

**Input:** `/update Jane's surgery is December 15th at 9am`

**Actions:**
1. ✅ Parse: Event with person's name and specific time
2. ✅ Search 6-People/ for "Jane" → finds `jane-doe.md`
3. ✅ Check calendar for conflicts at 9am on Dec 15
4. ✅ No conflict found
5. ❓ AskUserQuestion:
   ```
   "I'm creating 'Jane's surgery' on December 15 at 9:00 AM. Should I add attendees?

   Options:
   - Add [[Jane Doe]] - She should receive the invite
   - No attendees - Just for my calendar awareness
   - Let me add manually - I'll specify who to invite"
   ```
6. **User selects: "Add Jane Doe"**
7. ✅ Extract email from Jane's person file: `jane.doe@email.com`
8. ✅ Create calendar event:
   ```
   Summary: "Jane's surgery"
   Time: Dec 15, 2025 9:00-10:00 AM
   Attendees: jane.doe@email.com
   ```
9. ✅ Add to daily note
10. ⚡ `person-file-management` skill activates (health info detected)
11. ✅ Auto-updates Jane's person file with surgery information
12. ✅ Confirm: "Created calendar event with [[Jane Doe]] as attendee and updated her file"

### Example 14: Birthday Detection (Skill Integration)

**Input:** `/update John Smith's birthday is March 15th`

**Actions:**
1. ✅ Parse: Birthday mention detected
2. ⚡ `birthday-awareness` skill **automatically activates**
3. ✅ Skill checks calendar for existing birthday
4. ❌ No existing birthday found
5. ❓ Skill asks via AskUserQuestion:
   ```
   "I noticed [[John Smith]]'s birthday is March 15th. Should I:

   Options:
   - Add recurring birthday event to calendar
   - Update [[John Smith]]'s file with birthday
   - Do both
   - Just note it in daily memory"
   ```
6. **User selects: "Do both"**
7. ✅ Skill creates recurring yearly birthday event
8. ✅ Skill updates John's person file
9. ✅ `/update` adds to daily note: `- Captured [[John Smith]]'s birthday (March 15th)`
10. ✅ Confirm: "Created recurring birthday event and updated [[John Smith]]'s file"

### Example 15: Person Info Auto-Update (Skill Integration)

**Input:** `/update Sarah Miller is moving to Austin next month for her new role at Tesla`

**Actions:**
1. ✅ Parse: Major life event detected (moving + job change)
2. ⚡ `person-file-management` skill **automatically activates**
3. ✅ Skill detects: Moving (major life event) + Job change (major life event)
4. ✅ Skill finds person file: `6-People/Professional/{{company_2_name}}/sarah-miller.md`
5. ✅ Skill meets AUTO-UPDATE criteria (major life events)
6. ✅ Skill updates Sarah's file:
   ```markdown
   ## Personal Notes

   - Moving to Austin next month for new role at Tesla (from [[2025-11-28 daily note]])
   ```
7. ✅ Skill updates `modified` date in frontmatter
8. ✅ `/update` adds to daily note with person link
9. ✅ Confirm: "Updated [[Sarah Miller]]'s file with relocation and job change information"

### Example 16: Multiple Skills Activation

**Input:** `/update Alex Johnson's birthday is tomorrow, and he's having surgery next week on the 5th at 2pm`

**Actions:**
1. ✅ Parse: Birthday mention + health event + calendar time
2. ⚡ `birthday-awareness` skill activates for birthday
3. ⚡ `person-file-management` skill activates for surgery (health info)
4. ✅ Birthday skill: Checks calendar, asks about creating birthday event
5. ✅ Person file skill: Auto-updates Alex's file with surgery info (meets AUTO-UPDATE criteria)
6. ✅ Calendar attendee detection: Asks about adding Alex to surgery appointment
7. ✅ All three processes complete
8. ✅ Confirm: "Created birthday event for [[Alex Johnson]], scheduled surgery appointment with him as attendee, and updated his file with surgery details"

## Edge Cases

### No Clear Action Detected

If the input doesn't clearly indicate any action type, default to:
1. Add as Quick Note with timestamp
2. Ask: "I've captured this as a quick note. Did you want me to create a task or calendar event from this?"

### Multiple Companies Referenced

If multiple companies are mentioned, ask which one the task belongs to, or create separate tasks.

### Past Time Reference (Completed Action)

If user describes a completed past action without a date parameter, treat as a completed action for TODAY:
- `/update I went to the store this morning`
- Log in Quick Notes: `- [HH:MM] Went to the store this morning`
- Don't create a task

### Future Dated Items

If user specifies a future date ("next Tuesday", "in two weeks"):
1. **Calculate the ISO date** (e.g., "next Tuesday" → `2025-12-10`)
2. **Create a calendar event** for that date (if time-specific)
3. **Add task with due date** using ISO format: `- [ ] 🟡 Task description 📅 YYYY-MM-DD`

**Examples:**
```markdown
# User says: "need to call insurance next Tuesday"
- [ ] 🟡 Call insurance 📅 2025-12-10

# User says: "submit proposal by the 15th"
- [ ] 🟡 Submit proposal 📅 2025-12-15

# User says: "follow up with Alex in two weeks"
- [ ] 🟡 Follow up with [[Alex Smith]] 📅 2025-12-21
```

**Important**: Always use ISO format `📅 YYYY-MM-DD` for machine-parseable queries.

### Missing Journal Section

If adding narrative content to an older note that doesn't have the "Journal" section:
1. Add the full Journal section (Reflections, Daily Memories, Quick Notes)
2. Maintain existing section order
3. Add entry to appropriate subsection

### Very Old Dates

If user tries to update a note from months/years ago:
1. Confirm: "You're adding a memory to [date] - is that correct?"
2. Proceed if confirmed
3. Still add cross-reference to TODAY's Quick Notes

### Ambiguous Hybrid Content

If unsure whether content is narrative, work, or hybrid:
1. Default to treating it as both
2. Add to both Daily Memories and Quick Notes
3. Mention: "Added to both Daily Memories (narrative) and Quick Notes (work context)"

## Integration

This command leverages:
- `daily-note` skill for daily note structure
- `task-system` skill for priority formatting
- `work-logging` skill for progress updates
- **`birthday-awareness` skill** for automatic birthday detection and calendar management
- **`person-file-management` skill** for automatic person file creation and updates
- **`historical-memory` skill** for capturing biographical/historical information when past events, life milestones, or "X years ago" expressions are detected - routes to biography.md, Life-Timeline.md, or person files
- Calendar MCP for event creation and conflict checking
- Person notes in 6-People/ for relationship links
- Project notes in 1-Projects/ for project links
- Life Events Timeline in 7-MOCs/ for major events
- Biography in 2-Areas/Personal/biography.md for life history context
- Annual Planning in 2-Areas/Personal/Years/ for year themes and goals
- **Obsidian block references** for cross-temporal linking
