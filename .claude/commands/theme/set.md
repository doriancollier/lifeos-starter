---
description: Set the editor theme for VS Code and Obsidian
argument-hint: "[theme-name]"
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Theme Set Command

Apply a theme to both VS Code and Obsidian simultaneously.

## Arguments

- `$ARGUMENTS` - Theme name (e.g., "midnight", "red", "forest", "purple", "orange", "ocean", or a custom theme name)

## Execution

### 1. Validate Theme Exists

If no argument provided, list available themes and ask user to choose:

```bash
python "$CLAUDE_PROJECT_DIR/.claude/skills/theme-management/scripts/generate_theme.py" --list
```

### 2. Apply Theme

Run the generation script:

```bash
python "$CLAUDE_PROJECT_DIR/.claude/skills/theme-management/scripts/generate_theme.py" "$ARGUMENTS"
```

### 3. Verify Success

Check that files were updated:
- `.vscode/settings.json` - should have `workbench.colorCustomizations`
- `.obsidian/snippets/themed-chrome.css` - should exist
- `.obsidian/appearance.json` - should have `themed-chrome` in `enabledCssSnippets`

### 4. Report Results

Tell the user:

```markdown
## Theme Applied: [theme_name]

**VS Code**: Reload window to see changes (Cmd+Shift+P → "Reload Window")
**Obsidian**: Changes should be visible immediately

Files updated:
- `.vscode/settings.json`
- `.obsidian/snippets/themed-chrome.css`
- `.obsidian/appearance.json`
```

## Error Handling

If theme not found:
1. List available themes
2. Suggest using `/theme:create` for custom themes
3. Suggest `/theme:from-color` to generate from a favorite color
