"""
notifications.py — Event bus for ride lifecycle events (Observer pattern).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class EventType(Enum):
    RIDE_REQUESTED    = "RIDE_REQUESTED"
    DRIVER_MATCHED    = "DRIVER_MATCHED"
    DRIVER_ARRIVING   = "DRIVER_ARRIVING"
    TRIP_STARTED      = "TRIP_STARTED"
    TRIP_COMPLETED    = "TRIP_COMPLETED"
    RIDE_CANCELLED    = "RIDE_CANCELLED"
    PAYMENT_PROCESSED = "PAYMENT_PROCESSED"
    RATING_SUBMITTED  = "RATING_SUBMITTED"


@dataclass
class RideEvent:
    event_type : EventType
    timestamp  : datetime = field(default_factory=datetime.now)
    data       : Dict[str, Any] = field(default_factory=dict)


class EventBus:
    """Publish-subscribe event bus for ride events."""

    def __init__(self) -> None:
        self._subscribers: Dict[EventType, List[Callable[[RideEvent], None]]] = {}
        self._history: List[RideEvent] = []

    def subscribe(self, event_type: EventType,
                  handler: Callable[[RideEvent], None]) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: RideEvent) -> None:
        self._history.append(event)
        for handler in self._subscribers.get(event.event_type, []):
            try:
                handler(event)
            except Exception:
                pass  # Don't let handler errors break the flow

    @property
    def history(self) -> List[RideEvent]:
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()


# ============================================================
# Built-in handlers
# ============================================================

class AuditLogHandler:
    """Logs all events to an in-memory audit trail."""

    def __init__(self) -> None:
        self.logs: List[str] = []

    def __call__(self, event: RideEvent) -> None:
        msg = f"[{event.timestamp:%H:%M:%S}] {event.event_type.value}"
        if "ride_id" in event.data:
            msg += f" | ride={event.data['ride_id'][:8]}"
        self.logs.append(msg)


class NotificationHandler:
    """Simulated push notification stub."""

    def __init__(self) -> None:
        self.notifications: List[Dict[str, str]] = []

    def __call__(self, event: RideEvent) -> None:
        messages = {
            EventType.DRIVER_MATCHED  : "Your driver is on the way!",
            EventType.DRIVER_ARRIVING : "Your driver is arriving now!",
            EventType.TRIP_STARTED    : "Your trip has started. Enjoy your ride!",
            EventType.TRIP_COMPLETED  : "You've arrived! Rate your ride.",
            EventType.RIDE_CANCELLED  : "Your ride has been cancelled.",
        }
        msg = messages.get(event.event_type)
        if msg:
            self.notifications.append({
                "to": event.data.get("rider_name", "Rider"),
                "message": msg,
            })


def create_default_bus() -> EventBus:
    """Create an EventBus with standard handlers wired up."""
    bus = EventBus()
    audit = AuditLogHandler()
    notifier = NotificationHandler()

    for et in EventType:
        bus.subscribe(et, audit)
    for et in (EventType.DRIVER_MATCHED, EventType.DRIVER_ARRIVING,
               EventType.TRIP_STARTED, EventType.TRIP_COMPLETED,
               EventType.RIDE_CANCELLED):
        bus.subscribe(et, notifier)

    return bus
