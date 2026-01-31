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
2. Use the `open` command with the `obsidian://` URI scheme
3. The format is: `open "obsidian:///absolute/path/to/file.md"`

## Important notes

- The path must be absolute (starting with `/`)
- The vault root is: `{{vault_path}}`
- Spaces in paths are handled automatically by quoting the URL
- Obsidian must be installed and the vault must be open/registered

## Examples

### Open a specific note by path
```bash
open "obsidian://{{vault_path}}/README.md"
```

### Open today's daily note
```bash
open "obsidian://{{vault_path}}/4-Daily/$(date +%Y-%m-%d).md"
```

### Open a note in a subdirectory
```bash
open "obsidian://{{vault_path}}/2-Areas/{{company_1_name}}/Overview.md"
```

## Vault structure reference

Common locations in this vault:
- Daily notes: `4-Daily/YYYY-MM-DD.md`
- Projects: `1-Projects/Current/` or `1-Projects/Backlog/`
- Areas: `2-Areas/{{{company_1_name}},{{company_2_name}},{{company_3_name}},Personal}/`
- Meeting notes: `5-Meetings/YYYY/MM-Month/`
- People: `6-People/Professional/` or `6-People/Personal/`
- MOCs: `7-MOCs/`
