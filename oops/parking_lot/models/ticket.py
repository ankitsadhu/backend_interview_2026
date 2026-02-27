"""
models/ticket.py
----------------
ParkingTicket is a value object — immutable once issued.
It tracks entry time and is resolved at exit to compute duration.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from .vehicle import Vehicle
from .spot import ParkingSpot


@dataclass(frozen=True)
class ParkingTicket:
    ticket_id:  str
    vehicle:    Vehicle
    spot:       ParkingSpot
    floor_id:   int
    entry_time: datetime

    @staticmethod
    def issue(vehicle: Vehicle, spot: ParkingSpot) -> "ParkingTicket":
        return ParkingTicket(
            ticket_id  = str(uuid.uuid4())[:8].upper(),
            vehicle    = vehicle,
            spot       = spot,
            floor_id   = spot.floor_id,
            entry_time = datetime.now(),
        )

    def duration_hours(self, exit_time: datetime | None = None) -> float:
        end = exit_time or datetime.now()
        delta = end - self.entry_time
        return max(delta.total_seconds() / 3600, 0.0)

    def __repr__(self) -> str:
        return (
            f"Ticket[{self.ticket_id}] "
            f"{self.vehicle} @ Floor {self.floor_id}/{self.spot.spot_id} "
            f"in={self.entry_time.strftime('%H:%M:%S')}"
        )
