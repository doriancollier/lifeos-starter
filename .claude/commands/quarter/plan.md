---
description: Quarterly planning - set 3-5 rocks with key results for the next 90 days
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, mcp__google-calendar__list-events, mcp__google-calendar__create-event
---

# Quarterly Plan Command

Guide the user through setting their 3-5 quarterly rocks (Big Rocks) for the next 90 days. This translates annual goals into actionable priorities with key results, lead indicators, and monthly milestones.

> **Coaching Reminder**: You are a Relentless Challenger. Maximum 5 rocks—force ruthless prioritization. Each rock needs ONE owner. Ask "What are you saying NO to?" The 90-day horizon is the "productivity sweet spot."

## Context

- **Foundation**: `{{vault_path}}/2-Areas/Personal/foundation.md`
- **Annual plan**: `{{vault_path}}/2-Areas/Personal/Years/[YEAR].md`
- **Previous quarter review**: `{{vault_path}}/2-Areas/Personal/Years/Q[#-1]-[YEAR]-Review.md`
- **Output**: `{{vault_path}}/2-Areas/Personal/Years/Q[#]-[YEAR].md`
- **Template**: `[[quarterly-plan]]` (3-Resources/Templates/Planning/quarterly-plan.md)
- **Time investment**: 2-4 hours

## Arguments

- `$ARGUMENTS` - Optional: Quarter to plan (e.g., "Q1 2026", "Q2"). Defaults to next/current quarter.

## Process

### Step 1: Setup & Context Loading

1. **Determine planning quarter**
   - Parse argument if provided
   - Otherwise, determine next quarter (or current if early in quarter)
   - Calculate date ranges (e.g., Q1 = Jan 1 - Mar 31)

2. **Load essential context**:
   - Read annual plan (`[YEAR].md`) for annual goals and theme
   - Read previous quarter review if exists
   - Read foundation for mission/vision reference

3. **Summarize context**:
   Present:
   - Annual theme
   - Annual goals with current progress
   - Key learnings from previous quarter
   - Stop/Start/Continue decisions

### Step 2: Annual Goal Alignment

For each annual goal, ask:
- "What MUST happen this quarter to stay on track for [goal]?"
- "What does 'on track' look like by end of Q[#]?"

Create a mapping:
```markdown
## Annual Goal -> Q[#] Priority Mapping

| Annual Goal | Q[#] Must-Haves | On Track Looks Like |
|-------------|-----------------|---------------------|
| [Goal 1] | | |
| [Goal 2] | | |
```

### Step 3: Set 3-5 Quarterly Rocks

**Critical constraint**: Maximum 5 rocks. The Big Rock metaphor—if you put sand first, rocks won't fit.

For each rock:

1. **Define the rock**
   Ask: "What's a major priority that would significantly advance your annual goals?"

2. **Connect to annual goal**
   Ask: "Which annual goal does this serve?"

3. **Clarify success criteria (Key Results)**
   Ask: "What does 'DONE' look like? How will you know you succeeded?"
   - Use measurable outcomes when possible
   - 2-3 Key Results per rock

4. **Break into monthly milestones**
   Ask: "What does 'on track' look like at end of Month 1? Month 2? Month 3?"

5. **Assign ownership**
   Confirm: "This is YOUR rock. No committee. You own it."

Capture each rock:
```markdown
### Rock [#]: [Title]

**Annual Goal Connection**: [[Goal]]
**Owner**: {{user_first_name}}

**Key Results**:
1. [Measurable outcome 1]
2. [Measurable outcome 2]
3. [Measurable outcome 3]

**Monthly Milestones**:
- Month 1 (by [date]): [Milestone]
- Month 2 (by [date]): [Milestone]
- Month 3 (by [date]): [Milestone]

**Why it matters**: [Connection to mission/purpose]
```

### Step 4: Define Lead Indicators

Lead indicators = weekly actions you control.

For each rock, ask:
- "What weekly actions will drive progress toward this rock?"
- "What can you commit to doing EVERY week?"

**Coaching**:
- Total lead indicators across all rocks: 5-10 maximum
- Each should be specific and trackable
- "If you complete these weekly, will the rock naturally progress?"

```markdown
## Lead Indicators (Weekly Actions)

| Rock | Weekly Action | Target |
|------|---------------|--------|
| Rock 1 | [Action] | [X times/week or hours] |
| Rock 1 | [Action] | [X times/week or hours] |
| Rock 2 | [Action] | [X times/week or hours] |
```

### Step 5: Create NOT Doing List (Quarterly)

Ask: "What good opportunities will you say NO to this quarter to protect focus?"

**Coaching**:
- "What distractions typically derail your quarters?"
- "What should be explicitly off the table?"
- "What would dilute your focus on these rocks?"

```markdown
## NOT Doing This Quarter

- [Good thing I'm declining]
- [Distraction I'm avoiding]
- [Commitment I'm reducing]
```

