---
description: Monthly retrospective using 4Ls format (Liked, Learned, Lacked, Longed For) plus Energy Audit
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Monthly Retrospective Command

Guide the user through a **60-90 minute monthly retrospective** using the 4Ls format plus Energy Audit and Role Balance check. This is a deeper systemic review than the weekly retrospective.

> **Coaching Reminder**: Monthly retrospectives catch patterns that weekly ones miss. This is about systems and sustainability, not just tasks. Apply the Prime Directive with self-compassion.

## Context

- **Daily notes directory**: `{{vault_path}}/4-Daily/`
- **Template**: `[[monthly-retro]]` in `workspace/3-Resources/Templates/Retrospectives/`
- **Output location**: `workspace/3-Resources/Reviews/Monthly/YYYY-MM-retro.md`
- **Role documents**: `workspace/2-Areas/Personal/Roles/`

## Process

Execute these steps **conversationally**, allowing deeper exploration than weekly retros.

### Step 1: Gather Context (10 min)

1. **Get month boundaries**
   ```bash
   # First and last day of the month being reviewed
   date -v1d +%Y-%m-%d  # First of current month
   date -v1d -v+1m -v-1d +%Y-%m-%d  # Last of current month
   ```

2. **Aggregate month data**:
   - Total tasks completed vs. planned
   - Weekly retro summaries (if available)
   - Energy levels across weeks
   - Fears faced count
   - Meeting load
   - Goals progress

3. **Scan for patterns**:
   - Recurring carryover tasks
   - Chronic energy drains
   - Repeated learnings (not yet applied)

4. **Present summary**:
   ```
   "This month: X tasks completed, Y fears faced, Z weekly retros done.
   Energy trend: [increasing/stable/declining].
   Key projects touched: [list]."
   ```

### Step 2: Set the Stage (5 min)

Open with Prime Directive and set intention:
> "This is about understanding the month, not judging it. We're looking for patterns and systems, not blame."

Ask: "What's your overall feeling about this month, 1-10?"

Ask: "In one sentence, how would you describe this month?"

### Step 3: 4Ls Analysis (30 min)

#### Liked (What energized and worked) - 8 min

Ask: "What energized you this month? What worked well?"

Prompt if needed:
- "What accomplishments are you proud of?"
- "Which relationships flourished?"
- "What habits served you well?"
- "When did you feel most alive/in flow?"

**Capture 5-7 items.**

#### Learned (Skills, insights, patterns) - 8 min

Ask: "What did you learn this month—skills, insights, patterns?"

Prompt if needed:
- "What surprised you about yourself?"
- "What do you understand now that you didn't before?"
- "What patterns became visible?"
- "What truths did you avoid acknowledging until now?"

**Capture 4-6 items.**

#### Lacked (Gaps in resources, support, systems) - 8 min

Ask: "What was missing this month? Resources, support, systems?"

Prompt if needed:
- "What did you need but not have?"
- "Where did systems break down?"
- "What skills would have helped?"
- "What support was missing?"

**Capture 3-5 items.**

**Coaching moment**: If lacked items are within control, ask: "What stopped you from getting this?"

#### Longed For (What would make next month better) - 6 min

Ask: "What do you long for? What would make next month better?"

Prompt if needed:
- "If you could change one thing, what would it be?"
- "What would your ideal month look like?"
- "What are you hungry for that you're not getting?"

**Capture 2-4 items.**

### Step 4: Energy Audit (15 min)

This section identifies what creates vs. drains energy for sustainable performance.

#### Energy-Creating Activities

Ask: "What activities gave you energy this month?"

Categories to explore:
- Work activities (which projects, tasks, meetings)
- Relationships (which interactions)
- Personal practices (exercise, hobbies, rest)
- Environments (where were you most energized)

**Capture 5-8 items.**

#### Energy-Draining Activities

Ask: "What activities drained your energy this month?"

Categories to explore:
- Work activities (which were exhausting)
- Relationships (which interactions depleted you)
- Obligations (what felt like a chore)
- Environments (where did you feel drained)

**Capture 5-8 items.**

#### Energy Balance Assessment

Present the ratio:
- "You identified X energy-creators and Y energy-drainers."

Ask: "Is this sustainable? What needs to change?"

Create three lists:
- **Do More**: Activities to increase
- **Do Less**: Activities to decrease
- **Stop Doing**: Activities to eliminate

