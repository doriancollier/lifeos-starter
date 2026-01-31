---
description: Comprehensive weekly review with Planning System 2.0 frameworks
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# Weekly Review Command

Guide the user through a comprehensive weekly review as their **Level 10 Coach**. This is the linchpin connecting quarterly strategy to daily execution.

> **Coaching Reminder**: A week is "short enough to control, but long enough to be flexible." This review transforms productivity everywhere. Push for honest reflection, celebrate identity-consistent action, and surface patterns.

## Context

- **Daily notes directory**: `{{vault_path}}/4-Daily/`
- **Projects directory**: `{{vault_path}}/1-Projects/Current/`
- **Year file**: `{{vault_path}}/2-Areas/Personal/Years/2026.md`
- **Foundation**: `{{vault_path}}/2-Areas/Personal/foundation.md`

## Review Flow

Execute these steps **sequentially**, integrating the weekly-review skill for deep analysis.

### Step 1: Gather Week's Data

**Collect all daily notes from the past 7 days:**

```bash
for i in {0..6}; do
  d=$(date -v-${i}d +%Y-%m-%d)
  echo "=== ${d} ==="
  cat "{{vault_path}}/4-Daily/${d}.md" 2>/dev/null | head -100
done
```

**Extract key metrics:**
- Tasks completed vs. planned
- A-priority completion rate
- Fears faced vs. avoided
- Alignment scores (if captured)
- Energy levels across the week

### Step 2: Quadrant Assessment (Eisenhower Matrix)

**Analyze time distribution across the four quadrants:**

| Quadrant | Description | Target | Actual |
|----------|-------------|--------|--------|
| Q1 | Urgent + Important (crises, deadlines) | 15-25% | ? |
| Q2 | Not Urgent + Important (planning, prevention, relationships) | 50-65% | ? |
| Q3 | Urgent + Not Important (interruptions, some meetings) | 10-15% | ? |
| Q4 | Not Urgent + Not Important (time wasters, escape activities) | <10% | ? |

**Categorize completed tasks:**
- Review each completed task from the week
- Assign to quadrant
- Calculate percentages

**Present analysis:**
```markdown
### Quadrant Distribution

| Quadrant | Hours | Percentage | Target | Status |
|----------|-------|------------|--------|--------|
| Q1 (Urgent+Important) | X | X% | 15-25% | [On/Over/Under] |
| Q2 (Important, Not Urgent) | X | X% | 50-65% | [On/Over/Under] |
| Q3 (Urgent, Not Important) | X | X% | 10-15% | [On/Over/Under] |
| Q4 (Neither) | X | X% | <10% | [On/Over/Under] |
```

**Coaching questions:**
- If Q1 is high: "You're in reactive mode. What prevention (Q2) would reduce crises?"
- If Q2 is low: "Your strategic work is being crowded out. What will you protect next week?"
- If Q3 is high: "You're being driven by others' urgency. What can you delegate or decline?"
- If Q4 is high: "What are you avoiding? This is escape behavior."

### Step 3: Leverage Audit

**Identify highest and lowest leverage activities:**

Ask: "What was your highest-leverage activity this week?"

**Leverage criteria:**
- Did it build a system that saves time repeatedly?
- Did it create an asset (code, content, relationship) that compounds?
- Did it require YOUR specific knowledge and judgment?
- Could it have been delegated at 70% quality?

**Present:**
```markdown
### Leverage Audit

**Highest Leverage Activities**:
1. [Activity] - [Why it's high leverage]
2. [Activity] - [Why it's high leverage]

**Lowest Leverage Activities** (consider eliminating/delegating):
1. [Activity] - [Could be: delegated/automated/eliminated]
2. [Activity] - [Could be: delegated/automated/eliminated]

**Leverage Ratio**: [High-leverage hours] / [Total work hours] = X%
```

**Target**: At least 40% of work hours should be high-leverage.

**Coaching**: "You spent X hours on low-leverage work. What system could you build to reclaim that time?"

### Step 4: Role Check-In

**Review each role's attention this week:**

