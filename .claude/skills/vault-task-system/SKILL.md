---
name: vault-task-system
description: Understand and work with the task priority system used in daily notes. Use when managing tasks, setting priorities, finding blocked items, or moving tasks between days.
kind: skill
---

# Task System Skill

This vault uses a structured task priority system within daily notes. All tasks use markdown checkboxes with emoji-based priority indicators.

## Priority Levels

| Priority | Emoji | Meaning | Rules |
|----------|-------|---------|-------|
| **A Priority** | `🔴` | Critical tasks | Max 5 per day, numbered by urgency (1-5) |
| **B Priority** | `🟡` | Important tasks | No limit, no numbering |
| **C Priority** | `🟢` | Nice-to-have | No limit, no numbering |
| **Blocked** | `🔵` | Waiting on dependency | Must specify what/who blocking |

## Due Dates

Tasks can have due dates using the `📅 YYYY-MM-DD` format. Due dates are **annotations**, not a separate priority type—any task can have a due date.

### Format

```markdown
# Due date at end of task (after priority)
- [ ] 🟡 Call insurance about prescription 📅 2025-12-10
- [ ] 🔴1. Submit proposal to client 📅 2025-12-15
- [ ] 🔵 Wait for callback - Waiting: Texas Diabetes 📅 2025-12-10

# Completed task with due date
- [x] 🟡 File quarterly taxes 📅 2025-12-15
```

### Why ISO Format (YYYY-MM-DD)?

1. **Machine-parseable** — grep and Python can query without external libraries
2. **Sortable** — alphabetically = chronologically
3. **Unambiguous** — no "Dec 5" vs "5 Dec" confusion
4. **Obsidian Tasks compatible** — works with popular plugins

### Querying Due Dates

```bash
# Tasks due today
grep -rn "📅 $(date +%Y-%m-%d)" "{{vault_path}}/4-Daily/"*.md | grep "\- \[ \]"

# All tasks with due dates
grep -rEn "📅 [0-9]{4}-[0-9]{2}-[0-9]{2}" "{{vault_path}}/4-Daily/"*.md

# Tasks due this month (December 2025)
grep -rn "📅 2025-12-" "{{vault_path}}/4-Daily/"*.md | grep "\- \[ \]"

# Overdue tasks (requires date calculation - use Python or /vault-tasks:due command)
```

### When to Use Due Dates

| Scenario | Use Due Date? | Notes |
|----------|--------------|-------|
| Hard deadline | ✅ Yes | `📅 2025-12-15` |
| Appointment/meeting | ✅ Yes | Also create calendar event |
| "Someday" task | ❌ No | Use 🟢 C-priority instead |
| Blocked waiting | ✅ Optional | Add if waiting has deadline |
| Recurring | ❌ No | Use calendar recurring events |

## Task Format

Tasks live under their parent project in the Work section of daily notes:

```markdown
## Work

### Quick Hits
*Tasks under 15 minutes, no project context needed*

- [ ] 🔴1. Call passport office
- [ ] Quick email to Alex

### {{company_1_name}}

#### [[AB-Email-Drip-Campaigns]] `current`
*Next: Complete segmentation logic*

- [ ] 🔴2. Review drip email copy
- [ ] 🟡 Test email sequences
- [ ] 🔵 Wait for design assets - Waiting: Design team

### {{company_2_name}}

#### [[AssetOps]] `current`
*Next: Fix CVE and deploy*

- [ ] 🔴3. Fix Next.js CVE vulnerability
- [ ] 🟡 Deploy claiming updates
```

### Task Format Patterns

```markdown
# A-Priority (numbered, max 5 per day)
- [ ] 🔴1. Most critical task
- [ ] 🔴2. Second most critical

# B-Priority (important, no numbering)
- [ ] 🟡 Important task
- [ ] 🟡 Another important task

# C-Priority (nice-to-have)
- [ ] 🟢 Nice-to-have task

# Blocked (specify dependency)
- [ ] 🔵 Blocked task - Waiting: [person/thing]

# Completed
- [x] 🔴1. Completed critical task
- [x] 🟡 Completed important task
```

## Task Location

Tasks appear in these locations in daily notes:

1. **Quick Hits** - Short tasks (<15 min) without project context
2. **Project sections** - Tasks grouped under `#### [[Project Name]] \`status\`` headers
3. **Journal → Quick Notes** - Timestamped progress updates

## Finding Tasks

### All incomplete tasks in a daily note
```bash
grep -E "^- \[ \]" "{{vault_path}}/4-Daily/YYYY-MM-DD.md"
```

### All A priority (critical) tasks
```bash
grep -E "^- \[ \] 🔴" "{{vault_path}}/4-Daily/"*.md
```

### All blocked tasks
```bash
grep -E "^- \[ \] 🔵" "{{vault_path}}/4-Daily/"*.md
```

### Completed tasks from today
```bash
grep -E "^- \[x\]" "{{vault_path}}/4-Daily/$(date +%Y-%m-%d).md"
```

## Task Lifecycle

```
New Task → A/B/C Priority → Completed
                ↓
          Blocked (🔵) → Unblocked → Completed
                ↓
          Carryover to Next Day
```

## Best Practices

