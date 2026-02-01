---
description: Generate a complete theme from your favorite color
argument-hint: "[hex-color]"
allowed-tools: Read, Write, Bash, AskUserQuestion
---

# Theme From Color Command

Generate a full 7-color palette from a single hex color.

## Arguments

- `$ARGUMENTS` - Hex color (e.g., "#4a9eff" or "4a9eff")

## Execution

### 1. Validate Color

If no argument provided, ask the user:

```
question: "What's your favorite color? (Enter a hex code like #4a9eff)"
header: "Color"
options:
  - label: "Blue (#4a9eff)"
    description: "Professional, calm, trustworthy"
  - label: "Green (#4ade80)"
    description: "Natural, growth, balance"
  - label: "Purple (#a855f7)"
    description: "Creative, unique, sophisticated"
  - label: "Orange (#f97316)"
    description: "Energetic, warm, enthusiastic"
```

Validate the hex format:
- Strip leading `#` if present
- Must be exactly 6 hexadecimal characters
- Case insensitive

### 2. Ask for Theme Name

```
question: "What would you like to name this theme?"
header: "Name"
options:
  - label: "personal (Recommended)"
    description: "A theme just for you"
  - label: "custom"
    description: "Generic custom theme"
  - label: "brand"
    description: "Your brand colors"
```

### 3. Generate and Apply

Run the generation script:

```bash
python3 .claude/skills/theme-management/scripts/generate_theme.py \
  --from-color "[hex]" --name "[name]" --save
```

### 4. Show Generated Palette

Display the generated colors:

```markdown
## Generated Theme: [name]

From your color **[input_hex]**, I created this palette:

| Color | Value | Purpose |
|-------|-------|---------|
| accent | [input] | Active indicators |
| accentLight | [computed] | Icons, highlights |
| primary | [computed] | Titlebar, status |
| primaryInactive | [computed] | Inactive titlebar |
| secondary | [computed] | Activity bar, ribbon |
| tertiary | [computed] | Sidebar background |
| border | [computed] | Borders |

Theme saved to `.user/themes.yaml` and applied.

**VS Code**: Reload window to see changes
**Obsidian**: Changes should be visible immediately
```

### 5. Offer Refinement

Ask if they want to adjust:

```
question: "Does the theme look good, or would you like to adjust any colors?"
header: "Adjust"
options:
  - label: "Looks great!"
    description: "Keep the theme as-is"
  - label: "Adjust colors"
    description: "I'll help you fine-tune specific colors"
```

If they want to adjust, invoke `/theme:edit [name]`.

## Color Generation Algorithm

The script uses these derivations:

```
accent       = input color
accentLight  = lighten(accent, 20%)
primary      = darken(accent, 40%)
primaryInactive = darken(accent, 55%)
secondary    = darken(accent, 60%)
tertiary     = darken(accent, 75%)
border       = darken(accent, 30%)
```

This ensures:
- Proper contrast hierarchy (tertiary darkest → primary brightest for chrome)
- Accent stands out against all backgrounds
- Visual harmony from single color source
