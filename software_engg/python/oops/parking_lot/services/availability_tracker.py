"""
services/availability_tracker.py
----------------------------------
Observer pattern — any component can subscribe to slot change events.
ParkingLot publishes events; dashboard or alerting systems consume them.
"""

from dataclasses import dataclass
from typing import Callable
from ..models.spot import ParkingSpot
from ..models.vehicle import Vehicle


@dataclass
class SlotEvent:
    event_type: str          # "PARKED" | "VACATED"
    floor_id:   int
    spot_id:    str
    vehicle:    Vehicle | None
    free_after: int          # total free spots in lot after this event


# Type alias for subscriber callbacks
Subscriber = Callable[[SlotEvent], None]


class AvailabilityTracker:
    """
    Maintains real-time free-spot counts and notifies subscribers on changes.
    """

    def __init__(self, total_spots: int):
        self._free: int = total_spots
        self._subscribers: list[Subscriber] = []

    # ── subscription ─────────────────────────────────────────────────────────

    def subscribe(self, callback: Subscriber) -> None:
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Subscriber) -> None:
        self._subscribers.remove(callback)

    # ── state ────────────────────────────────────────────────────────────────

    @property
    def free_spots(self) -> int:
        return self._free

    @property
    def is_full(self) -> bool:
        return self._free == 0

    # ── event publishing ─────────────────────────────────────────────────────

    def on_parked(self, spot: ParkingSpot, vehicle: Vehicle) -> None:
        self._free -= 1
        self._publish(SlotEvent("PARKED", spot.floor_id, spot.spot_id, vehicle, self._free))

    def on_vacated(self, spot: ParkingSpot) -> None:
        self._free += 1
        self._publish(SlotEvent("VACATED", spot.floor_id, spot.spot_id, None, self._free))

    def _publish(self, event: SlotEvent) -> None:
        for sub in self._subscribers:
            sub(event)
