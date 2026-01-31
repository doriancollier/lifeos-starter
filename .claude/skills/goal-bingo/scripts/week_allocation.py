#!/usr/bin/env python3
"""
Continuous Chain Method for Bingo Week Allocation

Algorithm:
1. January 2026 starts on the Monday closest to January 1st
   - If Jan 1 is Mon-Thu: use previous Monday
   - If Jan 1 is Fri-Sun: use next Monday
2. Each subsequent month starts on the Monday after the previous month's last Sunday
3. Each month continues until it has covered enough weeks to include most of the month's days

This creates a continuous chain of weeks with no gaps or overlaps.
"""

from datetime import date, timedelta
from calendar import monthrange
from typing import NamedTuple


class MonthAllocation(NamedTuple):
    """Represents a month's bingo week allocation."""
    month_name: str
    month_num: int
    start_monday: date
    end_sunday: date
    num_weeks: int
    distance_from_first: int  # Positive = after 1st, negative = before


def get_weekday_name(d: date) -> str:
    """Return the weekday name for a date."""
    return d.strftime("%A")


def find_closest_monday_to_jan1(year: int) -> date:
    """
    Find the Monday closest to January 1st using the rule:
    - If Jan 1 is Mon-Thu: use previous Monday
    - If Jan 1 is Fri-Sun: use next Monday
    """
    jan1 = date(year, 1, 1)
    weekday = jan1.weekday()  # 0=Monday, 6=Sunday

    if weekday <= 3:  # Mon-Thu (0-3): use previous Monday
        days_back = weekday
        return jan1 - timedelta(days=days_back)
    else:  # Fri-Sun (4-6): use next Monday
        days_forward = 7 - weekday
        return jan1 + timedelta(days=days_forward)


def calculate_weeks_for_month(start_monday: date, month: int, year: int) -> tuple[date, int]:
    """
    Calculate how many weeks a month should have and return the end Sunday.

    A month needs enough weeks to include most of the month's days.
    We count how many days of the calendar month fall within each bingo week,
    and stop when we've covered most of the month.
    """
    _, days_in_month = monthrange(year, month)
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)

    current_monday = start_monday
    weeks = 0
    days_covered = 0

    while True:
        week_end = current_monday + timedelta(days=6)  # Sunday
        weeks += 1

        # Count days in this week that belong to the calendar month
        for i in range(7):
            day = current_monday + timedelta(days=i)
            if month_start <= day <= month_end:
                days_covered += 1

        # Check if we should stop
        # We need to include the week that contains the majority of remaining days
        # Rule: Continue until the next Monday is past the middle of the next month
        # OR we've covered at least half the month's days

        next_monday = current_monday + timedelta(days=7)

        # Stop if:
        # 1. We've covered at least half the month AND
        # 2. The next Monday is in the next month or very late in current month
        if days_covered >= days_in_month // 2:
            # Check if next week would primarily belong to next month
            next_week_in_month = 0
            for i in range(7):
                day = next_monday + timedelta(days=i)
                if month_start <= day <= month_end:
                    next_week_in_month += 1

            # If next week has 3 or fewer days in our month, stop here
            if next_week_in_month <= 3:
                break

        current_monday = next_monday

    end_sunday = current_monday + timedelta(days=6)
    return end_sunday, weeks


def calculate_continuous_chain(year: int) -> list[MonthAllocation]:
    """Calculate the continuous chain allocation for all 12 months."""
    allocations = []

    # January starts on the Monday closest to Jan 1
    current_monday = find_closest_monday_to_jan1(year)

    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    for month in range(1, 13):
        end_sunday, num_weeks = calculate_weeks_for_month(current_monday, month, year)

        # Calculate distance from 1st of the month
        first_of_month = date(year, month, 1)
        distance = (current_monday - first_of_month).days

        allocation = MonthAllocation(
            month_name=month_names[month - 1],
            month_num=month,
            start_monday=current_monday,
            end_sunday=end_sunday,
            num_weeks=num_weeks,
            distance_from_first=distance
        )
        allocations.append(allocation)

        # Next month starts on the Monday after this month's end Sunday
        current_monday = end_sunday + timedelta(days=1)

    return allocations


