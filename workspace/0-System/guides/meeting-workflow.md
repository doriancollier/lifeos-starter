---
title: "Meeting Workflow Guide"
created: "2025-12-02"
status: "active"
---

# Meeting Workflow Guide

Preparation, capture, and follow-up for meetings in LifeOS.

## The Meeting Lifecycle

```
Preparation → Capture → Follow-up
      ↓           ↓          ↓
/meeting:prep   Template   Action Items
```

## Before the Meeting

### Quick Prep

```
/meeting:prep [person or topic]
```

This gathers context for your meeting:

### What Gets Gathered

| Category | Information |
|----------|-------------|
| **Attendees** | Name, role, communication style, recent interactions |
| **Previous Meetings** | Past discussions, decisions made, patterns |
| **Open Action Items** | What's outstanding between you |
| **Related Projects** | Active work relevant to the discussion |
| **Suggested Agenda** | Topics based on history and open items |

### Prep Output Format

```markdown
## Meeting Prep: [Meeting Title]

### Attendees
- **Alex Smith** - CPO - Prefers Slack, values directness

### Previous Meetings
- 2025-11-25: Discussed analytics roadmap, agreed on Q1 priorities
- 2025-11-18: Reviewed collector engagement metrics

### Open Action Items
- [ ] Alex: Review PR for analytics dashboard - Due: today
- [ ] You: Send updated specs - Due: this week

### Related Projects
- [[Example-Project-1]] - Status: In Progress
- [[Example-Project-2]] - Status: Active

### Suggested Agenda Items
1. Follow up on PR review
2. Decision needed on Q1 timeline
3. Update on feature testing
```

## Recurring Meeting Templates

For recurring meetings (weekly syncs, standups), LifeOS auto-matches templates.

### How Template Matching Works

1. You run `/meeting:prep Engineering Sync`
2. System normalizes → `engineering-sync`
3. Searches `3-Resources/Templates/recurring-meeting-*.md`
4. Finds `recurring-meeting-engineering-sync.md`
5. Surfaces pre-meeting checklist and agenda structure

### Available Recurring Templates

| Meeting | Template | Schedule |
|---------|----------|----------|
| Engineering Sync | `recurring-meeting-engineering-sync.md` | Monday 11:30 AM |
| AssetOps Sync | `recurring-meeting-assetops.md` | Daily 2:30 PM |

### What Templates Include

```markdown
## Pre-Meeting Checklist
- [ ] Check Linear board for open issues
- [ ] Review PRs awaiting review
- [ ] Note any blocked items

## Standard Agenda
1. Open issues review
2. PR/Code review status
3. Blockers and dependencies
4. Week priorities
```

## During the Meeting

### Create Meeting Note

Choose the company context:

```
/meeting:ab [title]      # {{company_1_name}}
/meeting:144 [title]     # {{company_2_name}}
/meeting:emh [title]     # {{company_3_name}}
```

### Note Location

**Simple meetings** (single file):
```
5-Meetings/YYYY/MM-Month/YYYY-MM-DD-title.md
```

**Complex meetings** (multiple artifacts):
```
5-Meetings/YYYY/MM-Month/YYYY-MM-DD-title/
├── meeting.md              # Main meeting note (canonical)
├── transcript.md           # AI or manual transcript
├── notes-attendee.md       # Notes from specific attendee
└── attachments/            # PDFs, slides, other files
```

Use the directory structure when a meeting has:
- Transcripts from Otter.ai, Fireflies, etc.
- Notes from multiple attendees
- Presentation slides or attachments
- Reference documents discussed

### Adding Artifacts via Inbox

Drop meeting-related files into `0-Inbox/` and run `/inbox:process`:
1. Drop file: `0-Inbox/product-sync-transcript.txt`
2. Run `/inbox:process`
3. Claude matches to meeting, creates directory if needed, moves file

### Meeting Note Structure

```markdown
---
title: "Product Sync"
date: "2025-12-02"
company: "{{company_1_name}}"
attendees: ["Alex Smith", "Sam Taylor"]
type: "sync"
has_artifacts: false          # Set to true when meeting has transcript/notes/attachments
---

# Product Sync

## Artifacts
<!-- Only include when has_artifacts: true -->
| Type | File | Source |
|------|------|--------|
| Transcript | [[transcript]] | Otter.ai |

## Pre-Meeting Context
[Auto-populated from prep if available]

## Key Discussions
- Topic 1: [details]
- Topic 2: [details]

## Decisions Made
- Decision 1: We will do X
- Decision 2: Approved approach Y

## Action Items
- [ ] @Alex: Review PR by Wednesday
- [ ] @{{user_first_name}}: Send updated specs by Friday
- [ ] @Sam: Check infrastructure capacity

## Follow-up
- Schedule follow-up for next week
- Check on X before next meeting
```

## After the Meeting

### Extract Action Items

When processing meeting transcripts via `/inbox:process`, action items are extracted and routed.

#### Action Item Format in Meeting Notes

