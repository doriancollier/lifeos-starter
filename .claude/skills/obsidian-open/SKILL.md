---
name: obsidian-open
description: Opens markdown files from this Obsidian vault in the Obsidian app interface. Use when the user wants to view, preview, or open a note in Obsidian rather than just reading it in the terminal.
---

# Obsidian Open

Opens markdown files in the Obsidian desktop application using the native URI scheme.

## When to use

- User asks to "open" or "view" a note in Obsidian
- User wants to see the rendered markdown with Obsidian features (backlinks, graph, etc.)
- User says "show me this in Obsidian" or similar

## Instructions

1. Determine the absolute path to the markdown file the user wants to open
2. Use the obsidian_manager.py script which handles vault registration automatically
3. The format is: `python3 {{vault_path}}/.claude/scripts/obsidian_manager.py open "/absolute/path/to/file.md"`

## Important notes

- The path must be absolute (starting with `/`)
- The vault root is: `{{vault_path}}`
- The script auto-registers the vault in Obsidian if needed (idempotent)
- Returns JSON with success status and any registration info

## Examples

### Open a specific note by path
```bash
python3 {{vault_path}}/.claude/scripts/obsidian_manager.py open "{{vault_path}}/README.md"
```

### Open today's daily note
```bash
python3 {{vault_path}}/.claude/scripts/obsidian_manager.py open "{{vault_path}}/workspace/4-Daily/$(date +%Y-%m-%d).md"
```

### Open a note in a subdirectory
```bash
python3 {{vault_path}}/.claude/scripts/obsidian_manager.py open "{{vault_path}}/workspace/2-Areas/{{company_1_name}}/Overview.md"
```

### Check vault registration status
```bash
python3 {{vault_path}}/.claude/scripts/obsidian_manager.py check
```

## Vault structure reference

Common locations in this vault:
- Daily notes: `workspace/4-Daily/YYYY-MM-DD.md`
- Projects: `workspace/1-Projects/Current/` or `workspace/1-Projects/Backlog/`
- Areas: `workspace/2-Areas/{{{company_1_name}},{{company_2_name}},{{company_3_name}},Personal}/`
- Meeting notes: `workspace/5-Meetings/YYYY/MM-Month/`
- People: `workspace/6-People/Professional/` or `workspace/6-People/Personal/`
- MOCs: `workspace/7-MOCs/`
