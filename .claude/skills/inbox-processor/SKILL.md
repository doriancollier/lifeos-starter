---
name: inbox-processor
description: Identify and route files in the inbox. Activates when user mentions inbox, drops files, or asks about processing incoming content.
allowed-tools: Read, Write, Glob, Bash
---

# Inbox Processor Skill

Knowledge for identifying file types and routing them to the correct vault location.

## When This Skill Activates

- User mentions "inbox", "dropped a file", "new file to process"
- User says "I put a [thing] in the inbox"
- User asks about processing or routing files
- During `/inbox:process` command execution

## Inbox Location

```
{{vault_path}}/workspace/0-Inbox/
```

This is a staging area for files that need triage before permanent placement.

## File Type Identification

### Meeting Transcripts

**Indicators:**
- Filename contains "transcript"
- Content has speaker labels: `Speaker Name:`, `{{user_first_name}}:`, `Speaker 1:`
- Timestamps: `[00:00:00]`, `00:15`, `(10:30)`
- AI notetaker signatures: "Otter.ai", "Fireflies", "Grain", "tl;dv"
- Long-form conversation structure

**Routing:** `workspace/5-Meetings/YYYY/MM-Month/YYYY-MM-DD-title/transcript.md`

### Meeting Notes

**Indicators:**
- Contains "Meeting Notes", "Notes from", "Summary"
- Has attendee list or "Participants:"
- Action items section
- Agenda or discussion points
- Company context ({{company_1_name}}, {{company_2_name}}, EMC)

**Routing:** `workspace/5-Meetings/YYYY/MM-Month/YYYY-MM-DD-title/meeting.md` or `notes-[person].md`

### Person Information

**Indicators:**
- Contact details (email, phone)
- Role/title information
- "About [Name]" or bio content
- Relationship context

**Routing:** `workspace/6-People/Professional/[Company]/` or `workspace/6-People/Personal/`

### Project Documents

**Indicators:**
- PRD, requirements, specs
- Roadmap content
- Project timeline or milestones
- Task lists with deadlines

**Routing:** `workspace/1-Projects/Current/[Project]/`

### Reference Material

**Indicators:**
- How-to guides
- Documentation
- Templates or boilerplate
- Research or reference content

**Routing:** `workspace/3-Resources/References/` or `workspace/3-Resources/Templates/`

## Meeting Matching

When a file appears to be meeting-related, try to match it to an existing meeting:

### By Date
Extract date from:
- Filename: `2025-12-03-sync.md`
- Content: "December 3, 2025", "12/3/25", "2025-12-03"
- Timestamps in transcript headers

### By Attendees
Look for names and match to:
- Calendar events for that date
- Existing meeting notes mentioning same people

### By Topic
Match keywords to:
- Recurring meeting names (Product Sync, Engineering Sync)
- Project names (from `workspace/1-Projects/Current/`)
- Company indicators (from contacts-config.json)

## Multi-Artifact Meeting Structure

When a meeting has multiple artifacts, use directory structure:

```
workspace/5-Meetings/YYYY/MM-Month/YYYY-MM-DD-title/
├── meeting.md              # Main meeting note (canonical)
├── transcript.md           # Full transcript
├── transcript-otter.md     # If multiple transcripts (different sources)
├── notes-attendee.md       # Notes from specific attendee
├── slides.pdf              # Presentation
└── attachments/            # Other files
    ├── screenshot.png
    └── reference.pdf
```

### Meeting Note Frontmatter

```yaml
---
title: "Product Sync"
date: "2025-12-03"
company: "{{company_1_name}}"
attendees: ["Alex", "Sam", "{{user_first_name}}"]
type: "meeting"
has_artifacts: true
---
```

### Artifacts Section in Meeting Note

```markdown
## Artifacts

| Type | File | Source |
|------|------|--------|
| Transcript | [[transcript]] | Otter.ai |
| Notes | [[notes-attendee]] | Attendee's notes |
| Slides | [Presentation](slides.pdf) | — |
```

## Task Extraction & Deduplication

When processing transcripts and meeting notes, extract action items and check for duplicates.

### Task Extraction Patterns

**Direct Assignment (highest confidence):**
| Pattern | Example | Assignee |
|---------|---------|----------|
| "I'll [verb]" | "I'll create the dashboard" | Speaker ({{user_first_name}}) |
| "I will [verb]" | "I will send the specs" | Speaker |
| "@[Name] will" | "@Alex will review" | Named person |
| "[Name] to [verb]" | "{{user_first_name}} to draft email" | Named person |
| "[Name]: [verb]" | "Sam: check the sold-out state" | Named person |

