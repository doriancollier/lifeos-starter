---
title: "Health Configuration"
type: "config"
version: "1.0"
created: "2026-01-11"
updated: "2026-01-11"
---

# Health Configuration

Configuration for the Health Tracking Integration system.

## Data Source

```yaml
health_export_path: ""  # Configure on first /health:sync - path to Health Auto Export folder
file_pattern: "HealthAutoExport-*.json"
database_path: "data/health/health.db"
```

## Daily Goals

These mirror your Apple Fitness ring goals plus additional wellness targets.

```yaml
daily_goals:
  # Fitness Rings
  active_energy_kcal: 410      # Move ring
  exercise_minutes: 30         # Exercise ring
  stand_hours: 10              # Stand ring

  # Activity
  step_count: 5000             # Winter target - increase in spring

  # Wellness
  sleep_hours: 7.5             # Minimum target
  water_oz: 64                 # Daily hydration

  # Not currently tracking
  # mindful_minutes: 10
```

## Long-term Goals (Milestones)

Track progress toward body composition and fitness milestones.

```yaml
milestone_goals:
  body_fat_percent:
    current: null              # Updated automatically from health data
    target: 18.0
    deadline: "2026-12-31"
    direction: "decrease"
    monthly_target: 0.7        # Target monthly reduction

  # Future milestones (uncomment when ready)
  # weight_lbs:
  #   current: null
  #   target: 185
  #   deadline: "2026-12-31"
  #   direction: "decrease"

  # vo2_max:
  #   current: null
  #   target: 45
  #   deadline: "2026-12-31"
  #   direction: "increase"
```

## Display Preferences

```yaml
display:
  units:
    weight: "lbs"
    distance: "miles"
    water: "oz"

  # Metrics shown in daily note Health section
  show_in_daily_note:
    - active_energy
    - exercise_minutes
    - stand_hours
    - step_count
    - sleep_hours
    - resting_heart_rate
    - body_fat_percent         # When available
```

## Sync Settings

```yaml
sync:
  backfill_days: 7             # Days to import on initial setup
  auto_sync_on_session: true   # Sync health data on Claude Code session start
  partial_data_indicator: true # Show "as of [time]" for incomplete days
```

## Coaching Integration

```yaml
coaching:
  # When to surface health insights
  integration_points:
    - daily_plan               # Morning planning
    - daily_eod                # End of day review
    - weekly_review            # Weekly patterns

  # Alerts and warnings
  alerts:
    sleep_under_hours: 6       # Warn if sleep consistently low
    ring_streak_broken: 3      # Days without closing rings
    body_fat_stalled_weeks: 4  # Weeks without progress

  # Celebration thresholds
  celebrate:
    ring_streak_days: 7        # Celebrate 7-day streaks
    milestone_progress: 25     # Celebrate 25%, 50%, 75% milestones
```

## Metric Mapping

Maps Health Auto Export JSON field names to our internal names.

```yaml
metric_mapping:
  # Fitness Rings
  active_energy: "active_energy"
  apple_exercise_time: "exercise_minutes"
  apple_stand_hour: "stand_hours"

  # Activity
  step_count: "step_count"
  walking_running_distance: "distance_km"
  flights_climbed: "flights_climbed"

  # Body Composition
  weight_body_mass: "weight_kg"
  body_fat_percentage: "body_fat_percent"

  # Cardio & Recovery
  vo2_max: "vo2_max"
  resting_heart_rate: "resting_heart_rate"
  heart_rate_variability: "hrv_ms"

  # Wellness
  sleep_analysis: "sleep_data"
  dietary_water: "water_ml"
  mindful_minutes: "mindful_minutes"
```

## Notes

- Body fat measurements from smart scale may have 2-3% variance
- Sleep data comes from Oura Ring (primary) and Apple Watch
- Resting heart rate and HRV from Oura Ring
- Step count combines iPhone and Apple Watch sources
