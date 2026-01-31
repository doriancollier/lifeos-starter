#!/usr/bin/env python3
"""
Health Sync - Sync Health Auto Export data to SQLite database.

Integrates Apple Health data (via Health Auto Export app) into LifeOS for
AI-coached health goal achievement with automatic tracking and trend analysis.

Usage:
    python3 health_sync.py init-db                      # Initialize database schema
    python3 health_sync.py sync                         # Sync today's data
    python3 health_sync.py sync --days 7                # Sync last N days
    python3 health_sync.py status                       # Show today's status
    python3 health_sync.py status --format compact      # Compact one-liner for hooks
    python3 health_sync.py status --date 2026-01-10     # Show specific date
    python3 health_sync.py goals                        # Show goal progress with streaks
    python3 health_sync.py daily-note-section           # Generate markdown for daily note
    python3 health_sync.py coaching --context morning   # Morning coaching prompts
    python3 health_sync.py coaching --context evening   # Evening coaching prompts
    python3 health_sync.py coaching --context weekly    # Weekly review prompts
    python3 health_sync.py export-csv                   # Export to CSV

Data Source:
    Health Auto Export app → iCloud Drive → JSON files → SQLite database

Database: .claude/data/health.db
Config: 0-System/config/health-config.md
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ============================================================================
# Configuration
# ============================================================================

VAULT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = VAULT_ROOT / "0-System" / "config" / "health-config.md"
DB_PATH = VAULT_ROOT / ".claude" / "data" / "health.db"

# Default export path (can be overridden by config)
DEFAULT_EXPORT_PATH = Path.home() / "Library" / "Mobile Documents" / "iCloud~com~ifunography~HealthExport" / "Documents" / "Dc test automation"

# Unit conversions
KG_TO_LBS = 2.20462
KM_TO_MILES = 0.621371
ML_TO_OZ = 0.033814

# ============================================================================
# Database Schema
# ============================================================================

SCHEMA = """
-- Daily health metrics (one row per day)
CREATE TABLE IF NOT EXISTS daily_health (
    date TEXT PRIMARY KEY,              -- YYYY-MM-DD

    -- Fitness Rings
    active_energy_kcal REAL,            -- Move ring
    exercise_minutes INTEGER,           -- Exercise ring
    stand_hours INTEGER,                -- Stand ring

    -- Activity
    step_count INTEGER,
    distance_km REAL,
    flights_climbed INTEGER,

    -- Body Composition
    weight_kg REAL,
    body_fat_percent REAL,

    -- Cardio Fitness
    vo2_max REAL,
    resting_heart_rate INTEGER,
    hrv_ms REAL,

    -- Sleep
    sleep_hours REAL,
    sleep_deep_hours REAL,
    sleep_rem_hours REAL,
    sleep_core_hours REAL,
    sleep_awake_hours REAL,

    -- Wellness
    mindful_minutes INTEGER,
    water_ml INTEGER,

    -- Metadata
    source_file TEXT,                   -- JSON filename
    file_modified TEXT,                 -- When JSON was last modified
    synced_at TEXT,                     -- When we imported it
    is_complete INTEGER DEFAULT 0       -- 1 if after midnight sync
);

-- Goals table
CREATE TABLE IF NOT EXISTS health_goals (
    id INTEGER PRIMARY KEY,
    goal_type TEXT NOT NULL,            -- 'daily' or 'milestone'
    metric TEXT NOT NULL,               -- 'active_energy', 'body_fat_percent', etc.
    target_value REAL NOT NULL,
    target_date TEXT,                   -- For milestones: YYYY-MM-DD
    created_at TEXT NOT NULL,
    achieved_at TEXT,
    notes TEXT
);

-- Goal history (for tracking changes over time)
CREATE TABLE IF NOT EXISTS goal_history (
    id INTEGER PRIMARY KEY,
    goal_id INTEGER,
    previous_value REAL,
    new_value REAL,
    changed_at TEXT NOT NULL,
    reason TEXT,
    FOREIGN KEY (goal_id) REFERENCES health_goals(id)
);

