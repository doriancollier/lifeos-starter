---
name: planning-cadence
description: Guide planning at all horizons from annual to daily. Use during planning sessions, reviews, goal setting, or when connecting daily actions to larger purpose.
allowed-tools: Read, Grep, Glob
---

# Planning Cadence Skill

Guides multi-horizon planning that connects identity to daily execution through cascading layers.

## When to Activate

- Morning planning (`/daily:plan`) - reference weekly Big 3 and quarterly rocks
- Weekly review - assess progress against quarterly goals
- Monthly review - check quarterly milestones
- Quarterly planning - set rocks aligned to annual goals
- Annual planning - connect goals to foundation
- When user feels disconnected from purpose or overwhelmed by tasks
- When asking "Why does this matter?" or "What should I focus on?"

## The Complete Cascade

```
Foundation (Identity/Mission/Vision)
    |
Annual (3-5 goals, yearly theme)
    |
Quarterly (3-5 rocks, 90-day focus)
    |
Monthly (theme, milestones)
    |
Weekly (Big 3, role-based rocks)
    |
Daily (A/B/C priorities)
```

**The Single Question**: At each level, ask "How does this support the level above?"

## Horizon Summary

| Layer | Focus | Horizon | Key Question | Time Investment |
|-------|-------|---------|--------------|-----------------|
| Foundation | Who you are | Lifetime | "What matters most?" | Annual review |
| Annual | Where you're going | 12 months | "What will this year be about?" | 4-8 hours/year |
| Quarterly | What you'll accomplish | 90 days | "What must happen to stay on track?" | 2-4 hours/quarter |
| Monthly | How you'll progress | 30 days | "What milestones advance the quarter?" | 2-3 hours/month |
| Weekly | What you'll prioritize | 7 days | "What Big Rocks get scheduled first?" | 60-90 min/week |
| Daily | What you'll execute | Today | "Which A-tasks move the needle?" | 10-15 min/day |

## Cadence Schedule

### Daily (10-15 minutes)
- **Morning**: Set A/B/C priorities, verify alignment with Weekly Big 3
- **Evening**: Review completions, identify tomorrow's focus
- **Key Question**: "Which weekly rock does today's plan advance?"

### Weekly (60-90 minutes, Friday afternoon recommended)
- Review before planning: process inboxes, capture wins/lessons
- Set Big 3 for next week - if accomplished, week is a success
- Map Big 3 to roles: Father, Husband, {{company_1_name}}, {{company_2_name}}, EMC, Self
- Check quarterly rock status (Red/Yellow/Green)
- **Key Question**: "What will you say 'no' to this week to protect your Big 3?"

### Monthly (2-3 hours, last Sunday of month)
- Two phases: Review (backward), then Planning (forward)
- Use RPM: Result, Purpose, Massive Action Plan
- Role balance assessment: Rate each role, identify neglected areas
- Check quarterly milestones
- **Key Question**: "Which role is being neglected that matters deeply?"

### Quarterly (2-4 hours, plus optional 1-2 day retreat)
- Set 3-5 Rocks with ONE owner each
- Define Key Results and monthly milestones
- Establish lead indicators (5-10 weekly actions total)
- Create NOT Doing list
- **Key Question**: "What good opportunities are you saying NO to?"

### Annual (4-8 hours, December/January)
- Set yearly theme (one word/phrase as decision filter)
- Define 3-5 annual goals across life domains
- Create NOT Doing list
- Role balance check
- Mid-year check in July
- **Key Question**: "What am I putting down to pick this up?"

## Key Questions by Horizon

### Daily Planning
- "What's the ONE thing that would make today a success?"
- "Does this task advance a weekly rock?"
- "Am I being productive or just busy?"

### Weekly Planning
- "What are the 3 things that would make this week a success?"
- "Which of these aligns most with your quarterly goals?"
- "Did you over-prioritize professional work last week?" (Known bias)

### Monthly Planning
- "At the end of this month, how will I know I succeeded?"
- "Is this monthly plan serving your mission or just keeping you busy?"
- "Where's the gap between philosophy and action?"

### Quarterly Planning
- "Looking at annual goals, what must happen THIS quarter?"
- "For each priority: What does 'done' look like?"
- "What does 'on track' look like at week 4, week 8, week 12?"

### Annual Planning
- "If anything were possible, what would I achieve in each life domain?"
- "Does this theme apply to all areas of my life?"
- "What did I learn about what really matters this year?"

## Cross-Horizon Alignment Check

| When Planning | Reference | Key Question |
|---------------|-----------|--------------|
| Daily | Weekly Big 3 | "Which rock does this advance?" |
| Weekly | Quarterly rocks | "Am I on track for Q goals?" |
| Monthly | Quarterly progress | "Are milestones being hit?" |
| Quarterly | Annual goals | "What must happen to stay on track?" |
| Annual | Foundation | "Does this serve my mission/vision?" |

