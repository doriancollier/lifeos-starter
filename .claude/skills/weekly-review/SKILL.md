---
name: weekly-review
description: Aggregate weekly accomplishments, patterns, and insights from daily notes. Use for end-of-week reviews, planning, or understanding work patterns over time.
---

# Weekly Review Skill

Aggregates and analyzes data from daily notes to support weekly reviews and planning.

## Data Sources

- **Daily notes**: `4-Daily/YYYY-MM-DD.md`
- **Meeting notes**: `5-Meetings/YYYY/MM-Month/`
- **Projects**: `1-Projects/Current/`

## Weekly Review Components

### 1. Task Completion Analysis

```bash
# Find completed tasks from the past week
for i in {0..6}; do
  date_str=$(date -v-${i}d +%Y-%m-%d)
  echo "=== $date_str ==="
  grep -E "^- \[x\]" "{{vault_path}}/4-Daily/${date_str}.md" 2>/dev/null
done
```

### 2. Incomplete Task Carryover

```bash
# Find tasks that appeared in multiple days (carried over)
for i in {0..6}; do
  date_str=$(date -v-${i}d +%Y-%m-%d)
  grep -E "^- \[ \]" "{{vault_path}}/4-Daily/${date_str}.md" 2>/dev/null
done | sort | uniq -c | sort -rn
```

### 3. Meeting Summary

```bash
# List meetings from the past week
find "{{vault_path}}/5-Meetings/2025/" -name "*.md" -mtime -7
```

### 4. Energy & Mood Patterns

```bash
# Extract energy levels from daily notes
for i in {0..6}; do
  date_str=$(date -v-${i}d +%Y-%m-%d)
  echo -n "$date_str: "
  grep "energy_level:" "{{vault_path}}/4-Daily/${date_str}.md" 2>/dev/null
done
```

### 5. Company Time Distribution

Count tasks and activities by company:
- {{company_1_name}}
- {{company_2_name}}
- {{company_3_name}}
- Personal

## Weekly Review Output Template

```markdown
# Weekly Review: [Start Date] - [End Date]

## Accomplishments

### {{company_1_name}}
- [Completed items]

### {{company_2_name}}
- [Completed items]

### {{company_3_name}}
- [Completed items]

### Personal
- [Completed items]

## Key Decisions Made
- [Decision 1] - [Context]
- [Decision 2] - [Context]

## Meetings Held
- [Date]: [Meeting] with [People]
- [Date]: [Meeting] with [People]

## Tasks Carried Over
- [ ] [Task that's been pending]
- [ ] [Another pending task]

## Blocked Items
- [Item] - Waiting for: [blocker]

## Patterns Observed

### Energy
- Average energy: [high/medium/low]
- Best days: [days]
- Challenging days: [days]

### Time Distribution
- {{company_1_name}}: ~X%
- {{company_2_name}}: ~X%
- EMC: ~X%
- Personal: ~X%

## Wins
1. [Big win]
2. [Another win]

## Challenges
1. [Challenge faced]
2. [Area for improvement]

## Next Week Focus
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

## Notes for Future Self
- [Insight or learning]
- [Pattern to watch]
```

## Insights to Surface

### Productivity Patterns
- Which days were most productive?
- What types of tasks got done vs deferred?
- Are A-priority tasks getting completed?

### Work-Life Balance
- Time spent on Personal vs work contexts
- Energy level trends
- Any burnout signals?

### Relationship Health
- Who did you interact with this week?
- Any relationships need attention?

### Project Progress
- Movement on active projects
- Backlog items addressed
- New projects started

## Integration

- Use **task-system** skill for task analysis
- Use **context-switch** skill for company breakdowns
- Use **person-context** skill for relationship insights

---

## Planning System 2.0 Enhancements

These additions integrate strategic review patterns from [[planning-horizons]] and [[framework-prompts]].

### Pareto Check

Identify the vital few activities that drove most results:

