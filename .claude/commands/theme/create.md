---
description: Create a custom theme palette interactively
argument-hint: "[theme-name]"
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion
---

# Theme Create Command

Create a custom theme with an interactive wizard.

## Arguments

- `$ARGUMENTS` - Name for the new theme (required)

## Execution

### 1. Validate Name

If no name provided, ask for one using AskUserQuestion.

Validate the name:
- Lowercase, alphanumeric, hyphens allowed
- No spaces or special characters
- Not a built-in theme name (midnight, red, forest, purple, orange, ocean)

### 2. Choose Creation Method

Ask the user using AskUserQuestion:

```
question: "How would you like to create your theme?"
header: "Method"
options:
  - label: "Generate from a single color (Recommended)"
    description: "Pick your favorite color and I'll generate a full palette"
  - label: "Define all 7 colors manually"
    description: "Full control over every color in the palette"
  - label: "Start from an existing theme"
    description: "Copy and modify a built-in preset"
```

### 3A. Generate from Color

If user chose "Generate from a single color":

1. Ask for their color:
   ```
   question: "What hex color would you like as your accent/highlight color?"
   header: "Accent"
   options:
     - label: "Blue (#4a9eff)"
       description: "Professional, calm"
     - label: "Green (#4ade80)"
       description: "Natural, growth"
     - label: "Purple (#a855f7)"
       description: "Creative, unique"
     - label: "Orange (#f97316)"
       description: "Energetic, warm"
   ```

2. Generate and save theme:
   ```bash
   python "$CLAUDE_PROJECT_DIR/.claude/skills/theme-management/scripts/generate_theme.py" \
     --from-color "<hex>" --name "$ARGUMENTS" --save
   ```

### 3B. Manual Definition

If user chose "Define all 7 colors":

Collect each color using AskUserQuestion or ask them to provide all 7:

1. **primary** - Titlebar/status bar background
2. **primaryInactive** - Inactive titlebar (darker than primary)
3. **secondary** - Activity bar/ribbon (darker than primary)
4. **tertiary** - Sidebar background (darkest)
5. **border** - Border color
6. **accent** - Active indicators, focus rings
7. **accentLight** - Icons, highlights (lighter than accent)

Save to `.user/themes.yaml`:

```yaml
custom_themes:
  [theme-name]:
    name: "[Theme Name]"
    description: "Custom theme"
    primary: "[hex]"
    primaryInactive: "[hex]"
    secondary: "[hex]"
    tertiary: "[hex]"
    border: "[hex]"
    accent: "[hex]"
    accentLight: "[hex]"
```

### 3C. Copy from Existing

If user chose "Start from an existing theme":

1. Ask which preset to copy
2. Load that palette from `palettes.yaml`
3. Ask which colors to modify
4. Save modified palette to `.user/themes.yaml`

### 4. Apply Theme

After saving, apply the new theme:

```bash
python "$CLAUDE_PROJECT_DIR/.claude/skills/theme-management/scripts/generate_theme.py" "$ARGUMENTS"
```

### 5. Report Results

```markdown
## Custom Theme Created: [theme_name]

Your theme has been saved to `.user/themes.yaml` and applied.

**VS Code**: Reload window to see changes
**Obsidian**: Changes should be visible immediately

To use this theme again: `/theme:set [theme_name]`
To modify it: `/theme:edit [theme_name]`
```
