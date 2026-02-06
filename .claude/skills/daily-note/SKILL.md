---
name: daily-note
description: Work with Obsidian daily notes including auto-creation, navigation, and understanding the daily note structure. Automatically creates missing daily notes and offers planning when needed. Use when the user mentions daily notes, today's tasks, daily planning, or morning/evening routines.
allowed-tools: Read, Write, Bash, AskUserQuestion, Glob
---

# Daily Note Skill

Manages daily notes in this Obsidian vault. Daily notes are the primary capture point for tasks, reflections, fears, state tracking, and alignment with personal values.

> **Note**: Daily notes include state tracking, fear logging, and alignment scoring to bridge the gap between philosophy and action.

## Vault Location

- **Daily notes directory**: `{{vault_path}}/workspace/4-Daily/`
- **Naming format**: `YYYY-MM-DD.md` (e.g., `2025-11-24.md`)
- **Template location**: `{{vault_path}}/workspace/3-Resources/Templates/daily-enhanced.md`
- **Projects directory**: `{{vault_path}}/workspace/1-Projects/Current/`

## Daily Note Structure

Each daily note contains these sections:

### YAML Frontmatter
```yaml
date: "YYYY-MM-DD"
day_of_week: "Monday"
energy_level: "medium"      # high, medium, low
state_morning:              # 1-10 state score from morning
state_evening:              # 1-10 state score from evening
alignment_score:            # 1-10 how well actions matched values
focus_areas: []
fear_faced: false           # Did they face their planned fear?
tags: ["daily"]
type: "daily-note"
```

### Main Sections

1. **Morning Check-in**:
   - **Brain Dump**: Raw capture from morning planning — what was on the user's mind before structured planning
   - Energy level (from frontmatter)
   - State score (1-10)
   - Mood
   - Intentions (result-focused)
   - Premeditatio Malorum (challenges anticipated)
   - Fear to face today

2. **Daily Rhythms** - Habit tracking aligned with 2026 goals:
   - **Non-Negotiable**: Daily Practice (audio), Daily Movement
   - **High-Impact**: Sleep Protocol, Morning Light, No caffeine after 2pm, One Appreciation ({{partner_name}}), {{child_name}} Moment
   - Track completion with checkboxes; aggregate in weekly review

3. **Today's Events** - Two tables:
   - **All-Day Events**: Events without specific times (birthdays, holidays, deadlines)
   - **Scheduled Events**: Timed events with location/meeting link

4. **Work** - Organized by company with project groupings:
   - **Quick Hits**: Tasks under 15 minutes, no project context needed
   - **{{company_1_name}}**: Projects grouped as `#### [[Project Name]] \`status\``
   - **{{company_2_name}}**: Same structure
   - **EMC**: Same structure
   - **Personal**: Same structure

   Each project section includes:
   - Obsidian link to project file
   - Status badge from project frontmatter
   - "Next:" line with `next_steps` from project frontmatter
   - Tasks with priority emoji (🔴/🟡/🟢) or blocked (🔵 + dependency)

5. **Fears** - Fear tracking section:
   - **Faced Today**: Fears confronted with type, difficulty, outcome, identity reinforced
   - **Avoided Today**: Fears avoided with reason and carry-forward decision
   - **Planned for Tomorrow**: Fear to face next day

6. **Journal** - Personal capture:
   - **Reflections**: Thoughts, observations, feelings
   - **Daily Memories**: Narrative/diary entries with 📖 emoji
   - **Quick Notes**: Work progress, timestamped logs

7. **End of Day** - Enhanced reflection:
   - State check (morning vs evening)
   - Reflection questions (best self, fell short, grateful)
   - Alignment score (1-10)
   - What went well
   - What could improve
   - Tomorrow's focus (MITs, fear, role)

8. **AI Processing Notes** - Context for AI to remember:
   - Alignment observations
   - Fear patterns
   - Role balance
   - Energy/state patterns

## Project Population