**Weekly Pareto Analysis**:
- "Which 20% of activities created 80% of value this week?"
- "What tasks could be eliminated entirely? What would happen if you just stopped?"
- "What compounded this week — positively and negatively?"
- "What can you subtract rather than add?" (Via Negativa)

**Pattern recognition**:
- Track which activities consistently appear in the vital 20%
- Identify recurring low-value time sinks
- Surface activities that looked productive but weren't

### Quadrant Assessment

Analyze time distribution across Eisenhower quadrants:

```markdown
## Quadrant Time Assessment

| Quadrant | Target | Actual | Notes |
|----------|--------|--------|-------|
| Q1 (Urgent + Important) | 20-25% | __% | Crises handled |
| Q2 (Important, Not Urgent) | 60-65% | __% | Strategic work |
| Q3 (Urgent, Not Important) | 10-15% | __% | Should delegate |
| Q4 (Neither) | <5% | __% | Eliminate |

**Q1 Crisis Audit**: What could Q2 work have prevented?
**Q2 Protection**: Did I protect strategic time?
**Q3 Delegation Review**: What should I stop doing myself?
**Q4 Elimination**: What time sinks did I indulge?
```

**Coaching prompts**:
- "Did I spend 60%+ of productive time in Q2?"
- "Which Q1 crises could have been prevented with earlier Q2 work?"
- "What Q2 activities am I scheduling first next week — before other appointments fill the calendar?"

### Energy Audit

Track 4-dimension energy patterns for the week:

```markdown
## Weekly Energy Audit

### Energy Levels by Day
| Day | Physical | Emotional | Mental | Spiritual |
|-----|----------|-----------|--------|-----------|
| Mon | /10 | /10 | /10 | /10 |
| Tue | /10 | /10 | /10 | /10 |
| Wed | /10 | /10 | /10 | /10 |
| Thu | /10 | /10 | /10 | /10 |
| Fri | /10 | /10 | /10 | /10 |

### Patterns
- **Energizers this week**:
- **Drainers this week**:
- **Average energy level**: /10
- **Best days**:
- **Challenging days**:

### Grip Stress Check (INTJ-specific)
- [ ] Any impulsive behavior this week?
- [ ] If yes, what triggered it?
- [ ] Solitude time needed?
```

**Coaching prompts**:
- "What energized me this week? What depleted me?"
- "What one shift would restore balance?"
- "You're showing physical energy at 4/10 for the third day. When will you actually rest?"

### Role Check-In

Review each role's attention and health:

```markdown
## Weekly Role Check-In

| Role | Time/Attention | Satisfaction (1-10) | One Action |
|------|----------------|---------------------|------------|
| Provider | | /10 | |
| Father | | /10 | |
| Partner | | /10 | |
| Self | | /10 | |
| {{company_1_name}} | | /10 | |
| {{company_2_name}} | | /10 | |
| EMC | | /10 | |

**Neglect pattern**: Which roles chronically neglected? Why?
**Enrichment win**: Where did one role enrich another?
**Known bias check**: Did I over-prioritize professional work?
```

**Coaching prompts**:
- "Which roles got attention? Which were neglected? Why?"
- "Where did work enrich family? Family enrich work?"
- "Did I over-prioritize professional work this week?" (known bias)
- "What family opportunity am I surfacing for next week?"

### Strategic Audit

Assess whether you worked ON your life/business or just IN it:

**Key questions**:
- "Did I work ON my life/business or just IN it this week?"
- "What leverage am I building that will pay off in 6-12 months?"
- "Was I productive or just busy?"
- "Where did I provide negative leverage — blocking others, unclear communication, waffling on decisions?"

**Systems thinking**:
- "What feedback loops were active? Did I amplify the virtuous ones?"
- "What patterns emerged? What repeated? What surprised me?"
- "What am I avoiding? Why?"

### Big Rocks Review

Assess weekly rock completion:

