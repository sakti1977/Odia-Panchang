"""
Generate monthly Panchang PDF for printing and offline access.
This makes the Panchang accessible to users without internet access.
"""

from datetime import date, timedelta
from typing import Optional
import io


def generate_monthly_text(year: int, month: int, panchang_data: list) -> str:
    """
    Generate a text-based monthly Panchang suitable for PDF conversion.
    This provides a simple, printable format.

    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
        panchang_data: List of daily panchang dictionaries

    Returns:
        Formatted text string
    """
    from src.translations import CHANDRA_MASA

    # Month names in Odia and English
    month_names = {
        1: ("January", "ଜାନୁଆରୀ"),
        2: ("February", "ଫେବୃଆରୀ"),
        3: ("March", "ମାର୍ଚ୍ଚ"),
        4: ("April", "ଏପ୍ରିଲ"),
        5: ("May", "ମେ"),
        6: ("June", "ଜୁନ"),
        7: ("July", "ଜୁଲାଇ"),
        8: ("August", "ଅଗଷ୍ଟ"),
        9: ("September", "ସେପ୍ଟେମ୍ବର"),
        10: ("October", "ଅକ୍ଟୋବର"),
        11: ("November", "ନଭେମ୍ବର"),
        12: ("December", "ଡିସେମ୍ବର"),
    }

    month_en, month_or = month_names.get(month, ("", ""))

    lines = []
    lines.append("=" * 80)
    lines.append(f"ଓଡ଼ିଆ ପଞ୍ଜିକା - Odia Panchang".center(80))
    lines.append(f"{month_or} {year} - {month_en} {year}".center(80))
    lines.append("=" * 80)
    lines.append("")

    # Header
    lines.append(f"{'Date':<12} {'Vara':<15} {'Tithi':<20} {'Nakshatra':<20} {'Festivals':<30}")
    lines.append("-" * 80)

    for day_data in panchang_data:
        date_str = day_data.get("date", "")
        vara = f"{day_data.get('vara', {}).get('or', '')} / {day_data.get('vara', {}).get('en', '')}"
        tithi = f"{day_data.get('tithi', {}).get('or', '')} ({day_data.get('paksha', {}).get('or', '')})"
        nakshatra = day_data.get('nakshatra', {}).get('or', '')

        festivals = day_data.get('festivals', [])
        festival_str = ""
        if festivals:
            festival_names = [f.get('name', {}).get('or', '') for f in festivals]
            festival_str = ", ".join(festival_names[:2])  # Show max 2 festivals
            if len(festivals) > 2:
                festival_str += "..."

        lines.append(f"{date_str:<12} {vara:<15} {tithi:<20} {nakshatra:<20} {festival_str:<30}")

    lines.append("")
    lines.append("=" * 80)
    lines.append("Sunrise/Sunset times are for Puri, Odisha")
    lines.append("For other cities, please check online at the API")
    lines.append("=" * 80)

    return "\n".join(lines)


def generate_calendar_view(year: int, month: int, panchang_data: list) -> str:
    """
    Generate a calendar-style view of the month with Panchang details.

    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
        panchang_data: List of daily panchang dictionaries

    Returns:
        Formatted calendar string
    """
    import calendar

    # Create a mapping of date to panchang data
    date_map = {day_data['date']: day_data for day_data in panchang_data}

    lines = []
    lines.append("\n" + "=" * 100)
    lines.append(f"ମାସିକ ପଞ୍ଜିକା - Monthly Panchang: {month}/{year}".center(100))
    lines.append("=" * 100 + "\n")

    # Get calendar for the month
    cal = calendar.monthcalendar(year, month)

    # Day headers
    lines.append("  Mon        Tue        Wed        Thu        Fri        Sat        Sun")
    lines.append("-" * 100)

    for week in cal:
        week_line = []
        for day in week:
            if day == 0:
                week_line.append("          ")
            else:
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                if date_str in date_map:
                    day_data = date_map[date_str]
                    tithi_or = day_data.get('tithi', {}).get('or', '')[:4]
                    week_line.append(f"{day:2d} {tithi_or:<6}")
                else:
                    week_line.append(f"{day:2d}        ")
        lines.append(" ".join(week_line))

    lines.append("\n" + "=" * 100)

    # List all festivals in the month
    lines.append("\nFestivals this month:")
    lines.append("-" * 100)

    festival_dates = {}
    for day_data in panchang_data:
        festivals = day_data.get('festivals', [])
        if festivals:
            date_str = day_data.get('date', '')
            festival_dates[date_str] = festivals

    if festival_dates:
        for date_str in sorted(festival_dates.keys()):
            festivals = festival_dates[date_str]
            for fest in festivals:
                fest_name_or = fest.get('name', {}).get('or', '')
                fest_name_en = fest.get('name', {}).get('en', '')
                lines.append(f"  {date_str}: {fest_name_or} ({fest_name_en})")
    else:
        lines.append("  No major festivals this month")

    lines.append("\n" + "=" * 100)

    return "\n".join(lines)
