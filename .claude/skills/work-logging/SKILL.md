---
name: work-logging
description: Log work progress conversationally by updating task status, adding subtasks, and creating timestamped Quick Notes entries. Use when the user reports completing work items or making progress on tasks.
---

# Work Logging Skill

Enables conversational progress tracking in daily notes through subtask creation and timestamped logging.

## When to Use

Activate this skill when the user reports progress on tasks:
- "I checked the doctor's message"
- "Just finished the analytics review"
- "Called Alex and sent the follow-up"
- "Done with the prescription"

## Dual-Track Logging Pattern

Every progress report should update BOTH:

### 1. Nested Subtasks

Add checkboxes under the parent task in the daily note.

**Location:** Under the relevant task in `### A/B/C Priority Tasks` sections

**Format:**
```markdown
- [ ] 🔴1. [Parent task] - Company: [context]
  - [x] [Completed action user reported]
  - [ ] [Next logical step if applicable]
```

**Example:**
```markdown
- [ ] 🔴1. Renew levothyroxine prescription - Company: Personal
  - [x] Check message from doctor
  - [ ] Call pharmacy to confirm
  - [ ] Pick up prescription
```

### 2. Timestamped Quick Notes

Add context, decisions, or observations to the Quick Notes section.

**Location:** `### Quick Notes` section in the daily note

**Format:**
```markdown
- [HH:MM] [Task context]: [What happened] - [Optional next step or insight]
```

**Example:**
```markdown
### Quick Notes
- [10:26] Prescription: Starting - need to check doctor's message first
- [10:35] Prescription: Doctor approved refill, calling CVS next
- [10:45] Prescription: Complete - ready for pickup tomorrow at CVS on Lamar
```

## Detection Patterns

Recognize these as progress reports requiring logging:

| User Says | Action |
|-----------|--------|
| "I [verb] [thing]" | Check off subtask, add log entry |
| "[Thing] is done" | Mark task/subtask complete |
| "Just finished [thing]" | Check off, add completion log |
| "[Verb]ed [thing]" | Check off subtask (e.g., "Called Alex") |
| "Working on [thing]" | Add "in progress" log entry |
| "Need to [thing] next" | Add new subtask |

## Step-by-Step Process

When user reports progress:

1. **Identify the parent task** in today's daily note
2. **Check if subtask exists** - if not, add it
3. **Mark subtask complete** with `[x]`
4. **Add timestamped log entry** with context
5. **Suggest next step** if logical follow-up exists

## Example Interaction

**User:** "I checked the doctor's message - she said the refill is approved"

**Claude does:**

1. Finds: `- [ ] 🔴1. Renew levothyroxine prescription - Company: Personal`
2. Updates to:
```markdown
- [ ] 🔴1. Renew levothyroxine prescription - Company: Personal
  - [x] Check message from doctor
  - [ ] Call pharmacy to confirm refill
```
3. Adds to Quick Notes:
```markdown
- [10:35] Prescription: Doctor approved refill - need to call pharmacy next
```
4. Responds: "Got it - checked off the doctor message. Next step: call the pharmacy to confirm. Ready?"

## Completing Parent Tasks

When all subtasks are done OR user says the main task is complete:

1. Mark parent task complete: `- [x] 🔴1. Task - Company: Context`
2. Add final log entry: `- [10:45] Prescription: Complete - picking up tomorrow`
3. Celebrate briefly and suggest next A-priority task

## Integration Notes

- **Daily note location:** `{{vault_path}}/4-Daily/YYYY-MM-DD.md`
- **Subtasks go under:** The parent task in `Today's Task Overview` section
- **Logs go in:** `### Quick Notes` section (for work/task progress)
- **NOT for:** `### Daily Memories` section (that's for narrative/diary entries - see `/update` command)
- **Timestamps:** Use current time in 24-hour format `[HH:MM]`
- Works with `daily-note` and `task-system` skills

## Distinction: Work Logs vs Narrative Memories

This skill handles **work progress logging** in Quick Notes:
- Task completions and progress updates
- Project status and technical notes
- Work-related context and decisions

For **narrative/diary content** (personal stories, dreams, family moments), use Daily Memories via the `/update` command instead.

## Best Practices

1. **Keep subtasks actionable** - verb + object ("Call pharmacy", not "Pharmacy")
2. **Log context that matters** - decisions, blockers, insights
3. **Don't over-log** - quick confirmations don't need detailed notes
4. **Suggest next steps** - keep momentum going
5. **Use task context prefix** in logs (e.g., "Prescription: ...")

## Enhancements

### Leverage Assessment

When logging work, note the leverage level of the completed activity:

**Leverage Categories:**
| Level | Definition | Examples |
|-------|------------|----------|
| **High Leverage** | Creates compounding returns; builds systems, relationships, or capabilities | Writing documentation, creating templates, strategic decisions, mentoring, building automation |
| **Medium Leverage** | Moves important work forward with clear value | Project execution, reviews, meetings that unblock others |
| **Low Leverage** | Necessary but not multiplying impact | Admin tasks, routine maintenance, reactive work |

**Log Format Enhancement:**
```markdown
### Quick Notes
- [10:35] Prescription: Doctor approved refill [Low-L] - calling CVS next
- [11:00] LifeOS: Created task sync detection system [High-L] - will save hours weekly
- [14:00] {{company_1_name}}: Reviewed analytics dashboard [Medium-L] - ready for Alex's review
```

**Weekly Insight:** During `/weekly:review`, surface leverage distribution:
- "This week: X% High-Leverage, Y% Medium-Leverage, Z% Low-Leverage work"
- Flag if low-leverage work dominated

### Strategic Value Tag

Distinguish between working ON vs. IN the business/life:

**ON the business/life (strategic):**
- Building systems and processes
- Strategic planning and decision-making
- Relationship and capability building
- Creating assets that compound

**IN the business/life (tactical):**
- Executing predefined tasks
- Handling routine operations
- Responding to requests
- Maintenance work

**Log Format Enhancement:**
```markdown
### Quick Notes
- [10:35] EMC: Created inventory tracking template [ON] - systematizing operations
- [11:00] {{company_1_name}}: Reviewed PR comments [IN] - standard code review
- [14:00] Personal: Annual review with financial advisor [ON] - strategic wealth planning
```

### Big Rock Attribution

When logging work, connect it to the relevant Big Rock (quarterly priority) when applicable:

**Why this matters:**
- Reveals if daily work actually serves strategic priorities
- Surfaces drift toward "gravel" at expense of "Big Rocks"
- Creates accountability for quarterly goal progress

**Log Format Enhancement:**
```markdown
### Quick Notes
- [10:35] {{company_1_name}}: Built collector engagement dashboard [High-L, ON]
  - Big Rock: Q1 Analytics Platform
- [14:00] Personal: Called insurance about claim [Low-L, IN]
  - (No Big Rock - maintenance)
```

**Question to surface during logging:**
- "Does this work advance a Big Rock or is it just handling gravel?"
- "If this doesn't connect to a quarterly priority, should it have been done at all?"

### Enhanced Quick Notes Format

For significant work items, use enriched format:

```markdown
### Quick Notes
- [HH:MM] [Context]: [What happened]
  - Leverage: [High/Medium/Low]
  - Strategic: [ON/IN]
  - Big Rock: [Name or "Maintenance"]
  - Next: [Follow-up action if applicable]
```

**When to use enriched format:**
- A-priority work completed
- Work that took significant time (>30 min)
- Strategic or high-leverage activities
- During weekly review reflection

**When to use simple format:**
- Quick task completions
- Routine maintenance
- Low-stakes items