**Explicit Markers (high confidence):**
| Pattern | Example |
|---------|---------|
| "Action item:" | "Action item: review PR by Wednesday" |
| "TODO:" | "TODO: update the documentation" |
| "Task:" | "Task: schedule follow-up meeting" |
| "Follow up:" | "Follow up: check with Alex on timeline" |

**Implicit Tasks (medium confidence - verify with user):**
| Pattern | Example |
|---------|---------|
| "We need to..." | "We need to start L2 planning this month" |
| "We should..." | "We should track key metrics" |
| "Make sure to..." | "Make sure to monitor the generator" |
| "Let's..." | "Let's check the sold-out state" |
| "Can you..." | "Can you send that over?" |

**AI Notetaker Formats:**

Supernormal format:
```
Tasks
- Unassigned: Check sold out state on expedition page
- {{user_name}}: Create initial dashboards for tracking metrics
```

Otter.ai format:
```
Action Items:
• [Owner] Task description
```

### Deduplication Heuristics

**Same task indicators:**
- 70%+ word overlap in task description
- Same assignee AND similar action verb
- Same project context AND similar outcome

**Search locations for duplicates:**
1. Daily notes (last 7 days): `workspace/4-Daily/*.md`
2. Current projects: `workspace/1-Projects/Current/**/*.md`
3. Recent meetings: `workspace/5-Meetings/2025/**/*.md`

**Keyword extraction for search:**
- Remove stop words (the, a, an, to, for, with)
- Extract action verb + noun phrase
- Example: "Create dashboards for wallet metrics" → search "dashboard wallet metrics"

### Task Routing Decisions

| Assignee | Suggested Routing |
|----------|-------------------|
| {{user_first_name}} | Daily note + Project file (if applicable) |
| Others | Meeting note only (reference) |
| Unassigned | Ask user or meeting note only |

### Cross-Link Format

**In meeting.md:**
```markdown
## Action Items

### Assigned to {{user_first_name}}
- [ ] Create dashboards for wallet metrics - [[AB-New-Wallet-Reports]]

### Assigned to Others
- [ ] @Matt: Check expedition sold-out state

### Already Tracked Elsewhere
- Push scheduling updates → [[2025-12-03#🔴2]]
```

**In daily note:**
```markdown
- [ ] 🟡 Create dashboards - Company: {{company_1_name}} - [[meeting#Action Items|from Product Sync]]
```

**In project:**
```markdown
- [ ] Create dashboards - Source: [[2025-12-03-product-sync/meeting]]
```

## Decision Extraction

### Decision Patterns
Look for patterns:
- "We decided...", "Let's go with..."
- "The plan is...", "Agreed:"
- "Decision:", "We're going to..."
- "[Thing] will be [definition]" (e.g., "A user will be a wallet that holds...")

### Key Topics
Identify main discussion threads by:
- Topic changes in conversation
- Section headers if present
- Clustering related discussion

## Company Detection

| Indicators | Company |
|------------|---------|
| Keywords from contacts-config.json | {{company_1_name}} |
| Keywords from contacts-config.json | {{company_2_name}} |
| Keywords from contacts-config.json | {{company_3_name}} |
| Family, {{partner_name}}, {{child_name}}, personal topics | Personal |

## Quick Reference: Routing Table

| Content Type | Destination Pattern |
|--------------|---------------------|
| Daily note content | `workspace/4-Daily/YYYY-MM-DD.md` |
| Meeting transcript | `workspace/5-Meetings/YYYY/MM-Month/YYYY-MM-DD-title/transcript.md` |
| Meeting notes | `workspace/5-Meetings/YYYY/MM-Month/YYYY-MM-DD-title/meeting.md` |
| Person info | `workspace/6-People/[Professional or Personal]/[name].md` |
| Project doc | `workspace/1-Projects/Current/[Project]/[doc].md` |
| Template | `workspace/3-Resources/Templates/[name].md` |
| Reference | `workspace/3-Resources/References/[name].md` |
| Unknown | Ask user or `workspace/8-Scratch/` temporarily |

## Integration

- **`/inbox:process`**: Main command that uses this skill's knowledge
- **session-context-loader**: Surfaces inbox item count at session start
- **meeting-prep skill**: Can leverage transcript content for future prep
- **work-logging skill**: Extracted action items flow through normal task system