When creating or populating a daily note, projects should be dynamically pulled from `workspace/1-Projects/Current/`:

1. **Scan projects**: Read all `.md` files in `workspace/1-Projects/Current/` (including subdirectories)
2. **Read frontmatter**: Extract `title`, `status`, `company`, `next_steps`
3. **Filter**: Only include projects with `status: current`
4. **Group by company**: {{company_1_name}}, {{company_2_name}}, EMC, Personal
5. **Format each project**:
   ```markdown
   #### [[Project-Name]] `current`
   *Next: next_steps from frontmatter*

   - [ ]
   ```

**Company mapping** (from project frontmatter):
| `company` value | Section |
|-----------------|---------|
| "{{company_1_name}}" | {{company_1_name}} |
| "{{company_2_name}}" | {{company_2_name}} |
| "EMC" | EMC |
| "Personal" | Personal |

## Auto-Creation Behavior

**When to auto-create**: This skill automatically creates missing daily notes whenever:
- A command references a specific date (`/update`, `/update yesterday`, `/daily:capture`)
- A prompt mentions "today", "today's tasks", "daily note", etc.
- Any operation needs to read or write to a daily note

**Creation process**:

1. **Check if target daily note exists** at `workspace/4-Daily/YYYY-MM-DD.md`

2. **If missing, create it**:
   - Read template from template location
   - Replace template variables:
     - `{{date:YYYY-MM-DD}}` → actual date (e.g., `2025-11-28`)
     - `{{date:dddd}}` → day of week (e.g., `Friday`)
     - `{{date:ddd, MMM D, YYYY}}` → formatted date (e.g., `Fri, Nov 28, 2025`)
   - Write new daily note to `workspace/4-Daily/YYYY-MM-DD.md`
   - Silently confirm: "Created daily note for YYYY-MM-DD"

3. **After creation, check if planning is needed** (see Planning Detection below)

4. **If planning needed**, offer to run `/daily:plan`

**Planning Detection**: A daily note is considered "unplanned" if **2 or more** of these are true:
- Morning Check-in section has only placeholder text
- Energy level is still default (`energy_level: "medium"`)
- Work section has no real tasks (only placeholders)
- Today's Events tables are empty

**When to offer `/daily:plan`**:

Offer planning when **ALL** of these conditions are met:
1. Daily note was just created (not pre-existing)
2. Date is today (not past or future dates)
3. Current time is before 12:00 PM (morning hours)
4. Daily note appears unplanned (meets 2+ criteria above)
5. User is NOT already running `/daily:plan`, `/daily:eod`, or `/daily:standup`

**How to offer planning**:

Use AskUserQuestion with this format:
```
"I created today's daily note. Your day isn't fully planned yet. Would you like to run /daily:plan now?"

Options:
- "Yes, run /daily:plan" - Start guided morning planning workflow
- "No, I'll plan later" - Continue with what I was doing
```

If user selects "Yes", execute `/daily:plan` using the SlashCommand tool.

