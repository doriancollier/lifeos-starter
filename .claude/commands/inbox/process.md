---
description: Process files in the inbox - identify, route, and organize
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, mcp__google-calendar__list-events, mcp__google-calendar__search-events
---

# Inbox Process Command

Process files dropped in the `workspace/0-Inbox/` directory. Identify what each file is, route it to the correct location, and extract useful information.

## Context

- **Inbox location**: `{{vault_path}}/0-Inbox/`
- **Purpose**: Staging area for files that need triage before being placed in the correct location

## Order of Operations

### Step 1: Scan Inbox

```bash
ls -la "{{vault_path}}/0-Inbox/" | grep -v "^total" | grep -v "gitkeep" | grep -v "^d"
```

If inbox is empty, report:
```markdown
📥 **Inbox is empty** — No files to process.
```

### Step 2: For Each File, Identify Type

Read each file and determine what it is:

| Pattern | Type | Destination |
|---------|------|-------------|
| Contains "transcript", timestamps like `[00:00]`, speaker labels | Meeting Transcript | `workspace/5-Meetings/` |
| Contains "Meeting Notes", attendee lists, action items | Meeting Notes | `workspace/5-Meetings/` |
| Contains person information, contact details | Person Note | `workspace/6-People/` |
| Contains project info, tasks, deadlines | Project | `workspace/1-Projects/` |
| Contains "template", reusable structure | Template | `workspace/3-Resources/Templates/` |
| PDF, image, or binary file | Attachment | Depends on context |
| Unknown | Ask user | — |

### Step 3: For Meeting Artifacts

When a file is identified as meeting-related:

#### 3a. Extract Meeting Metadata

From the content, try to identify:
- **Date**: Look for dates in filename or content
- **Title/Topic**: Meeting subject
- **Attendees**: Names mentioned
- **Company**: {{company_1_name}}, {{company_2_name}}, EMC, Personal

#### 3b. Search for Existing Meeting Note

```bash
# Search by date
find "{{vault_path}}/5-Meetings" -name "*YYYY-MM-DD*" -type f

# Search by topic/attendees
grep -r "[topic or attendee name]" "{{vault_path}}/5-Meetings" --include="*.md" -l
```

Also check today's calendar for matching meetings:
- Use `mcp__google-calendar__list-events` for today's meetings
- Match by attendee names or meeting title

#### 3c. Route the Artifact

**If existing meeting note found:**
1. Check if meeting note is a file or directory
2. If file: Convert to directory structure
3. Move artifact into meeting directory with proper naming

**If no existing meeting found:**
Ask user:
```
"I found a transcript for what appears to be a [topic] meeting on [date].
I couldn't find an existing meeting note. Would you like me to:
1. Create a new meeting note and attach this transcript
2. Just move the transcript to 5-Meetings/ with a sensible name
3. Tell me which meeting this belongs to"
```

### Step 4: Create Meeting Directory (if needed)

When converting a flat meeting note to a directory:

**Before:**
```
5-Meetings/2025/12-December/2025-12-03-product-sync.md
```

**After:**
```
5-Meetings/2025/12-December/2025-12-03-product-sync/
├── meeting.md              # Original note (renamed)
├── transcript.md           # New artifact
└── attachments/            # For non-markdown files
```

**Update meeting.md frontmatter:**
```yaml
---
title: "Product Sync"
date: "2025-12-03"
company: "{{company_1_name}}"
has_artifacts: true
---
```

**Add artifacts section to meeting.md:**
```markdown
## Artifacts

- [[transcript|Transcript]]
```

### Step 5: For Non-Meeting Files

**Person files**: Route to `workspace/6-People/Professional/[Company]/` or `workspace/6-People/Personal/`

**Project files**: Route to `workspace/1-Projects/Current/[Project]/` or ask which project

**Unknown files**: Ask user:
```
"I found a file called [filename] but I'm not sure where it belongs.
Content preview: [first 200 chars]

Where should this go?
1. [Suggested location based on content]
2. workspace/8-Scratch/ (temporary)
3. Tell me where"
```

### Step 6: Extract and Route Tasks

For meeting transcripts and notes, extract action items and route them intelligently with deduplication.

#### 6a. Extract Tasks Using Patterns

Look for these patterns in content:

**Direct assignment:**
- "I'll do X", "I will X", "I need to X"
- "@{{user_first_name}} will", "{{user_first_name}} to", "{{user_first_name}}: do X"
- "@[Name] will", "[Name] to do", "[Name]: action"

**Explicit markers:**
- "Action item:", "TODO:", "Follow up:"
- "Task:", "Need to:", "Make sure to"

**Implicit tasks:**
- "Can you...", "Would you...", "Could you..."
- "We should...", "We need to...", "Let's make sure..."
- "Someone should...", "This needs to be..."

