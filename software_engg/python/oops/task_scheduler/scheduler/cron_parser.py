"""
cron_parser.py — Full cron expression parser.

Field order (6-field extended cron):
    second  minute  hour  day-of-month  month  day-of-week

Supported syntax per field:
    *           → every value
    ?           → any value (alias for * in day-of-month / day-of-week)
    n           → exact value
    n-m         → range (inclusive)
    */s         → every s-th value
    n-m/s       → every s-th value in range
    a,b,c       → list / comma-separated
    Named months: JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC
    Named days  : MON TUE WED THU FRI SAT SUN

Special alias strings (replace entire expression):
    @yearly / @annually   → 0 0 0 1 1 *
    @monthly              → 0 0 0 1 * *
    @weekly               → 0 0 0 * * 0
    @daily / @midnight    → 0 0 0 * * *
    @hourly               → 0 0 * * * *
    @every_minute         → 0 * * * * *
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Set

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIELD_NAMES = ("second", "minute", "hour", "day", "month", "weekday")

FIELD_RANGES = {
    "second" : (0, 59),
    "minute" : (0, 59),
    "hour"   : (0, 23),
    "day"    : (1, 31),
    "month"  : (1, 12),
    "weekday": (0, 6),   # 0 = Sunday, 6 = Saturday
}

MONTH_NAMES = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
    "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
    "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

DAY_NAMES = {
    "SUN": 0, "MON": 1, "TUE": 2, "WED": 3,
    "THU": 4, "FRI": 5, "SAT": 6,
}

ALIASES = {
    "@yearly"    : "0 0 0 1 1 *",
    "@annually"  : "0 0 0 1 1 *",
    "@monthly"   : "0 0 0 1 * *",
    "@weekly"    : "0 0 0 * * 0",
    "@daily"     : "0 0 0 * * *",
    "@midnight"  : "0 0 0 * * *",
    "@hourly"    : "0 0 * * * *",
    "@every_minute": "0 * * * * *",
}


class CronParser:
    """Parse a cron expression and calculate the next run time."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def validate(cls, expression: str) -> None:
        """Raise ValueError if *expression* is not a valid cron string."""
        expression = cls._resolve_alias(expression)
        parts = expression.split()
        if len(parts) != 6:
            raise ValueError(
                f"Cron expression must have 6 fields, got {len(parts)}: '{expression}'"
            )
        for field, part in zip(FIELD_NAMES, parts):
            cls._parse_field(part, field)  # raises if invalid

    @classmethod
    def get_next_run(cls, expression: str, after: datetime) -> datetime:
        """Return the first datetime after *after* that satisfies *expression*."""
        expression = cls._resolve_alias(expression)
        parts = expression.split()
        if len(parts) != 6:
            raise ValueError(f"Expected 6 cron fields, got {len(parts)}")

        seconds  = cls._parse_field(parts[0], "second")
        minutes  = cls._parse_field(parts[1], "minute")
        hours    = cls._parse_field(parts[2], "hour")
        days     = cls._parse_field(parts[3], "day")
        months   = cls._parse_field(parts[4], "month")
        weekdays = cls._parse_field(parts[5], "weekday")

        # Start searching from the next second
        candidate = after.replace(microsecond=0)
        from datetime import timedelta
        candidate += timedelta(seconds=1)

        # Safety cap: search up to 4 years ahead
        limit = after.replace(year=after.year + 4)

        while candidate < limit:
            if candidate.month not in months:
                # Jump to the first valid month
                candidate = cls._advance_month(candidate, months)
                continue

            if candidate.day not in days or candidate.weekday() not in cls._iso_to_cron_days(weekdays):
                candidate = cls._advance_day(candidate, days, weekdays)
                continue

            if candidate.hour not in hours:
                candidate = cls._advance_hour(candidate, hours)
                continue

            if candidate.minute not in minutes:
                candidate = cls._advance_minute(candidate, minutes)
                continue

            if candidate.second not in seconds:
                candidate = cls._advance_second(candidate, seconds)
                continue

            return candidate  # ✓ all fields match

        raise RuntimeError(f"Could not find next run time for expression: '{expression}'")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _resolve_alias(cls, expression: str) -> str:
        return ALIASES.get(expression.lower(), expression)

    @classmethod
    def _parse_field(cls, token: str, field: str) -> Set[int]:
        """Parse one cron field token and return the set of matching integers."""
        lo, hi = FIELD_RANGES[field]
        name_map = MONTH_NAMES if field == "month" else (DAY_NAMES if field == "weekday" else {})

        result: Set[int] = set()
        for part in token.split(","):
            part = part.strip()
            if part in ("*", "?"):
                result.update(range(lo, hi + 1))
            elif "/" in part:
                base, step_s = part.split("/", 1)
                step = cls._to_int(step_s, field, name_map)
                if step <= 0:
                    raise ValueError(f"Step must be > 0 in field '{field}': '{part}'")
                if base in ("*", "?"):
                    base_vals = list(range(lo, hi + 1))
                elif "-" in base:
                    a, b = base.split("-", 1)
                    a, b = cls._to_int(a, field, name_map), cls._to_int(b, field, name_map)
                    base_vals = list(range(a, b + 1))
                else:
                    start = cls._to_int(base, field, name_map)
                    base_vals = list(range(start, hi + 1))
                result.update(base_vals[::step])
            elif "-" in part:
                a, b = part.split("-", 1)
                a, b = cls._to_int(a, field, name_map), cls._to_int(b, field, name_map)
                if a > b:
                    raise ValueError(f"Range start > end in field '{field}': '{part}'")
                result.update(range(a, b + 1))
            else:
                result.add(cls._to_int(part, field, name_map))

        # Validate all values are within allowed range
        for v in result:
            if not (lo <= v <= hi):
                raise ValueError(
                    f"Value {v} out of range [{lo},{hi}] in field '{field}'"
                )
        return result

    @staticmethod
    def _to_int(token: str, field: str, name_map: dict) -> int:
        token = token.upper()
        if token in name_map:
            return name_map[token]
        try:
            return int(token)
        except ValueError:
            raise ValueError(f"Invalid token '{token}' in field '{field}'")

    @staticmethod
    def _iso_to_cron_days(cron_days: Set[int]) -> Set[int]:
        """
        Cron weekday: 0=Sunday … 6=Saturday
        Python weekday(): 0=Monday … 6=Sunday
        Convert cron day set to Python isoweekday set.
        """
        mapping = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
        return {mapping[d] for d in cron_days}

    # ------------------------------------------------------------------
    # Advancement helpers (jump forward when a field doesn't match)
    # ------------------------------------------------------------------

    @staticmethod
    def _advance_second(dt: datetime, valid_seconds: Set[int]) -> datetime:
        from datetime import timedelta
        valid = sorted(s for s in valid_seconds if s > dt.second)
        if valid:
            return dt.replace(second=valid[0], microsecond=0)
        # Overflow to next minute
        return (dt.replace(second=0, microsecond=0) + timedelta(minutes=1))

    @staticmethod
    def _advance_minute(dt: datetime, valid_minutes: Set[int]) -> datetime:
        from datetime import timedelta
        valid = sorted(m for m in valid_minutes if m > dt.minute)
        if valid:
            return dt.replace(minute=valid[0], second=0, microsecond=0)
        return (dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))

    @staticmethod
    def _advance_hour(dt: datetime, valid_hours: Set[int]) -> datetime:
        from datetime import timedelta
        valid = sorted(h for h in valid_hours if h > dt.hour)
        if valid:
            return dt.replace(hour=valid[0], minute=0, second=0, microsecond=0)
        return (dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1))

    @staticmethod
    def _advance_day(dt: datetime, valid_days: Set[int], valid_weekdays: Set[int]) -> datetime:
        from datetime import timedelta
        cron_to_py = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
        py_weekdays = {cron_to_py[w] for w in valid_weekdays}

        candidate = dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        for _ in range(400):
            if candidate.day in valid_days and candidate.weekday() in py_weekdays:
                return candidate
            candidate += timedelta(days=1)
        raise RuntimeError("Could not advance to valid day within 400 days")

    @staticmethod
    def _advance_month(dt: datetime, valid_months: Set[int]) -> datetime:
        from datetime import timedelta
        # Move to first day of the next candidate month
        year, month = dt.year, dt.month
        for _ in range(50):
            month += 1
            if month > 12:
                month = 1
                year += 1
            if month in valid_months:
                return datetime(year, month, 1, 0, 0, 0)
        raise RuntimeError("Could not advance to valid month within 50 months")