```markdown
## Action Items

### Assigned to {{user_first_name}}
- [ ] Create dashboards for wallet metrics - [[AB-New-Wallet-Reports]]
- [ ] Draft email strategy - [[AB-Email-Drip-Campaigns]]

### Assigned to Others
- [ ] @Sam: Check expedition sold-out state
- [ ] @Alex: Compile updated timelines post-strategy meetings

### Unassigned
- [ ] Outline technical areas affected by L2 support

### Already Tracked Elsewhere
- Push scheduling updates → [[2025-12-03#🔴2]]
```

#### Routing Options

| Destination | When to Use |
|-------------|-------------|
| **Meeting note only** | Reference, tasks for others, unassigned |
| **Daily note** | {{user_first_name}}'s tasks for immediate tracking |
| **Project file** | Project-specific work |
| **Both daily + project** | Cross-linked for visibility |

#### Deduplication

Before adding tasks, the system checks for existing similar tasks in:
- Daily notes (last 7 days)
- Project files
- Recent meeting notes

Already-tracked tasks are marked with `→ Tracked in [[location]]` rather than duplicated.

#### Cross-Link Convention

Tasks that exist in multiple places use wiki-links:

**In meeting note:**
```markdown
- [ ] Task description → Tracked in [[2025-12-03#🔴2]]
```

**In daily note:**
```markdown
- [ ] 🟡 Task - Company: {{company_1_name}} - [[meeting#Action Items|from Product Sync]]
```

**In project file:**
```markdown
- [ ] Task description - Source: [[2025-12-03-product-sync/meeting]]
```

### Update Person Files

When significant information emerges about attendees:

```markdown
Learned in meeting that Alex is focusing on mobile strategy for Q1.
→ Update [[Alex Smith]] person file
```

The `person-file-management` skill can help automatically.

### Link to Projects

Connect meeting notes to relevant projects:

```markdown
## Related
- [[Project-Name-1]]
- [[Project-Name-2]]
```

## Meeting Types

### Standard Meeting Templates

| Type | Created By | Use Case |
|------|------------|----------|
| {{company_1_name}} | `/meeting:ab` | AB work meetings |
| {{company_2_name}} | `/meeting:144` | 144 work meetings |
| {{company_3_name}} | `/meeting:emh` | EMC business meetings |
| Personal | Manual | Family, medical, etc. |

### Recurring vs One-Off

| Type | Template Location | Notes |
|------|-------------------|-------|
| Recurring | `3-Resources/Templates/recurring-meeting-*.md` | Auto-matched by name |
| One-off | Standard company template | Created on demand |

## Key People Reference

Key people are loaded from `/0-System/config/contacts-config.json`.

### Finding Company Contacts

Check `contacts-config.json` under:
- `companies.company_1.contacts` → {{company_1_name}} team
- `companies.company_2.contacts` → {{company_2_name}} contacts

### Finding Person Information

```
/create:person [name]
```

