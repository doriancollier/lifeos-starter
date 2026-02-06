---
name: daily-timebox
description: Create timeboxed focus blocks on calendar for daily tasks, promoting structured work and healthy lifestyle. Use when user wants to timebox their day, create focus blocks, or schedule their daily tasks.
allowed-tools: Read, Grep, Glob, Bash, mcp__google-calendar__list-events, mcp__google-calendar__create-event, mcp__google-calendar__update-event, mcp__google-calendar__delete-event, mcp__google-calendar__get-current-time
---

# Daily Timebox Skill

Creates timeboxed focus blocks on calendar to structure the workday around tasks from the daily note.

## ⚠️ Authentication Recovery

**If any calendar MCP tool returns an auth error**: Run this command immediately:

```bash
GOOGLE_OAUTH_CREDENTIALS="{{vault_path}}/gcp-oauth.keys.json" npx -y @cocal/google-calendar-mcp auth
```

---

## When to Activate

- User says "timebox my day", "create focus blocks", "schedule my tasks"
- During `/daily:plan` when user wants calendar-based scheduling
- User invokes `/daily:timebox`

## Core Settings

| Setting | Value |
|---------|-------|
| Calendar | `{{user_email}}` (primary) |
| Working hours | 8:00 AM - 6:00 PM |
| Timezone | America/Chicago |
| Default duration | 1 hour |
| Minimum duration | 30 minutes |
| Transparency | `transparent` (doesn't block availability) |

## Color Coding

| Context | Color ID | Color Name |
|---------|----------|------------|
| {{company_1_name}} | 4 | Flamingo |
| {{company_2_name}} | 5 | Banana |
| Personal | 1 | Lavender |
| EMC | 3 | Grape |
| Breaks/Wellness | 2 | Sage |

## Event Format

**Focus blocks:**
- Summary: `[Focus] Project/Context Name`
- Description: List of tasks to accomplish
- Extended properties: Full tagging standard (see below)

**Wellness blocks:**
- Summary: `[Break] Lunch`, `[Break] Movement`, or `[Break] Afternoon Reset`
- Color: Sage (2)
- Extended properties: Full tagging standard (see below)

### Extended Properties (Tagging Standard)

All timebox events MUST include these tags for system identification:

```javascript
extendedProperties: {
  "private": {
    "source": "claude-code",           // Identifies system origin
    "feature": "timebox",              // Feature type
    "created": "YYYY-MM-DD",           // Creation date
    "vault_link": "workspace/4-Daily/YYYY-MM-DD.md"  // Source daily note
  }
}
```

**Why this matters:**
- Enables safe rebuild (only system events get replaced)
- Distinguishes from real meetings
- Allows feature-specific cleanup
- Maintains historical record

See [Calendar Tagging Convention](/workspace/3-Resources/Documentation/calendar-tagging-convention.md) for full specification.

## Context Windows

Context windows are user-created calendar events that **guide** where tasks should be scheduled. They are NOT hard blocks - timeboxes can overlay them, but should respect their intent.

### Identifying Context Windows

An event is a **context window** if it meets BOTH criteria:

1. **Name contains a keyword**: `Focus`, `Window`, or `Time` (case-insensitive)
2. **Transparency is `transparent`**: Event doesn't block availability

### Extracting Company from Context Windows

Parse the company/context from the event name prefix:

| Event Name | Extracted Company | Timebox Behavior |
|------------|-------------------|------------------|
| `AB Focus` | {{company_1_name}} | AB tasks go HERE |
| `AB Window` | {{company_1_name}} | AB tasks go HERE |
| `AB Time` | {{company_1_name}} | AB tasks go HERE |
| `144 Focus` | {{company_2_name}} | 144 tasks go HERE |
| `EMC Window` | {{company_3_name}} | EMC tasks go HERE |
| `Personal Time` | Personal | Personal tasks go HERE |
| `Open Focus` | Open/Any | Catch-all for any work |
| `Wind Down` | Special | Light/no scheduling |

**Parsing logic:**
1. Check if summary contains "Focus", "Window", or "Time"
2. Extract prefix before the keyword (e.g., "AB" from "AB Focus")
3. Map prefix to company: `AB` → {{company_1_name}}, `144` → {{company_2_name}}, `EMC` → {{company_3_name}}, `Personal` → Personal, `Open` → any

### Context Window Behavior

| Task Company | Scheduling Rule |
|--------------|-----------------|
| {{company_1_name}} | Schedule WITHIN `AB Focus/Window/Time` if available |
| {{company_2_name}} | Schedule WITHIN `144 Focus/Window/Time` if available, else `Open Focus` |
| EMC | Schedule WITHIN `EMC Focus/Window/Time` if available, else `Open Focus` |
| Personal | Schedule in `Open Focus` or gaps, avoid company-specific windows |
| Wellness | Can overlay ANY window (lunch, breaks are exceptions) |

### Special Cases

- **Wind Down**: Recognized as a protected transition period. Schedule only light tasks or nothing.
- **No matching window**: If a task's company has no dedicated window, use `Open Focus` or available gaps.
- **Multiple windows**: If multiple windows exist for same company, fill first one, overflow to second.

---

## Algorithm

### Step 1: Gather Context

1. Get current time via `mcp__google-calendar__get-current-time`
2. Read today's daily note from `workspace/4-Daily/YYYY-MM-DD.md`
3. Extract A and B priority tasks (skip C priority)
4. Check existing calendar events for today (to avoid conflicts with real meetings)
5. **Identify context windows** (events with "Focus"/"Window"/"Time" + `transparency: transparent`)

### Step 2: Identify Existing Timeboxes

Search for events with system tagging:
```
mcp__google-calendar__list-events with:
- calendarId: "{{user_email}}"
- timeMin: today 00:00:00
- timeMax: today 23:59:59
- privateExtendedProperty: ["source=claude-code", "feature=timebox"]
```

**Note:** For backwards compatibility, also check for legacy `timebox=true` tag.

### Step 3: Group Tasks by Project/Context

Bundle related tasks together:
- All {{company_1_name}} tasks → one "AB Focus" block
- All {{company_2_name}} tasks → one "144 Focus" block
- All Personal tasks → one "Personal Focus" block
- All EMC tasks → one "EMC Focus" block

### Step 4: Estimate Durations

| Task Count | Suggested Duration |
|------------|-------------------|
| 1 small task | 30 min |
| 1-2 tasks | 1 hour |
| 3-4 tasks | 1.5-2 hours |
| 5+ tasks | 2+ hours (consider splitting) |

Use judgment based on task complexity.

### Step 5: Schedule Blocks

**Working hours**: 8:00 AM - 6:00 PM

**Required wellness blocks (NON-NEGOTIABLE):**

| Block | Default Time | Duration | Flexibility |
|-------|-------------|----------|-------------|
| Lunch | 12:00 PM - 1:00 PM | 1 hour (30 min minimum if packed) | Shift around meetings, NEVER skip |
| Movement | 1:00 PM - 1:20 PM | 20 min | After lunch, can be post-lunch walk |
| Afternoon Reset | 3:00 PM - 3:20 PM | 20 min | Stretch, walk, fresh air |

**Lunch scheduling rules:**
1. **Preferred**: 12:00 PM - 1:00 PM (1 hour)
2. **If meeting conflicts**: Find next available 30-60 min slot after meeting ends
3. **Packed schedule**: 30 min minimum is acceptable, but flag it: "⚠️ Short lunch today"
4. **NEVER schedule work 11:30 AM - 1:30 PM without a lunch block**

**Movement block rules:**
1. Immediately after lunch when possible (aids digestion, mental reset)
2. Can be combined with afternoon reset if schedule is tight
3. Purpose: Walk, stretch, fresh air — not just sitting break

**Short breaks**: 5-10 min between focus blocks when back-to-back

**Scheduling priority:**
1. Preserve existing real meetings (non-timebox events)
2. **Add wellness blocks FIRST** — these are non-negotiable infrastructure
3. **Match tasks to context windows:**
   - AB tasks → schedule within `AB Focus/Window/Time`
   - 144 tasks → schedule within `144 Focus/Window/Time` or `Open Focus`
   - EMC tasks → schedule within `EMC Focus/Window/Time` or `Open Focus`
   - Personal tasks → schedule in `Open Focus` or gaps outside company windows
4. If no matching context window exists, use available gaps
5. Higher priority tasks (A) get earlier slots within their context window

**Warning triggers:**
- If lunch < 30 min: "⚠️ No lunch block possible — consider rescheduling"
- If no movement block fits: "⚠️ Dense schedule — find 10 min for a walk"
- If 3+ hours of back-to-back focus: "⚠️ Long focus stretch — breaks matter"

**Context-aware scheduling example:**

```
Calendar has:
- 9:30 AM - 1:30 PM: "AB Focus" (transparent)
- 2:00 PM - 4:00 PM: "Open Focus" (transparent)

Tasks:
- [AB] Review PRs
- [AB] Update dashboard
- [Personal] Call doctor
- [144] Write proposal

Schedule:
- 9:30-11:00: [Focus] {{company_1_name}} (Review PRs, Update dashboard)
- 12:00-1:00: [Break] Lunch
- 2:00-3:00: [Focus] {{company_2_name}} (Write proposal)
- 3:00-3:30: [Focus] Personal (Call doctor)
```

### Step 6: Create Calendar Events

For each timebox:
```
mcp__google-calendar__create-event with:
- calendarId: "{{user_email}}"
- summary: "[Focus] Project Name" or "[Break] Type"
- start: "YYYY-MM-DDTHH:MM:SS"
- end: "YYYY-MM-DDTHH:MM:SS"
- timeZone: "America/Chicago"
- colorId: [appropriate color]
- transparency: "transparent"
- description: "Tasks:\n- Task 1\n- Task 2\n..."
- extendedProperties: {
    "private": {
      "source": "claude-code",
      "feature": "timebox",
      "created": "YYYY-MM-DD",
      "vault_link": "workspace/4-Daily/YYYY-MM-DD.md"
    }
  }
```

## Update Behavior

When updating an existing timeboxed day:

1. **Find existing timeboxes** using `privateExtendedProperty: ["source=claude-code", "feature=timebox"]`
   - Also check legacy format: `privateExtendedProperty: ["timebox=true"]`
2. **Identify past vs future**: Compare event start time to current time
3. **Leave past timeboxes untouched** (historical record)
4. **Only modify/replace future timeboxes**

To update future timeboxes:
1. Delete future timebox events (only those with system tags)
2. Re-schedule based on current task list and remaining time
3. **Important**: Never delete events without `source=claude-code` tag - those are real meetings

## Output Format

After creating timeboxes, present summary:

```markdown
## Today's Timeboxed Schedule

| Time | Block | Tasks |
|------|-------|-------|
| 8:00-10:00 | [Focus] {{company_1_name}} | Task 1, Task 2 |
| 10:00-10:10 | [Break] | Short break |
| 10:10-11:30 | [Focus] {{company_2_name}} | Task 3 |
| 12:00-1:00 | [Break] Lunch | |
| ... | ... | ... |

**Total focus time**: X hours
**Breaks**: Y minutes
```

## Edge Cases

- **No tasks for today**: Inform user, don't create empty timeboxes
- **All tasks completed**: Celebrate, offer to help with next priorities
- **Conflicts with meetings**: Schedule around them, note limited availability
- **Late start**: Only timebox remaining hours, skip past slots
- **Too many tasks**: Warn user, suggest prioritizing or moving some to tomorrow

## Integration

- Works with `task-system` skill for understanding task priorities
- Works with `calendar-management` skill patterns for event creation
- Can be invoked during `/daily:plan` workflow
- Standalone via `/daily:timebox` command

---

## Enhancements

These scheduling enhancements integrate with [[planning-horizons]] and [[decision-frameworks]] to create more effective daily schedules.

### 90-Minute Sprint Structure

**The Ultradian Rhythm**: Deep work is most effective in 90-minute cycles, matching the body's natural ultradian rhythm.

**Sprint Structure:**

| Phase | Duration | Purpose |
|-------|----------|---------|
| Focus Sprint | 90 minutes | Deep, uninterrupted work |
| Recovery | 15-20 minutes | Movement, hydration, mental reset |
| Focus Sprint | 90 minutes | Second deep work block |
| Longer Break | 30-60 minutes | Lunch or substantial break |

**Implementation:**

1. **When grouping tasks**, aim for 90-minute focus blocks:
   - Prefer 90-min blocks over 60-min when tasks support it
   - 2-3 tasks of medium complexity = 90 min block
   - 1 complex/creative task = dedicated 90 min block

2. **Block naming for 90-min sprints:**
   ```
   - summary: "[Sprint 1] {{company_1_name}} Deep Work"
   - summary: "[Sprint 2] {{company_2_name}}"
   ```

3. **Maximum consecutive sprints**: 2-3 sprints before requiring substantial break

**Example Daily Structure:**
```
8:00-9:30   [Sprint 1] Deep Work (A-priority)
9:30-9:45   [Break] Movement
9:45-11:15  [Sprint 2] Secondary Focus
11:15-11:30 [Break] Short break
11:30-12:00 Light work / communications
12:00-1:00  [Break] Lunch
1:00-1:20   [Break] Movement
1:20-2:50   [Sprint 3] Afternoon Focus
2:50-3:10   [Break] Afternoon Reset
3:10-4:40   [Sprint 4] Final Sprint
4:40-6:00   Wind down / low-energy tasks
```

### Energy-Aware Scheduling

**Match Task Type to Energy Level**: Schedule demanding work during peak energy, routine work during troughs.

**INTJ Energy Pattern** (typical, adjust based on individual observation):

| Time Block | Energy Level | Best For |
|------------|--------------|----------|
| 8:00-11:00 | Peak | Complex/creative work, A-priorities, deep thinking |
| 11:00-12:00 | Moderate | Important but less demanding tasks |
| 12:00-2:00 | Low (post-lunch) | Light tasks, communications, admin |
| 2:00-4:00 | Recovering | Moderate focus work |
| 4:00-6:00 | Declining | Routine tasks, planning tomorrow |

**Scheduling Rules:**

1. **A-priorities → Morning sprints (8:00-11:00)**
   - First sprint of the day = highest priority deep work
   - Creative/strategic work gets peak energy hours

2. **B-priorities → Mid-day or afternoon**
   - Important but less cognitively demanding
   - Can handle some interruption

3. **C-priorities → Energy troughs**
   - After lunch (1:00-2:00)
   - Late afternoon (after 4:00)
   - Administrative, routine, or quick tasks

4. **Communications/meetings → Late morning or mid-afternoon**
   - Avoid first 90 minutes of day (protect deep work start)
   - 11:00-12:00 or 2:00-3:00 are good meeting windows

**Task Classification for Energy:**

| Task Characteristic | Energy Requirement | Scheduling Priority |
|--------------------|-------------------|---------------------|
| Creative, novel, strategic | High | Morning peak |
| Analysis, problem-solving | High | Morning peak |
| Writing (original content) | High | Morning peak |
| Meetings with decisions | Medium-High | Late morning |
| Routine communications | Low | Post-lunch trough |
| Administrative tasks | Low | Late afternoon |
| Reading/review | Medium | Flexible |

### Recovery Blocks

**Strategic Recovery Between Sprints**: Recovery is not optional—it's infrastructure for sustained performance.

**Recovery Types:**

| Type | Duration | Frequency | Activities |
|------|----------|-----------|------------|
| Micro-break | 5 min | Every 45-60 min | Stand, stretch, eye rest |
| Sprint recovery | 15-20 min | Between 90-min sprints | Walk, hydrate, fresh air |
| Major break | 30-60 min | After 2-3 sprints | Lunch, longer walk, full reset |
| End-of-day wind down | 30 min | 5:30-6:00 PM | Light tasks, tomorrow prep |

**Implementation:**

1. **After every focus block**, automatically add recovery:
   ```
   If focus_block.duration >= 60 minutes:
     Add 15-min recovery block after
   If focus_block.duration >= 90 minutes:
     Add 20-min recovery block after
   ```

2. **Recovery block format:**
   ```
   mcp__google-calendar__create-event with:
   - summary: "[Recovery] Movement & Reset"
   - colorId: "2"  # Sage
   - description: "Stand, walk, hydrate. Mental reset before next sprint."
   ```

3. **Warning for missing recovery:**
   ```
   If 3+ hours of focus blocks without recovery block:
     Warning: "⚠️ Long focus stretch (3+ hours) without recovery. Add breaks to maintain performance."
   ```

**Recovery Activities to Suggest:**
- Walk (outdoors if possible)
- Stretch/movement
- Hydration
- Fresh air
- Brief meditation/breathing
- Non-screen activity

### Big Rock Priority

**Rocks Before Gravel**: Schedule Big Rocks (quarterly priorities) FIRST, then fill with gravel (routine tasks).

**Big Rock Identification:**

1. Check quarterly rocks in year file (`workspace/2-Areas/Personal/Years/YYYY.md`)
2. Check weekly Big 3 in daily note
3. A-priority tasks that directly advance quarterly goals

**Scheduling Order:**

```
1. Check calendar for existing meetings (immovable)
2. Identify today's Big Rock tasks (tasks serving quarterly priorities)
3. Schedule Big Rocks in PEAK ENERGY slots first
4. Add wellness blocks (lunch, movement, breaks)
5. Schedule remaining A-priorities
6. Fill gaps with B-priorities
7. C-priorities only if time remains
```

**Big Rock Validation:**

For each A-priority task, ask:
- "Which quarterly rock does this advance?"
- "Is this urgent-important or just urgent?"
- "Would completing this move the needle on my 90-day goals?"

**Gravel Detection:**

Tasks that are NOT Big Rocks (should not get peak energy slots):
- Routine communications
- Administrative tasks
- Tasks without clear goal connection
- "Should do" tasks that don't serve priorities

**Example Application:**

```
Daily Note has:
A-priorities:
- 🔴 Review {{company_1_name}} roadmap (connects to Q1 Rock: Product Strategy)
- 🔴 Call insurance (routine, no rock connection)
- 🔴 Write 144 proposal (connects to Q1 Rock: 144 Launch)

Scheduling:
✓ {{company_1_name}} roadmap → 8:00-9:30 [Sprint 1] (Big Rock, peak energy)
✓ 144 proposal → 9:45-11:15 [Sprint 2] (Big Rock, high energy)
✓ Insurance call → 1:30-2:00 (Gravel, post-lunch)
```

**Weekly Big 3 Integration:**

At session start or during `/daily:plan`:
```
Check: "What are your Weekly Big 3?"
→ Ensure at least one Big 3 item gets a morning sprint slot today
→ Flag if Big 3 items have no scheduled time
```

See [[planning-horizons]] for the complete planning cascade and Big Rock methodology.
