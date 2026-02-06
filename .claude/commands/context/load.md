---
description: Load work context for any company
argument-hint: [company-id]
allowed-tools: Read, Grep, Glob, Bash
---

# Load Company Context

Switch mental context to a specific company or area.

## Arguments

- `$ARGUMENTS` - Company identifier: `ab`, `144`, `emh`, or `personal`

## Company ID Mapping

| ID | Company Placeholder | Area Path |
|----|---------------------|-----------|
| `ab` | {{company_1_name}} | `workspace/2-Areas/{{company_1_name}}/` |
| `144` | {{company_2_name}} | `workspace/2-Areas/{{company_2_name}}/` |
| `emh` | {{company_3_name}} | `workspace/2-Areas/{{company_3_name}}/` |
| `personal` | Personal | `workspace/2-Areas/Personal/` |

## Task

Load and summarize the current context for the specified company:

### 1. Resolve Company Name
- Map the company ID to the full company name using the config
- Load contacts from `workspace/0-System/config/contacts-config.json`

### 2. Read Area Overview
- Check `workspace/2-Areas/[Company]/` for any overview or status files

### 3. Find Active Projects
- List projects in `workspace/1-Projects/Current/` related to this company

### 4. Check Today's Tasks
- Search today's daily note for company tasks
- Look for `Company: [Company Name]` in task lines

### 5. Find Recent Meetings
- Check `workspace/5-Meetings/` for recent meetings with this company
- Look for meetings with key colleagues

### 6. Review Key People Status
- Check person files in `workspace/6-People/Professional/[Company]/`
- Any open action items with them

## Output Format

```markdown
## [Company Name] Context Loaded

### Your Role
[From contacts config or area overview]

### Key People
- [List key people and their roles from contacts config]

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

## Examples

```
/context:load ab       # Load {{company_1_name}} context
/context:load 144      # Load {{company_2_name}} context
/context:load personal # Load personal context
```
