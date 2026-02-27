"""
tests/test_state_machine.py — Tests for ReservationStateMachine.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hotel.models import ReservationStatus
from hotel.state_machine import InvalidTransitionError, ReservationStateMachine

sm = ReservationStateMachine()


# ============================================================
# Valid transitions
# ============================================================

def test_pending_to_confirmed():
    result = sm.transition(ReservationStatus.PENDING, ReservationStatus.CONFIRMED)
    assert result == ReservationStatus.CONFIRMED


def test_pending_to_cancelled():
    result = sm.transition(ReservationStatus.PENDING, ReservationStatus.CANCELLED)
    assert result == ReservationStatus.CANCELLED


def test_confirmed_to_checked_in():
    result = sm.transition(ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN)
    assert result == ReservationStatus.CHECKED_IN


def test_confirmed_to_cancelled():
    result = sm.transition(ReservationStatus.CONFIRMED, ReservationStatus.CANCELLED)
    assert result == ReservationStatus.CANCELLED


def test_checked_in_to_checked_out():
    result = sm.transition(ReservationStatus.CHECKED_IN, ReservationStatus.CHECKED_OUT)
    assert result == ReservationStatus.CHECKED_OUT


# ============================================================
# Invalid transitions
# ============================================================

def test_pending_to_checked_in_invalid():
    with pytest.raises(InvalidTransitionError):
        sm.transition(ReservationStatus.PENDING, ReservationStatus.CHECKED_IN)


def test_pending_to_checked_out_invalid():
    with pytest.raises(InvalidTransitionError):
        sm.transition(ReservationStatus.PENDING, ReservationStatus.CHECKED_OUT)


def test_checked_in_to_cancelled_invalid():
    with pytest.raises(InvalidTransitionError):
        sm.transition(ReservationStatus.CHECKED_IN, ReservationStatus.CANCELLED)


def test_checked_in_to_confirmed_invalid():
    with pytest.raises(InvalidTransitionError):
        sm.transition(ReservationStatus.CHECKED_IN, ReservationStatus.CONFIRMED)


# ============================================================
# Terminal states — no transitions allowed
# ============================================================

def test_checked_out_is_terminal():
    assert sm.is_terminal(ReservationStatus.CHECKED_OUT)
    with pytest.raises(InvalidTransitionError):
        sm.transition(ReservationStatus.CHECKED_OUT, ReservationStatus.PENDING)


def test_cancelled_is_terminal():
    assert sm.is_terminal(ReservationStatus.CANCELLED)
    with pytest.raises(InvalidTransitionError):
        sm.transition(ReservationStatus.CANCELLED, ReservationStatus.CONFIRMED)


# ============================================================
# can_transition helper
# ============================================================

def test_can_transition_true():
    assert sm.can_transition(ReservationStatus.PENDING, ReservationStatus.CONFIRMED) is True


def test_can_transition_false():
    assert sm.can_transition(ReservationStatus.CHECKED_OUT, ReservationStatus.PENDING) is False


def test_allowed_transitions_pending():
    allowed = sm.allowed_transitions(ReservationStatus.PENDING)
    assert ReservationStatus.CONFIRMED in allowed
    assert ReservationStatus.CANCELLED in allowed
    assert ReservationStatus.CHECKED_IN not in allowed


def test_allowed_transitions_terminal():
    for terminal in (ReservationStatus.CHECKED_OUT, ReservationStatus.CANCELLED):
        assert len(sm.allowed_transitions(terminal)) == 0


# ============================================================
# InvalidTransitionError message
# ============================================================

def test_error_message():
    try:
        sm.transition(ReservationStatus.CHECKED_OUT, ReservationStatus.PENDING)
    except InvalidTransitionError as exc:
        assert "CHECKED_OUT" in str(exc)
        assert "PENDING" in str(exc)