| Role | Time Invested | Satisfaction (1-10) | Needs More/Less |
|------|---------------|---------------------|-----------------|
| Father | X hours | ? | ? |
| Partner | X hours | ? | ? |
| Provider ({{company_1_name}}) | X hours | ? | ? |
| Provider ({{company_2_name}}) | X hours | ? | ? |
| Provider (EMC) | X hours | ? | ? |
| Self | X hours | ? | ? |

**For each role, ask:**
- "How did you show up in this role?"
- "What went well?"
- "What needs attention?"

**Known bias check**: "Did you over-prioritize professional work this week?"

**Surface neglected roles**: "Which role is being neglected that matters deeply?"

**Role-specific prompts:**
- **Father**: "How many hours of quality one-on-one time with {{child_name}}? What was your best conversation?"
- **Partner**: "Did you maintain the 5:1 positive-to-negative ratio with {{partner_name}}? Any Four Horsemen moments?"
- **Self**: "Did you invest in your own growth, health, or renewal?"

### Step 5: Energy Audit (4-Dimension Patterns)

**Analyze energy patterns across the week:**

```markdown
### Weekly Energy Audit

| Day | Physical | Emotional | Mental | Spiritual | Notes |
|-----|----------|-----------|--------|-----------|-------|
| Mon | ? | ? | ? | ? | |
| Tue | ? | ? | ? | ? | |
| Wed | ? | ? | ? | ? | |
| Thu | ? | ? | ? | ? | |
| Fri | ? | ? | ? | ? | |
| Sat | ? | ? | ? | ? | |
| Sun | ? | ? | ? | ? | |

**Weekly Averages**: Physical: X | Emotional: X | Mental: X | Spiritual: X
```

**Pattern analysis:**
- Which dimension is consistently lowest?
- Which days were highest/lowest energy?
- What activities correlated with energy gains/drains?

**Recovery assessment:**
- Did you take regular breaks? (Respite)
- Did you maintain sleep/exercise routines? (Regimen)
- Did you practice structured work-off time? (Disengagement)

**Burnout warning signs:**
- Physical average below 5
- Emotional volatility (high variance)
- Mental fog persisting multiple days
- Spiritual disconnection from purpose

**Coaching**: If burnout signs present: "Your energy reserves are depleted. What recovery do you need before next week?"

### Step 6: Big Rocks Review

**Check quarterly rocks status:**

```bash
# Check for quarterly rocks reference
grep -r "Quarterly\|Q[1-4] Rock\|Big Rock" "{{vault_path}}/2-Areas/Personal/Years/2026.md"
```

**For each quarterly rock:**

| Rock | Status | This Week's Progress | Next Week's Focus |
|------|--------|---------------------|-------------------|
| [Rock 1] | Green/Yellow/Red | [Progress] | [Focus] |
| [Rock 2] | Green/Yellow/Red | [Progress] | [Focus] |
| [Rock 3] | Green/Yellow/Red | [Progress] | [Focus] |

**Weekly Big 3 Assessment:**

