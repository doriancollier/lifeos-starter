---
name: task-sync
description: Synchronize task states between daily notes and project files. Use after modifying tasks, or when sync-pending is detected at session start.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Task Sync Skill

Maintains consistency between tasks in daily notes and their source project files. This skill handles bidirectional synchronization.

## When to Use

1. **After modifying tasks** in daily notes or project files
2. **At session start** when `.claude/sync-pending` exists
3. **On user request** ("sync my tasks", "reconcile tasks")
4. **After PostToolUse hook** suggests syncing

## Sync Direction

| Change Location | Sync To | Priority |
|-----------------|---------|----------|
| Daily Note → | Project File | Daily note is source of truth for *today's* work |
| Project File → | Daily Note | Project file is source of truth for *all tasks* |

## Task Matching

Tasks are matched by **fuzzy text comparison** after normalizing:

1. Strip priority emoji (🔴🟡🟢🔵)
2. Strip numbering (`1. `, `2. `)
3. Strip "Company:" suffix
4. Normalize whitespace
5. Compare with 70% similarity threshold

### Example Match
```
Daily: "- [x] 🔴1. Fix Next.js CVE vulnerability"
Project: "- [x] Fix Next.js CVE-2025-55182"
→ Match (both about fixing Next.js CVE)
```

## Sync Rules

### Completion Status
- If task is completed in daily note → mark complete in project
- If task is completed in project → mark complete in daily note (if present)
- Completed tasks stay completed (no un-completing)

### Task Creation
- New task in project file → add to today's daily note under that project section
- New task in daily note → add to project file's Tasks section
- Only sync tasks for projects that exist in both files

### Blocked Status
- 🔵 (blocked) in daily note → add "BLOCKED" note to project task
- Blocked resolved in project → consider removing 🔵 in daily note

## File Locations

- **Daily notes**: `{{vault_path}}/4-Daily/YYYY-MM-DD.md`
- **Projects**: `{{vault_path}}/1-Projects/Current/`
- **Sync queue**: `{{vault_path}}/.claude/sync-queue.json`
- **Sync pending flag**: `{{vault_path}}/.claude/sync-pending`

## Sync Process

### 1. Check for Pending Syncs

```bash
# Check if sync is pending
cat "{{vault_path}}/.claude/sync-pending" 2>/dev/null

# Read sync queue
cat "{{vault_path}}/.claude/sync-queue.json" 2>/dev/null
```

### 2. Load Files to Compare

For each project in daily note's Work section:

1. Read the daily note
2. Extract tasks under the project section
3. Read the project file
4. Extract tasks from project's Tasks section

### 3. Compare and Reconcile

For each task:

```
IF task exists in daily note but not project:
  → Add to project file (if it's a real task, not temporary)

IF task exists in project but not daily note:
  → Consider adding to today's daily note (if project is in focus areas)

IF task completed in one but not other:
  → Mark as completed in both
```

### 4. Write Updates

Use the Edit tool to update files with minimal changes.

### 5. Clear Sync Queue

After processing, clear the queue:

```bash
rm "{{vault_path}}/.claude/sync-pending" 2>/dev/null
echo "[]" > "{{vault_path}}/.claude/sync-queue.json"
```

## Daily Note Task Format

Tasks in daily notes are under project sections:

```markdown
### {{company_1_name}}

#### [[AB-Email-Drip-Campaigns]] `current`
*Next: Complete segmentation logic*

- [ ] 🔴2. Review drip email copy
- [x] 🟡 Test email sequences
- [ ] 🔵 Wait for design assets - Waiting: Design team
```

## Project File Task Format

Tasks in project files are typically under a Tasks section:

```markdown
## Tasks

- [ ] Review drip email copy
- [x] Test email sequences
- [ ] Wait for design assets (BLOCKED: Design team)
```

## Conflict Resolution

When tasks conflict (e.g., marked complete in one file, incomplete in another):

1. **Most recent wins** - Check file modification times
2. **Completion wins** - A completed task stays completed
3. **Daily note wins** - For today's date, daily note is authoritative

## Example Sync Scenario

**Situation**: User manually checked off a task in Obsidian (project file)

1. Git commit triggers `git-task-sync-detector.sh`
2. Script creates `.claude/sync-pending`
3. Next Claude Code session starts
4. SessionStart hook sees pending sync
5. Claude uses `task-sync` skill
6. Skill reads project file, finds completed task
7. Skill reads today's daily note
8. Skill finds matching task, marks it complete
9. Skill clears sync queue

## Integration

This skill works with:
- `daily-note` skill for daily note structure
- `task-system` skill for task formatting
- `work-logging` skill for progress updates
- PostToolUse hook `task-sync-detector.py` for real-time detection
- Git hook `git-task-sync-detector.sh` for external change detection
- SessionStart hook for pending sync processing

## Limitations

- Only syncs tasks between daily notes and project files
- Does not sync meeting notes (those are cross-linked instead)
- Does not create project files (use `/create:project`)
- 70% similarity threshold may miss significantly reworded tasks
