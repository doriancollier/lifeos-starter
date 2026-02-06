---
description: Sync health data from Health Auto Export and show status
argument-hint: "[days]"
allowed-tools: Read, Bash
---

# Health Sync Command

Manually sync health data from Health Auto Export app and display current health status.

## When to Use

- To refresh health data mid-day after activity
- When automatic session sync didn't run
- To check detailed health metrics
- Before weekly reviews for updated data

## Context

- **Script**: `.claude/scripts/health_sync.py`
- **Database**: `.claude/data/health.db`
- **Config**: `workspace/0-System/config/health-config.md`
- **Skill**: `.claude/skills/health-awareness/SKILL.md`

## Arguments

- `[days]` - Optional: Number of days to sync (default: 7)

## Task

Execute these steps in order:

### 0. Check Configuration (First Run Detection)

Read `workspace/0-System/config/health-config.md` and check if `health_export_path` is empty:

```yaml
health_export_path: ""  # Empty = needs configuration
```

**If health_export_path is empty:**
1. Use AskUserQuestion to ask the user for their Health Auto Export folder path:
   - Prompt: "Where is your Health Auto Export folder located?"
   - Provide options:
     - Default iCloud location: `~/Library/Mobile Documents/iCloud~com~ifunography~HealthExport/Documents/`
     - Custom path (let them specify)
2. Update `workspace/0-System/config/health-config.md` with the provided path
3. Continue with sync

**If health_export_path is set:** Continue to Step 1.

### 1. Sync Recent Data

```bash
# Sync last N days of health data (default: 7)
python3 "{{vault_path}}/.claude/scripts/health_sync.py" sync --days {days}
```

### 2. Show Today's Status

```bash
# Get today's health status
python3 "{{vault_path}}/.claude/scripts/health_sync.py" status
```

### 3. Show Goal Progress

```bash
# Get goal progress with 7-day averages
python3 "{{vault_path}}/.claude/scripts/health_sync.py" goals
```

## Output Format

Present results in a clear summary:

```markdown
## Health Sync Complete

### Sync Results
- **Files synced**: X day(s)
- **Dates**: 2026-01-05 through 2026-01-11

### Today's Status

| Metric | Current | Goal | Status |
|--------|---------|------|--------|
| Move | 205 kcal | 410 | 🟨 50% |
| Exercise | 15 min | 30 | 🟨 50% |
| Stand | 5 hrs | 10 | 🟨 50% |
| Steps | 2,500 | 5,000 | 🟨 50% |
| Sleep | 5.7 hrs | 7.5 | 🟩 76% |

*Data as of [time] - may update*

### 7-Day Averages vs Goals

| Metric | Avg | Goal | Trend |
|--------|-----|------|-------|
| Move | 450 kcal | 410 | ✅ Exceeding |
| Exercise | 35 min | 30 | ✅ Exceeding |
| Stand | 9 hrs | 10 | 🟨 Close |
| Sleep | 6.4 hrs | 7.5 | ⚠️ Below target |

### Milestone Progress

| Goal | Current | Target | Deadline | Progress |
|------|---------|--------|----------|----------|
| Body Fat | 25.8% | 18% | Dec 2026 | ~7.8% to go |

### Coaching Insight

[Based on data, provide ONE focused insight:]
- Sleep debt warning if avg < 7 hrs
- Ring streak celebration if all closed
- Plateau warning if body fat stalled
```

## Status Indicators

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not started (0-24%) |
| 🟨 | In progress (25-74%) |
| 🟩 | Almost there (75-99%) |
| ✅ | Goal met (100%+) |

## Related

- `/daily:plan` - Morning planning includes health overview
- `/daily:eod` - End of day includes health summary
- `/weekly:review` - Weekly health patterns
