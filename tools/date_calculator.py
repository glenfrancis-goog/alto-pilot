"""Deterministic Date Calculator Tool for Agentic Workflows."""

from datetime import datetime, timedelta
from typing import Dict, Any

# Standard 2026 Public Holidays (Singapore baseline for Elevate)
SG_PUBLIC_HOLIDAYS_2026 = {
    "2026-01-01": "New Year's Day",
    "2026-02-17": "Chinese New Year",
    "2026-02-18": "Chinese New Year",
    "2026-03-20": "Hari Raya Puasa",
    "2026-04-03": "Good Friday",
    "2026-05-01": "Labour Day",
    "2026-05-31": "Vesak Day",
    "2026-06-17": "Hari Raya Haji",
    "2026-08-09": "National Day",
    "2026-08-10": "National Day (Observed)",
    "2026-11-08": "Deepavali",
    "2026-12-25": "Christmas Day"
}

def calculate_working_days(start_date: str, end_date: str, country: str = "SG") -> Dict[str, Any]:
    """
    Calculates exact business/working days between start_date and end_date (inclusive),
    strictly excluding weekend days (Saturday/Sunday) and recognized public holidays.
    Dates must be formatted as YYYY-MM-DD.
    """
    try:
        start = datetime.strptime(start_date.strip(), "%Y-%m-%d")
        end = datetime.strptime(end_date.strip(), "%Y-%m-%d")
    except ValueError as e:
        return {"error": f"Invalid date format: {e}. Use YYYY-MM-DD."}

    if start > end:
        return {"error": f"start_date ({start_date}) cannot be after end_date ({end_date})."}

    cur = start
    working_days = 0
    weekend_days = 0
    holiday_days = 0
    holidays_encountered = []

    while cur <= end:
        iso_str = cur.strftime("%Y-%m-%d")
        is_weekend = cur.weekday() >= 5
        is_holiday = iso_str in SG_PUBLIC_HOLIDAYS_2026

        if is_weekend:
            weekend_days += 1
        elif is_holiday:
            holiday_days += 1
            holidays_encountered.append(f"{iso_str} ({SG_PUBLIC_HOLIDAYS_2026[iso_str]})")
        else:
            working_days += 1
        cur += timedelta(days=1)

    total_calendar_days = (end - start).days + 1

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_calendar_days": total_calendar_days,
        "working_days": working_days,
        "weekend_days": weekend_days,
        "holiday_days": holiday_days,
        "holidays_encountered": holidays_encountered
    }

def calculate_calendar_days(start_date: str, end_date: str) -> int:
    """Calculates total continuous calendar days inclusive between two dates."""
    start = datetime.strptime(start_date.strip(), "%Y-%m-%d")
    end = datetime.strptime(end_date.strip(), "%Y-%m-%d")
    return (end - start).days + 1