**When NOT to offer planning**:
- Date is in the past (e.g., `/update yesterday`)
- Date is in the future
- Current time is after 12:00 PM
- User is already running `/daily:plan`
- User is running `/daily:eod` (end of day)
- User is running `/daily:standup` (assumes day is done)
- Daily note already existed (don't nag about existing unplanned notes)

## Common Operations

### Find today's daily note
```bash
# Today's note path
ls "{{vault_path}}/workspace/4-Daily/$(date +%Y-%m-%d).md"
```

### Open daily note in Obsidian
```bash
open "obsidian://{{vault_path}}/workspace/4-Daily/$(date +%Y-%m-%d).md"
```

### Find recent daily notes
```bash
ls -la "{{vault_path}}/workspace/4-Daily/" | tail -10
```

### Search for content in daily notes
```bash
grep -r "search term" "{{vault_path}}/workspace/4-Daily/"
```

## Task Formatting

Tasks in daily notes use priority emojis:

| Priority | Format | Meaning |
|----------|--------|---------|
| 🔴 | `- [ ] 🔴 Task` | A priority - critical, do first |
| 🟡 | `- [ ] 🟡 Task` | B priority - important |
| 🟢 | `- [ ] 🟢 Task` | C priority - nice to have |
| 🔵 | `- [ ] 🔵 Task - Waiting: [dep]` | Blocked on dependency |

**Numbered A-priorities**: When a task is truly the top priority, number it:
- `- [ ] 🔴1. Call passport office` (most critical)
- `- [ ] 🔴2. Fix CVE blocker` (second most critical)

Max 5 numbered A-priority tasks per day.

## Integration with Other Skills

- Use **task-system** skill for understanding task priorities
- Use **obsidian-open** skill to open notes in Obsidian UI
- Use **meeting-prep** skill when daily note references upcoming meetings
- Use **calendar-awareness** skill to populate Today's Events section
- Use **weekly-review** skill to aggregate Daily Rhythms compliance across the week

## Examples

### Creating a new daily note
1. Copy template from `workspace/3-Resources/Templates/daily-enhanced.md`
2. Replace date variables
3. Save to `workspace/4-Daily/YYYY-MM-DD.md`
4. Populate with current projects (optional, done during planning)

### Finding incomplete tasks from a specific day
```bash
grep -E "^- \[ \]" "{{vault_path}}/workspace/4-Daily/2025-11-24.md"
```

### Auto-creation workflow example

**Scenario**: User runs `/update need to call doctor about prescription` at 9:30 AM, but today's daily note doesn't exist yet.

**Workflow**:
1. ✅ `daily-note` skill activates (update command references daily note)
2. ✅ Check: Daily note for today doesn't exist
3. ✅ Read template and replace variables
4. ✅ Write new file to `workspace/4-Daily/YYYY-MM-DD.md`
5. ✅ Check planning criteria (Morning empty, no tasks, etc.)
6. ❓ Ask user if they want to run `/daily:plan`
7. **If "Yes"**: Execute `/daily:plan` → User goes through guided planning
8. **If "No"**: Continue with `/update` → Add task to daily note

## Past Day Memory Routing

When the user shares memories about a **past day within 7 days**, route them to the correct daily note rather than today's note.

### Detection

Look for temporal references that indicate a past day:

| Pattern | Example | Calculation |
|---------|---------|-------------|
| "yesterday" | "Yesterday I met with..." | Today - 1 day |
| "last night" | "Last night we went..." | Today - 1 day |
| Day name | "On Saturday we..." | Most recent past Saturday |
| "the Xth" | "On the 5th I..." | That date in current/previous month |
| "X days ago" | "Two days ago..." | Today - X days |
| Explicit date | "On December 5th..." | That specific date |

**7-day limit**: Only apply this routing for memories within 7 days. Older memories should use the `historical-memory` skill instead.

### Routing Logic

When a memory references a past day:

1. **Identify the target date** from temporal references
2. **Check if target daily note exists**:
   - If not, create it from template (same as auto-creation behavior)
3. **Add full memory to target day's note**:
   - Location: `### Daily Memories` section
   - Format: Full narrative detail with [[wikilinks]] for people
4. **Add brief reference to today's note**:
   - Location: `### Quick Notes` section
   - Format: `- [HH:MM] Recalled memories from [target date]: [1-line summary per memory]`

### Examples

**User says**: "Yesterday I met with Alex. It was a good meeting. He's planning an event on March 3rd, 2026."

**Target day (Dec 6) gets**:
```markdown
### Daily Memories

- Met with [[Alex Chen]] - good meeting, learned several things. He's planning an event on **March 3rd, 2026** to reveal all the work he's been up to
```

**Today (Dec 7) gets**:
```markdown
### Quick Notes

- [16:30] Recalled memories from Dec 6: Alex meeting (March 3rd event reveal)
```

**Mixed-day example**: "Yesterday {{child_name}} and I had a driving lesson, and today {{partner_name}} and I went to lunch."

Route each memory to its respective day:
- "{{child_name}} driving lesson" → Yesterday's note (full details)
- "Lunch with {{partner_name}}" → Today's note (full details, since it's today)
- Today's Quick Notes: Reference to recalled memories from yesterday

