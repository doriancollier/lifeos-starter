---
name: theme-management
description: Generate synchronized VS Code + Obsidian themes from color palettes. Use when user asks about themes, colors, or visual customization.
---

# Theme Management Skill

Generates synchronized VS Code and Obsidian themes from a single color palette definition.

## When to Use

- User asks to change the theme or colors
- User mentions their favorite color
- Setting up a new vault (during onboarding)
- User wants visual distinction between projects

## Design Philosophy

**Chrome-only theming**: Themes apply to UI elements (titlebar, sidebar, tabs, status bar, ribbon) only. Document content uses default editor styling for maximum readability.

This approach:
- Preserves document readability with well-tested defaults
- Provides visual context/identity without affecting content
- Avoids issues with syntax highlighting and document colors

## Color System

### Core Palette (7 colors - user configurable)

| Key | Purpose | Example |
|-----|---------|---------|
| `primary` | Titlebar, status bar backgrounds | `#1a1a2e` |
| `primaryInactive` | Inactive title/status | `#141428` |
| `secondary` | Activity bar, ribbon, active tabs | `#16213e` |
| `tertiary` | Sidebar backgrounds | `#0f0f1a` |
| `border` | All borders | `#2a2a4a` |
| `accent` | Active indicators, focus rings | `#4a9eff` |
| `accentLight` | Icons, highlights | `#7eb8ff` |

### Computed Colors (derived automatically)

| Key | Derivation | Purpose |
|-----|------------|---------|
| `primaryHover` | lighten(primary, 15%) | Hover states |
| `accentAlpha20` | accent + "20" | Selection backgrounds |
| `accentAlpha15` | accent + "15" | Highlight backgrounds |

### Neutral Colors (hardcoded - semantic)

| Color | Purpose |
|-------|---------|
| `#ffffff` | Text on primary/accent |
| `#cccccc` | Inactive foreground |
| `#999999` | Muted text (tabs) |
| `#666666` | Empty state text |

## Built-in Presets

| Theme | Character | Primary | Accent |
|-------|-----------|---------|--------|
| `midnight` (default) | Deep navy | `#1a1a2e` | `#4a9eff` |
| `red` | Dark crimson | `#8B0000` | `#ff0000` |
| `forest` | Nature green | `#1a3320` | `#4ade80` |
| `purple` | Royal purple | `#2d1b4e` | `#a855f7` |
| `orange` | Warm amber | `#3d2000` | `#f97316` |
| `ocean` | Teal cyan | `#0c2d3f` | `#22d3ee` |

## Commands

| Command | Purpose |
|---------|---------|
| `/theme:set [name]` | Apply a theme (preset or custom) |
| `/theme:create [name]` | Interactive custom theme wizard |
| `/theme:edit [name]` | Modify an existing palette |
| `/theme:from-color [hex]` | Generate theme from favorite color |

## Generate Theme from Color

When generating from a single hex color:

```
accent       = input color
accentLight  = lighten(accent, 20%)
primary      = darken(accent, 40%)
primaryInactive = darken(accent, 55%)
secondary    = darken(accent, 60%)
tertiary     = darken(accent, 75%)
border       = darken(accent, 30%)
```

## File Structure

```
.claude/skills/theme-management/
├── SKILL.md                              # This documentation
├── palettes.yaml                         # Built-in preset palettes
├── templates/
│   ├── vscode-colors.json                # VS Code colorCustomizations template
│   └── obsidian-chrome.css               # Obsidian CSS template
└── scripts/
    └── generate_theme.py                 # Generation script

.user/themes.yaml                         # Custom user themes
```

## Output Files

When a theme is applied:

| File | Content |
|------|---------|
| `.vscode/settings.json` | `workbench.colorCustomizations` merged in |
| `.obsidian/snippets/themed-chrome.css` | Generated CSS |
| `.obsidian/appearance.json` | Snippet enabled |

## Best Practices

### For Users

1. **Start with a preset** - Try built-in themes before customizing
2. **Use `/theme:from-color`** - Easiest way to personalize
3. **Reload VS Code** - After theme changes, reload window (Cmd+Shift+P → "Reload Window")

### For Theme Creation

1. **Contrast requirements** - Primary/accent need sufficient contrast with white text
2. **Dark backgrounds** - tertiary should be darkest, secondary lighter, primary for emphasis
3. **Accent visibility** - accent color should stand out against secondary/tertiary backgrounds
4. **Test both editors** - Apply and verify in both VS Code and Obsidian

### Common Mistakes to Avoid

1. **Theming document content** - Don't modify editor text, cursor, or syntax colors
2. **Insufficient contrast** - Ensure text remains readable
3. **Too many bright colors** - UI chrome should be subtle, not distracting
4. **Forgetting primaryInactive** - Should be noticeably darker than primary

## Integration Points

- **Setup Onboarding**: Asks favorite color, generates personal theme
- **Identity Config**: `favorite_color` stored in `.user/identity.yaml`
- **Custom Themes**: Saved to `.user/themes.yaml`

## CLI Usage

```bash
# List available themes
python .claude/skills/theme-management/scripts/generate_theme.py --list

# Apply a preset
python .claude/skills/theme-management/scripts/generate_theme.py midnight

# Generate from color
python .claude/skills/theme-management/scripts/generate_theme.py --from-color "#4a9eff" --name personal --save

# Apply custom theme
python .claude/skills/theme-management/scripts/generate_theme.py personal
```

## Troubleshooting

**Theme not showing in VS Code:**
- Reload window: Cmd+Shift+P → "Developer: Reload Window"
- Check `.vscode/settings.json` exists and has `workbench.colorCustomizations`

**Theme not showing in Obsidian:**
- Check Settings → Appearance → CSS Snippets
- Ensure `themed-chrome` is enabled
- Look for syntax errors in `.obsidian/snippets/themed-chrome.css`

**Colors look wrong:**
- Verify palette values are valid 6-character hex codes
- Check for typos in color values
- Ensure no conflicting CSS snippets are enabled
