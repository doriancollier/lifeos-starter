---
name: health-awareness
description: Health data integration and coaching for daily planning. Use during /daily:plan, /daily:eod, weekly reviews, or when user asks about health metrics, fitness rings, sleep, weight, or body composition goals.
---

# Health Awareness Skill

Integrates Apple Health data into LifeOS workflows for coached health goal achievement.

## When to Activate

- During `/daily:plan` morning planning
- During `/daily:eod` end of day review
- During weekly review health assessment
- When user asks about health metrics, fitness rings, sleep, weight, body fat
- When user mentions health goals or progress
- When low sleep or missed goals are detected

## Data Source

Health data is synced from Health Auto Export app via `.claude/scripts/health_sync.py`.

**Database**: `.claude/data/health.db`
**Config**: `workspace/0-System/config/health-config.md`

## Quick Commands

```bash
# Sync today's health data
python3 .claude/scripts/health_sync.py sync

# Sync last N days
python3 .claude/scripts/health_sync.py sync --days 7

# Get today's status
python3 .claude/scripts/health_sync.py status

# Get compact status (for session context)
python3 .claude/scripts/health_sync.py status --format compact

# Get specific date
python3 .claude/scripts/health_sync.py status --date 2026-01-10

# View goal progress (with streaks, closure rates, insights)
python3 .claude/scripts/health_sync.py goals

# Generate Health section for daily note
python3 .claude/scripts/health_sync.py daily-note-section

# Generate coaching prompts (context-aware)
python3 .claude/scripts/health_sync.py coaching --context morning
python3 .claude/scripts/health_sync.py coaching --context evening
python3 .claude/scripts/health_sync.py coaching --context weekly

# Export to CSV
python3 .claude/scripts/health_sync.py export-csv
```

## Daily Goals

| Metric | Target | Notes |
|--------|--------|-------|
| Move (Active Energy) | 410 kcal | Apple Watch Move ring |
| Exercise | 30 min | Apple Watch Exercise ring |
| Stand | 10 hrs | Apple Watch Stand ring |
| Steps | 5,000 | Winter target (increase in spring) |
| Sleep | 7.5 hrs | Minimum for recovery |
| Water | 64 oz | Daily hydration |

## Milestone Goals

| Metric | Current | Target | Deadline |
|--------|---------|--------|----------|
| Body Fat % | 25.8% | 18% | Dec 31, 2026 |

Monthly target: ~0.7% reduction

## Integration with Daily Planning

### Morning Check-in

When running `/daily:plan`, sync health data and report:

1. **Yesterday's Summary**
   - Ring closure status (Move/Exercise/Stand)
   - Sleep duration and quality
   - Any notable metrics (RHR, HRV)

2. **Weekly Trends**
   - 7-day averages vs goals
   - Sleep debt accumulation
   - Milestone progress

3. **Coaching Prompts** (surface when relevant)
   - Sleep under 6 hrs: "Your sleep has been under target. How will you protect rest tonight?"
   - Rings not closing: "You've missed your Move goal 3 days in a row. What's blocking activity?"
   - Body fat stalled: "Progress has plateaued. Time to review nutrition or training?"

### Daily Note Health Section

Add this section to daily notes when health data is available:

```markdown
## Health Metrics

### Today's Progress

| Metric | Current | Goal | Status |
|--------|---------|------|--------|
| Move | X kcal | 410 | [status] |
| Exercise | X min | 30 | [status] |
| Stand | X hrs | 10 | [status] |
| Steps | X | 5,000 | [status] |
| Sleep | X hrs | 7.5 | [status] |

*Last synced: [timestamp]*
```

Status indicators:
- ⬜ 0-24% (not started)
- 🟨 25-74% (in progress)
- 🟩 75-99% (almost there)
- ✅ 100%+ (goal met)

## Coaching Triggers

### Sleep Alerts

| Condition | Coaching Response |
|-----------|-------------------|
| Single night < 6 hrs | Note it, ask about recovery plan |
| 3+ nights < 7 hrs | "Sleep debt is accumulating. This affects everything." |
| 7-day avg < 7 hrs | Serious intervention - recommend schedule review |

### Ring Alerts

| Condition | Coaching Response |
|-----------|-------------------|
| Missed 1 ring | Acknowledge, no intervention |
| Missed all 3 rings | "What happened yesterday? Any blockers?" |
| 3+ day streak broken | "You had a X-day streak. What got in the way?" |

### Body Composition

| Condition | Coaching Response |
|-----------|-------------------|
| On track (monthly target met) | Celebrate progress |
| Stalled (4+ weeks no change) | Review approach, suggest adjustment |
| Trending wrong direction | Flag immediately, investigate |

## Weekly Review Integration

During weekly review, provide:

1. **Weekly Health Summary**
   - Ring closure rate (X/7 days each)
   - Average sleep vs target
   - Body composition trend (if data available)

2. **Pattern Recognition**
   - Best/worst days for each metric
   - Correlations (sleep vs energy ratings)
   - Weekend vs weekday patterns

3. **Next Week Focus**
   - One health priority based on data

## Output Formats

### Quick Summary (for daily planning)
```
Yesterday: Move ✅ | Exercise ✅ | Stand 🟨 (8/10) | Sleep 7.2 hrs ✅
7-day avg sleep: 6.4 hrs (below 7.5 target)
Body fat: 25.8% → 18% by Dec (on track)
```

### Detailed Status (for status command)
Run `python3 .claude/scripts/health_sync.py status` for full output.

## Related Skills

- **energy-management**: Health data feeds physical energy dimension
- **daily-note**: Health section integration
- **planning-cadence**: Weekly/monthly health reviews
