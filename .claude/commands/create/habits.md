---
description: Generate printable monthly habit tracker sheets
argument-hint: [month] [year] [tracker] (e.g., "January 2026 user")
allowed-tools: Read, Write, Edit, Glob, Bash, AskUserQuestion
---

# Create Habit Tracker Command

Generates printable monthly habit tracking sheets from tracker-specific configurations. Supports multiple trackers for different people with blank habit rows for handwriting.

## Arguments

- `$ARGUMENTS` - Month, year, and tracker name:
  - ` ` (empty) - Prompt for tracker and use current month
  - `January user` - January of current year for {{user_first_name}}
  - `January 2026 user` - January 2026 for {{user_first_name}}
  - `2026 user` or `2026 all user` - All 12 months for {{user_first_name}}
  - `January 2026 partner` - January 2026 for {{partner_name}}

## Task

### Step 0: Load Tracker Configuration

**FIRST**: List available trackers and load the specified one:

```bash
ls .claude/skills/habit-tracker/trackers/
```

Then read the tracker config (e.g., `user.json`):

```
.claude/skills/habit-tracker/trackers/{tracker}.json
```

If no tracker specified in arguments, use AskUserQuestion to let user select.

Also read shared styles:

```
.claude/skills/habit-tracker/shared-styles.json
```

### Step 1: Validate Tracker Config

Verify required fields exist:
- `id` - Tracker identifier
- `name` - Display name for header
- `habits[]` - Array of habits

For each habit, verify:
- `frequency` - Required: "daily" or "weekly"
- If NOT blank: `id`, `name`, `identity` required
- If blank: only `frequency` and optionally `target` required

### Step 2: Parse Arguments

Extract from `$ARGUMENTS`:
- **Month** (optional): January-December (if omitted, use current month)
- **Year** (optional): e.g., 2025, 2026 (if omitted, use current year)
- **Tracker** (required): e.g., user, partner, family
- **"all"**: Generate all 12 months

### Step 3: Calculate Week Boundaries

Run the week allocation script:

```bash
python3 .claude/skills/goal-bingo/scripts/week_allocation.py --month [MONTH] --year [YEAR] --json
```

This returns:
- `start_date`: First Monday (may be in previous month)
- `end_date`: Last Sunday
- `total_days`: Total days in grid (always multiple of 7)
- `days[]`: Array with each day's info (date, is_weekend, is_sunday, in_target_month)

### Step 4: Read the Template

Read from:

```
.claude/skills/habit-tracker/habit-tracker-template.html
```

### Step 5: Generate Day Numbers Header

For each day in the grid (from week allocation):

```html
<div class="day-number [weekend] [week-end] [outside-month]">{day}</div>
```

Classes:
- `weekend`: Saturday or Sunday
- `week-end`: Sunday (right border divider)
- `outside-month`: Day not in target month (grayed out)

### Step 6: Generate Habit Rows

For each habit in tracker config:

**Standard Daily Habit:**
```html
<div class="habit-row">
    <div class="habit-label">{habit.name}</div>
    <!-- For each day in grid -->
    <div class="day-checkbox-wrapper [week-end]">
        <div class="day-checkbox [weekend] [outside-month]"></div>
    </div>
</div>
```

**Standard Weekly Habit:**
```html
<div class="habit-row">
    <div class="habit-label">{habit.name}</div>
    <!-- For each day in grid -->
    <div class="day-checkbox-wrapper [week-end]">
        <!-- Only on Sundays: -->
        <div class="week-checkbox [outside-month]"></div>
    </div>
</div>
```

**Blank Daily Habit:**
```html
<div class="habit-row">
    <div class="habit-label-blank"></div>
    <!-- For each day in grid -->
    <div class="day-checkbox-wrapper [week-end]">
        <div class="day-checkbox [weekend] [outside-month]"></div>
    </div>
</div>
```

**Blank Weekly Habit:**
```html
<div class="habit-row">
    <div class="habit-label-blank"></div>
    <!-- For each day in grid -->
    <div class="day-checkbox-wrapper [week-end]">
        <!-- Only on Sundays: -->
        <div class="week-checkbox [outside-month]"></div>
    </div>
</div>
```

### Step 7: Generate Habit Details Section

For each habit:

**Standard Habit:**
```html
<div class="habit-details-row">
    <div class="identity-cell">
        <div class="identity-habit-name">{habit.name}</div>
        <div class="identity-statement">{habit.identity}</div>
    </div>
    <div class="stats-cell">
        <div class="stats-row">
            <div class="stat-item"><span class="stat-label">Target:</span> <span class="stat-value">{habit.target}%</span></div>
            <div class="stat-item"><span class="stat-label">Streak:</span> <span class="stat-value-handwrite">&nbsp;</span></div>
            <div class="stat-item"><span class="stat-label">Best:</span> <span class="stat-value-handwrite">&nbsp;</span></div>
            <div class="stat-item"><span class="stat-label">Done:</span> <span class="stat-value-handwrite">&nbsp;</span></div>
        </div>
        <div class="progress-container">
            <div class="progress-bar-wrapper">
                <div class="progress-fill"></div>
                <div class="target-marker" style="left: {habit.target}%"></div>
            </div>
            <div class="ruler"><!-- 0-100% ticks --></div>
        </div>
    </div>
</div>
```

