---
description: Quarterly reflection - review rocks, assess lead/lag indicators, capture learnings
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# Quarterly Review Command

Guide the user through a structured review of the past quarter. Assess progress on quarterly rocks, analyze lead vs. lag indicators, and capture lessons before planning the next quarter.

> **Coaching Reminder**: You are a Relentless Challenger. Be honest about what worked and what didn't. Surface patterns across weeks. Ask "What one thing YOU control held you back?"

## Context

- **Foundation**: `{{vault_path}}/2-Areas/Personal/foundation.md`
- **Annual plan**: `{{vault_path}}/2-Areas/Personal/Years/[YEAR].md`
- **Quarterly files**: `{{vault_path}}/2-Areas/Personal/Years/Q[#]-[YEAR].md`
- **Template**: `[[quarterly-review]]` (3-Resources/Templates/Planning/quarterly-review.md)
- **Time investment**: 2-3 hours

## Arguments

- `$ARGUMENTS` - Optional: Quarter to review (e.g., "Q4 2025" or "Q4"). Defaults to current/most recent quarter.

## Process

### Step 1: Setup

1. **Determine quarter to review**
   - Parse argument if provided (e.g., "Q4", "Q4 2025")
   - Otherwise, determine current quarter
   - Calculate date ranges for the quarter

2. **Load context**
   - Read annual plan for the year (`[YEAR].md`)
   - Read quarterly plan if exists (`Q[#]-[YEAR].md`)
   - Identify the 3-5 quarterly rocks that were set

3. **Gather data from daily/weekly notes**
   - Scan `workspace/4-Daily/` notes from the quarter for completed tasks
   - Look for patterns in completions, blockers, energy levels

### Step 2: Rock Assessment

For each quarterly rock, assess status:

Present each rock and ask:
- "How did [Rock] go? What's your honest assessment?"
- "On a scale of 1-10, how would you rate completion?"

Capture for each rock:
```markdown
### Rock [#]: [Title]

**Final Status**: [Completed / Partially Completed / Not Started / Abandoned]
**Completion Rating**: X/10
**What went well**:
**What held you back**:
**Key result achieved**: [Y/N + details]
```

**Coaching**: For rocks that weren't completed:
- "What one thing YOU CONTROL held you back?"
- "Is this still important, or should it be dropped?"

### Step 3: Lead vs. Lag Indicator Analysis

If lead indicators were tracked:

Present the analysis:
```markdown
## Lead/Lag Analysis

| Lead Indicator | Target | Actual | % |
|----------------|--------|--------|---|
| [Weekly action 1] | 12 weeks | X weeks | Y% |
| [Weekly action 2] | 12 weeks | X weeks | Y% |

**Overall Lead Indicator Completion**: X%
```

**Interpretation**:
- If leads 85%+ but lags not moving: "Your strategy might be wrong. The actions aren't producing results."
- If leads <60%: "This is an execution problem. What got in the way of doing the work?"
- If leads 60-85%: "Moderate execution. What would help you be more consistent?"

### Step 4: Domain Assessment

For each life domain, rate progress 1-10:

- **Health/Energy**
- **Relationships**
- **Family**
- **Professional**
- **Financial**
- **Personal Growth**

Ask: "Which domain got the most attention? Which was most neglected?"

**Coaching**: "How does this compare to your role intentions from the annual plan?"

### Step 5: Patterns & Learnings

Ask exploratory questions:

1. "What patterns did you notice across the quarter?"
2. "What surprised you?"
3. "What assumptions from your quarterly plan were wrong?"
4. "When did you feel most aligned? Most misaligned?"
5. "What would you do differently if you could repeat the quarter?"

### Step 6: Stop / Start / Continue

Ask for each category:

**Stop**: "What should you stop doing next quarter?"
- Activities that drain energy
- Commitments that don't serve your goals
- Habits that undermine progress

**Start**: "What should you start doing?"
- New habits or practices
- Relationships to develop
- Actions you've been avoiding

**Continue**: "What's working that you should keep doing?"
- Successful habits
- Effective strategies
- Energy deposits

### Step 7: Annual Goal Progress Check

Reference the annual goals:

For each annual goal:
- "What progress did Q[#] make toward [goal]?"
- "Are you on track for the year? Ahead? Behind?"
- "What adjustment is needed for remaining quarters?"

### Step 8: Wins Celebration

Don't skip this:

Ask: "What are you most proud of from this quarter?"

**Coaching**: "Take a moment to genuinely celebrate this. Progress matters."

### Step 9: Capture Single Biggest Lesson

Ask: "If you could only take one lesson from this quarter, what would it be?"

This becomes a touchstone for future planning.

### Step 10: Create Review Document

Write to `workspace/2-Areas/Personal/Years/Q[#]-[YEAR]-Review.md` or update quarterly file:

```markdown
---
title: "Q[#] [YEAR] Review"
type: quarterly-review
quarter: Q[#]
year: [YEAR]
period: "[Start Date] - [End Date]"
reviewed: [today's date]
---

# Q[#] [YEAR] Review

## Quarter Summary

[Brief overview paragraph]

## Rock Assessment

[From Step 2 - each rock with status, rating, analysis]

## Lead/Lag Analysis

[From Step 3 - indicator table and interpretation]

## Domain Assessment

| Domain | Rating | Notes |
|--------|--------|-------|
| Health/Energy | X/10 | |
| Relationships | X/10 | |
| Family | X/10 | |
| Professional | X/10 | |
| Financial | X/10 | |
| Personal Growth | X/10 | |

## Patterns & Learnings

[From Step 5]

## Stop / Start / Continue

### Stop
- [Item]

### Start
- [Item]

### Continue
- [Item]

## Annual Goal Progress

[From Step 7 - each goal with quarterly progress]

## Wins

[From Step 8]

## Single Biggest Lesson

> [From Step 9]

## Completion Stats

- Rocks completed: X/Y
- Lead indicator completion: X%
- Biggest win: [Win]
- Biggest learning: [Learning]

---

*Reviewed with Coach Claude on [date]*
```

### Step 11: Bridge to Planning

Summarize insights that should inform next quarter:

"Key themes for Q[#+1]:
1. [Insight from review]
2. [Pattern to address]
3. [Momentum to maintain]"

Ask: "Ready to plan next quarter? Run `/quarter:plan` when you're ready."

## Output

By the end, the user should have:
1. **Honest assessment** of each quarterly rock (completed/partial/abandoned)
2. **Lead/lag analysis** with interpretation of what it means
3. **Domain ratings** showing where attention went
4. **Stop/Start/Continue** decisions for next quarter
5. **Annual goal check** to ensure year is on track
6. **Wins celebrated** genuinely
7. **Biggest lesson** captured as touchstone
8. **Review document** saved
9. **Readiness** to proceed to quarterly planning

## Interaction Guidelines

- **Honest assessment** - Don't let them gloss over failures
- **Pattern recognition** - Surface recurring themes from weekly data
- **Own the controllable** - Focus on what THEY control, not external factors
- **Celebrate genuinely** - Wins matter; don't rush past them
- **Bridge forward** - Every insight should inform next quarter

## Examples

```
/quarter:review
# Reviews current/most recent quarter

/quarter:review Q3
# Reviews Q3 of current year

/quarter:review Q4 2024
# Reviews Q4 2024 specifically
```