def check_coverage(allocations: list[MonthAllocation], year: int) -> dict:
    """Check for gaps, overlaps, and total coverage."""
    results = {
        "total_weeks": sum(a.num_weeks for a in allocations),
        "gaps": [],
        "overlaps": [],
        "first_monday": allocations[0].start_monday,
        "last_sunday": allocations[-1].end_sunday,
    }

    # Check for gaps/overlaps between consecutive months
    for i in range(len(allocations) - 1):
        current_end = allocations[i].end_sunday
        next_start = allocations[i + 1].start_monday
        expected_next = current_end + timedelta(days=1)

        if next_start != expected_next:
            if next_start > expected_next:
                gap_days = (next_start - expected_next).days
                results["gaps"].append({
                    "after": allocations[i].month_name,
                    "before": allocations[i + 1].month_name,
                    "gap_days": gap_days
                })
            else:
                overlap_days = (expected_next - next_start).days
                results["overlaps"].append({
                    "months": f"{allocations[i].month_name} and {allocations[i + 1].month_name}",
                    "overlap_days": overlap_days
                })

    # Check if we cover roughly the whole year
    # Year should have 52 or 53 weeks
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)

    results["year_start_offset"] = (results["first_monday"] - year_start).days
    results["year_end_offset"] = (results["last_sunday"] - year_end).days

    return results


def print_results(allocations: list[MonthAllocation], coverage: dict, year: int):
    """Print formatted results."""
    print(f"\n{'=' * 90}")
    print(f"CONTINUOUS CHAIN METHOD - BINGO WEEK ALLOCATION {year}")
    print(f"{'=' * 90}\n")

    # Header
    print(f"{'Month':<12} {'Start Monday':<14} {'End Sunday':<14} {'Weeks':>5} {'Distance from 1st':>18}")
    print(f"{'-' * 12} {'-' * 14} {'-' * 14} {'-' * 5} {'-' * 18}")

    # Month rows
    for a in allocations:
        sign = "+" if a.distance_from_first >= 0 else ""
        print(f"{a.month_name:<12} {a.start_monday.strftime('%Y-%m-%d'):<14} {a.end_sunday.strftime('%Y-%m-%d'):<14} {a.num_weeks:>5} {sign}{a.distance_from_first:>17} days")

    print(f"\n{'=' * 90}")
    print("SUMMARY")
    print(f"{'=' * 90}\n")

    # Total weeks
    print(f"Total weeks covered: {coverage['total_weeks']}")
    print(f"Expected weeks in year: 52 (or 53 for leap year week boundaries)")

    # Coverage period
    print(f"\nCoverage period:")
    print(f"  First Monday: {coverage['first_monday'].strftime('%Y-%m-%d')} ({coverage['year_start_offset']:+d} days from Jan 1)")
    print(f"  Last Sunday:  {coverage['last_sunday'].strftime('%Y-%m-%d')} ({coverage['year_end_offset']:+d} days from Dec 31)")

    # Gaps and overlaps
    if coverage["gaps"]:
        print(f"\nGaps found: {len(coverage['gaps'])}")
        for gap in coverage["gaps"]:
            print(f"  - {gap['gap_days']} day gap between {gap['after']} and {gap['before']}")
    else:
        print(f"\nGaps found: None (continuous chain)")

    if coverage["overlaps"]:
        print(f"\nOverlaps found: {len(coverage['overlaps'])}")
        for overlap in coverage["overlaps"]:
            print(f"  - {overlap['overlap_days']} day overlap between {overlap['months']}")
    else:
        print(f"Overlaps found: None (no duplicate weeks)")

    # Distance statistics
    distances = [a.distance_from_first for a in allocations]
    print(f"\nDistance from 1st statistics:")
    print(f"  Minimum: {min(distances):+d} days")
    print(f"  Maximum: {max(distances):+d} days")
    print(f"  Average: {sum(distances) / len(distances):+.1f} days")

    # Week distribution
    week_counts = {}
    for a in allocations:
        week_counts[a.num_weeks] = week_counts.get(a.num_weeks, 0) + 1

    print(f"\nWeek distribution:")
    for weeks, count in sorted(week_counts.items()):
        print(f"  {weeks}-week months: {count}")

    # Verify Jan 1 rule
    jan1 = date(year, 1, 1)
    jan1_weekday = jan1.weekday()
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    print(f"\nJanuary 1st, {year} falls on: {weekday_names[jan1_weekday]}")
    if jan1_weekday <= 3:
        print(f"  Rule applied: Jan 1 is Mon-Thu, so use previous Monday")
    else:
        print(f"  Rule applied: Jan 1 is Fri-Sun, so use next Monday")
    print(f"  Selected start: {allocations[0].start_monday.strftime('%Y-%m-%d')}")