```markdown
## Weekly Big Rocks Review

### This Week's Big 3
1. [ ] [Rock 1] — Status: ___
2. [ ] [Rock 2] — Status: ___
3. [ ] [Rock 3] — Status: ___

### Assessment
- **Completed rocks**:
- **Deferred rocks**: Why?
- **Rocks that became gravel**: What happened?

### Next Week's Big 3
1. [ ]
2. [ ]
3. [ ]

**Quarterly alignment**: Do next week's rocks advance quarterly goals?
```

**Coaching prompts**:
- "What are the 3 things that, if accomplished, would make next week a success?"
- "If I only accomplished these 3 things next week, would I be satisfied?"
- "What will I say 'no' to next week to protect my Big 3?"

### Leverage Assessment

Evaluate highest-leverage activities:

**Weekly leverage questions**:
- "What was your highest-leverage activity this week? What made it high-leverage?"
- "Where did you create outsized returns from focused effort?"
- "What pattern of low-leverage time sinks do you see recurring?"

**Eliminate-Automate-Delegate review**:
- "What can I eliminate next week?"
- "What can I automate?"
- "What can I delegate (70% as good is good enough)?"

**Leverage tracking**:
```markdown
## Leverage Assessment

### Highest-Leverage Activities
1. [Activity] — Why high-leverage: ___
2. [Activity] — Why high-leverage: ___

### Low-Leverage Time Sinks
1. [Activity] — Should: Eliminate / Automate / Delegate
2. [Activity] — Should: Eliminate / Automate / Delegate

### Systems Built
- [System or automation created this week]

### Leverage Building for Next Week
- [What will compound over time]
```

### Habit & Rhythm Compliance

Track daily and weekly rhythm adherence:

```markdown
## Weekly Rhythms Compliance

### Daily Habits (7-day view)
| Habit | Mon | Tue | Wed | Thu | Fri | Sat | Sun | % |
|-------|-----|-----|-----|-----|-----|-----|-----|---|
| Daily Practice | | | | | | | | /7 |
| Daily Movement | | | | | | | | /7 |
| Sleep Protocol | | | | | | | | /7 |
| Morning Light | | | | | | | | /7 |
| No caffeine after 2pm | | | | | | | | /7 |
| One Appreciation ({{partner_name}}) | | | | | | | | /7 |
| {{child_name}} Moment | | | | | | | | /7 |

**Overall Daily Compliance**: __/49 (__%)

### Weekly Rhythms
| Rhythm | This Week | Notes |
|--------|-----------|-------|
| State of Union (with {{partner_name}}) | ☐ | |
| {{child_name}} One-on-One | ☐ | |
| Walks with {{partner_name}} (3x target) | _/3 | |
| Weekly Review | ☐ | |

**Weekly Rhythms Compliance**: __/4 (__%)
```

**Data collection**:
```bash
# Count completed daily rhythms from past week
for i in {0..6}; do
  date_str=$(date -v-${i}d +%Y-%m-%d)
  echo "=== $date_str ==="
  grep -E "^\- \[x\]" "{{vault_path}}/4-Daily/${date_str}.md" 2>/dev/null | grep -E "(Daily Practice|Daily Movement|Sleep Protocol|Morning Light|caffeine|Appreciation|{{child_name}} Moment)"
done
```

**Coaching prompts**:
- "You hit 5/7 on Daily Practice but only 2/7 on Daily Movement. What's blocking the movement habit?"
- "State of Union hasn't happened in 3 weeks. Is this avoidance or scheduling?"
- "Your rhythm compliance dropped from 85% to 60% this week. What changed?"
- "Which habit consistently falls off first when you're stressed?"

**Trend tracking**:
- Compare week-over-week compliance percentages
- Identify which habits are stable vs volatile
- Surface habits that need system support (reminders, environmental design)

### Related References

- [[planning-horizons]] — Multi-horizon planning framework
- [[framework-prompts]] — Complete coaching prompts library
- [[foundation]] — Identity, mission, vision, principles
- [[weekly-review-planning]] — Combined review and planning template
- [[2026]] — Current year goals and daily/weekly rhythms
