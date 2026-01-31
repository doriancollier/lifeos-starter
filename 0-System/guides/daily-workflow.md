---
title: "Daily Workflow Guide"
created: "2025-12-02"
status: "active"
---

# Daily Workflow Guide

How to use LifeOS for daily planning and execution.

> **LifeOS 2.0**: The daily workflow now includes coaching elements — state setting, fear tracking, and alignment scoring — to bridge the gap between your philosophy and daily action.

## Overview

The daily workflow follows a natural rhythm:

```
Morning Planning → Focused Work → Capture → Evening Review
       ↓                ↓            ↓            ↓
   /daily:plan    work-logging    /update     /daily:eod

With coaching integration:
- State setting (morning/evening)
- Fear commitment and tracking
- Alignment scoring
- Role balance checks
```

## Morning Planning

### Quick Start

```
/daily:plan
```

This launches an **interactive** planning session that takes ~5-10 minutes.

### What Happens

The planning workflow walks you through coached steps, starting with what's on YOUR mind:

1. **Brain Dump** — Clear your mind first. Dump tasks, worries, ideas before system checks
2. **Planning Horizons** — Connect to quarterly/monthly/weekly goals
3. **Setup & Calendar** — Creates today's note, fetches calendar
4. **Calendar Review** — See today's schedule, make immediate adjustments before planning
5. **Weekly Aggregation** — Capture yesterday's data into weekly doc
6. **Daily Practice Check** — Have you completed your audio practice?
7. **State Setting** — "What's your state right now, 1-10?" with reset protocols
8. **Premeditatio Malorum** — What challenges might you face? Create if-then plans
9. **Review Yesterday** — Shows completed vs incomplete tasks, alignment patterns
10. **Carryover Tasks** — Surfaces incomplete tasks from recent days
11. **Blocked Items** — Checks if any blockers are resolved
12. **Birthdays, Holidays, Meeting Prep** — Additional calendar context
13. **Project Deadlines** — Shows projects due within 7 days
14. **Energy Check** — 4-dimension assessment with INTJ grip stress awareness
15. **Fear Selection** — "What fear will you face today?" (critical for growth)
16. **A-Priority Selection** — Helps choose max 5 critical tasks, references brain dump items
17. **Focus Areas & Roles** — Sets which companies and roles need attention
18. **Update Daily Note** — Writes everything to your note including brain dump
19. **Timebox Schedule** — Creates calendar focus blocks
20. **First Action** — Coaching send-off with clear next step

### The Brain Dump

The planning session now starts with an open-ended capture moment:

> "What's on your mind this morning? Dump it all — tasks, worries, ideas, anything swirling."

This serves several purposes:
- **Clears mental clutter** before structured planning begins
- **Surfaces urgent items** that might override normal priorities
- **Captures concerns** that inform Premeditatio and fear selection
- **Creates a record** of what was occupying your mind at day-start

The brain dump content is processed silently and referenced later:
- Actionable items surface during A-priority selection
- Concerns inform Premeditatio and fear selection
- Calendar-related items are checked during calendar review
- Narratives are captured in the daily note

### Calendar Review Early

After fetching your calendar, you'll see the day's schedule immediately:

```
## Today's Calendar Reality

| Time | Event | Attendees |
|------|-------|-----------|
| 11:00 | Team Sync | 12 |
| 2:30 | 1:1 | 2 |

**Total scheduled time**: 2.5 hours
**Open blocks**: ~5 hours
```

You'll be asked: "Any immediate adjustments needed?" with options to:
- Continue planning (calendar is set)
- Reschedule/cancel something
- Add an event
- Review more carefully

This ensures you're planning against the ACTUAL day, not discovering conflicts later.

### Energy-Based Planning

Your energy level affects recommendations:

| Energy | A-Tasks | Recommendation |
|--------|---------|----------------|
| High | 4-5 | Tackle challenging work |
| Medium | 3-4 | Normal workload |
| Low | 2-3 | Focus on must-dos only |

### The Timeboxed Schedule

At the end of planning, you'll get focus blocks on your calendar:

```
| Time        | Block                  | Tasks               |
|-------------|------------------------|--------------------|
| 8:00-10:00  | [Focus] {{company_1_name}}     | Analytics review   |
| 10:00-10:10 | [Break]                | Short break        |
| 10:10-11:30 | [Focus] 144            | AssetOps work      |
| 12:00-1:00  | [Break] Lunch          | —                  |
| 1:00-1:20   | [Break] Movement       | Post-lunch walk    |
| 1:20-3:00   | [Focus] Personal       | Tasks              |
| 3:00-3:20   | [Break] Afternoon Reset| Stretch, fresh air |
```

