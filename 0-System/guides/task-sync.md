---
title: "Task Sync Guide"
created: "2025-12-03"
status: "active"
---

# Task Sync Guide

Bidirectional task synchronization between daily notes and project files.

## Overview

Tasks live in two places in LifeOS:
- **Daily Notes** (`4-Daily/`) — Today's actionable items with priorities
- **Project Files** (`1-Projects/Current/`) — All tasks for a project

Task Sync ensures these stay consistent when changes are made in either location.

## Why Task Sync?

### The Problem

Without sync, tasks drift apart:
- Complete a task in the daily note → project still shows incomplete
- Add a task to a project → doesn't appear in today's work
- Mark blocked in one place → other place unaware

### The Solution

A three-layer sync system that:
1. **Detects changes** in real-time during Claude Code sessions
2. **Queues external changes** made outside Claude Code
3. **Reconciles on demand** using the task-sync skill

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Task Sync System                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 1: Real-Time Detection (PostToolUse Hook)                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ task-sync-detector.py                                   │    │
│  │ • Triggers on Write/Edit to 1-Projects/ or 4-Daily/     │    │
│  │ • Extracts tasks from content                           │    │
│  │ • Identifies project context from section headers       │    │
│  │ • Writes to .claude/sync-queue.json                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                  │
│  Layer 2: Session Boundary Detection (SessionStart Hook)        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ session-context-loader.py                               │    │
│  │ • Checks for .claude/sync-pending flag                  │    │
│  │ • Reads sync-queue.json for unprocessed items           │    │
│  │ • Surfaces pending syncs in session context             │    │
│  │ • Suggests running task-sync skill                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                  │
│  Layer 3: External Change Detection (Git Hook)                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ git-task-sync-detector.sh                               │    │
│  │ • Runs on git post-commit                               │    │
│  │ • Analyzes diffs for task changes                       │    │
│  │ • Creates .claude/sync-pending flag                     │    │
│  │ • Next session picks up the pending flag                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                  │
│  Reconciliation: task-sync Skill                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ • Reads sync queue                                       │    │
│  │ • Compares tasks in daily notes vs project files        │    │
│  │ • Matches tasks using fuzzy text comparison             │    │
│  │ • Updates both files to be consistent                   │    │
│  │ • Clears sync queue and pending flag                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Sync Files

| File | Purpose | Format |
|------|---------|--------|
| `.claude/sync-queue.json` | Queue of pending task changes | JSON array |
| `.claude/sync-pending` | Flag indicating external changes | Timestamp |

### Sync Queue Format

```json
[
  {
    "timestamp": "2025-12-03T14:30:00Z",
    "source_file": "4-Daily/2025-12-03.md",
    "source_type": "daily",
    "project": "Analytics-Dashboard",
    "task_count": 3,
    "processed": false
  }
]
```

## Task Matching

Tasks are matched between files using **fuzzy text comparison**.

### Normalization Steps

Before comparison, tasks are normalized:

1. Strip priority emoji (🔴🟡🟢🔵📅)
2. Strip numbering (`1. `, `2. `, etc.)
3. Strip `Company: X` suffix
4. Strip `Waiting for: X` suffix
5. Normalize whitespace

### Match Example

```
Daily Note:   "- [x] 🔴1. Fix Next.js CVE vulnerability - Company: {{company_2_name}}"
Project File: "- [x] Fix Next.js CVE-2025-55182"

Normalized:   "Fix Next.js CVE vulnerability" vs "Fix Next.js CVE-2025-55182"
Similarity:   ~85%
Result:       MATCH (above 70% threshold)
```

### Threshold

- **70% similarity** — Tasks are considered the same
- Below 70% — Tasks are different, no sync action

## Sync Direction

| Change Made In | Syncs To | Authority |
|----------------|----------|-----------|
| Daily Note | Project File | Daily note is truth for *today's* work |
| Project File | Daily Note | Project file is truth for *all tasks* |

### Conflict Resolution

When tasks conflict:

