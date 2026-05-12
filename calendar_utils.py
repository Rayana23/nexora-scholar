from datetime import datetime, timedelta, timezone, time
from icalendar import Calendar

MY_TZ = timezone(timedelta(hours=8))


def to_gmt8(value):
    """
    Converts ICS date/datetime values into timezone-aware GMT+8 datetimes.
    Handles both timed events and all-day events.
    """
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.combine(value, time.min)

    if dt.tzinfo is None:
        return dt.replace(tzinfo=MY_TZ)

    return dt.astimezone(MY_TZ)


def parse_ics(file):
    cal = Calendar.from_ical(file.read())
    events = []

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        start_raw = component.get("dtstart").dt
        end_raw = component.get("dtend").dt if component.get("dtend") else start_raw

        start = to_gmt8(start_raw)

        if isinstance(end_raw, datetime):
            end = to_gmt8(end_raw)
        else:
            # All-day events usually have date end. Treat as blocking the full day.
            end = datetime.combine(end_raw, time.max).replace(tzinfo=MY_TZ)

        summary = str(component.get("summary", "Untitled event"))
        events.append((start, end, summary))

    return sorted(events, key=lambda x: x[0])


def get_next_monday():
    today = datetime.now(MY_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    days_until_monday = (7 - today.weekday()) % 7

    # If running on Sunday, next Monday is tomorrow.
    if days_until_monday == 0:
        days_until_monday = 7

    return today + timedelta(days=days_until_monday)


def get_monday_to_sunday_dates():
    monday = get_next_monday()
    return [monday + timedelta(days=i) for i in range(7)]


def group_events_by_date(events):
    grouped = {}

    for start, end, summary in events:
        key = start.strftime("%Y-%m-%d")
        grouped.setdefault(key, [])
        grouped[key].append((start, end, summary))

    return grouped


def compute_free_blocks_for_day(day, events_for_day, wake_hour=6, sleep_hour=23):
    """
    Creates free blocks for a day.
    Existing calendar events remain fixed. We only compute open windows around them.
    """
    day_start = day.replace(hour=wake_hour, minute=0, second=0, microsecond=0)
    day_end = day.replace(hour=sleep_hour, minute=0, second=0, microsecond=0)

    busy = []
    for start, end, summary in events_for_day:
        # Clip to planning day.
        start = max(start, day_start)
        end = min(end, day_end)

        if start < end:
            busy.append((start, end, summary))

    busy = sorted(busy, key=lambda x: x[0])

    free = []
    cursor = day_start

    for start, end, _ in busy:
        if start > cursor:
            free.append((cursor, start))
        if end > cursor:
            cursor = end

    if cursor < day_end:
        free.append((cursor, day_end))

    return free


def build_week_calendar_context(events, wake_hour=6, sleep_hour=23):
    days = get_monday_to_sunday_dates()
    grouped = group_events_by_date(events)

    lines = []

    for day in days:
        key = day.strftime("%Y-%m-%d")
        readable = day.strftime("%A, %Y-%m-%d")
        events_for_day = grouped.get(key, [])
        free_blocks = compute_free_blocks_for_day(day, events_for_day, wake_hour, sleep_hour)

        lines.append(f"\n{readable}")

        lines.append("Fixed calendar events:")
        if events_for_day:
            for start, end, summary in events_for_day:
                lines.append(f"- {start.strftime('%H:%M')}–{end.strftime('%H:%M')} | {summary}")
        else:
            lines.append("- None")

        lines.append("Available free blocks:")
        if free_blocks:
            for start, end in free_blocks:
                duration_mins = int((end - start).total_seconds() / 60)
                if duration_mins >= 20:
                    lines.append(f"- {start.strftime('%H:%M')}–{end.strftime('%H:%M')} ({duration_mins} min)")
        else:
            lines.append("- No free blocks")

    return "\n".join(lines)