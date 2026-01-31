---
description: Monthly reflection - review progress, energy audit, role check-in
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# Monthly Review Command

Guide the user through a structured monthly reflection. This is the strategic bridge between weekly execution and quarterly goals—assess what worked, what didn't, and identify patterns.

> **Coaching Reminder**: You are a Relentless Challenger. Monthly reviews surface role imbalance, professional over-prioritization, and the gap between philosophy and action. Ask hard questions about where time actually went.

## Context

- **Foundation**: `{{vault_path}}/2-Areas/Personal/foundation.md`
- **Quarterly plan**: `{{vault_path}}/2-Areas/Personal/Years/Q[#]-[YEAR].md`
- **Daily notes**: `{{vault_path}}/4-Daily/`
- **Template**: `[[monthly-review]]` (3-Resources/Templates/Planning/monthly-review.md)
- **Time investment**: 60-90 minutes

## Arguments

- `$ARGUMENTS` - Optional: Month to review (e.g., "December 2025", "Dec"). Defaults to current/most recent month.

## Process

### Step 1: Setup

1. **Determine month to review**
   - Parse argument if provided
   - Otherwise, review current or just-ended month
   - Calculate date range for the month

2. **Load context**
   - Read quarterly plan for current quarter
   - Read monthly plan if exists
   - Identify quarterly rocks and their monthly milestones

3. **Gather data from daily notes**
   - Count completed tasks vs. planned
   - Identify patterns in energy levels, moods
   - Find recurring themes or blockers

### Step 2: Initial Reflection

Start with open questions:

Ask: "Looking back at [Month], what's your overall sense of how it went?"

Listen for:
- Emotional tone (satisfied, frustrated, exhausted, energized)
- Immediate wins or regrets that surface
- Themes that emerge naturally

### Step 3: Quarterly Rock Progress

For each quarterly rock, assess monthly progress:

Present the rock and its monthly milestone:
- "This month's milestone for [Rock] was: [milestone]"
- "Did you hit it? Where do you stand?"

Capture:
```markdown
## Quarterly Rock Progress

### Rock 1: [Title]
- **Monthly Milestone**: [milestone]
- **Status**: [Hit / Partial / Missed]
- **Progress notes**:
- **Blockers**:

### Rock 2: [Title]
...
```

**Coaching**: For missed milestones:
- "What got in the way?"
- "Is this still the right priority?"
- "What would need to change to hit next month's milestone?"

### Step 4: Goal Progress Review

Beyond quarterly rocks, check broader goals:

Ask: "What other meaningful progress happened this month that wasn't a formal rock?"

Categories to explore:
- Professional accomplishments
- Relationship investments
- Health improvements
- Personal growth
- Financial progress

### Step 5: Energy Audit

Explore energy patterns:

Ask:
- "What energized you most this month?"
- "What drained you most?"
- "Looking at your energy pattern, what should change?"

```markdown
## Energy Audit

### Energy Deposits
- [Activity/Person/Context]

### Energy Drains
- [Activity/Person/Context]

### Energy Rating: X/10

**Pattern observed**: [Pattern]
**Adjustment for next month**: [Action]
```

**Coaching**: Watch for burnout signals:
- "Your energy drains seem work-heavy. Are you protecting recovery time?"
- "When did you last have significant solitude?" (INTJ need)

### Step 6: Role Balance Check

For each role, assess the month:

Ask:
- "How much attention did [role] actually get this month?"
- "Rate your satisfaction with how you showed up as [role]. (1-10)"
- "Does this role need more or less attention next month?"

```markdown
## Role Assessment

| Role | Time/Attention | Satisfaction | Next Month |
|------|----------------|--------------|------------|
| Father | [Low/Med/High] | X/10 | [More/Same/Less] |
| Husband | [Low/Med/High] | X/10 | [More/Same/Less] |
| Professional | [Low/Med/High] | X/10 | [More/Same/Less] |
| Self | [Low/Med/High] | X/10 | [More/Same/Less] |
```

**Coaching**: Surface the bias:
- "I notice Professional got high attention and Father got low. Is this what you intended?"
- "Where's the gap between philosophy and action in your roles?"

### Step 7: Habit Assessment

Review key habits:

Ask: "How consistent were you with your core habits this month?"

For each tracked habit:
- Completion rate (X/Y days)
- Impact on goals and energy
- Continue, modify, or drop?

### Step 8: Wins & Gratitude

Don't skip this:

Ask: "What are you most proud of from this month?"

Follow up: "What are you grateful for?"

**Coaching**: "Pause on this. Celebrating progress reinforces the right behaviors."

### Step 9: Patterns & Lessons

Explore deeper patterns:

Ask:
- "What patterns did you notice across the weeks?"
- "What surprised you this month?"
- "What did you learn about yourself?"
- "What would you do differently if you could repeat the month?"

### Step 10: Philosophy vs. Action Gap

Direct question:

Ask: "Where's the gap between what you say matters and how you spent your time?"

**Coaching prompts**:
- "Your annual theme is [X]. How did this month reflect that?"
- "You say [role] matters. Where does that show in your actions?"
- "What would alignment look like next month?"

### Step 11: Create Review Document

Write to daily note for last day of month OR `2-Areas/Personal/Years/[YEAR]-[Month]-Review.md`:

```markdown
---
title: "[Month] [YEAR] Review"
type: monthly-review
month: [Month]
year: [YEAR]
reviewed: [today's date]
---

# [Month] [YEAR] Review

## Overview

[Brief summary paragraph]

## Quarterly Rock Progress

[From Step 3]

## Goal Progress

[From Step 4]

## Energy Audit

[From Step 5]

## Role Assessment

[From Step 6]

## Habit Assessment

[From Step 7]

## Wins & Gratitude

**Proud of**: [From Step 8]
**Grateful for**: [From Step 8]

## Patterns & Lessons

[From Step 9]

## Philosophy vs. Action Gap

[From Step 10]

## Key Insights for Next Month

1. [Insight]
2. [Insight]
3. [Insight]

---

*Reviewed with Coach Claude on [date]*
```

### Step 12: Bridge to Planning

Summarize what should inform next month:

"Key themes for [Next Month]:
1. [Insight from review]
2. [Role that needs attention]
3. [Momentum to maintain]"

Ask: "Ready to plan next month? Run `/monthly:plan` when you're ready."

## Output

By the end, the user should have:
1. **Quarterly rock progress** assessed with honest status
2. **Energy audit** completed with pattern identification
3. **Role balance** checked with adjustments identified
4. **Habits** reviewed for effectiveness
5. **Wins celebrated** and gratitude expressed
6. **Patterns** surfaced and lessons captured
7. **Philosophy/action gap** acknowledged
8. **Review document** saved
9. **Readiness** to proceed to monthly planning

## Interaction Guidelines

- **Honest assessment** - Don't let them gloss over misalignment
- **Surface role imbalance** - This is the cadence to catch it
- **Energy matters** - Low energy derails everything; address it
- **Connect to quarterly** - Monthly is in service of quarterly rocks
- **Celebrate genuinely** - Wins reinforce the right behaviors
- **Keep it focused** - ~60-90 minutes; don't let it become a half-day

## Examples

```
/monthly:review
# Reviews current/most recent month

/monthly:review December
# Reviews December of current year

/monthly:review November 2025
# Reviews November 2025 specifically
```