### Edge Cases

| Situation | Behavior |
|-----------|----------|
| Past day's note doesn't exist | Create it from template first, then add memory |
| Memory is >7 days old | Use `historical-memory` skill instead (routes to biography/timeline) |
| Mixed today + past memories | Route each to correct day, today's note gets references |
| Ambiguous date ("last week") | Ask for clarification or default to 7 days ago |
| Future date mentioned in memory | That's context within the memory, not the target date |

### Integration

This behavior activates whenever memories are being captured via:
- `/update` command with past-day references
- `work-logging` skill with narrative content
- Direct conversation when user shares "what happened" stories
- `/daily:plan` when reviewing yesterday

---

## Enhancements

These additions integrate the multi-horizon planning framework from [[planning-horizons]] and the coaching prompts from [[framework-prompts]].

### Energy Assessment

Start each morning planning session with a 4-dimension energy check:

```markdown
## Energy Assessment
- Physical: _/10
- Emotional: _/10
- Mental: _/10
- Spiritual: _/10

Energy allocation plan:
- High-energy window: [time] → [high-value work]
- Recovery needed: [yes/no] → [action]
```

**Coaching prompts**:
- "What's my energy stock right now? (Physical/Emotional/Mental/Spiritual)"
- "Am I matching high-energy periods to high-value work?"
- When physical energy is low: "When will you actually rest?"

### Role Awareness

During morning planning, surface role context:

**Prompt to include**:
- "Which roles will I embody today? How will I show up in each?"
- "What's one way each role can enrich another today?"

**Key roles**: Provider, Father, Partner, Self, {{company_1_name}}, {{company_2_name}}, EMC

**End-of-day role reflection**:
- "Which roles did I honor? Which were neglected?"
- "Where did one role enrich another today?"

### Weekly Big 3 Reference

At the start of daily planning, surface the Weekly Big 3:

```markdown
### Weekly Big 3 Status
1. [ ] [Weekly Priority 1] - Progress: ___
2. [ ] [Weekly Priority 2] - Progress: ___
3. [ ] [Weekly Priority 3] - Progress: ___

**Today's contribution**: Which Big 3 does today's plan advance?
```

**Coaching prompts**:
- "Is today's plan aligned with your quarterly rocks?"
- "At least one A-task should advance a weekly rock"
- "If Big 3 items haven't been scheduled, flag it"

### Values Check

Connect daily intentions to core values (Courage and Love):

**Morning prompts**:
- "How will I embody courage and love today?"
- "Does this task advance a monthly milestone?"
- "What challenges might I face today? How will I handle adversity with grace?"

**Evening reflection**:
- "Did I live my values today? Where did I slip?"
- "Did I show up with courage AND love, or just efficiency?"

### Horizon Connection

Every daily note should connect upward through the planning cascade:

```
Foundation (Identity/Mission/Vision)
    ↓
Annual (3-5 goals, yearly theme)
    ↓
Quarterly (3-5 rocks, 90-day focus)
    ↓
Monthly (theme, milestones)
    ↓
Weekly (Big 3, role-based rocks)
    ↓
Daily (A/B/C priorities) ← YOU ARE HERE
```

**Key question during planning**:
- "What quarterly rock does today's plan advance?"
- "Does this A-task connect to my weekly Big 3?"
- "Am I being productive or just busy?"

**Cross-horizon alignment check table**:

| When Planning | Reference | Key Question |
|---------------|-----------|--------------|
| Daily | Weekly Big 3 | "Which rock does this advance?" |
| Weekly | Quarterly rocks | "Am I on track for Q goals?" |

### Related References

- [[planning-horizons]] — The complete multi-horizon planning framework
- [[framework-prompts]] — Full library of coaching prompts by context
- [[foundation]] — Identity, mission, vision, principles