-- Sync log
CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY,
    synced_at TEXT NOT NULL,
    dates_synced TEXT,                  -- JSON array of dates
    records_updated INTEGER,
    notes TEXT
);
"""

# ============================================================================
# Helper Functions
# ============================================================================

def get_db_connection() -> sqlite3.Connection:
    """Get database connection, creating DB if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with schema."""
    conn = get_db_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")


def get_export_path() -> Path:
    """Get health export path from config or use default."""
    # For now, use default. TODO: Parse config file
    return DEFAULT_EXPORT_PATH


def find_json_files(days: int = 1) -> list[Path]:
    """Find JSON files for the last N days."""
    export_path = get_export_path()
    if not export_path.exists():
        print(f"Error: Export path not found: {export_path}")
        return []

    today = datetime.now().date()
    files = []

    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        filename = f"HealthAutoExport-{date_str}.json"
        filepath = export_path / filename

        if filepath.exists():
            files.append(filepath)
        else:
            # Try without leading zeros (some exports vary)
            pass

    return files


def parse_json_file(filepath: Path) -> dict:
    """Parse a Health Auto Export JSON file and aggregate metrics."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    metrics = data.get('data', {}).get('metrics', [])
    result = {
        'source_file': filepath.name,
        'file_modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
    }

    # Extract date from filename
    date_str = filepath.stem.replace('HealthAutoExport-', '')
    result['date'] = date_str

    for metric in metrics:
        name = metric.get('name', '')
        data_points = metric.get('data', [])

        if not data_points:
            continue

        # Aggregate based on metric type
        if name == 'active_energy':
            total = sum(d.get('qty', 0) for d in data_points)
            result['active_energy_kcal'] = round(total, 1)

        elif name == 'apple_exercise_time':
            total = sum(d.get('qty', 0) for d in data_points)
            result['exercise_minutes'] = int(total)

        elif name == 'apple_stand_hour':
            total = sum(d.get('qty', 0) for d in data_points)
            result['stand_hours'] = int(total)

        elif name == 'step_count':
            total = sum(d.get('qty', 0) for d in data_points)
            result['step_count'] = int(total)

        elif name == 'walking_running_distance':
            total = sum(d.get('qty', 0) for d in data_points)
            units = metric.get('units', 'km')
            if units == 'mi':
                # Convert miles to km for storage
                result['distance_km'] = round(total / KM_TO_MILES, 2)
            else:
                result['distance_km'] = round(total, 2)

        elif name == 'flights_climbed':
            total = sum(d.get('qty', 0) for d in data_points)
            result['flights_climbed'] = int(total)

        elif name == 'weight_body_mass':
            # Take most recent reading
            # Note: units may be 'lb' or 'kg' depending on export settings
            if data_points:
                weight = data_points[-1].get('qty', 0)
                units = metric.get('units', 'kg')
                if units == 'lb':
                    # Convert lbs to kg for storage
                    result['weight_kg'] = round(weight / KG_TO_LBS, 2)
                else:
                    result['weight_kg'] = round(weight, 2)

        elif name == 'body_fat_percentage':
            # Take most recent reading
            if data_points:
                result['body_fat_percent'] = round(data_points[-1].get('qty', 0), 1)

        elif name == 'vo2_max':
            # Take most recent reading
            if data_points:
                result['vo2_max'] = round(data_points[-1].get('qty', 0), 1)

        elif name == 'resting_heart_rate':
            # Take most recent reading
            if data_points:
                result['resting_heart_rate'] = int(data_points[-1].get('qty', 0))

        elif name == 'heart_rate_variability':
            # Average HRV for the day
            values = [d.get('qty', 0) for d in data_points if d.get('qty')]
            if values:
                result['hrv_ms'] = round(sum(values) / len(values), 1)

        elif name == 'sleep_analysis':
            # Parse sleep data - can be aggregated or per-stage format
            total_sleep = 0
            deep = rem = core = awake = 0

            for d in data_points:
                # Check for aggregated Oura/Apple format
                if 'totalSleep' in d:
                    total_sleep = d.get('totalSleep', 0)
                    deep = d.get('deep', 0)
                    rem = d.get('rem', 0)
                    core = d.get('core', 0)
                    awake = d.get('awake', 0)
                    break  # Aggregated record, no need to continue
                else:
                    # Per-stage format
                    value = d.get('value', d.get('qty', ''))
                    if isinstance(value, str):
                        qty = d.get('qty', 0)
                        if 'deep' in value.lower():
                            deep += qty
                        elif 'rem' in value.lower():
                            rem += qty
                        elif 'core' in value.lower() or 'light' in value.lower():
                            core += qty
                        elif 'awake' in value.lower():
                            awake += qty
                        else:
                            total_sleep += qty
                    elif isinstance(value, (int, float)):
                        total_sleep += value

            # Store values (already in hours from Oura format)
            if total_sleep or deep or rem or core:
                result['sleep_hours'] = round(total_sleep if total_sleep else (deep + rem + core), 2)
                result['sleep_deep_hours'] = round(deep, 2) if deep else None
                result['sleep_rem_hours'] = round(rem, 2) if rem else None
                result['sleep_core_hours'] = round(core, 2) if core else None
                result['sleep_awake_hours'] = round(awake, 2) if awake else None

        elif name == 'mindful_minutes':
            total = sum(d.get('qty', 0) for d in data_points)
            result['mindful_minutes'] = int(total)

        elif name == 'dietary_water':
            total = sum(d.get('qty', 0) for d in data_points)
            result['water_ml'] = int(total)

    return result


def upsert_health_data(conn: sqlite3.Connection, data: dict) -> bool:
    """Insert or update health data for a date."""
    columns = [
        'date', 'active_energy_kcal', 'exercise_minutes', 'stand_hours',
        'step_count', 'distance_km', 'flights_climbed',
        'weight_kg', 'body_fat_percent', 'vo2_max',
        'resting_heart_rate', 'hrv_ms',
        'sleep_hours', 'sleep_deep_hours', 'sleep_rem_hours',
        'sleep_core_hours', 'sleep_awake_hours',
        'mindful_minutes', 'water_ml',
        'source_file', 'file_modified', 'synced_at', 'is_complete'
    ]

    # Add sync timestamp
    data['synced_at'] = datetime.now().isoformat()

    # Check if this is a complete day (after midnight of the next day)
    try:
        data_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        today = datetime.now().date()
        data['is_complete'] = 1 if data_date < today else 0
    except:
        data['is_complete'] = 0

    # Build the upsert query
    placeholders = ', '.join(['?' for _ in columns])
    update_clause = ', '.join([f'{col} = excluded.{col}' for col in columns if col != 'date'])

    query = f"""
        INSERT INTO daily_health ({', '.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT(date) DO UPDATE SET {update_clause}
    """

    values = [data.get(col) for col in columns]

    try:
        conn.execute(query, values)
        return True
    except Exception as e:
        print(f"Error upserting data for {data.get('date')}: {e}")
        return False