This searches for or creates a person file with relationship details.

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/meeting:prep [name]` | Prepare context for meeting |
| `/meeting:ab [title]` | Create {{company_1_name}} meeting note |
| `/meeting:144 [title]` | Create {{company_2_name}} meeting note |
| `/meeting:emh [title]` | Create EMC meeting note |
| `/create:person [name]` | Look up or create person file |

## Best Practices

### Do

1. **Prep before important meetings** — 5 minutes saves confusion
2. **Create notes during** — Capture while fresh
3. **Link to people** — Use `[[Person Name]]` syntax
4. **Link to projects** — Connect context
5. **Clear action items** — Who, what, when

### Don't

1. **Don't skip prep for recurring meetings** — Templates help
2. **Don't leave orphan notes** — Link to projects/people
3. **Don't hoard action items** — Move to daily notes if needed
4. **Don't forget follow-up** — Set reminders

## SuperNormal Meeting Sync

Automatic import of AI-generated meeting notes and transcripts from [SuperNormal](https://supernormal.com).

### What Gets Imported

| File | Contents |
|------|----------|
| `meeting.md` | Structured note with company, attendees, action items |
| `notes-supernormal.md` | SuperNormal's AI-generated summary and tasks |
| `transcript.md` | Full meeting transcript with timestamps |

### Folder Naming

```
5-Meetings/YYYY/MM-Month/YYYY-MM-DD-HH-MM-{company}-{title}/
```

**Example**: `2026-01-07-11-15-ab-planning/`

The sync script automatically detects:
- **Company**: Based on attendees and content keywords
- **Meeting title**: Cleans up generic titles, detects meeting type
- **Attendees**: From greeting patterns in transcript (see limitations below)
- **Time**: Extracted from SuperNormal headers

### Company Detection

| Company | Detection Triggers |
|---------|-------------------|
| {{company_1_name}} | Contacts from contacts-config.json + keywords from config |
| {{company_2_name}} | Contacts from contacts-config.json + keywords from config |
| {{company_3_name}} | {{partner_name}} + keywords from config |
| Personal | Default when no company indicators found |

### Meeting Title Detection

| Pattern in Content | Generated Title |
|-------------------|-----------------|
| "product sync/meeting/call" | Planning |
| "standup" | Standup |
| "retrospective" | Retrospective |
| "review" | Review |
| "1:1" or "one on one" | 1:1 |

### Running the Sync

```bash
cd 0-System/scripts/supernormal
node sync-meetings.js              # Sync new meetings only
node sync-meetings.js --all        # Re-sync all meetings
node sync-meetings.js --dry-run    # Preview what would be synced
```

**First run**: Browser opens, complete Google OAuth login in SuperNormal. Session is persisted in `chrome-profile/`.

### Output File Format

All three files include YAML frontmatter:

```yaml
---
title: "Planning"
date: "2026-01-07"
company: "ab"
attendees: ["{{user_name}}", "Alex Smith", "Sam Taylor"]
source: "supernormal"
---
```

**meeting.md** additionally shows:
- Company name with full display ("{{company_1_name}}")
- Attendees with wiki-links (`[[Attendee Name]]`)
- Meeting time
- Action items categorized by assignee (extracted from SuperNormal tasks)
- Related people links

### Attendee Detection

SuperNormal does **not** provide an explicit attendee list or speaker diarization. The sync script uses **greeting pattern detection** to identify attendees:

**How it works:**
1. {{user_first_name}} (meeting owner) is always included
2. Script searches for greetings like "Hey [Name]", "What's up [Name]"
3. Only known people from `KNOWN_PEOPLE` database are added

**Limitations:**
- People who join without being greeted by name may be missed
- People who join late (e.g., "Sorry, I'm late") may not be detected
- Manual review of attendee lists is recommended for accuracy

**Example:** If Matt joins with "Hey everybody" → "Sorry, I'm late", there's no greeting *to* Matt, so he won't be auto-detected.

### Known People

The sync script loads known team members from `/0-System/config/contacts-config.json`:

| Source | Location |
|--------|----------|
| {{company_1_name}} | `contacts-config.json` → `companies.company_1.contacts` |
| {{company_2_name}} | `contacts-config.json` → `companies.company_2.contacts` |
| Collaborators | `contacts-config.json` → `collaborators` |
| Personal | `contacts-config.json` → `personal.partner`, `personal.children` |

Add new contacts via `/setup:onboard` or by editing `contacts-config.json` directly.

### Script Location

```
0-System/scripts/supernormal/
├── sync-meetings.js          # Main automation script
├── sync-state.json           # Tracks downloaded meetings
├── chrome-profile/           # Persistent browser session
├── migrate-add-processed.js  # Migration for processed field
└── package.json              # Dependencies (playwright)
```

## Meeting Processing

After syncing meetings, use `/meeting:process` to analyze them with full context.

### Why Process Meetings?

SuperNormal provides basic AI summaries, but the `meeting-processor` agent has access to:
- Your current projects and goals
- Relationship history with attendees
- Your quarterly priorities
- Recent daily notes for context

This enables:
- Connecting discussion topics to existing projects
- Identifying implicit commitments ("I'll look into that")
- Asking clarifying questions
- Routing action items to the right places

### Processing State

Each meeting.md tracks whether it's been processed:

```yaml
---
processed: false          # Has this been analyzed with Claude?
processed_date: null      # When was it processed?
---
```

### Running the Process

```bash
/meeting:process              # Process oldest unprocessed meeting
/meeting:process --list       # Show all unprocessed meetings
/meeting:process [path]       # Process specific meeting
```

### Processing Flow

1. **Agent analyzes** - Reads transcript, loads your context, generates enhanced analysis
2. **Q&A with you** - Clarifies ambiguities, confirms action items
3. **Updates vault** - Adds tasks to daily note, updates projects, updates person files
4. **Marks processed** - Sets `processed: true` with date
5. **Offers next** - Asks if you want to process the next meeting

### What Gets Generated

After processing, meeting.md includes:

```markdown
## Claude Analysis

*Processed: 2026-01-07*

### Enhanced Summary
[Deeper analysis than SuperNormal]

### Connections Identified
- [[Project Name]] - [How it connects]

### Follow-up Items
- [Items identified for follow-up]
```

### Integration with /update

Processing uses the same patterns as `/update`:
- Tasks routed to daily notes under appropriate projects
- Person info updates person files
- Calendar items created as needed

## Integration with Other Features

### Calendar Integration

When you check calendar events in `/daily:plan`, meetings are surfaced:
- Meeting time and attendees
- Prompt for prep if meeting is soon

### Person Context

The `person-context` skill provides deeper attendee information:
- Communication style
- Relationship history
- Recent interactions

### Complex Prep with Agents

For data-heavy prep, use the `context-isolator` agent to:
- Pull calendar context without flooding conversation
- Search vault deeply for relevant context
- Aggregate information from multiple sources

The `meeting-prep` skill handles most preparation automatically.

## Related Guides

- [[daily-workflow|Daily Workflow]] — Meeting integration
- [[calendar-integration|Calendar Integration]] — Scheduling
