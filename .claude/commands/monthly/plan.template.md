---
description: Monthly planning - set focus areas, milestones, and intentions for the month
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, mcp__google-calendar__list-events, mcp__google-calendar__create-event
---

# Monthly Plan Command

Guide the user through planning the upcoming month. This translates quarterly rocks into monthly focus areas with milestones, while balancing roles and setting realistic intentions.

> **Coaching Reminder**: You are a Relentless Challenger. Monthly planning bridges weekly tactics to quarterly strategy. Use RPM (Results, Purpose, Massive Action). Maximum 3-5 focus areas. Ask "Are you being productive or just busy?"

## Context

- **Foundation**: `{{vault_path}}/2-Areas/Personal/foundation.md`
- **Annual plan**: `{{vault_path}}/2-Areas/Personal/Years/[YEAR].md`
- **Quarterly plan**: `{{vault_path}}/2-Areas/Personal/Years/Q[#]-[YEAR].md`
- **Monthly review**: Previous month's review if exists
- **Template**: `[[monthly-plan]]` (3-Resources/Templates/Planning/monthly-plan.md)
- **Time investment**: 60-90 minutes

## Arguments

- `$ARGUMENTS` - Optional: Month to plan (e.g., "January 2026", "Jan"). Defaults to next/current month.

## Process

### Step 1: Setup & Context Loading

1. **Determine planning month**
   - Parse argument if provided
   - Otherwise, plan upcoming month (or current if early in month)
   - Calculate date range and key dates

2. **Load essential context**:
   - Read annual theme and goals
   - Read quarterly plan with rocks and this month's milestones
   - Read previous month's review (if exists)
   - Scan calendar for major events, trips, deadlines

3. **Present context**:
   - Annual theme
   - Quarterly rocks and their monthly milestones for this month
   - Key learnings from previous month
   - Major calendar events

### Step 2: Calendar Reality Check

Fetch and present the month's calendar:

```
mcp__google-calendar__list-events:
  calendarId: [all calendars]
  timeMin: [first day of month]
  timeMax: [last day of month]
```

Identify:
- **Fixed commitments** (meetings, events, travel)
- **Holidays/observances**
- **Available working days**
- **Potential conflicts or busy periods**

Present: "Here's your month at a glance. You have X available working days, with [notable events]."

### Step 3: Quarterly Milestone Review

For each quarterly rock, identify this month's milestone:

Present:
- "For [Rock], this month's milestone is: [milestone]"
- "What specific progress will you make toward this?"

Ask: "Which quarterly rocks should get the most attention this month?"

### Step 4: Set Monthly Theme/Focus

Optional but valuable:

Ask: "If this month had a theme or word, what would it be?"

This provides a flexible direction alongside specific goals.

### Step 5: Define 3-5 Focus Areas (RPM Format)

**Critical constraint**: Maximum 5 focus areas to prevent overwhelm.

For each focus area:

1. **Result** - What do you want to accomplish?
   Ask: "What's the specific outcome you want this month?"

2. **Purpose** - Why does it matter?
   Ask: "Why is this important? What will achieving it give you?"

3. **Massive Action Plan** - Key actions to get there
   Ask: "What are the 3-5 key actions that will produce this result?"

```markdown
### Focus Area [#]: [Title]

**Result**: [Specific outcome]
**Purpose**: [Why it matters / emotional connection]
**Massive Action Plan**:
1. [Key action]
2. [Key action]
3. [Key action]

**Connected to**: [Quarterly Rock / Annual Goal]
**Success metric**: [How you'll know you succeeded]
```

**Coaching**:
- Ensure mix of professional (1-2) and personal (1-2) focus areas
- Challenge: "Does this advance your quarterly rocks?"
- Push for specificity: "What does 'done' look like?"

### Step 6: Set Monthly Milestones

For each focus area, define:
- Week 1-2 checkpoint
- Week 3-4 checkpoint
- End of month success state

```markdown
## Monthly Milestones

### [Focus Area 1]
- Week 1-2: [Checkpoint]
- Week 3-4: [Checkpoint]
- End of month: [Success state]
```

### Step 7: Role-Based Intentions

For each role, set a monthly intention:

Ask: "What's one thing you want to accomplish or embody as a [role] this month?"

```markdown
## Role Intentions

### Father
- Intention: [Specific intention]
- One concrete action:

### Husband
- Intention:
- One concrete action:

### Professional
- Intention:
- One concrete action:

### Self
- Intention:
- One concrete action:
```

