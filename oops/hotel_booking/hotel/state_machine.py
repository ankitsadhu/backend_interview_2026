"""
state_machine.py — Reservation lifecycle state machine.

Valid transitions:
  PENDING     → CONFIRMED
  PENDING     → CANCELLED
  CONFIRMED   → CHECKED_IN
  CONFIRMED   → CANCELLED
  CHECKED_IN  → CHECKED_OUT

Terminal states (no transitions allowed):
  CHECKED_OUT, CANCELLED
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Set
from .models import ReservationStatus


class InvalidTransitionError(Exception):
    """Raised when an illegal state transition is attempted."""

    def __init__(self, from_status: ReservationStatus, to_status: ReservationStatus) -> None:
        self.from_status = from_status
        self.to_status   = to_status
        super().__init__(
            f"Cannot transition from {from_status.value} → {to_status.value}"
        )


# Map each state → set of legal next states
_TRANSITIONS: Dict[ReservationStatus, FrozenSet[ReservationStatus]] = {
    ReservationStatus.PENDING    : frozenset({
        ReservationStatus.CONFIRMED,
        ReservationStatus.CANCELLED,
    }),
    ReservationStatus.CONFIRMED  : frozenset({
        ReservationStatus.CHECKED_IN,
        ReservationStatus.CANCELLED,
    }),
    ReservationStatus.CHECKED_IN : frozenset({
        ReservationStatus.CHECKED_OUT,
    }),
    ReservationStatus.CHECKED_OUT: frozenset(),   # terminal
    ReservationStatus.CANCELLED  : frozenset(),   # terminal
}


class ReservationStateMachine:
    """Validates and executes reservation state transitions."""

    @staticmethod
    def can_transition(
        current: ReservationStatus,
        target: ReservationStatus,
    ) -> bool:
        return target in _TRANSITIONS.get(current, frozenset())

    @staticmethod
    def transition(
        current: ReservationStatus,
        target: ReservationStatus,
    ) -> ReservationStatus:
        """
        Validate and return *target* state.
        Raises InvalidTransitionError if the transition is illegal.
        """
        if not ReservationStateMachine.can_transition(current, target):
            raise InvalidTransitionError(current, target)
        return target

    @staticmethod
    def allowed_transitions(current: ReservationStatus) -> FrozenSet[ReservationStatus]:
        return _TRANSITIONS.get(current, frozenset())

    @staticmethod
    def is_terminal(status: ReservationStatus) -> bool:
        return len(_TRANSITIONS.get(status, frozenset())) == 0
