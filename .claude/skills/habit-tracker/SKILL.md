---
name: habit-tracker
description: Generate monthly printable habit tracking sheets with streak tracking and progress bars. Supports multiple trackers for different people with blank habit rows for handwriting.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
---

# Habit Tracker Skill

Generate beautiful, printable monthly habit tracking sheets with configurable habits, progress bars with rulers, streak tracking, and support for multiple trackers and blank/handwritten habits.

## Quick Start

### 1. List Available Trackers

Check what trackers exist:

```bash
ls .claude/skills/habit-tracker/trackers/
```

Available trackers: `user.json`, `partner.json`, etc.

### 2. Generate a Habit Tracker

```bash
/create:habits January 2026 {{user_first_name}}    # {{user_first_name}}'s January tracker
/create:habits February 2026 partner  # {{partner_name}}'s February tracker
/create:habits 2026 {{user_first_name}}            # All 12 months for {{user_first_name}}
```

### 3. Create a New Tracker

Copy an existing tracker and modify:

```bash
cp .claude/skills/habit-tracker/trackers/user.json \
   .claude/skills/habit-tracker/trackers/{{child_name}}.json
```

Then edit `{{child_name}}.json` with new habits and identity statements.

---

## Directory Structure

```
.claude/skills/habit-tracker/
├── SKILL.md                      # This documentation
├── habit-tracker-template.html   # HTML template with placeholders
├── tracker.schema.json           # JSON Schema for validation
├── shared-styles.json            # Shared visual styles
└── trackers/                     # One config file per tracker
    ├── user.json
    ├── partner.json
    └── [other trackers].json
```

---

## Tracker Configuration

Each tracker is a JSON file in `trackers/` with this structure:

```json
{
  "$schema": "../tracker.schema.json",
  "id": "user",
  "name": "{{user_first_name}}'s Tracker",
  "subtitle": "80% consistency, not perfection",
  "recovery": "If you miss a day, that's okay. Just don't miss two in a row.",
  "habits": [
    {
      "id": "exercise",
      "name": "Exercise",
      "frequency": "daily",
      "target": 80,
      "identity": "I am someone who moves my body every day..."
    },
    {
      "id": "blank-1",
      "frequency": "daily",
      "target": 80,
      "blank": true
    }
  ]
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase, alphanumeric with hyphens) |
| `name` | string | Display name shown on printed tracker |
| `habits` | array | List of habits to track |

### Optional Fields

| Field | Default | Description |
|-------|---------|-------------|
| `subtitle` | "80% consistency, not perfection" | Shown in header |
| `recovery` | "If you miss a day..." | Recovery message at bottom |

---

## Habit Definition

### Standard Habit

```json
{
  "id": "exercise",
  "name": "Exercise",
  "frequency": "daily",
  "target": 80,
  "identity": "I am someone who moves my body every day because..."
}
```

### Blank Habit (for Handwriting)

```json
{
  "id": "blank-1",
  "frequency": "daily",
  "target": 80,
  "blank": true
}
```

Blank habits render:
- **Name column**: Wide underline for handwriting the habit name
- **Checkboxes**: Normal daily or weekly circles
- **Identity section**: Blank underlines for writing identity statement
- **Stats section**: Normal Target/Streak/Best/Done fields

### Habit Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes (unless blank) | Unique identifier |
| `name` | Yes (unless blank) | Display name |
| `frequency` | Yes | `"daily"` or `"weekly"` |
| `target` | No (default: 80) | Target percentage 0-100 |
| `identity` | Yes (unless blank) | Identity statement |
| `blank` | No | Set to `true` for handwritten habits |

---

## Week Boundary Calculation

Uses the same script as Goal Bingo for consistent week alignment:

```bash
python3 .claude/skills/goal-bingo/scripts/week_allocation.py --month 1 --year 2026 --json
```

**Key rule**: Habit tracker always starts on a Monday, even if that Monday is in the previous month. Days outside the target month are shown grayed out.

---

## Template Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{{TRACKER_NAME}}` | From tracker config `name` field |
| `{{MONTH_NAME}}` | Full month name (e.g., "JANUARY") |
| `{{YEAR}}` | Four-digit year |
| `{{SUBTITLE}}` | From tracker config `subtitle` field |
| `{{DAYS_IN_GRID}}` | Total days in grid (always multiple of 7) |
| `{{DAY_NUMBERS}}` | Generated day number header row |
| `{{HABIT_ROWS}}` | Generated habit rows with checkboxes |
| `{{HABIT_DETAILS}}` | Bottom section with identity + stats |
| `{{RECOVERY_MESSAGE}}` | From tracker config `recovery` field |