def sync_data(days: int = 1) -> dict:
    """Sync health data for the last N days."""
    init_database()  # Ensure DB exists

    files = find_json_files(days)
    if not files:
        return {'success': False, 'message': 'No JSON files found', 'dates': []}

    conn = get_db_connection()
    synced_dates = []
    errors = []

    for filepath in files:
        try:
            data = parse_json_file(filepath)
            if upsert_health_data(conn, data):
                synced_dates.append(data['date'])
            else:
                errors.append(f"Failed to upsert {filepath.name}")
        except Exception as e:
            errors.append(f"Error parsing {filepath.name}: {e}")

    conn.commit()

    # Log the sync
    conn.execute("""
        INSERT INTO sync_log (synced_at, dates_synced, records_updated, notes)
        VALUES (?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        json.dumps(synced_dates),
        len(synced_dates),
        '; '.join(errors) if errors else None
    ))
    conn.commit()
    conn.close()

    return {
        'success': len(errors) == 0,
        'dates': synced_dates,
        'errors': errors,
        'message': f"Synced {len(synced_dates)} day(s)"
    }


def get_status(date: Optional[str] = None) -> dict:
    """Get health data status for a specific date or today."""
    if not DB_PATH.exists():
        return {'error': 'Database not initialized. Run: python3 health_sync.py init-db'}

    conn = get_db_connection()
    target_date = date or datetime.now().strftime('%Y-%m-%d')

    row = conn.execute(
        "SELECT * FROM daily_health WHERE date = ?",
        (target_date,)
    ).fetchone()

    if not row:
        conn.close()
        return {'date': target_date, 'data': None, 'message': 'No data for this date'}

    result = dict(row)
    conn.close()

    return {'date': target_date, 'data': result}


def get_goal_progress() -> dict:
    """Calculate progress toward goals with ring closure rates and streaks."""
    if not DB_PATH.exists():
        return {'error': 'Database not initialized'}

    conn = get_db_connection()

    # Daily goals (from config - hardcoded for now)
    daily_goals = {
        'active_energy_kcal': 410,
        'exercise_minutes': 30,
        'stand_hours': 10,
        'step_count': 5000,
        'sleep_hours': 7.5
    }

    # Get latest body fat reading
    latest = conn.execute("""
        SELECT date, body_fat_percent, weight_kg
        FROM daily_health
        WHERE body_fat_percent IS NOT NULL
        ORDER BY date DESC
        LIMIT 1
    """).fetchone()

    # Get 7-day average for daily metrics
    week_avg = conn.execute("""
        SELECT
            AVG(active_energy_kcal) as avg_energy,
            AVG(exercise_minutes) as avg_exercise,
            AVG(stand_hours) as avg_stand,
            AVG(step_count) as avg_steps,
            AVG(sleep_hours) as avg_sleep
        FROM daily_health
        WHERE date >= date('now', '-7 days')
    """).fetchone()

    # Get last 7 days of data for ring closure counts
    week_data = conn.execute("""
        SELECT date, active_energy_kcal, exercise_minutes, stand_hours, step_count, sleep_hours
        FROM daily_health
        WHERE date >= date('now', '-7 days')
        ORDER BY date DESC
    """).fetchall()

    # Get last 30 days for streak calculation
    month_data = conn.execute("""
        SELECT date, active_energy_kcal, exercise_minutes, stand_hours, step_count, sleep_hours
        FROM daily_health
        WHERE date >= date('now', '-30 days')
        ORDER BY date DESC
    """).fetchall()

    conn.close()

    # Calculate ring closure rates (days met / 7)
    closure_rates = {
        'move': 0,
        'exercise': 0,
        'stand': 0,
        'steps': 0,
        'sleep': 0
    }

    for row in week_data:
        if row['active_energy_kcal'] and row['active_energy_kcal'] >= daily_goals['active_energy_kcal']:
            closure_rates['move'] += 1
        if row['exercise_minutes'] and row['exercise_minutes'] >= daily_goals['exercise_minutes']:
            closure_rates['exercise'] += 1
        if row['stand_hours'] and row['stand_hours'] >= daily_goals['stand_hours']:
            closure_rates['stand'] += 1
        if row['step_count'] and row['step_count'] >= daily_goals['step_count']:
            closure_rates['steps'] += 1
        if row['sleep_hours'] and row['sleep_hours'] >= daily_goals['sleep_hours']:
            closure_rates['sleep'] += 1

    # Calculate current streaks (consecutive days meeting goal, most recent first)
    def calculate_streak(data: list, metric: str, goal: float) -> int:
        streak = 0
        for row in data:
            value = row[metric]
            if value and value >= goal:
                streak += 1
            else:
                break
        return streak

    streaks = {
        'move': calculate_streak(month_data, 'active_energy_kcal', daily_goals['active_energy_kcal']),
        'exercise': calculate_streak(month_data, 'exercise_minutes', daily_goals['exercise_minutes']),
        'stand': calculate_streak(month_data, 'stand_hours', daily_goals['stand_hours']),
        'steps': calculate_streak(month_data, 'step_count', daily_goals['step_count']),
        'sleep': calculate_streak(month_data, 'sleep_hours', daily_goals['sleep_hours'])
    }

    # Milestone goals with progress calculation
    milestone_goals = {
        'body_fat_percent': {'current': 25.8, 'target': 18.0, 'deadline': '2026-12-31'}
    }

    # Calculate days remaining to deadline
    try:
        deadline = datetime.strptime(milestone_goals['body_fat_percent']['deadline'], '%Y-%m-%d').date()
        today = datetime.now().date()
        days_remaining = (deadline - today).days
    except:
        days_remaining = None

    # Calculate progress percentage toward body fat goal
    bf_current = latest['body_fat_percent'] if latest else milestone_goals['body_fat_percent']['current']
    bf_start = milestone_goals['body_fat_percent']['current']  # Starting point
    bf_target = milestone_goals['body_fat_percent']['target']
    bf_progress = ((bf_start - bf_current) / (bf_start - bf_target)) * 100 if bf_start != bf_target else 0

    result = {
        'daily_averages': dict(week_avg) if week_avg else {},
        'daily_goals': daily_goals,
        'closure_rates': closure_rates,
        'streaks': streaks,
        'latest_body_fat': {
            'date': latest['date'] if latest else None,
            'value': latest['body_fat_percent'] if latest else None,
            'weight_lbs': round(latest['weight_kg'] * KG_TO_LBS, 1) if latest and latest['weight_kg'] else None
        },
        'milestone_goals': milestone_goals,
        'milestone_progress': {
            'body_fat_percent': {
                'progress_pct': round(bf_progress, 1),
                'remaining': round(bf_current - bf_target, 1) if bf_current else None,
                'days_remaining': days_remaining
            }
        }
    }

    return result


def generate_daily_note_section(date: Optional[str] = None) -> str:
    """Generate markdown for daily note Health Metrics section."""
    target_date = date or datetime.now().strftime('%Y-%m-%d')
    status = get_status(target_date)
    progress = get_goal_progress()

    if not status.get('data'):
        return """## Health Metrics

### Today's Progress

| Metric | Current | Goal | Status |
|--------|---------|------|--------|
| Move | -- kcal | 410 | ⬜ |
| Exercise | -- min | 30 | ⬜ |
| Stand | -- hrs | 10 | ⬜ |
| Steps | -- | 5,000 | ⬜ |
| Sleep | -- hrs | 7.5 | -- |

*Last synced: --*

### Long-term Progress

| Goal | Current | Target | Deadline | Trend |
|------|---------|--------|----------|-------|
| Body Fat | --% | 18% | Dec 2026 | -- |
"""

    data = status['data']
    goals = {
        'active_energy_kcal': 410,
        'exercise_minutes': 30,
        'stand_hours': 10,
        'step_count': 5000,
        'sleep_hours': 7.5
    }

    def status_icon(current, goal):
        """Return status icon for goal completion."""
        if not current:
            return "⬜"
        pct = (current / goal) * 100 if goal else 0
        if pct >= 100:
            return "✅"
        elif pct >= 75:
            return "🟩"
        elif pct >= 25:
            return "🟨"
        return "⬜"

    def format_pct(current, goal):
        """Format percentage."""
        if not current:
            return ""
        pct = int((current / goal) * 100) if goal else 0
        return f" {pct}%"

    # Today's metrics
    move = data.get('active_energy_kcal')
    exercise = data.get('exercise_minutes')
    stand = data.get('stand_hours')
    steps = data.get('step_count')
    sleep = data.get('sleep_hours')

    move_str = f"{int(move)} kcal" if move else "-- kcal"
    exercise_str = f"{int(exercise)} min" if exercise else "-- min"
    stand_str = f"{int(stand)} hrs" if stand else "-- hrs"
    steps_str = f"{int(steps):,}" if steps else "--"
    sleep_str = f"{sleep:.1f} hrs" if sleep else "-- hrs"

    # Get body fat info
    bf = progress.get('latest_body_fat', {})
    bf_value = bf.get('value')
    bf_date = bf.get('date')
    milestone_progress = progress.get('milestone_progress', {}).get('body_fat_percent', {})

    # Determine body fat trend
    bf_trend = "--"
    if bf_value:
        progress_pct = milestone_progress.get('progress_pct', 0)
        if progress_pct > 0:
            bf_trend = f"↓ {progress_pct}%"
        else:
            bf_trend = "→ Starting"

    # Build the section
    synced_time = data.get('synced_at', '')[:16].replace('T', ' ') if data.get('synced_at') else '--'
    complete_note = "" if data.get('is_complete') else " (partial)"

    lines = [
        "## Health Metrics",
        "",
        "### Today's Progress",
        "",
        "| Metric | Current | Goal | Status |",
        "|--------|---------|------|--------|",
        f"| Move | {move_str} | 410 | {status_icon(move, goals['active_energy_kcal'])}{format_pct(move, goals['active_energy_kcal'])} |",
        f"| Exercise | {exercise_str} | 30 | {status_icon(exercise, goals['exercise_minutes'])}{format_pct(exercise, goals['exercise_minutes'])} |",
        f"| Stand | {stand_str} | 10 | {status_icon(stand, goals['stand_hours'])}{format_pct(stand, goals['stand_hours'])} |",
        f"| Steps | {steps_str} | 5,000 | {status_icon(steps, goals['step_count'])}{format_pct(steps, goals['step_count'])} |",
        f"| Sleep | {sleep_str} | 7.5 | {status_icon(sleep, goals['sleep_hours']) if sleep else '--'} |",
        "",
        f"*Last synced: {synced_time}{complete_note}*",
        "",
        "### Long-term Progress",
        "",
        "| Goal | Current | Target | Deadline | Trend |",
        "|------|---------|--------|----------|-------|",
        f"| Body Fat | {bf_value}% | 18% | Dec 2026 | {bf_trend} |" if bf_value else "| Body Fat | --% | 18% | Dec 2026 | -- |",
    ]

    return "\n".join(lines)


def export_to_csv(output_path: Optional[str] = None):
    """Export health data to CSV."""
    if not DB_PATH.exists():
        print("Error: Database not initialized")
        return

    import csv

    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM daily_health ORDER BY date DESC").fetchall()
    conn.close()

    if not rows:
        print("No data to export")
        return

    output = output_path or str(VAULT_ROOT / ".claude" / "data" / "health_export.csv")

    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(row)

    print(f"Exported {len(rows)} records to: {output}")


def format_status_compact(status: dict) -> str:
    """Format status as a compact one-liner for session context."""
    if 'error' in status:
        return f"Error: {status['error']}"

    if not status.get('data'):
        return "No health data available"

    data = status['data']
    date = status['date']

    # Daily goals for comparison
    goals = {
        'active_energy_kcal': 410,
        'exercise_minutes': 30,
        'stand_hours': 10,
        'step_count': 5000,
        'sleep_hours': 7.5
    }

    def ring_icon(current, goal):
        """Return status icon for ring completion."""
        if not current:
            return "⬜"
        pct = (current / goal) * 100 if goal else 0
        if pct >= 100:
            return "✅"
        elif pct >= 75:
            return "🟩"
        elif pct >= 25:
            return "🟨"
        return "⬜"

    # Build compact summary
    move_icon = ring_icon(data.get('active_energy_kcal'), goals['active_energy_kcal'])
    exercise_icon = ring_icon(data.get('exercise_minutes'), goals['exercise_minutes'])
    stand_icon = ring_icon(data.get('stand_hours'), goals['stand_hours'])

    parts = [f"Move {move_icon}", f"Exercise {exercise_icon}", f"Stand {stand_icon}"]

    if data.get('sleep_hours'):
        sleep_icon = ring_icon(data.get('sleep_hours'), goals['sleep_hours'])
        parts.append(f"Sleep {data.get('sleep_hours'):.1f}h {sleep_icon}")

    return f"{date}: " + " | ".join(parts)


def format_status_output(status: dict) -> str:
    """Format status output for display."""
    if 'error' in status:
        return f"Error: {status['error']}"

    if not status.get('data'):
        return f"No data for {status['date']}"

    data = status['data']
    date = status['date']

    # Daily goals for comparison
    goals = {
        'active_energy_kcal': 410,
        'exercise_minutes': 30,
        'stand_hours': 10,
        'step_count': 5000,
        'sleep_hours': 7.5
    }

    def progress_bar(current, goal):
        if not current or not goal:
            return "---"
        pct = min(100, int((current / goal) * 100))
        if pct >= 100:
            return f"[{'=' * 10}] {pct}%"
        filled = pct // 10
        return f"[{'=' * filled}{' ' * (10 - filled)}] {pct}%"

    def ring_status(current, goal, unit=""):
        if not current:
            return f"---{' ' + unit if unit else ''}"
        pct = (current / goal) * 100 if goal else 0
        current_display = int(current) if current == int(current) else round(current, 1)
        if pct >= 100:
            return f"{current_display}/{goal} ✓{' ' + unit if unit else ''}"
        return f"{current_display}/{goal} ({int(pct)}%){' ' + unit if unit else ''}"

    lines = [
        f"Health Data for {date}",
        "=" * 40,
        "",
        "FITNESS RINGS",
        f"  Move:     {ring_status(data.get('active_energy_kcal'), goals['active_energy_kcal'], 'kcal')}",
        f"  Exercise: {ring_status(data.get('exercise_minutes'), goals['exercise_minutes'], 'min')}",
        f"  Stand:    {ring_status(data.get('stand_hours'), goals['stand_hours'], 'hrs')}",
        "",
        "ACTIVITY",
        f"  Steps:    {data.get('step_count'):,}" + (f" / {goals['step_count']:,}" if data.get('step_count') else "") if data.get('step_count') else "  Steps:    ---",
        f"  Distance: {round(data.get('distance_km', 0) * KM_TO_MILES, 1) if data.get('distance_km') else '---'} mi",
        f"  Flights:  {data.get('flights_climbed') or '---'}",
        "",
        "RECOVERY",
        f"  Sleep:    {data.get('sleep_hours') or '---'} hrs",
        f"  RHR:      {data.get('resting_heart_rate') or '---'} bpm",
        f"  HRV:      {data.get('hrv_ms') or '---'} ms",
        "",
    ]

    if data.get('body_fat_percent') or data.get('weight_kg'):
        lines.extend([
            "BODY COMPOSITION",
            f"  Weight:   {round(data['weight_kg'] * KG_TO_LBS, 1) if data.get('weight_kg') else '---'} lbs",
            f"  Body Fat: {data.get('body_fat_percent') or '---'}%",
            "",
        ])

    complete = "Yes" if data.get('is_complete') else "No (partial)"
    lines.extend([
        f"Data complete: {complete}",
        f"Last synced: {data.get('synced_at', 'Unknown')[:19]}",
    ])

    return "\n".join(lines)


def format_goals_output(progress: dict) -> str:
    """Format goal progress for display."""
    if 'error' in progress:
        return f"Error: {progress['error']}"

    goals = progress.get('daily_goals', {})
    avgs = progress.get('daily_averages', {})
    closure = progress.get('closure_rates', {})
    streaks = progress.get('streaks', {})
    bf = progress.get('latest_body_fat', {})
    milestone_progress = progress.get('milestone_progress', {}).get('body_fat_percent', {})

    def trend_icon(avg, goal):
        """Return trend icon comparing average to goal."""
        if not avg or not goal:
            return "---"
        pct = (avg / goal) * 100
        if pct >= 100:
            return "✅ Exceeding"
        elif pct >= 90:
            return "🟩 On track"
        elif pct >= 75:
            return "🟨 Close"
        else:
            return "⚠️ Below"

    def streak_display(streak):
        """Format streak with fire emoji for notable streaks."""
        if streak >= 7:
            return f"🔥 {streak} days"
        elif streak >= 3:
            return f"✨ {streak} days"
        elif streak > 0:
            return f"{streak} days"
        else:
            return "0 days"

    lines = [
        "Goal Progress Report",
        "=" * 50,
        "",
        "DAILY GOALS - 7-Day Performance",
        "-" * 50,
        "",
        "| Metric     | Avg      | Goal   | Trend        | Days Met | Streak     |",
        "|------------|----------|--------|--------------|----------|------------|",
    ]

    # Move
    move_avg = avgs.get('avg_energy')
    move_goal = goals.get('active_energy_kcal', 410)
    lines.append(f"| Move       | {int(move_avg) if move_avg else '---':>6} kcal | {move_goal:>4} kcal | {trend_icon(move_avg, move_goal):<12} | {closure.get('move', 0)}/7      | {streak_display(streaks.get('move', 0)):<10} |")

    # Exercise
    ex_avg = avgs.get('avg_exercise')
    ex_goal = goals.get('exercise_minutes', 30)
    lines.append(f"| Exercise   | {int(ex_avg) if ex_avg else '---':>6} min  | {ex_goal:>4} min  | {trend_icon(ex_avg, ex_goal):<12} | {closure.get('exercise', 0)}/7      | {streak_display(streaks.get('exercise', 0)):<10} |")

    # Stand
    st_avg = avgs.get('avg_stand')
    st_goal = goals.get('stand_hours', 10)
    lines.append(f"| Stand      | {int(st_avg) if st_avg else '---':>6} hrs  | {st_goal:>4} hrs  | {trend_icon(st_avg, st_goal):<12} | {closure.get('stand', 0)}/7      | {streak_display(streaks.get('stand', 0)):<10} |")

    # Steps
    steps_avg = avgs.get('avg_steps')
    steps_goal = goals.get('step_count', 5000)
    lines.append(f"| Steps      | {int(steps_avg) if steps_avg else '---':>6}     | {steps_goal:>5}   | {trend_icon(steps_avg, steps_goal):<12} | {closure.get('steps', 0)}/7      | {streak_display(streaks.get('steps', 0)):<10} |")

    # Sleep
    sleep_avg = avgs.get('avg_sleep')
    sleep_goal = goals.get('sleep_hours', 7.5)
    sleep_avg_str = f"{sleep_avg:.1f}" if sleep_avg else "---"
    lines.append(f"| Sleep      | {sleep_avg_str:>6} hrs  | {sleep_goal:>4} hrs  | {trend_icon(sleep_avg, sleep_goal):<12} | {closure.get('sleep', 0)}/7      | {streak_display(streaks.get('sleep', 0)):<10} |")

    lines.extend([
        "",
        "",
        "MILESTONE GOALS",
        "-" * 50,
    ])

    if bf.get('value'):
        remaining = milestone_progress.get('remaining', 0)
        days_left = milestone_progress.get('days_remaining', 0)
        progress_pct = milestone_progress.get('progress_pct', 0)

        lines.extend([
            "",
            f"Body Fat: {bf.get('value')}% → 18.0% by Dec 31, 2026",
            f"  Current: {bf.get('value')}% (measured {bf.get('date')})",
            f"  Weight:  {bf.get('weight_lbs')} lbs",
            f"  Remaining: {remaining}% to lose",
            f"  Progress: {progress_pct}%",
            f"  Days left: {days_left}",
            "",
        ])

        # Progress bar
        bar_len = 30
        filled = int((progress_pct / 100) * bar_len) if progress_pct > 0 else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        lines.append(f"  [{bar}] {progress_pct}%")
    else:
        lines.append("\n  No body composition data available")

    lines.extend([
        "",
        "",
        "INSIGHTS",
        "-" * 50,
    ])

    # Generate coaching insights
    insights = []

    # Sleep insight
    if sleep_avg and sleep_avg < 7:
        debt = (7.5 - sleep_avg) * 7
        insights.append(f"⚠️ Sleep debt: ~{debt:.0f} hours below target this week")
    elif sleep_avg and sleep_avg >= 7.5:
        insights.append(f"✅ Sleep is on target - great foundation!")

    # Ring closure insight
    all_rings = closure.get('move', 0) + closure.get('exercise', 0) + closure.get('stand', 0)
    if all_rings == 21:
        insights.append("🏆 Perfect week! All rings closed every day!")
    elif all_rings >= 18:
        insights.append("🌟 Strong week - most rings closed")
    elif all_rings < 10:
        insights.append("💪 Room for improvement - focus on consistency")

    # Streak insight
    max_streak = max(streaks.values()) if streaks else 0
    if max_streak >= 7:
        streak_name = [k for k, v in streaks.items() if v == max_streak][0]
        insights.append(f"🔥 {max_streak}-day {streak_name} streak! Keep it going!")

    if not insights:
        insights.append("Keep tracking to build trends and insights")

    for insight in insights:
        lines.append(f"  • {insight}")

    return "\n".join(lines)


def generate_coaching_prompts(context: str = "general") -> str:
    """Generate coaching prompts based on health data and context.

    Args:
        context: One of 'morning', 'evening', 'weekly', or 'general'

    Returns:
        String with relevant coaching prompts
    """
    if not DB_PATH.exists():
        return "No health data available for coaching insights."

    progress = get_goal_progress()
    yesterday_status = get_status()

    prompts = []
    avgs = progress.get('averages', {})
    closure = progress.get('closure_rates', {})
    streaks = progress.get('streaks', {})
    yesterday = yesterday_status.get('data', {})

    goals = {
        'sleep_hours': 7.5,
        'active_energy_kcal': 410,
        'exercise_minutes': 30,
        'stand_hours': 10,
    }

    # --- SLEEP-RELATED PROMPTS ---
    sleep_yesterday = yesterday.get('sleep_hours')
    sleep_avg = avgs.get('avg_sleep')

    if context in ['morning', 'general']:
        if sleep_yesterday and sleep_yesterday < 6:
            prompts.append(f"⚠️ SLEEP ALERT: You got {sleep_yesterday:.1f} hours last night. How will you protect rest tonight? Consider fewer A-priorities today.")
        elif sleep_yesterday and sleep_yesterday < 7:
            prompts.append(f"💤 Sleep was under target ({sleep_yesterday:.1f} hrs). Physical energy may be affected.")

        if sleep_avg and sleep_avg < 7:
            debt = (7.5 - sleep_avg) * 7
            prompts.append(f"📉 7-day sleep average: {sleep_avg:.1f} hrs (vs 7.5 target). Sleep debt is ~{debt:.0f} hours. This affects everything—energy, focus, mood.")

    if context in ['evening', 'general']:
        if sleep_yesterday and sleep_yesterday < 6:
            prompts.append("Tonight is critical for recovery. Consider: no screens 1 hour before bed, cool room, consistent bedtime.")

    # --- RING-RELATED PROMPTS ---
    move_yesterday = yesterday.get('active_energy_kcal')
    exercise_yesterday = yesterday.get('exercise_minutes')
    stand_yesterday = yesterday.get('stand_hours')

    # Count how many rings were closed yesterday
    rings_closed = 0
    if move_yesterday and move_yesterday >= goals['active_energy_kcal']:
        rings_closed += 1
    if exercise_yesterday and exercise_yesterday >= goals['exercise_minutes']:
        rings_closed += 1
    if stand_yesterday and stand_yesterday >= goals['stand_hours']:
        rings_closed += 1

    if context in ['morning', 'general']:
        if rings_closed == 0:
            prompts.append("⚠️ All three rings missed yesterday. What happened? Any blockers?")
        elif rings_closed == 3:
            prompts.append("✅ Great work closing all rings yesterday! Keep the momentum.")

        # Streak alerts
        for metric, streak in streaks.items():
            if streak == 0 and closure.get(metric, 0) >= 3:
                prompts.append(f"⚡ Your {metric} streak just reset. You were at {closure.get(metric, 0)+1} days. What got in the way?")

    if context in ['evening', 'general']:
        # Check today's progress if available
        today_status = get_status(datetime.now().strftime('%Y-%m-%d'))
        today = today_status.get('data', {})

        move_today = today.get('active_energy_kcal', 0) or 0
        exercise_today = today.get('exercise_minutes', 0) or 0
        stand_today = today.get('stand_hours', 0) or 0

        missing_rings = []
        if move_today < goals['active_energy_kcal']:
            pct = int((move_today / goals['active_energy_kcal']) * 100)
            missing_rings.append(f"Move ({pct}%)")
        if exercise_today < goals['exercise_minutes']:
            pct = int((exercise_today / goals['exercise_minutes']) * 100)
            missing_rings.append(f"Exercise ({pct}%)")
        if stand_today < goals['stand_hours']:
            pct = int((stand_today / goals['stand_hours']) * 100)
            missing_rings.append(f"Stand ({pct}%)")

        if missing_rings:
            prompts.append(f"🎯 Rings not yet closed: {', '.join(missing_rings)}. Any intention to complete before bed?")
        else:
            prompts.append("🏆 All rings closed today! That's consistent action.")

    # --- STREAK CELEBRATION ---
    if context in ['morning', 'weekly', 'general']:
        max_streak = max(streaks.values()) if streaks else 0
        if max_streak >= 7:
            streak_name = [k for k, v in streaks.items() if v == max_streak][0]
            prompts.append(f"🔥 {max_streak}-day {streak_name} streak! Keep it going!")

    # --- WEEKLY PATTERNS ---
    if context in ['weekly', 'general']:
        all_rings = closure.get('move', 0) + closure.get('exercise', 0) + closure.get('stand', 0)
        if all_rings == 21:
            prompts.append("🏆 Perfect week! All rings closed every day!")
        elif all_rings >= 18:
            prompts.append("🌟 Strong week - closed most rings")
        elif all_rings < 10:
            prompts.append("💪 Room for improvement this week. What's blocking consistency?")

        if sleep_avg and sleep_avg < 7:
            prompts.append(f"📊 Weekly sleep pattern: {sleep_avg:.1f} hrs average. Consider what's preventing consistent rest.")

    # --- BODY COMPOSITION ---
    milestone = progress.get('milestone_progress', {})
    if context in ['weekly', 'general'] and milestone:
        progress_pct = milestone.get('progress_pct', 0)
        if milestone.get('weeks_stalled', 0) >= 4:
            prompts.append("📈 Body composition progress has stalled (4+ weeks). Time to review nutrition or training?")
        elif progress_pct >= 50:
            prompts.append(f"💪 Body composition: {progress_pct}% toward goal. Keep the momentum!")

    # --- FORMAT OUTPUT ---
    if not prompts:
        return "✅ Health metrics look good. Keep up the consistent effort!"

    output_lines = ["HEALTH COACHING INSIGHTS", "=" * 40, ""]
    for prompt in prompts:
        output_lines.append(f"  • {prompt}")
        output_lines.append("")

    return "\n".join(output_lines)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Health Sync - Manage health data")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # init-db
    subparsers.add_parser('init-db', help='Initialize database')

    # sync
    sync_parser = subparsers.add_parser('sync', help='Sync health data')
    sync_parser.add_argument('--days', type=int, default=1, help='Days to sync')

    # status
    status_parser = subparsers.add_parser('status', help='Show health status')
    status_parser.add_argument('--date', help='Date (YYYY-MM-DD)')
    status_parser.add_argument('--json', action='store_true', help='Output as JSON')
    status_parser.add_argument('--format', choices=['full', 'compact'], default='full',
                               help='Output format (full or compact)')

    # goals
    goals_parser = subparsers.add_parser('goals', help='Show goal progress')
    goals_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # export-csv
    export_parser = subparsers.add_parser('export-csv', help='Export to CSV')
    export_parser.add_argument('--output', help='Output file path')

    # daily-note-section
    daily_note_parser = subparsers.add_parser('daily-note-section', help='Generate Health section for daily note')
    daily_note_parser.add_argument('--date', help='Date (YYYY-MM-DD)')

    # coaching
    coaching_parser = subparsers.add_parser('coaching', help='Generate coaching prompts based on health data')
    coaching_parser.add_argument('--context', choices=['morning', 'evening', 'weekly', 'general'],
                                  default='general', help='Context for coaching prompts')

    args = parser.parse_args()

    if args.command == 'init-db':
        init_database()

    elif args.command == 'sync':
        result = sync_data(args.days)
        if result.get('errors'):
            for error in result['errors']:
                print(f"Warning: {error}")
        print(result['message'])
        if result['dates']:
            print(f"Dates synced: {', '.join(result['dates'])}")

    elif args.command == 'status':
        status = get_status(args.date)
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        elif args.format == 'compact':
            print(format_status_compact(status))
        else:
            print(format_status_output(status))

    elif args.command == 'goals':
        progress = get_goal_progress()
        if args.json:
            print(json.dumps(progress, indent=2, default=str))
        else:
            print(format_goals_output(progress))

    elif args.command == 'export-csv':
        export_to_csv(args.output)

    elif args.command == 'daily-note-section':
        print(generate_daily_note_section(args.date))

    elif args.command == 'coaching':
        print(generate_coaching_prompts(args.context))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