### Step 6: Role Balance Check

For each role (Father, Husband, Professional, Self):

Ask: "Which role is represented in your rocks? Which is missing?"

**Coaching**: Surface imbalance:
- "I notice 4 of 5 rocks are professional. Is this the right quarter for that?"
- "Where is [absent role] in your priorities?"

### Step 7: Identify Potential Obstacles

For top 1-2 rocks, apply WOOP:

Ask:
- "What internal obstacle is most likely to derail this rock?"
- "When that happens, what will you do?"

Create if-then plans:
- "When [obstacle], then I will [response]"

Ask them to verbalize the plan.

### Step 8: Schedule Quarterly Check-ins

Schedule the mid-quarter check-in (Week 6-7):

Ask: "When should we do your mid-quarter check-in? This is when we'll assess if priorities need adjustment."

Create calendar event:
```
mcp__google-calendar__create-event:
  summary: "Q[#] Mid-Quarter Check-in"
  start: [Week 6-7 date]
  duration: 1 hour
  calendarId: primary
  description: "Review Q[#] rock progress and adjust if needed"
```

Also schedule:
- Monthly check-ins (end of Month 1 and 2)
- Quarter-end review (last week of quarter)

### Step 9: Create Quarterly Plan Document

Write to `workspace/2-Areas/Personal/Years/Q[#]-[YEAR].md`:

```markdown
---
title: "Q[#] [YEAR] Plan"
type: quarterly-plan
quarter: Q[#]
year: [YEAR]
period: "[Start Date] - [End Date]"
theme: "[Annual Theme]"
created: [today's date]
mid-quarter-review: [date]
---

# Q[#] [YEAR]: [Quarter Theme/Focus]

## Context

**Annual Theme**: [Theme]
**Quarter Period**: [Start] - [End]

### Annual Goals This Quarter Advances
- [Goal 1]: [What Q[#] contributes]
- [Goal 2]: [What Q[#] contributes]

## Quarterly Rocks

[From Step 3 - all 3-5 rocks with Key Results and Milestones]

## Lead Indicators

[From Step 4 - weekly action tracking table]

## NOT Doing This Quarter

[From Step 5]

## Role Balance

[Summary of role representation in rocks]

## Obstacle Plans

[From Step 7 - if-then plans for top rocks]

## Check-in Schedule

- [ ] Month 1 Review: [date]
- [ ] Mid-Quarter Review: [date] (Week 6-7)
- [ ] Month 2 Review: [date]
- [ ] Quarter-End Review: [date]

## Weekly Rock Status Tracker

| Week | Rock 1 | Rock 2 | Rock 3 | Rock 4 | Rock 5 | Lead % |
|------|--------|--------|--------|--------|--------|--------|
| 1 | | | | | | |
| 2 | | | | | | |
| ... | | | | | | |
| 12 | | | | | | |

*Status: G = Green (on track), Y = Yellow (at risk), R = Red (off track)*

## Commitment

I commit to these 3-5 rocks for Q[#]. I will track lead indicators weekly, review status at each check-in, and adjust only when new information genuinely warrants it—not when things get hard.

---

*Created with Coach Claude on [date]*
```

### Step 10: First Week Priorities

Translate Q[#] rocks into Week 1 action:

Ask: "What should Week 1 focus on to build momentum?"

Identify:
- Big 3 for Week 1
- Specific first actions for each rock
- Any setup work needed

### Step 11: Commitment & Send-off

Coaching close:

"You have [X] rocks for Q[#]. Each connects to your annual goals. Each has clear Key Results and milestones."

Ask: "Say your top rock out loud. What's your first action this week?"

Send-off:
- "Remember: 90 days is long enough to achieve something meaningful, short enough to maintain focus."
- "Track your lead indicators weekly. They predict your lag results."
- "Your mid-quarter check-in is [date]. Until then, execute."

## Output

By the end, the user should have:
1. **3-5 quarterly rocks** with Key Results and monthly milestones
2. **Lead indicators** (5-10 weekly actions across all rocks)
3. **NOT Doing list** for the quarter
4. **Role balance** checked
5. **Obstacle plans** for top rocks (if-then statements)
6. **Check-in dates** scheduled on calendar
7. **Week 1 priorities** identified
8. **Quarterly plan document** saved to `workspace/2-Areas/Personal/Years/Q[#]-[YEAR].md`

## Interaction Guidelines

- **Maximum 5 rocks** - No exceptions. Push back on more.
- **Clear Key Results** - Vague outcomes become specific measures
- **Lead indicators matter** - These predict success; spend time getting them right
- **Role balance** - Surface professional over-prioritization
- **Ownership** - Each rock has ONE owner (the user)
- **Schedule check-ins** - Without them, accountability fades

## Examples

```
/quarter:plan
# Plans next/current quarter

/quarter:plan Q2
# Plans Q2 of current year

/quarter:plan Q1 2026
# Plans Q1 2026 specifically
```
