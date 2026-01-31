---
description: Load {{company_1_name}} work context
allowed-tools: Read, Grep, Glob, Bash
---

# Load {{company_1_name}} Context

Switch mental context to {{company_1_name}} work.

## Task

Load and summarize the current {{company_1_name}} context:

### 1. Read Area Overview
- Check `2-Areas/{{company_1_name}}/` for any overview or status files

### 2. Find Active Projects
- List projects in `1-Projects/Current/` related to {{company_1_name}}

### 3. Check Today's Tasks
- Search today's daily note for {{company_1_name}} tasks
- Look for `Company: {{company_1_name}}` in task lines

### 4. Find Recent Meetings
- Check `5-Meetings/` for recent {{company_1_name}} meetings
- Look for meetings with key colleagues

### 5. Review Key People Status
- Check person files in `6-People/Professional/`
- Any open action items with them

## Output Format

```markdown
## {{company_1_name}} Context Loaded

### Your Role
[Configure your role at this company]

### Key People
- [List key people and their roles]

### Active Projects
- [List current projects]

### Today's Tasks
- [List any tasks marked for this company]

### Recent Activity
- [Last meeting and outcome]
- [Any recent decisions]

### Open Items
- [Pending decisions or blockers]

### Focus Reminder
Think: [Key focus areas for this company]
Communication: [Communication style notes]
```
