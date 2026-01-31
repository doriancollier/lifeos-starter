---
description: Create a new {{company_1_name}} meeting note
argument-hint: [meeting-title]
allowed-tools: Read, Write, Bash, Glob
---

# Create {{company_1_name}} Meeting Note

Create a new meeting note for {{company_1_name}} using the company template.

## Arguments

- `$ARGUMENTS` - The meeting title (e.g., "Product Sync with Alex")

## Context

- **Template**: `{{vault_path}}/3-Resources/Templates/meeting.md`
- **Output directory**: `{{vault_path}}/5-Meetings/YYYY/MM-Month/` (use current year and month)
- **Today's date**: !`date +%Y-%m-%d`

## Task

1. Read the meeting template and set `{{company}}` to "{{company_1_name}}"
2. Create a new meeting note with filename format: `YYYY-MM-DD - [Meeting Title].md`
3. Replace template variables:
   - `{{title}}` with the meeting title from arguments
   - `{{date:YYYY-MM-DD}}` with today's date
4. Ensure the output directory exists (create if needed)
5. Save the file
6. Open it in Obsidian

## Key {{company_1_name}} Attendees

Common attendees loaded from `/0-System/config/contacts-config.json` under `companies.company_1.contacts`.

Suggest relevant attendees based on meeting title and their roles.

## Output

- Confirm the file was created
- Show the file path
- List suggested attendees based on meeting title
- Open the note in Obsidian