Focus blocks are created as **transparent** calendar events (don't block availability) with extended properties for easy identification.

**Wellness blocks are non-negotiable** — they're scheduled first, and work fills around them. If your schedule is packed, lunch can be 30 min minimum, but it should never be skipped.

## Daily Note Structure

Every daily note follows this structure (enhanced for LifeOS 2.0):

```markdown
---
date: "YYYY-MM-DD"
day_of_week: "Monday"
energy_level: "medium"
state_morning:              # 1-10 state score
state_evening:              # 1-10 state score
alignment_score:            # 1-10 values-action match
focus_areas: ["{{company_1_name}}", "Personal"]
fear_faced: false           # Did you face your planned fear?
---

# YYYY-MM-DD

## Morning Check-in
- Energy level, state score, mood
- Daily Practice completion status
- Intentions (result-focused)
- Premeditatio Malorum (challenges anticipated)
- Fear to face today

## Today's Events
- All-day events table
- Scheduled events table

## Work
### Quick Hits (tasks under 15 min)
### {{company_1_name}}
### {{company_2_name}}
### {{company_3_name}}
### Personal

## Fears
### Faced Today (with type, difficulty, outcome, identity reinforced)
### Avoided Today (with reason, carry-forward decision)
### Planned for Tomorrow

## Journal
### Reflections
### Daily Memories (narrative/diary)
### Quick Notes (work logs)

## End of Day
- State check (morning vs evening)
- Reflection questions
- Alignment score
- What went well / could improve
- Tomorrow's focus (MITs, fear, role)

## AI Processing Notes
- Alignment observations
- Fear patterns
- Role balance
- Energy/state patterns
```

## During the Day

### Quick Capture

For quick additions to your daily note:

```
/daily:capture [text]
```

Or use the universal smart capture:

```
/update [anything]
```

The `/update` command intelligently routes content:
- Tasks → Task sections
- Calendar events → Calendar + daily note
- Narrative content → Daily Memories
- Work updates → Quick Notes
- Birthday mentions → Creates recurring calendar events

### Logging Work Progress

When you complete work, just say what you did:

```
"I finished the analytics review"
"Called Alex about the roadmap"
"Done with the prescription call"
```

The `work-logging` skill automatically:

1. **Finds the parent task** in your daily note
2. **Adds/checks off subtasks**:
   ```markdown
   - [ ] 🔴1. Renew prescription - Company: Personal
     - [x] Check doctor's message
     - [x] Call pharmacy
     - [ ] Pick up prescription
   ```
3. **Adds timestamped log entry**:
   ```markdown
   ### Quick Notes
   - [10:35] Prescription: Doctor approved, calling CVS next
   - [10:45] Prescription: Complete - pickup ready tomorrow
   ```

### The Dual-Track Pattern

Every progress report updates two places:

| Track | Location | Purpose |
|-------|----------|---------|
| **Subtasks** | Under parent task | Track completion status |
| **Quick Notes** | Random Captures | Context, decisions, insights |

## Context Switching

When switching between work contexts:

```
/context:ab       # Load {{company_1_name}} context
/context:144      # Load {{company_2_name}} context
/context:emh      # Load {{company_3_name}} context
/context:personal # Load personal context
```

This loads the relevant company file from `2-Areas/[Company]/context.md`.

## Evening Review

### Quick Review

```
/daily:eod
```

This launches an **interactive** coaching review (11 steps) that helps you:
- Review tasks completed and incomplete
- Account for fear (faced or avoided with learning capture)
- Check state (morning vs evening comparison)
- Answer reflection questions
- Score alignment (1-10 values-action match)
- Check role balance (did family get attention?)
- Set up tomorrow (MITs, fear, role focus)

### What Gets Updated

1. **State Check** — Morning vs evening state comparison
2. **Fear Accountability** — Faced or avoided with detailed capture
3. **Reflection Questions** — Best self, fell short, grateful for
4. **Alignment Score** — With notes on what affected it
5. **Role Balance** — Which roles got attention, which were neglected
6. **Tomorrow Preparation** — MITs, fear to face, role needing attention
7. **AI Processing Notes** — Patterns for future reference

## Commands Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/daily:note` | Open today's note | Quick access |
| `/daily:plan` | Morning planning | Start of day |
| `/daily:capture [text]` | Quick add to note | Fast capture |
| `/daily:tasks` | Review open tasks | Check status |
| `/daily:timebox` | Create focus blocks | Structure your time |
| `/daily:standup` | Generate standup summary | Before team meetings |
| `/daily:eod` | End of day review | Close out the day |
| `/update [text]` | Smart universal capture | Any time |

## Auto-Creation Behavior

LifeOS automatically creates missing daily notes when:
- You reference a date (`/update yesterday`)
- You run any daily command
- The system needs to read/write a daily note

### Planning Offer

If a daily note is created in the morning (before noon) and appears unplanned, you'll be asked:

```
"I created today's daily note. Your day isn't fully planned yet.
Would you like to run /daily:plan now?"
```

This only happens:
- For today's date (not past dates)
- Before 12:00 PM
- When the note has placeholder content
- When not already running a planning command

## Tips for Success

1. **Complete Daily Practice first** — It sets your state for everything else
2. **Start with `/daily:plan`** — Even 5 minutes of coached planning helps
3. **Commit to a fear** — Everything you want is on the other side of fear
4. **Limit A-priorities** — Max 5, ideally 3-4, and know WHY each matters
5. **Log as you go** — Conversational updates keep things current
6. **Use timeboxing** — Focus blocks reduce decision fatigue
7. **End with `/daily:eod`** — Close loops, account for fear, set up tomorrow
8. **Be honest in alignment scoring** — The goal is growth, not perfection

## The Coaching Difference

LifeOS 2.0 adds coaching elements throughout the day:

| Moment | Coaching Question |
|--------|-------------------|
| Before A-priorities | "Why does this matter? How does it serve your mission?" |
| When avoiding tasks | "Is this strategic adjustment or avoidance?" |
| When energy is low | "Is this genuine fatigue or grip stress? When did you last have solitude?" |
| End of day | "Where did you show up as your best self? Where did you fall short?" |
| When skipping fear | "What was the cost of not facing this today?" |

## Related Guides

- [[task-management|Task Management]] — The A/B/C priority system
- [[calendar-integration|Calendar Integration]] — Timeboxing and scheduling
- [[board-advisors|Personal Board of Advisors]] — Multi-perspective deliberation
