---
description: Create a new meeting note for any company
argument-hint: [company-id] [meeting-title]
allowed-tools: Read, Write, Bash, Glob
---

# Create Meeting Note

Create a new meeting note for a specified company using the generic meeting template.

## Arguments

- `$ARGUMENTS` - Format: `[company-id] [meeting-title]`
  - `company-id`: One of `ab` ({{company_1_name}}), `144` ({{company_2_name}}), `emh` ({{company_3_name}}), `personal`
  - `meeting-title`: The meeting title (e.g., "Product Sync with Alex")

## Context

- **Template**: `{{vault_path}}/3-Resources/Templates/meeting.md`
- **Output directory**: `{{vault_path}}/5-Meetings/YYYY/MM-Month/` (use current year and month)
- **Today's date**: Use `date +%Y-%m-%d`
- **Contacts config**: `{{vault_path}}/0-System/config/contacts-config.json`

## Company ID Mapping

| ID | Company | Config Key |
|----|---------|------------|
| `ab` | {{company_1_name}} | `company_1` |
| `144` | {{company_2_name}} | `company_2` |
| `emh` | {{company_3_name}} | `company_3` |
| `personal` | Personal | N/A |

## Task

1. **Parse arguments** to extract company ID and meeting title
2. **Load contacts config** to get full company name
3. **Read the meeting template** from `workspace/3-Resources/Templates/meeting.md`
4. **Create meeting note** with filename format: `YYYY-MM-DD - [Meeting Title].md`
5. **Replace template variables**:
   - `{{title}}` with the meeting title
   - `{{date:YYYY-MM-DD}}` with today's date
   - `{{company}}` with the full company name
6. **Add company tag** to frontmatter tags array
7. **Ensure the output directory exists** (create if needed)
8. **Save the file**
9. **Open it in Obsidian** using the `obsidian-open` skill

## Attendee Suggestions

Load attendees from contacts config under `companies.[company_key].contacts`.

Suggest relevant attendees based on:
- Meeting title keywords
- Their roles

## Output

- Confirm the file was created
- Show the file path
- List suggested attendees based on meeting title
- Offer to open the note in Obsidian

## Examples

```
/meeting:create ab Product Sync with Alex
/meeting:create 144 Sprint Planning
/meeting:create personal Family Budget Discussion
```
