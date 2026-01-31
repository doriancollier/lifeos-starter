---
description: Generate printable Goal Bingo cards
argument-hint: year [month|all] (e.g., "2025", "2025 January", "2025 all")
allowed-tools: Read, Write, Edit, Glob
---

# Create Bingo Card Command

Generates printable Goal Bingo cards from structured goal data. Configuration is read from `config.json`.

## Arguments

- `$ARGUMENTS` - Year and optional month/type:
  - `2025` - Generate annual card only
  - `2025 January` - Generate January monthly card
  - `2025 all` - Generate annual + all 12 monthly cards
  - `2026 annual` - Generate only the annual card

## Task

### Step 0: Load Configuration

**FIRST**: Read the configuration file to get paths, owners, and styles:

```
.claude/skills/goal-bingo/config.json
```

This file contains:
- `owners[]` - People with id, name, color, cssClass, emoji
- `paths.goalsFile` - Where to find goal data
- `paths.templateFile` - HTML template for annual cards
- `paths.templateFileMonthly` - HTML template for monthly cards
- `paths.weekAllocationScript` - Python script for calculating week boundaries
- `paths.outputFolder` - Where to save generated cards
- `styles` - Visual settings (colors, header icon)

### Step 1: Parse Arguments

Extract from `$ARGUMENTS`:
- **Year** (required): e.g., 2025, 2026
- **Type** (optional):
  - No type or "annual" → Annual card only
  - Month name (January-December) → That month's card
  - "all" → Annual + all 12 monthly cards
  - "monthly" → All 12 monthly cards (no annual)

If no year provided, default to current year.

### Step 2: Read Goal Data

Read the goals file from `config.paths.goalsFile`.

Parse the relevant tables:
- **Annual Goals**: `## [Year] Annual Goals` table with Row, Col, Goal, Owner, Icon, Status
- **Weekly Goals**: `## [Year] Weekly Goals` table with Col, Goal, Owner, Icon

### Step 3: Read the Template

- **Annual cards**: Read from `config.paths.templateFile`
- **Monthly cards**: Read from `config.paths.templateFileMonthly`

### Step 4: Generate the Card(s)

#### For Annual Card:
1. Create a 5x5 grid
2. For each cell (row 1-5, col 1-5):
   - Find matching goal from annual goals table
   - Look up owner in `config.owners[]` by matching `id` or `name`
   - Apply CSS class from `owner.cssClass`
   - Add icon emoji
   - Add goal label
   - Add owner indicator emoji from `owner.emoji`
   - If status = "complete", add `bingo-cell-complete` class
3. Generate CSS dynamically from `config.owners[]`
4. Generate legend from `config.owners[]`
5. Update header with year and `config.styles.headerIcon`

#### For Monthly Card:

**Week Allocation (Continuous Chain Algorithm):**
Run `config.paths.weekAllocationScript` or calculate manually:
- January starts on Monday closest to Jan 1 (if Jan 1 is Mon-Thu: previous Monday; Fri-Sun: next Monday)
- Each subsequent month starts on the Monday after the previous month's last Sunday
- This creates a continuous chain with no gaps or overlaps
- Each month has 4-5 weeks

**Generate the card:**
1. Get week allocations for the year (run script or use cached data)
2. Find the month's start Monday and number of weeks
3. Create grid: 5 columns × (4 or 5) rows
4. Each row = one week, with same 5 weekly goals
5. Apply colors from `config.owners[]`
6. Add week labels as **start dates only** (e.g., "Dec 29", "Jan 5", "Jan 12")
7. Update header with month name (large) and year (smaller)
8. Add subtitle with full start date (e.g., "Starting Mon, Dec 29")

### Step 5: Save the Output

Save generated HTML to `config.paths.outputFolder`.

Naming convention:
- Annual: `Bingo-Annual-{year}.html`
- Monthly: `Bingo-Monthly-{year}-{month}.html`
- All monthly: `Bingo-Monthly-{year}-All.html`
- Everything: `Bingo-{year}-Complete.html`

### Step 6: Output Summary

```markdown
## Bingo Card Generated

**Type**: [Annual / Monthly / Complete Set]
**Year**: [year]
**File**: `[config.paths.outputFolder]/[filename].html`

### To Print
1. Open the HTML file in Chrome/Edge
2. Press Cmd+P (Mac) or Ctrl+P (Windows)
3. Check "Background graphics" for colors
4. Set margins to "None" or "Minimum"
5. Print or Save as PDF

### Card Contents
[Summary of what's on the card]

Would you like me to:
- [ ] Open the file in browser?
- [ ] Generate additional cards (monthly, annual)?
- [ ] Update goal completion status?
```

## Week Allocation Script

For accurate week calculations, run the week allocation script:

```bash
python3 .claude/skills/goal-bingo/scripts/week_allocation.py
```

This outputs all 12 months with:
- Start Monday
- End Sunday
- Number of weeks (4 or 5)
- Distance from 1st of month

**2026 Reference Data:**

| Month | Start | Weeks | Distance |
|-------|-------|-------|----------|
| January | Dec 29 | 5 | -3 days |
| February | Feb 2 | 4 | +1 day |
| March | Mar 2 | 4 | +1 day |
| April | Mar 30 | 5 | -2 days |
| May | May 4 | 4 | +3 days |
| June | Jun 1 | 4 | 0 days |
| July | Jun 29 | 5 | -2 days |
| August | Aug 3 | 4 | +2 days |
| September | Aug 31 | 4 | -1 day |
| October | Sep 28 | 5 | -3 days |
| November | Nov 2 | 4 | +1 day |
| December | Nov 30 | 5 | -1 day |

## Dynamic Color Mapping

Colors and CSS classes are read from `config.owners[]`:

```javascript
// For each owner in config.owners
// Generate: .bingo-cell-{owner.id} { background: {owner.color}; }
// And legend entry with owner.name, owner.color, owner.emoji
```

The "blank" cell style uses `config.styles.blankCellColor`.

## Examples

```bash
# Generate 2025 annual card
/create:bingo 2025

# Generate January 2025 monthly card
/create:bingo 2025 January

# Generate all 2025 cards (annual + 12 monthly)
/create:bingo 2025 all

# Generate just the monthly cards
/create:bingo 2025 monthly
```

## Edge Cases

- **No goals defined for year**: Warn user and offer to set up goals
- **Missing goal data**: Skip cell or show as blank
- **Year not in goals file**: Create placeholder section and prompt user to add goals
- **Unknown owner**: Fall back to blank cell style, warn user

## Configuration Reference

The command reads all settings from:
```
.claude/skills/goal-bingo/config.json
```

To add/remove/modify owners, edit that file. Changes take effect on next card generation.
