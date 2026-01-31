---
description: Generate standup summary from recent daily notes
allowed-tools: Read, Grep, Glob, Bash
---

# Standup Summary Command

Generate a standup-style summary from recent daily notes.

## Task

Create a concise standup update covering:
1. What was accomplished yesterday
2. What's planned for today
3. Any blockers

### 1. Find Yesterday's and Today's Daily Notes

```bash
# Yesterday
yesterday=$(date -v-1d +%Y-%m-%d)
# Today
today=$(date +%Y-%m-%d)

echo "Yesterday: $yesterday"
echo "Today: $today"
```

### 2. Extract Yesterday's Completed Tasks

Read yesterday's daily note and find:
- Completed tasks: `- [x]`
- Key decisions made
- Meetings held

### 3. Extract Today's Planned Tasks

Read today's daily note and find:
- A Priority tasks (🔴)
- B Priority tasks (🟡)
- Scheduled meetings

### 4. Find Blockers

Look for:
- Blocked tasks (🔵)
- Items marked "waiting for"
- Dependencies mentioned

## Output Format

```markdown
## Standup - [Today's Date]

### Yesterday
- [Completed task 1]
- [Completed task 2]
- [Key meeting/decision]

### Today
- 🔴 [A Priority 1]
- 🔴 [A Priority 2]
- 🟡 [B Priority items]

### Blockers
- [Blocked item] - Waiting for: [what/who]

### Meetings Today
- [Time]: [Meeting name]
```

## Company-Specific Standups

If user specifies a company, filter to only that context:
- `/standup ab` → {{company_1_name}} only
- `/standup 144` → {{company_2_name}} only
- `/standup emh` → {{company_3_name}} only

## Notes

- Keep it concise - this is for quick communication
- Focus on actionable items
- Highlight anything that needs help or is blocked
- Good for sharing in Slack or team standups