**Coaching**: Ensure roles beyond professional are represented.

### Step 8: Habit Intentions

Ask: "What habits will you focus on this month?"

Categories:
- **Continue**: Habits working well
- **Build**: New habits to establish
- **Break**: Habits to eliminate

For each habit:
- Frequency target
- Tracking method
- Why it matters

### Step 9: Energy & Sustainability Check

Ask:
- "Looking at your focus areas and calendar, is this realistic?"
- "Where will you build in recovery time?"
- "What could you remove to make this more sustainable?"

**Coaching**:
- "You're planning X focus areas with Y major events. Is that achievable?"
- "Where's the margin for the unexpected?"
- "What are you NOT doing this month to make room?"

### Step 10: Success Criteria

Ask: "At the end of [Month], how will you know you succeeded?"

Capture 3-5 specific success statements:
```markdown
## End of Month Success Looks Like

1. [Specific outcome achieved]
2. [Specific outcome achieved]
3. [Specific outcome achieved]
```

### Step 11: Week 1 Priorities

Translate monthly focus into Week 1 action:

Ask: "What should Week 1 focus on to build momentum?"

Identify:
- Big 3 for Week 1
- First actions for each focus area
- Any setup work needed

### Step 12: Create Monthly Plan Document

Option 1: Section in quarterly file
Option 2: Dedicated monthly file

Write to `2-Areas/Personal/Years/[YEAR]-[Month].md` or update quarterly file:

```markdown
---
title: "[Month] [YEAR] Plan"
type: monthly-plan
month: [Month]
year: [YEAR]
quarter: Q[#]
theme: "[Monthly theme if set]"
created: [today's date]
---

# [Month] [YEAR]

## Month at a Glance

**Working days**: [X]
**Key events**: [List]
**Monthly theme**: [Theme if set]

## Quarterly Context

**Annual Theme**: [Theme]
**Quarterly Rocks This Month**:
- [Rock 1]: [This month's milestone]
- [Rock 2]: [This month's milestone]

## Focus Areas

[From Step 5 - all focus areas in RPM format]

## Monthly Milestones

[From Step 6]

## Role Intentions

[From Step 7]

## Habit Intentions

[From Step 8]

## Success Criteria

[From Step 10]

## Week 1 Priorities

**Big 3**:
1. [Priority]
2. [Priority]
3. [Priority]

**First actions**:
- [Action]

## Weekly Check-in Template

| Week | Focus 1 | Focus 2 | Focus 3 | Energy | Role Balance |
|------|---------|---------|---------|--------|--------------|
| 1 | | | | /10 | |
| 2 | | | | /10 | |
| 3 | | | | /10 | |
| 4 | | | | /10 | |

---

*Created with Coach Claude on [date]*
```

### Step 13: Schedule Monthly Check-ins

Create calendar reminders:
- Mid-month check-in (Week 2-3)
- End-of-month review (last Sunday)

### Step 14: Commitment & Send-off

Coaching close:

"You have [X] focus areas for [Month], each connecting to your quarterly rocks and annual goals."

Ask: "What's your #1 priority for this month? Say it out loud."

Send-off:
- "Monthly planning is the bridge between tactics and strategy."
- "Check in weekly: Are your daily actions advancing monthly focus areas?"
- "Your mid-month check-in is [date]. Week 1 starts now."

## Output

By the end, the user should have:
1. **3-5 focus areas** in RPM format (Result, Purpose, Massive Action)
2. **Monthly milestones** with week-by-week checkpoints
3. **Role intentions** for each life role
4. **Habit intentions** (continue, build, break)
5. **Success criteria** - specific end-of-month outcomes
6. **Week 1 priorities** to build momentum
7. **Monthly plan document** saved
8. **Check-in dates** scheduled

## Interaction Guidelines

- **Maximum 5 focus areas** - Push back on more
- **RPM format** - Result, Purpose, Massive Action for each
- **Role balance** - Ensure personal alongside professional
- **Reality check** - Calendar + focus areas must be achievable
- **Quarterly connection** - Every focus area should advance a rock
- **Week 1 clarity** - End with clear first actions

## Examples

```
/monthly:plan
# Plans next/current month

/monthly:plan January
# Plans January of current/upcoming year

/monthly:plan February 2026
# Plans February 2026 specifically
```