**Supernormal/AI note format:**
- Look for `Tasks` section with bullet points
- Format: `- Unassigned: task` or `- Person Name: task`

#### 6b. Categorize Extracted Tasks

Group tasks by assignee:
- **{{user_first_name}}'s tasks**: Tasks assigned to {{user_first_name}}
- **Others' tasks**: Tasks assigned to specific other people
- **Unassigned**: Tasks without clear ownership

#### 6c. Deduplication Check

For each extracted task, search for existing similar tasks:

**Search locations:**
```bash
# Recent daily notes (last 7 days)
grep -r "[task keywords]" "{{vault_path}}/4-Daily/" --include="*.md" | head -20

# Current projects
grep -r "[task keywords]" "{{vault_path}}/1-Projects/Current/" --include="*.md" | head -10

# Recent meeting notes
grep -r "[task keywords]" "{{vault_path}}/5-Meetings/2025/" --include="*.md" | head -10
```

**Duplicate detection heuristics:**
- 70%+ word overlap in task description = likely same task
- Same assignee + similar keywords = likely same task
- Same project context + similar action = likely same task

#### 6d. Present Task Summary

Show the user what was found:

```markdown
## Extracted Action Items

### New Tasks (not found elsewhere)
| Task | Assignee | Suggested Location |
|------|----------|-------------------|
| Create dashboards for wallet metrics | {{user_first_name}} | Daily note + [[AB-New-Wallet-Reports]] |
| Draft email strategy | {{user_first_name}} | Daily note + [[AB-Email-Drip-Campaigns]] |
| Check expedition sold-out state | Matt | Meeting note only |

### Already Tracked
| Task | Existing Location |
|------|-------------------|
| Push scheduling updates | [[2025-12-03#🔴2]] |

### Decisions Made
- User definition: Wallet that holds {{company_1_name}} NFT
- L2 planning: Start this month
```

#### 6e. User Confirmation for Routing

Ask where to add new tasks:

```
For the 2 new {{user_first_name}} tasks, would you like me to:
1. Add to today's daily note (default for immediate tracking)
2. Add to relevant project files only
3. Add to both daily note AND project files (cross-linked)
4. Keep in meeting note only (reference, no active tracking)
```

#### 6f. Apply Task Routing

Based on user choice, add tasks with cross-links:

**In meeting.md Action Items section:**
```markdown
## Action Items

### Assigned to {{user_first_name}}
- [ ] Create dashboards for wallet metrics - [[AB-New-Wallet-Reports]]
- [ ] Draft email strategy - [[AB-Email-Drip-Campaigns]]

### Assigned to Others
- [ ] @Matt: Check expedition sold-out state

### Already Tracked Elsewhere
- Push scheduling updates → [[2025-12-03#🔴2]]
```

**In daily note (if selected):**
```markdown
- [ ] 🟡 Create dashboards for wallet metrics - Company: {{company_1_name}} - [[2025-12-03-product-sync/meeting#Action Items|from Product Sync]]
```

**In project file (if selected):**
```markdown
- [ ] Create dashboards for wallet metrics - Source: [[2025-12-03-product-sync/meeting]]
```

#### 6g. Extract Decisions

Also extract and log decisions:
- Add to meeting note's "Decisions Made" section
- Add to daily note's "Key Decisions Made" section

### Step 7: Move and Clean Up

After routing each file:
1. Move file to destination using `mv` command
2. Rename if needed to match conventions
3. Remove from inbox

### Step 8: Report Results

```markdown
## 📥 Inbox Processed

### Routed
| File | Destination | Action Taken |
|------|-------------|--------------|
| `transcript.md` | `workspace/5-Meetings/2025/12-December/2025-12-03-product-sync/` | Created meeting directory, extracted 3 action items |

### Extracted
- 3 action items added to today's daily note
- 2 decisions logged in meeting note

### Inbox Status
✅ Empty — all files processed
```

## File Naming Conventions

### Meeting Artifacts
| Type | Naming Pattern |
|------|----------------|
| Main note | `meeting.md` |
| Transcript | `transcript.md` or `transcript-[source].md` |
| Other's notes | `notes-[person].md` |
| Presentation | `slides.[ext]` or `presentation.[ext]` |
| Attachments | `attachments/[original-name]` |

### Meeting Directories
```
YYYY-MM-DD-title/
```

Example: `2025-12-03-product-sync/`

## Edge Cases

### Multiple files for same meeting
Process together, create directory, place all artifacts.

### File already exists at destination
Ask user: rename, overwrite, or skip.

### Binary files (PDF, images)
Place in `attachments/` subdirectory, create markdown link.

### Very long transcripts
Summarize key points, don't try to extract everything.

## Integration

- **inbox-processor skill**: Provides knowledge for identifying file types
- **meeting-prep skill**: Can use transcript content for future meeting prep
- **work-logging skill**: Action items extracted go through normal task flow
