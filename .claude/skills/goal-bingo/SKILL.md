---
name: goal-bingo
description: Generating printable Goal Bingo cards for gamified goal tracking. Use when user asks to create, generate, or print bingo cards, mentions "goal bingo", wants to track annual or monthly goals with bingo format, or needs to update bingo goal completion status.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
---

# Goal Bingo Skill

Generate beautiful, printable Goal Bingo cards for gamified goal tracking. Fully configurable for any family or team.

## First-Time Setup

Before first use, personalize the `config.json` file at `.claude/skills/goal-bingo/config.json`:

1. **Edit owner names**: Update `owners[].name` with actual family member names
2. **Adjust emojis**: Change `owners[].emoji` to preferred representations
3. **Update colors**: Modify `owners[].color` for preferred color scheme
4. **Verify paths**: Ensure `paths.goalsFile` points to your goals markdown file

The config includes a `{{user_first_name}}` placeholder that should be replaced with the actual name after vault personalization.

## Quick Start

### 1. Load Configuration First

**Always read config.json before generating cards:**

```
.claude/skills/goal-bingo/config.json
```

This defines owners (people), colors, paths, and prize tiers.

### 2. Generate a Card

**Annual Card:**
```
1. Read config.json
2. Read template from config.paths.templateFile
3. Read goals from config.paths.goalsFile
4. Parse "{year} Annual Goals" table
5. Replace template placeholders (see template file for list)
6. Save to config.paths.outputFolder/Bingo-Annual-{year}.html
```

**Monthly Card:**
```
1. Read config.json
2. Read template from config.paths.templateFileMonthly
3. Read goals from config.paths.goalsFile
4. Parse "{year} Weekly Goals" table
5. Run week_allocation.py or use continuous chain algorithm:
   - January starts on Monday closest to Jan 1
   - Each month chains from previous (no gaps/overlaps)
6. Replace template placeholders with 4-5 row grid
7. Week labels use start dates (e.g., "Dec 29", "Jan 5")
8. Save to config.paths.outputFolder/Bingo-Monthly-{year}-{month}.html
```

### 3. Update Goal Status

When a goal is completed, update the goals file:
```markdown
| Row | Col | Goal | Owner | Icon | Status |
| 1 | 1 | Goal Name | OwnerName | 🎯 | complete |
```

---

## Reference Documentation

| Topic | File | When to Read |
|-------|------|--------------|
| Game rules & prize mechanics | [rules.md](rules.md) | User asks how bingo works, earning draws, prize pool |
| Card generation details | [card-generation.md](card-generation.md) | Need HTML structure, date calculations, CSS generation |
| Annual HTML template | [bingo-card-template.html](bingo-card-template.html) | Need to understand annual card placeholders |
| Monthly HTML template | [bingo-card-template-monthly.html](bingo-card-template-monthly.html) | Need to understand monthly card placeholders |
| Week allocation script | [scripts/week_allocation.py](scripts/week_allocation.py) | Calculate week boundaries using continuous chain |
| Owner/path configuration | [config.json](config.json) | Adding owners, changing colors, updating paths |

---

## Card Types

### Annual Card
- **Grid**: 5x5
- **Content**: One-time goals (trips, milestones, health appointments)
- **One card per year**

### Monthly Card
- **Grid**: 5 columns x 4-5 rows
- **Content**: Recurring weekly habits
- **New card each month**
- **Start date**: Always a Monday (continuous chain - no gaps between months)
- **Week labels**: Start dates only (e.g., "Dec 29", "Jan 5")
- **Template**: `bingo-card-template-monthly.html`

---

## Configuration Overview

`config.json` contains:

```json
{
  "owners": [
    { "id": "person1", "name": "Person 1", "color": "#F5D0E0", "emoji": "👤" }
  ],
  "styles": {
    "pageBackground": "#E8F4FD",
    "headerIcon": "🐴"
  },
  "paths": {
    "goalsFile": "path/to/goals.md",
    "templateFile": "path/to/bingo-card-template.html",
    "templateFileMonthly": "path/to/bingo-card-template-monthly.html",
    "weekAllocationScript": "path/to/scripts/week_allocation.py",
    "outputFolder": "path/to/output/"
  },
  "prizeTiers": [
    { "id": "small", "emoji": "🟢" }
  ]
}
```

### Owner Lookup

Match goal owners to config by `id` or `name`:
```javascript
const owner = config.owners.find(o =>
  o.id === ownerName.toLowerCase() ||
  o.name.toLowerCase() === ownerName.toLowerCase()
);
```

---

## Goals File Format

The goals file (path in `config.paths.goalsFile`) uses markdown tables:

**Annual Goals:**
```markdown
## 2026 Annual Goals

| Row | Col | Goal | Owner | Icon | Status |
|-----|-----|------|-------|------|--------|
| 1 | 1 | Goal Name | OwnerName | 🎯 | incomplete |
```

**Weekly Goals:**
```markdown
## 2026 Weekly Goals

| Col | Goal | Owner | Icon |
|-----|------|-------|------|
| 1 | Weekly Goal | OwnerName | 🏃 |
```

---

## Example Prompts

| User Says | Action |
|-----------|--------|
| "Create the 2026 bingo card" | Generate annual card |
| "Make January's bingo card" | Generate monthly card |
| "Generate all monthly bingo cards" | Generate 12 monthly cards |
| "Update bingo - we completed X" | Update goal status |
| "How does bingo work?" | Read [rules.md](rules.md) |
| "Add a new person to bingo" | Update config.json |

---

## Integration Points

- **Annual Planning**: Offer to set up Goal Bingo during `/goals:review`
- **Goal Tracking**: Suggest updating bingo when goals complete
- **Reviews**: Check bingo progress during weekly/monthly reviews

---

## Sharing This Skill

To share with others:

1. Copy entire `.claude/skills/goal-bingo/` folder (includes template)
2. Edit `config.json` with their owners (names, colors, emojis)
3. Update `config.paths` to match their vault structure
4. Create a goals markdown file matching the table format above

The skill is fully self-contained — template, rules, and config all travel together.
