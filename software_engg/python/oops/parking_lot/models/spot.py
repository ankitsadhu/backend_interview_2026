"""
models/spot.py
--------------
A ParkingSpot belongs to exactly one floor.
SpotSize determines which vehicle types are compatible.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from .vehicle import Vehicle, VehicleType


class SpotSize(Enum):
    SMALL  = "Small"   # Motorcycles only
    MEDIUM = "Medium"  # Cars (and motorcycles)
    LARGE  = "Large"   # Trucks / any vehicle


# Which spot sizes can accept a given vehicle type
_ALLOWED: dict[VehicleType, set[SpotSize]] = {
    VehicleType.MOTORCYCLE: {SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE},
    VehicleType.CAR:        {SpotSize.MEDIUM, SpotSize.LARGE},
    VehicleType.TRUCK:      {SpotSize.LARGE},
}


@dataclass
class ParkingSpot:
    spot_id:  str
    floor_id: int
    size:     SpotSize
    _vehicle: Optional[Vehicle] = field(default=None, init=False, repr=False)

    # ── state ────────────────────────────────────────────────────────────────

    @property
    def is_available(self) -> bool:
        return self._vehicle is None

    @property
    def vehicle(self) -> Optional[Vehicle]:
        return self._vehicle

    # ── behaviour ────────────────────────────────────────────────────────────

    def can_fit(self, vehicle: Vehicle) -> bool:
        return self.is_available and self.size in _ALLOWED[vehicle.vehicle_type]

    def park(self, vehicle: Vehicle) -> None:
        if not self.can_fit(vehicle):
            raise ValueError(
                f"Spot {self.spot_id} cannot accept {vehicle} "
                f"(size={self.size.value}, available={self.is_available})"
            )
        self._vehicle = vehicle

    def vacate(self) -> Vehicle:
        if self.is_available:
            raise ValueError(f"Spot {self.spot_id} is already empty.")
        parked = self._vehicle
        self._vehicle = None
        return parked  # type: ignore[return-value]

    def __repr__(self) -> str:
        status = "FREE" if self.is_available else f"OCC-{self._vehicle}"
        return f"Spot[{self.spot_id} | {self.size.value} | {status}]"
