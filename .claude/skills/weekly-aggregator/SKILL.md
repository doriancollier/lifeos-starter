---
name: weekly-aggregator
description: Automatically aggregate yesterday's daily note data into the rolling weekly document. Called during /daily:plan to progressively build weekly reviews.
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Weekly Aggregator Skill

Progressively builds the weekly review document by aggregating data from daily notes. This eliminates the need to manually trigger `/weekly:review` by building the review incrementally.

## When to Activate

- **During `/daily:plan`**: Called automatically after daily note setup
- **Manually**: When user asks to update weekly aggregation
- **After `/daily:eod`**: Optionally to capture end-of-day data

## Core Concept

Instead of reconstructing a week's worth of data in one session, this skill captures data fresh each morning:

```
Mon: Aggregate Sunday's data → Weekly doc
Tue: Aggregate Monday's data → Weekly doc
Wed: Aggregate Tuesday's data → Weekly doc
...
Sun: Aggregate Saturday's data → Weekly doc
Mon: Run /weekly:reflect on complete doc
```

By the time reflection is needed, all data is already captured.

## File Locations

- **Weekly documents**: `workspace/3-Resources/Planning/Weekly/YYYY-Www.md`
- **Daily notes**: `workspace/4-Daily/YYYY-MM-DD.md`
- **Template**: `workspace/3-Resources/Templates/weekly-rolling.md`

## Week Numbering

Use ISO week numbering:
- Week starts on Monday
- Week 1 is the week containing the first Thursday of the year
- Format: `YYYY-Www` (e.g., `2026-W01`)

```bash
# Get current ISO week
date +%G-W%V

# Get yesterday's ISO week (for Monday, this is last week)
date -v-1d +%G-W%V
```

## Aggregation Process

### Step 1: Determine Context

```bash
# Today's date
today=$(date +%Y-%m-%d)
day_of_week=$(date +%A)

# Yesterday's date
yesterday=$(date -v-1d +%Y-%m-%d)
yesterday_dow=$(date -v-1d +%A)

# Week for the data being aggregated (yesterday's week)
data_week=$(date -v-1d +%G-W%V)
```

### Step 2: Check/Create Weekly Document

```bash
weekly_file="{{vault_path}}/workspace/3-Resources/Planning/Weekly/${data_week}.md"
```

If file doesn't exist:
1. Read template from `workspace/3-Resources/Templates/weekly-rolling.md`
2. Replace template variables:
   - `{{week_number}}` → week number (e.g., `01`)
   - `{{year}}` → year (e.g., `2026`)
   - `{{week_start}}` → Monday's date (e.g., `2025-12-30`)
   - `{{week_end}}` → Sunday's date (e.g., `2026-01-05`)
3. Write to weekly file path

### Step 3: Read Yesterday's Daily Note

```bash
daily_note="{{vault_path}}/workspace/4-Daily/${yesterday}.md"
```

Extract:
1. **Energy levels** from frontmatter (`energy_level`) or Morning Check-in
2. **Completed tasks**: Lines matching `^- \[x\]`
3. **A-priority completion**: Count completed 🔴 tasks vs total
4. **Fears faced**: Content from `### Faced Today` section
5. **Fears avoided**: Content from `### Avoided Today` section
6. **Alignment score**: From End of Day section or frontmatter
7. **Key accomplishments**: From `### What Went Well` section
8. **Daily Rhythms**: Check completion status of each habit

### Step 4: Update Weekly Document

Find the section for yesterday's day of week (e.g., `### Monday`) and update:

```markdown
### Monday
- **Energy**: P: 7/10 | E: 8/10 | M: 6/10 | S: 7/10
- **Completed Tasks**: 12 (A: 4/5, B: 6, C: 2)
- **Key Accomplishments**: Shipped email drip feature, had difficult conversation with stakeholder
- **Fears Faced**: 1 - Gave direct feedback to team member
- **Notes**: Good energy day, protected focus time well
```

### Step 5: Update Habit Compliance Table