What were your Big 3 for this week?
1. [Big 3 #1] - Completed? Yes/No/Partial
2. [Big 3 #2] - Completed? Yes/No/Partial
3. [Big 3 #3] - Completed? Yes/No/Partial

**Completion rate**: X/3 = X%

**If incomplete:**
- "What prevented completion?"
- "Was this a planning failure (too ambitious) or execution failure (didn't prioritize)?"
- "Should this carry forward or be dropped?"

### Step 7: Patterns & Insights

**Surface weekly patterns:**

Ask sequentially:
1. "What went well this week? What are you proud of?"
2. "What didn't go as planned? What felt overwhelming?"
3. "What did you learn? What would you do differently?"
4. "What patterns am I noticing across recent weeks?"

**Pareto check:**
- "Which 20% of activities drove 80% of results?"
- "What can you subtract rather than add?" (Via Negativa)

**Feedback loops:**
- "What reinforcing loops were active? Did you amplify the virtuous ones?"
- "What system traps did you fall into? (Policy resistance, wrong goal, etc.)"

**INTJ-specific:**
- "Any impulsive behavior this week?" (Se grip stress indicator)
- "If yes, what triggered it? Solitude time needed?"

### Step 8: Values Alignment

**Check alignment with core values:**

**Courage check:**
- "Where did you act despite fear this week?"
- "Where did you avoid something you should have faced?"

**Love check:**
- "Where did you express love through action?"
- "Did efficiency ever trump connection?"

**Ask**: "Did you show up with courage and love this week? Where? Where didn't you?"

**Pattern**: If courage is consistently low, this is a growth edge to address.

### Step 9: Plan Next Week's Big 3

**Before closing, set next week's priorities:**

1. "What are the 3 things that, if accomplished, would make next week a success?"
2. "Which of these aligns most with your quarterly goals?"
3. "What will you say 'no' to next week to protect your Big 3?"

**Role balance:**
- "Which role needs focus next week?"
- "What family opportunity are you surfacing?"
- "What's your personal development priority?"
- "What's your health/energy priority?"

**Time blocking:**
- "When is your peak energy time? What Big Rock goes there?"
- "What meetings can be shortened or eliminated?"
- "Where's your buffer time for the unexpected?"

### Step 10: Generate Summary

Output the weekly review summary:

```markdown
## Weekly Review - [Week of DATE]

### Quadrant Distribution
| Quadrant | Actual | Target | Status |
|----------|--------|--------|--------|
| Q1 | X% | 15-25% | [Status] |
| Q2 | X% | 50-65% | [Status] |
| Q3 | X% | 10-15% | [Status] |
| Q4 | X% | <10% | [Status] |

### Leverage Audit
- **Highest leverage**: [Activity]
- **Lowest leverage**: [Activity] - Opportunity: [delegate/automate/eliminate]
- **Leverage ratio**: X%

### Role Check-In
| Role | Time | Satisfaction | Trend |
|------|------|--------------|-------|
| [Role] | X hrs | X/10 | [Up/Down/Stable] |

### Energy Audit
- **Average**: P:X E:X M:X S:X
- **Lowest dimension**: [Dimension] - Recovery needed: [Action]
- **Burnout risk**: [Low/Medium/High]

### Big Rocks Status
| Rock | Status | Progress |
|------|--------|----------|
| [Rock] | [G/Y/R] | [%] |

**Big 3 Completion**: X/3

### Patterns & Insights
- **What went well**: [Summary]
- **What to improve**: [Summary]
- **Key pattern**: [Pattern]
- **Pareto insight**: [Top 20%]

### Values Alignment
- **Courage**: [Where showed up / Where missed]
- **Love**: [Where showed up / Where missed]

### Next Week's Big 3
1. [Big 3 #1] - Supports: [Quarterly rock]
2. [Big 3 #2] - Supports: [Quarterly rock]
3. [Big 3 #3] - Supports: [Quarterly rock]

**Role focus**: [Role needing attention]
**Energy priority**: [What dimension to restore]
```

### Step 11: Save and Close

**Save the review:**
- Create a weekly review note if using separate files, or
- Update the weekly planning section of the relevant daily note

**Offer next steps:**
- "Would you like to set up timeboxes for next week's Big 3?"
- "Any items to add to tomorrow's daily plan?"
- "Any patterns we should track going forward?"

**Closing affirmation:**
- "You took time to reflect honestly. That's how growth happens."
- "Your week is reviewed. Your next week is planned. Rest well."

## Output

By the end, the user should have:
1. **Quadrant analysis** - Time distribution across Eisenhower matrix
2. **Leverage audit** - Highest/lowest leverage activities identified
3. **Role check-in** - All roles reviewed with satisfaction scores
4. **Energy audit** - 4-dimension patterns analyzed, recovery needs identified
5. **Big rocks status** - Quarterly rocks and weekly Big 3 assessed
6. **Pattern recognition** - Key patterns and Pareto insights captured
7. **Values alignment** - Courage and love check completed
8. **Next week planned** - Big 3 set with role and energy priorities

## Coaching Notes

- **Don't rush this review** - 60-90 minutes is appropriate
- **Challenge professional bias** - Ask explicitly if work dominated
- **Celebrate identity-consistent moments** - Reinforce the fighter showing up
- **Surface the uncomfortable** - What are they avoiding?
- **Protect renewal** - If energy is depleted, next week needs recovery focus
- **Connect to purpose** - Every week should advance the mission

## Related Commands

- `/daily:plan` - Morning planning
- `/daily:eod` - End of day review
- `/goals:status` - Goals dashboard
- `/goals:review` - Deep goals review
