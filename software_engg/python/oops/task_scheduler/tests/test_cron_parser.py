"""
tests/test_cron_parser.py — Unit tests for the CronParser.
"""
import pytest
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scheduler.cron_parser import CronParser


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_valid_wildcard_expression():
    CronParser.validate("* * * * * *")


def test_valid_every_minute_alias():
    CronParser.validate("@every_minute")


def test_valid_daily_alias():
    CronParser.validate("@daily")


def test_invalid_too_few_fields():
    with pytest.raises(ValueError):
        CronParser.validate("* * * * *")  # 5 fields (standard cron), need 6


def test_invalid_out_of_range_second():
    with pytest.raises(ValueError):
        CronParser.validate("60 * * * * *")  # second > 59


def test_invalid_out_of_range_hour():
    with pytest.raises(ValueError):
        CronParser.validate("0 0 25 * * *")  # hour > 23


def test_invalid_step_zero():
    with pytest.raises(ValueError):
        CronParser.validate("*/0 * * * * *")  # step=0 is invalid


def test_invalid_range_inverted():
    with pytest.raises(ValueError):
        CronParser.validate("0 0 * * 12-1 *")  # month range inverted


def test_named_months_valid():
    CronParser.validate("0 0 0 1 JAN *")
    CronParser.validate("0 0 0 1 DEC *")


def test_named_days_valid():
    CronParser.validate("0 0 0 * * MON")
    CronParser.validate("0 0 0 * * SUN")


# ---------------------------------------------------------------------------
# Field parsing
# ---------------------------------------------------------------------------

def test_parse_list():
    result = CronParser._parse_field("1,3,5", "minute")
    assert result == {1, 3, 5}


def test_parse_range():
    result = CronParser._parse_field("1-5", "second")
    assert result == {1, 2, 3, 4, 5}


def test_parse_step():
    result = CronParser._parse_field("*/10", "second")
    assert result == {0, 10, 20, 30, 40, 50}


def test_parse_range_step():
    result = CronParser._parse_field("0-20/5", "minute")
    assert result == {0, 5, 10, 15, 20}


def test_parse_wildcard():
    result = CronParser._parse_field("*", "hour")
    assert result == set(range(0, 24))


def test_parse_question_mark():
    result = CronParser._parse_field("?", "weekday")
    assert result == set(range(0, 7))


def test_parse_named_month():
    result = CronParser._parse_field("MAR", "month")
    assert result == {3}


def test_parse_named_weekday():
    result = CronParser._parse_field("FRI", "weekday")
    assert result == {5}


# ---------------------------------------------------------------------------
# get_next_run
# ---------------------------------------------------------------------------

BASE = datetime(2025, 6, 15, 12, 30, 0)   # Sunday 12:30:00


def test_next_run_every_second():
    """Every second — next should be exactly 1 second later."""
    nxt = CronParser.get_next_run("* * * * * *", BASE)
    assert nxt == BASE.replace(second=1)


def test_next_run_every_minute():
    nxt = CronParser.get_next_run("@every_minute", BASE)
    # Next whole minute second=0 that is after BASE
    assert nxt == datetime(2025, 6, 15, 12, 31, 0)


def test_next_run_every_5_seconds():
    after = datetime(2025, 1, 1, 0, 0, 3)
    nxt   = CronParser.get_next_run("*/5 * * * * *", after)
    assert nxt == datetime(2025, 1, 1, 0, 0, 5)


def test_next_run_specific_hour():
    """Next 14:00:00 after 12:30."""
    nxt = CronParser.get_next_run("0 0 14 * * *", BASE)
    assert nxt == datetime(2025, 6, 15, 14, 0, 0)


def test_next_run_daily():
    nxt = CronParser.get_next_run("@daily", BASE)
    assert nxt == datetime(2025, 6, 16, 0, 0, 0)


def test_next_run_monthly():
    nxt = CronParser.get_next_run("@monthly", BASE)
    assert nxt == datetime(2025, 7, 1, 0, 0, 0)


def test_next_run_yearly():
    nxt = CronParser.get_next_run("@yearly", BASE)
    assert nxt == datetime(2026, 1, 1, 0, 0, 0)


def test_next_run_specific_month():
    """First second of November."""
    nxt = CronParser.get_next_run("0 0 0 1 11 *", BASE)
    assert nxt == datetime(2025, 11, 1, 0, 0, 0)


def test_next_run_crosses_day_boundary():
    """If the time has already passed today, should roll to tomorrow."""
    after = datetime(2025, 3, 10, 23, 0, 0)
    nxt   = CronParser.get_next_run("0 0 8 * * *", after)
    assert nxt == datetime(2025, 3, 11, 8, 0, 0)