**Blank Habit:**
```html
<div class="habit-details-row">
    <div class="identity-cell">
        <div class="identity-habit-name-blank"></div>
        <div class="identity-statement-blank">
            <span class="blank-line"></span>
            <span class="blank-line"></span>
        </div>
    </div>
    <div class="stats-cell">
        <div class="stats-row">
            <div class="stat-item"><span class="stat-label">Target:</span> <span class="stat-value">{habit.target || 80}%</span></div>
            <div class="stat-item"><span class="stat-label">Streak:</span> <span class="stat-value-handwrite">&nbsp;</span></div>
            <div class="stat-item"><span class="stat-label">Best:</span> <span class="stat-value-handwrite">&nbsp;</span></div>
            <div class="stat-item"><span class="stat-label">Done:</span> <span class="stat-value-handwrite">&nbsp;</span></div>
        </div>
        <div class="progress-container">
            <div class="progress-bar-wrapper">
                <div class="progress-fill"></div>
                <div class="target-marker" style="left: {habit.target || 80}%"></div>
            </div>
            <div class="ruler"><!-- 0-100% ticks --></div>
        </div>
    </div>
</div>
```

### Step 8: Replace Template Placeholders

| Placeholder | Value |
|-------------|-------|
| `{{TRACKER_NAME}}` | From tracker config `name` field |
| `{{MONTH_NAME}}` | Full month name uppercase (e.g., "JANUARY") |
| `{{YEAR}}` | Four-digit year |
| `{{SUBTITLE}}` | From tracker config `subtitle` (default: "80% consistency, not perfection") |
| `{{DAYS_IN_GRID}}` | Total days from week allocation |
| `{{DAY_NUMBERS}}` | Generated day number divs |
| `{{HABIT_ROWS}}` | Generated habit checkbox rows |
| `{{HABIT_DETAILS}}` | Generated identity + stats sections |
| `{{RECOVERY_MESSAGE}}` | From tracker config `recovery` |
| Style placeholders | Values from `shared-styles.json` |

### Step 9: Save the Output

Save generated HTML to:

```
3-Resources/Documents/Printables/Habit-Tracker-{Year}-{Month}-{TrackerName}.html
```

Where `TrackerName` is the capitalized tracker id (e.g., "{{user_first_name}}", "{{partner_name}}").

### Step 10: Output Summary

```markdown
## Habit Tracker Generated

**Tracker**: {tracker.name}
**Month**: {Month} {Year}
**File**: `3-Resources/Documents/Printables/Habit-Tracker-{Year}-{Month}-{TrackerName}.html`

### Habits Tracked

| Habit | Frequency | Target |
|-------|-----------|--------|
| {habit.name or "(blank)"} | {frequency} | {target}% |

### Week Boundaries
- Starts: {start Monday}
- Ends: {end Sunday}
- Grid days: {total_days}

### To Print
1. Open the HTML file in Chrome/Edge
2. Press Cmd+P (Mac) or Ctrl+P (Windows)
3. Check "Background graphics" for colors
4. Set margins to "None" or "Minimum"
5. Print or Save as PDF

Would you like me to:
- [ ] Open the file in browser?
- [ ] Generate additional months?
- [ ] Generate for another tracker?
```

## Examples

```bash
# Generate current month for {{user_first_name}}
/create:habits {{user_first_name}}

# Generate January 2026 for {{user_first_name}}
/create:habits January 2026 {{user_first_name}}

# Generate January 2026 for {{partner_name}}
/create:habits January 2026 partner

# Generate all 12 months for {{user_first_name}}
/create:habits 2026 {{user_first_name}}

# No tracker specified - will prompt
/create:habits January 2026
```

## Available Trackers

List trackers:
```bash
ls .claude/skills/habit-tracker/trackers/
```

Current trackers:
- `user` - {{user_first_name}}'s personal tracker
- `partner` - {{partner_name}}'s personal tracker

## Creating a New Tracker

1. Create new JSON file in `trackers/`:
   ```
   .claude/skills/habit-tracker/trackers/{name}.json
   ```

2. Use schema reference for validation:
   ```json
   {
     "$schema": "../tracker.schema.json",
     "id": "newtracker",
     "name": "New Tracker Name",
     "habits": [...]
   }
   ```

3. Run command with new tracker name

## Configuration Reference

| File | Purpose |
|------|---------|
| `trackers/*.json` | Per-tracker habit configurations |
| `shared-styles.json` | Visual styles (colors, sizes) |
| `tracker.schema.json` | JSON Schema for validation |
| `habit-tracker-template.html` | HTML template |
