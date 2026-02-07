---
description: Import meetings from SuperNormal
argument-hint: [--all | --dry-run]
allowed-tools: Bash, Read
---

# SuperNormal Meeting Sync Command

Import AI-generated meeting notes and transcripts from SuperNormal into the vault.

## Arguments

- `$ARGUMENTS` - Optional flags:
  - `--all` - Re-sync all meetings (overwrites existing)
  - `--dry-run` - Preview what would be synced without downloading
  - (no args) - Sync new meetings only (default)

## Task

### 1. Run the Sync Script

```bash
cd integrations/supernormal && node sync-meetings.js $ARGUMENTS
```

### 2. Handle First-Time Setup

If the browser opens and prompts for login:
- Complete Google OAuth login in SuperNormal
- Session is saved in `chrome-profile/` for future runs

### 3. Report Results

After sync completes, summarize:
- Number of meetings downloaded
- Any errors encountered
- Location of new meeting folders

## Output Format

```markdown
## SuperNormal Sync Complete

**Mode**: [Incremental / Full / Dry Run]
**Meetings synced**: [count]

### New Meetings
- `2026-01-07-11-15-ab-planning/` - {{company_1_name}} Planning
- `2026-01-05-16-54-ab-review/` - {{company_1_name}} Review

### Notes
- [Any errors or warnings]
- [Login required notice if applicable]
```

## What Gets Imported

Each meeting creates a folder in `workspace/5-Meetings/YYYY/MM-Month/`:

| File | Contents |
|------|----------|
| `meeting.md` | Structured note with attendees, action items |
| `notes-supernormal.md` | SuperNormal's AI summary |
| `transcript.md` | Full transcript with timestamps |

## Attendee Detection Limitation

SuperNormal doesn't provide explicit attendee lists. The script detects attendees from greeting patterns (e.g., "Hey [Name]"). Some attendees may be missed - manual review recommended.

## Related

- `/meeting:prep` - Prepare context before a meeting
- `/meeting:ab`, `/meeting:144`, `/meeting:emh` - Create manual meeting notes
- See `workspace/0-System/guides/meeting-workflow.md` for full documentation
