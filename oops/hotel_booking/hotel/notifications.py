"""
notifications.py — Observer / Event Bus for hotel domain events.

Usage:
    bus = EventBus()
    bus.subscribe(EventType.BOOKING_CREATED, audit_logger.handle)
    bus.publish(HotelEvent(EventType.BOOKING_CREATED, data={"reservation_id": ...}))
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List

logger = logging.getLogger("hotel.events")


# ============================================================
# Event types
# ============================================================

class EventType(Enum):
    BOOKING_CREATED   = "BOOKING_CREATED"
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    CHECKED_IN        = "CHECKED_IN"
    CHECKED_OUT       = "CHECKED_OUT"
    PAYMENT_PROCESSED = "PAYMENT_PROCESSED"
    ROOM_STATUS_CHANGED = "ROOM_STATUS_CHANGED"


# ============================================================
# Event
# ============================================================

@dataclass
class HotelEvent:
    event_type : EventType
    data       : Dict[str, Any] = field(default_factory=dict)
    timestamp  : datetime       = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.event_type.value} — {self.data}"


# ============================================================
# Event Bus
# ============================================================

Handler = Callable[[HotelEvent], None]


class EventBus:
    """Simple synchronous publish/subscribe event bus."""

    def __init__(self) -> None:
        self._subscribers: Dict[EventType, List[Handler]] = {et: [] for et in EventType}
        self.history: List[HotelEvent] = []

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: Handler) -> None:
        for et in EventType:
            self._subscribers[et].append(handler)

    def publish(self, event: HotelEvent) -> None:
        self.history.append(event)
        logger.debug("Event published: %s", event)
        for handler in self._subscribers[event.event_type]:
            try:
                handler(event)
            except Exception as exc:
                logger.error("Handler %s failed for event %s: %s", handler, event.event_type, exc)

    def clear_history(self) -> None:
        self.history.clear()


# ============================================================
# Built-in handlers
# ============================================================

class AuditLogHandler:
    """Writes every event to the Python logger (INFO level)."""

    def __init__(self) -> None:
        self._log: List[str] = []

    def handle(self, event: HotelEvent) -> None:
        msg = str(event)
        logger.info("AUDIT: %s", msg)
        self._log.append(msg)

    @property
    def entries(self) -> List[str]:
        return list(self._log)


class EmailNotificationHandler:
    """Stub: simulates sending email notifications."""

    def handle(self, event: HotelEvent) -> None:
        templates = {
            EventType.BOOKING_CREATED   : "Your booking #{id} is confirmed for {nights} night(s).",
            EventType.BOOKING_CANCELLED : "Your booking #{id} has been cancelled. Refund: ${refund}.",
            EventType.CHECKED_IN        : "Welcome! You have checked in to room {room}.",
            EventType.CHECKED_OUT       : "Thank you for staying with us! Invoice: ${total}.",
        }
        tmpl = templates.get(event.event_type)
        if tmpl:
            try:
                msg = tmpl.format(**event.data)
            except KeyError:
                msg = tmpl
            logger.info("EMAIL → %s: %s", event.data.get("guest_email", "guest"), msg)


class SMSNotificationHandler:
    """Stub: simulates sending SMS notifications."""

    def handle(self, event: HotelEvent) -> None:
        if event.event_type in (EventType.CHECKED_IN, EventType.CHECKED_OUT):
            phone = event.data.get("guest_phone", "N/A")
            logger.info("SMS → %s: %s", phone, event.event_type.value)


# ============================================================
# Default bus factory
# ============================================================

def create_default_bus() -> EventBus:
    bus   = EventBus()
    audit = AuditLogHandler()
    email = EmailNotificationHandler()
    sms   = SMSNotificationHandler()
    bus.subscribe_all(audit.handle)
    bus.subscribe(EventType.BOOKING_CREATED,   email.handle)
    bus.subscribe(EventType.BOOKING_CANCELLED, email.handle)
    bus.subscribe(EventType.CHECKED_IN,        email.handle)
    bus.subscribe(EventType.CHECKED_OUT,       email.handle)
    bus.subscribe(EventType.CHECKED_IN,        sms.handle)
    bus.subscribe(EventType.CHECKED_OUT,       sms.handle)
    return bus
