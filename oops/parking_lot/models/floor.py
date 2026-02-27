"""
models/floor.py
---------------
A ParkingFloor manages a flat list of ParkingSpots.
It knows nothing about pricing or tickets — pure data + spot queries.
"""

from typing import Optional
from .spot import ParkingSpot, SpotSize
from .vehicle import Vehicle, VehicleType


class ParkingFloor:
    def __init__(self, floor_id: int, spots: list[ParkingSpot]):
        self.floor_id = floor_id
        self._spots: dict[str, ParkingSpot] = {s.spot_id: s for s in spots}

    # ── queries ──────────────────────────────────────────────────────────────

    def available_spots(self) -> list[ParkingSpot]:
        return [s for s in self._spots.values() if s.is_available]

    def available_spots_for(self, vehicle: Vehicle) -> list[ParkingSpot]:
        return [s for s in self._spots.values() if s.can_fit(vehicle)]

    def get_spot(self, spot_id: str) -> Optional[ParkingSpot]:
        return self._spots.get(spot_id)

    def availability_summary(self) -> dict[str, int]:
        """Returns free count per SpotSize on this floor."""
        summary: dict[str, int] = {size.value: 0 for size in SpotSize}
        for spot in self._spots.values():
            if spot.is_available:
                summary[spot.size.value] += 1
        return summary

    def __repr__(self) -> str:
        total  = len(self._spots)
        free   = len(self.available_spots())
        return f"Floor[{self.floor_id}] ({free}/{total} free)"