### Step 5: Role Balance Check (10 min)

Review each role for balance:

| Role | Attention This Month | Health (1-10) |
|------|---------------------|---------------|
| Father | | |
| Partner | | |
| Professional (AB) | | |
| Professional (144) | | |
| Professional (EMC) | | |
| Self | | |

For each role, ask:
- "Did this role get appropriate attention?"
- "Is this role thriving, maintaining, or declining?"

**Flag imbalances**:
- If any role is below 5, it needs priority attention next month
- If Professional roles dominate, remind: "Is work crowding out what matters most?"

### Step 6: Generate Insights (5 min)

Based on the 4Ls and Energy Audit, surface patterns:

Ask: "What are the 2-3 biggest insights from this month?"

Connect to identity/mission:
- "How does this relate to becoming 'strong, loving, and courageous'?"
- "Where did you protect what matters? Where did you fail to?"
- "Are you enjoying the journey, or just optimizing it?"

### Step 7: Action Items (10 min)

Ask: "What 1-3 specific changes will you make next month?"

**Action Item Format:**
```
| Action | Category | Deadline | Success Metric |
|--------|----------|----------|----------------|
| [Action] | [System/Habit/Relationship/Work] | [Date] | [Metric] |
```

Rules:
- Maximum 3 actions
- Mix categories (don't make all actions work-related)
- Each must have clear success metric
- Consider adding a "Stop Doing" action

### Step 8: Close

Summarize:
```markdown
## Monthly Retrospective Summary - [Month Year]

**Overall Month Score**: X/10
**One-Sentence Summary**: [their sentence from Step 2]

**Top Wins**:
1. [biggest Liked]
2. [second biggest]

**Key Learnings**:
1. [most important]
2. [second]

**Energy Insight**: [primary do more/do less/stop]

**Role Needing Attention**: [lowest scoring role]

**Focus for Next Month**: [primary action]
```

Closing prompt:
- "Pain + Reflection = Progress. You've done the reflection. Now let's make next month a chapter you're proud of."

## Output

Create the monthly retro document:

```markdown
---
title: "[Month] [Year] Retrospective"
type: retrospective
period: monthly
date: YYYY-MM-DD
overall_score: X
---

# [Month] [Year] Retrospective

**Overall Score**: X/10
**One-Sentence Summary**: [summary]

## 4Ls Analysis

### Liked (What energized and worked)
1.
2.
3.
4.
5.

### Learned (Skills, insights, patterns)
1.
2.
3.
4.

### Lacked (Gaps in resources, support, systems)
1.
2.
3.

### Longed For (What would make next month better)
1.
2.

## Energy Audit

### Energy-Creating Activities
-

### Energy-Draining Activities
-

### Changes Needed
**Do More**:
-

**Do Less**:
-

**Stop Doing**:
-

## Role Balance

| Role | Attention | Health (1-10) | Notes |
|------|-----------|---------------|-------|
| Father | | | |
| Partner | | | |
| Professional | | | |
| Self | | | |

**Role needing attention next month**: [role]

## Key Insights
1.
2.
3.

## Action Items

| Action | Category | Deadline | Success Metric |
|--------|----------|----------|----------------|
| | | | |
| | | | |
| | | | |

## Notes

---
*Next monthly retro scheduled for: [last Friday of next month]*
```

**Location**: `workspace/3-Resources/Reviews/Monthly/YYYY-MM-retro.md`

## Interaction Guidelines

- **Allow 60-90 minutes** - Don't rush deep reflection
- **Start with wins** - Build momentum before gaps
- **Watch for patterns** - Connect to previous months if available
- **Energy is key** - The Energy Audit reveals sustainability issues
- **Role balance matters** - Don't let work dominate every month
- **INTJ consideration** - Include emotional/relational insights, not just systems
- **Blameless** - Focus on systems, not character flaws

## Examples

**Example Energy-Creating**:
- Deep work on product strategy (flow state)
- 1:1 walks with {{partner_name}}
- Evening reading time
- Morning coffee ritual before work

**Example Energy-Draining**:
- Back-to-back video calls
- Slack notification interruptions
- Ambiguous project requirements
- Late-night work sessions

**Example Role Balance Issue**:
"Partner role dropped to 4/10 this month. EMC work is bleeding into personal time. Need to re-establish boundaries."
