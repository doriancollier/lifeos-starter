---
description: Show tasks with due dates - today, overdue, and upcoming
allowed-tools: Read, Grep, Glob, Bash
---

# Tasks Due Command

Query tasks with due dates across daily notes, organized by urgency.

## Context

- **Daily notes directory**: `{{vault_path}}/4-Daily/`
- **Due date format**: `📅 YYYY-MM-DD` (ISO format)

## Task

1. **Get current date** for comparison
2. **Find all tasks with due dates** using grep for `📅 \d{4}-\d{2}-\d{2}`
3. **Parse and categorize** each task:
   - **Overdue**: Due date < today
   - **Due Today**: Due date = today
   - **Upcoming**: Due date within next 7 days
   - **Later**: Due date > 7 days out
4. **Only include incomplete tasks** (lines with `- [ ]`)
5. **Sort by date** within each category

## Execution

```python
# Use Python for date parsing (stdlib only, no external deps)
from datetime import datetime, timedelta
import re

TODAY = datetime.now().date()
PATTERN = re.compile(r'📅\s*(\d{4}-\d{2}-\d{2})')

# Categories
overdue = []
today_tasks = []
upcoming = []  # next 7 days
later = []

# For each line with 📅 and - [ ]:
#   - Extract date with regex
#   - Parse with datetime.strptime(date_str, '%Y-%m-%d')
#   - Compare to TODAY
#   - Categorize
```

## Output Format

```markdown
## 📅 Tasks by Due Date

**Today**: [YYYY-MM-DD] ([day of week])

---

### 🔴 Overdue ([count])

| Due | Days | Task | Source |
|-----|------|------|--------|
| 2025-12-05 | -2 | Call passport office | 2025-12-03.md |
| 2025-12-06 | -1 | Submit report | 2025-12-04.md |

---

### 📍 Due Today ([count])

| Task | Source |
|------|--------|
| Research endocrinologists | 2025-12-07.md |

---

### 📅 Upcoming - Next 7 Days ([count])

| Due | Days | Task | Source |
|-----|------|------|--------|
| 2025-12-10 | +3 | Call insurance | 2025-12-07.md |
| 2025-12-15 | +8 | Submit proposal | 2025-12-07.md |

---

### ⏳ Later ([count])

| Due | Days | Task | Source |
|-----|------|------|--------|
| 2026-01-05 | +29 | {{partner_name}}'s surgery prep | 2025-12-01.md |

---

### Summary

- **Action needed**: [count] overdue + [count] due today
- **This week**: [count] tasks
- **Oldest overdue**: [date] ([task])
```

## Edge Cases

- **No due dates found**: Report "No tasks with due dates found"
- **Only old prose format**: Warn about format and suggest migration
- **Invalid dates**: Skip and note "Could not parse date on line X"

## Notes

- This command queries ALL daily notes, not just recent ones
- Use for morning planning to catch overdue items
- Complement with `/daily:tasks` for full task overview