def get_month_allocation(year: int, month: int) -> MonthAllocation:
    """Get allocation for a specific month."""
    allocations = calculate_continuous_chain(year)
    return allocations[month - 1]


def output_json(allocation: MonthAllocation):
    """Output allocation as JSON."""
    import json

    # Build list of all days in the allocation
    days = []
    current = allocation.start_monday
    while current <= allocation.end_sunday:
        days.append({
            "date": current.strftime("%Y-%m-%d"),
            "day": current.day,
            "month": current.month,
            "year": current.year,
            "weekday": current.weekday(),  # 0=Mon, 6=Sun
            "is_weekend": current.weekday() >= 5,
            "is_sunday": current.weekday() == 6,
            "in_target_month": current.month == allocation.month_num or (
                # Handle year boundary for December/January
                (allocation.month_num == 1 and current.month == 12) or
                (allocation.month_num == 12 and current.month == 1)
            )
        })
        current += timedelta(days=1)

    # Correct in_target_month - it should only be True for days in the actual target month
    for d in days:
        d["in_target_month"] = d["month"] == allocation.month_num

    result = {
        "month_name": allocation.month_name,
        "month_num": allocation.month_num,
        "start_date": allocation.start_monday.strftime("%Y-%m-%d"),
        "end_date": allocation.end_sunday.strftime("%Y-%m-%d"),
        "num_weeks": allocation.num_weeks,
        "total_days": len(days),
        "days": days
    }

    print(json.dumps(result, indent=2))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Calculate week allocation for bingo/habit tracking")
    parser.add_argument("--year", type=int, default=2026, help="Year to calculate (default: 2026)")
    parser.add_argument("--month", type=int, choices=range(1, 13), metavar="1-12",
                        help="Specific month to output (1-12)")
    parser.add_argument("--json", action="store_true", help="Output as JSON (requires --month)")

    args = parser.parse_args()

    if args.json:
        if not args.month:
            parser.error("--json requires --month")
        allocation = get_month_allocation(args.year, args.month)
        output_json(allocation)
    elif args.month:
        # Print just one month in text format
        allocation = get_month_allocation(args.year, args.month)
        print(f"{allocation.month_name} {args.year}")
        print(f"  Start: {allocation.start_monday.strftime('%Y-%m-%d')} (Monday)")
        print(f"  End:   {allocation.end_sunday.strftime('%Y-%m-%d')} (Sunday)")
        print(f"  Weeks: {allocation.num_weeks}")
    else:
        # Full year display
        allocations = calculate_continuous_chain(args.year)
        coverage = check_coverage(allocations, args.year)
        print_results(allocations, coverage, args.year)


if __name__ == "__main__":
    main()