For each habit, mark the day's column:
- ✓ if completed (checkbox was checked in Daily Rhythms)
- ✗ if not completed
- - if no data

Update running totals in the Total column.

### Step 6: Update Aggregated Metrics

Recalculate running totals:
- Total tasks completed across all days
- Total A-priorities completed
- Total fears faced/avoided
- Running average energy (by dimension)
- Running average alignment score

## Data Extraction Patterns

### Energy from Daily Note

```bash
# From frontmatter
grep "energy_level:" daily_note.md

# From Morning Check-in (if 4-dimension tracked)
grep -A5 "## Morning Check-in" daily_note.md | grep -E "Physical|Emotional|Mental|Spiritual"
```

### Completed Tasks

```bash
grep -E "^- \[x\]" daily_note.md | wc -l

# A-priorities completed
grep -E "^- \[x\] 🔴" daily_note.md | wc -l

# Total A-priorities
grep -E "^- \[.\] 🔴" daily_note.md | wc -l
```

### Daily Rhythms Habits

```bash
# Check each habit in Daily Rhythms section
grep -A20 "## Daily Rhythms" daily_note.md | grep -E "^\- \[x\].*Daily Practice"
grep -A20 "## Daily Rhythms" daily_note.md | grep -E "^\- \[x\].*Daily Movement"
# ... etc for each habit
```

### Fears

```bash
# Count fears faced
grep -A50 "### Faced Today" daily_note.md | grep -E "^\- \[" | head -10

# Count fears avoided
grep -A50 "### Avoided Today" daily_note.md | grep -E "^\- \[" | head -10
```

### Alignment Score

```bash
grep -E "^\*\*Score\*\*:|alignment_score:" daily_note.md
```

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Yesterday's note doesn't exist | Skip aggregation, note in weekly doc |
| Week boundary (Monday aggregating Sunday) | Aggregate to previous week's doc |
| Mid-week start | Create doc, leave earlier days blank |
| Multiple runs same day | Update, don't duplicate |
| Missing sections in daily note | Use defaults/blanks, don't fail |

## Week Boundary Logic

On **Monday**, yesterday (Sunday) belongs to the **previous week**:

```python
# Pseudocode
if today.weekday() == 0:  # Monday
    # Sunday's data goes to LAST week's document
    data_week = yesterday.isocalendar()  # Previous week
    # Also: Check if last week's doc is complete for reflection prompt
```

## Integration Points

### With `/daily:plan`

Call this skill after daily note setup (Step 1) and before planning (Step 2):

```markdown
### Daily Plan Flow
1. Check/create today's daily note
2. **Run weekly-aggregator** ← Insert here
3. Continue with calendar sync, etc.
```

### With `/daily:eod`

Optionally call at end of day to capture same-day data (alignment score, fears faced, etc.) for more accurate metrics.

### With `/weekly:reflect`

When reflection is triggered:
1. Weekly doc is already populated with all daily data
2. User only needs to complete reflection sections
3. Dramatically reduces review time

### With `session-context-loader.py`

Hook detects:
- Monday morning → prompts for `/weekly:reflect` on last week's doc
- Incomplete weekly doc → suggests running aggregation

## Output

After running, confirm:
```
✅ Weekly aggregation complete for [yesterday's date]
   → Updated: workspace/3-Resources/Planning/Weekly/2026-W01.md
   → Completed tasks: 12
   → Fears faced: 1
   → Habit compliance: 5/7
```

## Silent Mode

When called from `/daily:plan`, run silently unless:
- This is the first aggregation of the week (mention doc created)
- There's an issue (missing daily note, etc.)
- It's Monday (mention last week's doc is ready for reflection)

## Coaching Prompts

Surface during aggregation when patterns emerge:

- "You've faced fears 5 days in a row. That's building courage systematically."
- "Daily Movement has dropped to 2/7 this week. What's blocking it?"
- "A-priority completion is 60% this week. Are you overcommitting?"
- "No State of Union logged yet this week. Schedule it?"