---

## Shared Styles

Visual styles are defined in `shared-styles.json` and apply to all trackers:

```json
{
  "page": { "background": "#ffffff" },
  "checkbox": { "size": "18px", "weekendStyle": "dashed" },
  "progress": { "targetMarkerColor": "#10b981" }
}
```

To customize colors globally, edit this file.

---

## JSON Schema Validation

The `tracker.schema.json` file provides:
- **Editor validation**: Red squiggles in VS Code when config is invalid
- **Autocomplete**: Suggestions for property names
- **Documentation**: Hover for field descriptions

Each tracker config should reference the schema:
```json
{
  "$schema": "../tracker.schema.json",
  ...
}
```

---

## Output Files

Generated trackers are saved to:
```
workspace/3-Resources/Documents/Printables/Habit-Tracker-{Year}-{Month}-{TrackerName}.html
```

Examples:
- `Habit-Tracker-2026-January-{{user_first_name}}.html`
- `Habit-Tracker-2026-February-{{partner_name}}.html`

---

## Slash Command

Use `/create:habits` to generate habit trackers:

```bash
/create:habits                           # Prompts for tracker and month
/create:habits January {{user_first_name}}            # {{user_first_name}}'s January, current year
/create:habits January 2026 {{user_first_name}}       # {{user_first_name}}'s January 2026
/create:habits 2026 {{user_first_name}}               # All 12 months for {{user_first_name}}
/create:habits January 2026 partner      # {{partner_name}}'s January 2026
```

---

## Adding a New Tracker

1. Create a new file in `trackers/`:
   ```bash
   touch .claude/skills/habit-tracker/trackers/{{child_name}}.json
   ```

2. Add the schema reference and required fields:
   ```json
   {
     "$schema": "../tracker.schema.json",
     "id": "{{child_name}}",
     "name": "{{child_name}}'s Tracker",
     "habits": [...]
   }
   ```

3. Define habits (see Habit Definition above)

4. Generate: `/create:habits January 2026 {{child_name}}`

---

## Adding a Blank Habit Row

To add a handwritten habit slot:

```json
{
  "id": "blank-1",
  "frequency": "daily",
  "target": 80,
  "blank": true
}
```

You can add multiple blank habits (`blank-1`, `blank-2`, etc.) for multiple handwritten rows.

---

## Integration Points

- **Daily Planning**: Reference habit tracker during `/daily:plan`
- **Weekly Review**: Check habit progress during `/weekly:review`
- **Monthly Planning**: Generate new tracker during `/monthly:plan`

---

## File Locations

| File | Path |
|------|------|
| Skill documentation | `.claude/skills/habit-tracker/SKILL.md` |
| HTML Template | `.claude/skills/habit-tracker/habit-tracker-template.html` |
| JSON Schema | `.claude/skills/habit-tracker/tracker.schema.json` |
| Shared Styles | `.claude/skills/habit-tracker/shared-styles.json` |
| Tracker Configs | `.claude/skills/habit-tracker/trackers/*.json` |
| Week allocation script | `.claude/skills/goal-bingo/scripts/week_allocation.py` |
| Generated output | `workspace/3-Resources/Documents/Printables/Habit-Tracker-*.html` |