1. **Most recent wins** — Based on file modification times
2. **Completion wins** — A completed task stays completed
3. **Daily note wins** — For today's date, daily note is authoritative

## Sync Rules

### Completion Status

- Completed in daily → Mark complete in project
- Completed in project → Mark complete in daily (if present)
- **Completed tasks never un-complete**

### Blocked Status

- 🔵 in daily note → Add `(BLOCKED: reason)` to project task
- Blocker resolved in project → Consider removing 🔵 in daily

### New Tasks

- New task in project → Consider adding to daily (if project in focus)
- New task in daily → Add to project's Tasks section

## Using the Sync System

### Automatic (Most Common)

The system works automatically:

1. You edit tasks in daily note or project file
2. PostToolUse hook detects the change
3. Change is queued in sync-queue.json
4. Hook suggests: "Task changes detected. Consider running task-sync skill."
5. You say "sync tasks" → task-sync skill runs
6. Both files are now consistent

### On Session Start

If external changes were made:

1. Session starts
2. SessionStart hook checks for pending syncs
3. Message appears: "[Task Sync] 3 task change(s) detected from external edits"
4. You run task-sync skill
5. Queue is cleared

### Manual Trigger

Say any of:
- "sync my tasks"
- "reconcile tasks"
- "run task sync"

## File Locations

### Daily Notes

```markdown
## Work

### {{company_1_name}}

#### [[Collector-Engagement]] `current`
*Next: Complete user research*

- [ ] 🔴2. Review engagement metrics - Company: {{company_1_name}}
- [x] 🟡 Draft proposal outline - Company: {{company_1_name}}
```

### Project Files

```markdown
## Tasks

- [ ] Review engagement metrics
- [x] Draft proposal outline
- [ ] User research interviews
- [ ] Compile findings report
```

## Hook Configuration

Hooks must be configured in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/.claude/hooks/task-sync-detector.py"
          }
        ]
      }
    ]
  }
}
```

See `.claude/hooks/README.md` for full configuration.

## Git Hook Setup (Optional)

For detecting external changes (Obsidian edits, VS Code, etc.):

```bash
# Create symlink
ln -s /path/to/.claude/hooks/git-task-sync-detector.sh \
      /path/to/.git/hooks/post-commit

# Make executable
chmod +x .git/hooks/post-commit
```

Now external changes trigger the sync-pending flag.

## Best Practices

### Do

1. **Sync after batch edits** — After updating multiple tasks
2. **Check sync on session start** — Address pending syncs early
3. **Use consistent task wording** — Helps matching algorithm
4. **Include company context** — Aids project identification

### Don't

1. **Don't rename tasks drastically** — May not match (below 70%)
2. **Don't ignore sync warnings** — Address them promptly
3. **Don't manually edit sync files** — Let hooks manage them

## Troubleshooting

### Sync Not Detecting Changes

1. Verify hooks are configured in `~/.claude/settings.json`
2. Check hooks are executable: `chmod +x .claude/hooks/*.py`
3. Ensure file is in `1-Projects/` or `4-Daily/`

### Tasks Not Matching

- Tasks may be worded too differently (below 70% similarity)
- Check that project section headers are correct: `#### [[Project-Name]]`
- Verify task format includes checkbox: `- [ ]` or `- [x]`

### Sync Queue Growing

- Run task-sync skill to process queue
- Check for errors in sync-queue.json format
- Clear manually if needed: `echo "[]" > .claude/sync-queue.json`

## Integration Points

- **task-system skill** — Understands task formats
- **work-logging skill** — Logs progress and triggers sync detection
- **daily-note skill** — Creates consistent daily note structure
- **PostToolUse hook** — Real-time change detection
- **SessionStart hook** — Pending sync awareness
- **Git hook** — External change detection

## Related Documentation

- [[task-management|Task Management Guide]] — Priority system and formats
- [[daily-workflow|Daily Workflow]] — How tasks flow through days
- [[hooks|Hooks]] — How hooks work in LifeOS
