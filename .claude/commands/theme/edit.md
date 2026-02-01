---
description: Edit an existing theme palette
argument-hint: "[theme-name]"
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion
---

# Theme Edit Command

Modify colors in an existing theme (preset or custom).

## Arguments

- `$ARGUMENTS` - Theme name to edit

## Execution

### 1. Load Theme

If no argument, list available themes and ask which to edit.

Load the palette:
- Check `.user/themes.yaml` for custom themes
- Check `.claude/skills/theme-management/palettes.yaml` for presets

### 2. Display Current Colors

Show the user the current palette:

```markdown
## Current Colors for [theme_name]

| Color | Value | Purpose |
|-------|-------|---------|
| primary | #xxxxxx | Titlebar, status bar |
| primaryInactive | #xxxxxx | Inactive titlebar |
| secondary | #xxxxxx | Activity bar, ribbon |
| tertiary | #xxxxxx | Sidebar background |
| border | #xxxxxx | Borders |
| accent | #xxxxxx | Active indicators |
| accentLight | #xxxxxx | Icons, highlights |
```

### 3. Ask What to Change

Use AskUserQuestion:

```
question: "Which colors would you like to change?"
header: "Edit"
multiSelect: true
options:
  - label: "primary"
    description: "Titlebar and status bar background"
  - label: "accent"
    description: "Active indicators and focus rings"
  - label: "All colors"
    description: "Review and potentially change each color"
```

### 4. Collect New Values

For each color being changed, ask for the new hex value.

Validate that values are proper 6-character hex codes.

### 5. Save Changes

**For custom themes**: Update `.user/themes.yaml` directly.

**For built-in presets**: Create a new custom theme instead:

```markdown
Note: Built-in presets are read-only. I'll save your modifications as a custom theme.
```

Ask for a name for the modified theme, then save to `.user/themes.yaml`.

### 6. Apply Updated Theme

```bash
python ./.claude/skills/theme-management/scripts/generate_theme.py "[theme_name]"
```

### 7. Report Results

```markdown
## Theme Updated: [theme_name]

Changed colors:
- [color1]: #old → #new
- [color2]: #old → #new

**VS Code**: Reload window to see changes
**Obsidian**: Changes should be visible immediately
```
