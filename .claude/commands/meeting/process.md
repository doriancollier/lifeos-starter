---
description: Process meeting notes with AI context, extract insights and tasks interactively
argument-hint: [meeting-path | --next | --list]
allowed-tools: Read, Write, Edit, Task, Bash, Glob, Grep, AskUserQuestion
---

# Meeting Processing Command

Process downloaded meeting notes with full context awareness. Extracts insights, identifies action items, asks clarifying questions, and updates the vault.

## Arguments

- `$ARGUMENTS` - Optional flags:
  - (no args) - Process oldest unprocessed meeting
  - `--next` - Same as above (explicit)
  - `--list` - Show all unprocessed meetings without processing
  - `[path]` - Process specific meeting directory

## Context

- **Meetings directory**: `{{vault_path}}/5-Meetings/`
- **Processing state**: Tracked via `processed: true/false` in meeting.md frontmatter
- **Agent**: Uses `meeting-processor` agent for heavy analysis

## Process

### Step 1: Parse Arguments and Find Meeting

```bash
MEETINGS_DIR="{{vault_path}}/5-Meetings"
```

**If `--list`:**
```bash
# Find all unprocessed meetings
grep -r -l "processed: false" "$MEETINGS_DIR" --include="meeting.md" 2>/dev/null | sort
```
Output the list and stop.

**If specific path provided:**
Verify the path exists and has meeting.md with `processed: false`.

**If no args or `--next`:**
```bash
# Find oldest unprocessed meeting (by directory name which includes date)
grep -r -l "processed: false" "$MEETINGS_DIR" --include="meeting.md" 2>/dev/null | sort | head -1
```

If no unprocessed meetings found:
```
All meetings have been processed! Run `/meeting:sync` to check for new meetings.
```

### Step 2: Confirm Meeting to Process

Before spawning the agent, confirm with user:

```markdown
## Ready to Process Meeting

**Meeting**: [Title from meeting.md]
**Date**: [Date]
**Company**: [Company]
**Attendees**: [List]

This meeting has not been processed yet. I'll analyze the transcript and notes with your full context (projects, goals, calendar) to extract:
- Enhanced key topics
- Action items with owners
- Questions to clarify
- Connections to existing work

**Proceed?**
```

Use AskUserQuestion:
- "Yes, process this meeting" (Recommended)
- "Skip to next unprocessed meeting"
- "Show me the list first"
- "Cancel"

### Step 3: Spawn Meeting Processor Agent

```
Use Task tool with subagent_type="meeting-processor"

Prompt:
"Process the meeting at: [MEETING_PATH]

Read the transcript, notes-supernormal.md, and meeting.md. Load relevant context based on the company and attendees. Return your analysis in the structured format specified in your instructions."
```

Wait for agent to return analysis.

### Step 4: Present Analysis and Q&A

Display the agent's analysis to the user.

Then use AskUserQuestion for each category of actions:

**For confirmed tasks:**
```
"The meeting identified these tasks for you:
1. [Task 1]
2. [Task 2]

Which should I add to today's daily note?"
- "Add all to daily note" (Recommended)
- "Let me review each one"
- "Skip tasks for now"
```

**For questions identified:**
```
"I have [N] questions about the meeting:

1. [Question 1]
   Context: "[Quote]"

How would you like to handle clarifications?"
- "Go through each question now"
- "Add questions to meeting note for later"
- "Skip questions"
```

**For project connections:**
```
"I identified connections to existing projects:
- [Topic] → [[Project Name]]

Should I update these project files with meeting insights?"
- "Yes, update relevant projects"
- "No, just note in meeting file"
```

**For person file updates:**
```
"I learned new information about attendees:
- [[Person]]: [Info]

Update their person files?"
- "Yes, update person files"
- "No, skip"
```

### Step 5: Execute Confirmed Actions

Based on user responses:

**Adding tasks to daily note:**
- Use the `daily-note` skill to ensure today's note exists
- Add tasks under appropriate project in Work section
- Format: `- [ ] 🟡 [Task] - from [[meeting-link|Meeting Title]]`

**Answering questions (if user chose to go through):**
- Present each question
- Capture user's answer
- Add answer to meeting.md Key Topics or Decisions section

**Updating projects:**
- Read project file
- Add meeting reference to relevant section
- Add any new tasks identified

**Updating person files:**
- Use `person-file-management` skill patterns
- Add to Personal Notes section with meeting reference

### Step 6: Update Meeting File

Update meeting.md with:

1. **Frontmatter changes:**
```yaml
processed: true
processed_date: "YYYY-MM-DD"
```

2. **Fill in Key Topics section** (from agent analysis)

3. **Fill in Decisions section** (from agent analysis)

4. **Add Claude Analysis section:**
```markdown
## Claude Analysis

*Processed: YYYY-MM-DD*

### Enhanced Summary
[Agent's enhanced summary]

### Connections Identified
- [[Project 1]] - [How it connects]
- [[Project 2]] - [How it connects]

### Follow-up Items
- [Items identified for follow-up]
```

### Step 7: Offer Next Meeting

After processing completes:

```bash
# Check for more unprocessed meetings
REMAINING=$(grep -r -l "processed: false" "$MEETINGS_DIR" --include="meeting.md" 2>/dev/null | wc -l)
```

If remaining > 0:
```
"Processing complete for [Meeting Title].

There are [N] more unprocessed meetings. Would you like to process the next one?"
```

Use AskUserQuestion:
- "Yes, process next meeting"
- "No, I'm done for now"
- "Show me the list of remaining"

If "Yes", loop back to Step 2 with next oldest meeting.

## Output Summary

After each meeting is processed, output:

```markdown
## Processing Complete: [Meeting Title]

### Actions Taken
- ✅ Added [N] tasks to daily note
- ✅ Updated [[Project Name]] with meeting notes
- ✅ Updated [[Person Name]] person file
- ✅ Answered [N] clarifying questions
- ✅ Marked meeting as processed

### Meeting File Updated
- Key Topics: Filled in
- Decisions: Filled in
- Claude Analysis: Added

### Remaining
[N] unprocessed meetings remaining
```

## Edge Cases

### Meeting already processed
If user provides a path to an already-processed meeting:
```
"This meeting was already processed on [date]. Would you like to re-process it?"
- "Yes, re-analyze with fresh context"
- "No, show me the existing analysis"
- "Cancel"
```

### No transcript available
If transcript.md is missing or empty:
```
"This meeting has no transcript. I can still process the SuperNormal notes, but analysis will be limited."
```
Proceed with notes-supernormal.md only.

### Agent returns error
If the meeting-processor agent fails:
```
"I encountered an error processing this meeting. Would you like me to try again or skip to the next one?"
```

## Integration

This command integrates with:
- `meeting-processor` agent for heavy analysis
- `daily-note` skill for task creation
- `task-system` skill for priority formatting
- `person-file-management` skill for person updates
- `/update` command patterns for routing content

## Related Commands

- `/meeting:sync` - Download meetings from SuperNormal
- `/meeting:prep` - Prepare for upcoming meetings
- `/update` - Smart capture (used for routing extracted content)