## Warning Signs of Disconnection

| Sign | Level Problem | Fix |
|------|---------------|-----|
| Busy but not progressing | Daily disconnected from weekly | Align A-tasks to Big 3 |
| Goals drifting | Weekly disconnected from quarterly | Review rocks weekly |
| Quarterly goals off track | Monthly milestones missing | Add mid-month check-in |
| Annual goals feel stale | Quarterly not updating annual | Quarterly foundation check |
| Everything feels meaningless | Annual disconnected from foundation | Revisit mission/vision |

## Templates & References

### Reference Documents
- [[planning-horizons]] - Full guide to multi-level planning
- [[foundation]] - Identity, mission, vision, principles

### Templates
- `3-Resources/Templates/Planning/` - All planning templates
- [[annual-year]], [[annual-retro]]
- [[quarterly-plan]], [[quarterly-review]], [[quarterly-retreat-agenda]]
- [[monthly-plan]], [[monthly-review]]
- [[weekly-review-planning]]

## Integration Points

### With Daily Note
- Morning planning references Weekly Big 3
- A-priorities should advance quarterly rocks
- Evening reflection assesses alignment

### With Goals Tracking
- Goals cascade from annual through quarterly
- Goal Bingo visualizes quarterly priorities
- Quarterly completion drives annual progress

### With Weekly Review
- Weekly Big 3 derived from quarterly rocks
- Red/Yellow/Green status on each rock
- Lead indicator tracking (aim for 85%+)

### With Coaching
Before planning sessions, Claude should ask:
- "How does this support the level above?"
- "Are you spreading too thin? What are you saying no to?"
- "Is this a legitimate strategic shift or shiny object syndrome?"

## Coaching Triggers

- If user sets >5 A-priorities: "Research shows 1-3 strategic priorities drive better results. Which are truly strategic?"
- If daily plan doesn't connect to weekly: "Which weekly rock does today's plan advance?"
- If quarterly review shows drift: "Your lead indicators are below 60%. What's really going on?"
- Before adding new goal: "What are you putting down to pick this up?"

## Periodic Review Triggers

Automatically suggest planning reviews based on calendar context.

### Trigger Conditions

| Review Type | Activation Condition | Prompt |
|-------------|---------------------|--------|
| **Weekly** | Sunday OR end of work week (Friday afternoon) | "It's the end of the week. Time for your weekly review?" |
| **Monthly** | Last 3 days of month OR first 2 days of new month | "Month is ending/starting. Time for monthly planning?" |
| **Quarterly** | Jan 1-7, Apr 1-7, Jul 1-7, Oct 1-7 | "New quarter starting. Time for quarterly planning?" |
| **Annual** | Dec 15-31 OR Jan 1-7 | "Year is ending/starting. Ready for annual planning?" |
| **Quarterly Check-in** | Every 4th weekly review (roughly week 4, 8, 12 of quarter) | "This is week [X] of the quarter. Time for a quarterly check-in on your rocks?" |

### Detection Logic

```
At session start or during planning:
1. Get current date
2. Check day of week (Sunday = weekly trigger)
3. Check day of month (last 3 or first 2 = monthly trigger)
4. Check month (Jan/Apr/Jul/Oct first week = quarterly trigger)
5. Check if December = annual trigger
6. Track weeks since last quarterly review for check-in trigger
```

### Trigger Behavior

**During `/daily:plan`**:
- If trigger condition met, surface before starting: "Before we plan today, [trigger prompt] Or would you prefer to focus on daily planning?"

**During session start**:
- If trigger condition met and review is overdue, suggest: "[Review type] review appears overdue. Want to schedule it?"

**Trigger Hierarchy** (only show highest priority):
1. Annual (if in window)
2. Quarterly (if in window)
3. Monthly (if in window)
4. Weekly (if Sunday/Friday)
5. Quarterly Check-in (if 4 weeks since last)

### Review Commands to Suggest

| Trigger | Suggested Action |
|---------|-----------------|
| Weekly | "Run `/weekly:review` or use [[weekly-review-planning]] template" |
| Monthly | "Use [[monthly-plan]] and [[monthly-review]] templates" |
| Quarterly | "Use [[quarterly-plan]] template or schedule a planning retreat" |
| Annual | "Use [[annual-year]] template for planning, [[annual-retro]] for review" |
| Quarterly Check-in | "Quick rocks status check: Red/Yellow/Green on each" |

### Quiet Periods

Don't trigger reviews during:
- Active deep work blocks
- Urgent task execution
- When user explicitly defers: "Noted. I'll remind you again [tomorrow/next week]."
