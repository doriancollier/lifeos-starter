# Card Generation Reference

Detailed instructions for generating Goal Bingo cards programmatically.

## Step-by-Step Generation Process

### Step 1: Load Configuration

```javascript
// Read config.json from skill directory
const config = JSON.parse(readFile('.claude/skills/goal-bingo/config.json'));
```

### Step 2: Read Goal Data

```javascript
// Use path from config
const goalsPath = config.paths.goalsFile;
const goalsContent = readFile(goalsPath);
```

Parse the markdown tables to extract:
- Annual goals: Row, Col, Goal, Owner, Icon, Status
- Weekly goals: Col, Goal, Owner, Icon

### Step 3: Map Owners to Styles

```javascript
// For each goal, find the matching owner from config
function getOwnerStyle(ownerName) {
  const owner = config.owners.find(o =>
    o.id === ownerName.toLowerCase() ||
    o.name.toLowerCase() === ownerName.toLowerCase()
  );
  return owner || { cssClass: 'bingo-cell-blank', color: config.styles.blankCellColor };
}
```

### Step 4: Generate CSS from Config

```css
/* Generate dynamically from config.owners */
.bingo-cell-{owner.id} { background: {owner.color}; }
.bingo-legend-swatch-{owner.id} { background: {owner.color}; }
```

### Step 5: Calculate Monthly Card Dates

For monthly cards, calculate the start date (first Monday).

**Algorithm**:
1. Find the first of the month
2. If it falls Mon-Thu: start = last Monday (may be previous month)
3. If it falls Fri-Sun: start = first Monday of current month
4. Count weeks from start to end of month (always 4 or 5)

See `/create:bingo` command for the canonical implementation.

### Step 6: Generate HTML

Use the template from `config.paths.templateFile` or generate fresh HTML.

### Step 7: Save Output

Save to `config.paths.outputFolder` with naming:
- Annual: `Bingo-Annual-{year}.html`
- Monthly: `Bingo-Monthly-{year}-{month}.html`
- Bundle: `Bingo-{year}-All.html`

---

## HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
  <title>{year} Bingo</title>
  <style>
    /* Base styles */
    .bingo-page { background: {config.styles.pageBackground}; }
    .bingo-cell { /* base cell styles */ }

    /* Owner styles - generated from config.owners */
    .bingo-cell-{id} { background: {color}; }

    /* Blank cell */
    .bingo-cell-blank { background: {config.styles.blankCellColor}; }
  </style>
</head>
<body>
  <div class="bingo-page">
    <header class="bingo-header">
      <span class="bingo-year">{year}</span>
      <span class="bingo-flower">{config.styles.headerIcon}</span>
      <span class="bingo-title">Bingo</span>
    </header>
    <div class="bingo-grid bingo-grid-5x5">
      <!-- Cells with owner colors and emojis -->
    </div>
    <div class="bingo-legend">
      <!-- Legend items from config.owners -->
    </div>
  </div>
</body>
</html>
```

---

## Generation Patterns

### Generate Annual Card

```
User: "Generate the 2026 annual bingo card"

1. Read config.json
2. Read goals file from config.paths.goalsFile
3. Parse "{year} Annual Goals" table
4. Create 5x5 grid HTML
5. Apply colors based on Owner (lookup in config.owners)
6. Add icons and goal names
7. Add owner emoji indicators
8. Mark completed goals with checkmark overlay
9. Generate legend from config.owners
10. Save to config.paths.outputFolder/Bingo-Annual-{year}.html
```

### Generate Single Monthly Card

```
User: "Generate January 2026 bingo card"

1. Read config.json
2. Read goals file
3. Parse "{year} Weekly Goals" table
4. Calculate start Monday for the month
5. Determine weeks in month view (4 or 5)
6. Create grid: 5 cols x (4-5) rows
7. Apply colors from config.owners
8. Add legend
9. Save to outputFolder/Bingo-Monthly-{year}-{month}.html
```

### Generate All Monthly Cards

```
User: "Generate all 2026 monthly bingo cards"

1. Read config.json
2. Read goals file
3. Loop through all 12 months
4. For each month, generate card using monthly pattern above
5. Combine into single multi-page document OR save as separate files
6. Save to outputFolder/Bingo-Monthly-{year}-All.html
```

---

## Print Workflow

1. Generate HTML card(s)
2. Open in Chrome/Edge
3. Press Cmd+P (Mac) or Ctrl+P (Windows)
4. Enable "Background graphics" for colors
5. Set margins to "None" or "Minimum"
6. Print or Save as PDF
