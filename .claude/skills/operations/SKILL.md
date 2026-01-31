---
name: operations
description: Math, date calculations, and reliable computation guidance. Use when performing arithmetic, date comparisons, duration calculations, or any operation requiring numerical precision.
---

# Operations Skill

This skill provides guidance for reliable math and date operations. LLMs are prone to arithmetic errors—always use proper tools for calculations.

## Core Principle

**Never rely on mental math.** Use Python, bash utilities, or MCP tools for all calculations.

## Date Operations

### Get Current Time

Always use the MCP calendar tool for current time with proper timezone:

```
mcp__google-calendar__get-current-time
```

This returns the current time in the vault owner's timezone (Central Time).

### Date Formatting

Use bash `date` for simple formatting:

```bash
# Today's date (ISO format)
date +%Y-%m-%d

# Yesterday
date -v-1d +%Y-%m-%d

# Tomorrow
date -v+1d +%Y-%m-%d

# Specific date formatting
date -j -f "%Y-%m-%d" "2026-01-15" +"%A, %B %d, %Y"
```

### Date Calculations

Use Python's `datetime` module for date math:

```python
from datetime import datetime, timedelta

# Parse a date
date = datetime.strptime("2026-01-15", "%Y-%m-%d")

# Add/subtract days
tomorrow = datetime.now() + timedelta(days=1)
last_week = datetime.now() - timedelta(days=7)

# Compare dates
today = datetime.now().date()
due_date = datetime.strptime("2026-01-10", "%Y-%m-%d").date()
is_overdue = due_date < today
days_until = (due_date - today).days

# Get day of week
day_name = date.strftime("%A")  # "Wednesday"
```

### Date Comparison Patterns

```python
from datetime import datetime, timedelta

TODAY = datetime.now().date()

# Categories for due date analysis
def categorize_due_date(date_str):
    due = datetime.strptime(date_str, "%Y-%m-%d").date()
    delta = (due - TODAY).days

    if delta < 0:
        return "overdue", abs(delta)
    elif delta == 0:
        return "today", 0
    elif delta <= 7:
        return "upcoming", delta
    else:
        return "later", delta
```

## Arithmetic Operations

### Simple Math

Use Python for arithmetic:

```python
# Basic operations
result = 42 * 17 + 8
percentage = (completed / total) * 100
average = sum(values) / len(values)
```

Or use `bc` for quick calculations:

```bash
echo "42 * 17 + 8" | bc
echo "scale=2; 100/7" | bc  # Decimal division
```

### Financial Calculations

```python
# Compound interest
principal = 10000
rate = 0.07
years = 5
future_value = principal * (1 + rate) ** years

# Percentage change
old_value = 100
new_value = 125
pct_change = ((new_value - old_value) / old_value) * 100
```

## Duration Calculations

### Time Between Dates

```python
from datetime import datetime

start = datetime.strptime("2026-01-01", "%Y-%m-%d")
end = datetime.strptime("2026-03-15", "%Y-%m-%d")

days = (end - start).days
weeks = days // 7
months_approx = days / 30.44  # Average days per month
```

### Working Days

```python
from datetime import datetime, timedelta

def count_weekdays(start_date, end_date):
    """Count weekdays between two dates (exclusive of end)."""
    count = 0
    current = start_date
    while current < end_date:
        if current.weekday() < 5:  # Monday=0, Friday=4
            count += 1
        current += timedelta(days=1)
    return count
```

## Common Patterns in This Vault

### Task Due Date Queries

```python
# Find overdue tasks (from task-system skill)
from datetime import datetime
import re

TODAY = datetime.now().date()
PATTERN = re.compile(r'📅\s*(\d{4}-\d{2}-\d{2})')

def is_overdue(line):
    match = PATTERN.search(line)
    if match and "- [ ]" in line:
        due = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        return due < TODAY
    return False
```

### Month Start Calculations (for Bingo cards)

```python
from datetime import datetime, timedelta

def get_month_start_monday(year, month):
    """Get the start Monday for a monthly bingo card."""
    first_of_month = datetime(year, month, 1)
    weekday = first_of_month.weekday()  # Monday=0

    if weekday <= 3:  # Mon-Thu: go back to last Monday
        days_back = weekday
        if days_back > 0:
            return first_of_month - timedelta(days=days_back)
        return first_of_month
    else:  # Fri-Sun: go forward to next Monday
        days_forward = 7 - weekday
        return first_of_month + timedelta(days=days_forward)
```

## When This Skill Applies

Use this skill when:
- Calculating days between dates
- Determining if something is overdue
- Computing percentages, averages, or totals
- Working with durations or time spans
- Any arithmetic beyond trivial single-digit operations

## Anti-Patterns to Avoid

1. **Mental date math**: "January 15 is... let me count... 12 days from now" → Use Python
2. **Estimating arithmetic**: "That's roughly 150" → Calculate exactly
3. **Day-of-week guessing**: "January 1, 2026 is probably a Wednesday" → Check with `date`
4. **Duration approximation**: "About 6 weeks" → Calculate: `(end - start).days // 7`

## Integration with Other Skills

- **task-system**: Uses date comparison for overdue detection
- **goal-bingo**: Uses month start calculations for card generation
- **calendar-management**: Uses duration calculations for event scheduling
- **daily-timebox**: Uses time calculations for focus block sizing