1. **Morning**: Set max 5 A-priority tasks, numbered 1-5 by urgency
2. **During day**: Work A tasks first, then B, then C
3. **When blocked**: Change to 🔵 and note what you're waiting for
4. **End of day**: Review and move incomplete tasks to tomorrow's daily note
5. **Project context**: Tasks live under their project's section, not scattered by priority

## Task Sync with Projects

Tasks in daily notes are associated with their projects via section headers:

```markdown
#### [[AssetOps]] `current`

- [ ] 🔴 Fix CVE blocker   ← This task is associated with AssetOps
```

When a task is completed, the `work-logging` skill can update:
1. The checkbox in the daily note
2. Add a timestamped Quick Note entry
3. Optionally update the project file's task list

## Cross-Day Task Queries

### Find tasks that appear in multiple days (carried over)
```bash
# Find a specific task text across daily notes
grep -r "task description" "{{vault_path}}/4-Daily/" --include="*.md"
```

### Find incomplete tasks from the past week
```bash
# List recent daily notes and search for incomplete tasks
for f in $(ls -t "{{vault_path}}/4-Daily/"*.md | head -7); do
  echo "=== $f ==="
  grep -E "^- \[ \]" "$f"
done
```

## Integration Notes

- Tasks inherit company context from their project section ({{company_1_name}}, {{company_2_name}}, EMC, Personal)
- Use wiki-links `[[Project Name]]` to connect tasks to projects
- Reference people with `[[Person Name]]` when tasks involve others
- Blocked tasks should reference the blocker for easy follow-up
- Quick Hits are for tasks without project context

---

## Enhancements

These additions integrate leverage thinking and quadrant assessment from [[planning-horizons]] and [[framework-prompts]].

### Leverage Filtering

Before marking a task as A-priority, apply the leverage test:

**4-Question A-Priority Filter**:
1. **High Impact?** — Does this create outsized results?
2. **Time-Sensitive?** — Is there a real deadline or consequence?
3. **Requires Your Judgment?** — Could someone else do it 70% as well?
4. **Clear Success Criteria?** — Do you know what "done" looks like?

If any answer is "No", consider downgrading or reframing the task.

**Coaching prompts**:
- "Is this high-leverage or could someone else do it?"
- "Does this require your specific knowledge and judgment?"
- "Is this building leverage (systems, code, content, relationships) or just trading time for output?"
- "What are you NOT doing because you're doing this? What's the opportunity cost?"

**Eliminate-Automate-Delegate hierarchy**:
Before doing any task yourself:
1. **Eliminate** — Does it need to exist at all?
2. **Automate** — Can a system do it?
3. **Delegate** — Can someone else do it 70% as well?
4. **Do it yourself** — Only for high-leverage work requiring your judgment

### Quadrant Assessment

Map tasks to Eisenhower quadrants before prioritizing:

| Quadrant | Description | Target Time | Action |
|----------|-------------|-------------|--------|
| **Q1** | Urgent + Important | 20-25% | Handle crises, do immediately |
| **Q2** | Important, Not Urgent | 60-65% | Schedule first, protect time |
| **Q3** | Urgent, Not Important | 10-15% | Delegate, batch, or decline |
| **Q4** | Neither | <5% | Eliminate ruthlessly |

**Key insight**: Q2 (Important but not urgent) is where real success lives. Most A-priorities should be Q2 work that you're treating as urgent by choice, not external pressure.

**Coaching prompts**:
- "Is this truly urgent, or are you feeling pressured by someone else's timeline?"
- "Is this your priority, or someone else's priority masquerading as yours?"
- "What Q2 work would this displace? Is that trade-off worth it?"
- "Is this task you're avoiding actually Q4 disguised as C-priority?"

**Avoidance detection**:
- "Is this strategic renewal or avoidance? Will you feel better or worse after?"
- "What important work are you using this to avoid?"
- "What's the Quadrant II activity you should do instead right now?"

### Strategic Lens

Ask whether tasks build capability or just complete work:

**Capability-building questions**:
- "Does this build capability (systems, skills, relationships) or just complete a task?"
- "What would compound about this work? What system could emerge from it?"
- "Are you working ON your life/business or just IN it?"
- "What leverage are you building that will pay off in 6-12 months?"

**LNO Framework** (Leverage, Neutral, Overhead):
- **L (Leverage)**: Do exceptionally — these are true A-priorities
- **N (Neutral)**: Do well enough — don't over-invest
- **O (Overhead)**: Do poorly or delegate — accept "good enough"

**Anti-perfectionism prompt**:
- "Is this perfectionism on a low-leverage task? Would 'good enough' free capacity for higher-leverage work?"

### Big Rock Check

Distinguish strategic priorities from busywork:

**The Big Rock test**:
- "Is this a Big Rock (1-3 activities that would make you proud of the week) or gravel (busywork that fills time)?"
- "If I only accomplished this one thing today, would I be satisfied?"
- "Does this task advance a weekly rock or quarterly goal?"

**Big Rocks scheduling principle**: Schedule Big Rocks FIRST, before other appointments fill your calendar. Like filling a jar — if you add sand first, the rocks won't fit.

**Daily connection**:
- At least one A-task should flow from Weekly Big 3
- Ask: "Which weekly rock does this advance?"

### Related References

- [[planning-horizons]] — Multi-horizon planning framework with Big Rocks principle
- [[framework-prompts]] — Leverage and quadrant assessment prompts
- [[foundation]] — Core values for strategic alignment
