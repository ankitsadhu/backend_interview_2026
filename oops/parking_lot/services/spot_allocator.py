"""
services/spot_allocator.py
--------------------------
Responsible ONLY for finding the best available spot for a vehicle.
Keeps the allocation strategy swappable (nearest floor first by default).
"""

from typing import Optional
from ..models.floor import ParkingFloor
from ..models.spot import ParkingSpot
from ..models.vehicle import Vehicle


class SpotAllocator:
    """
    Finds the best spot across all floors for a given vehicle.

    Strategy (default): nearest floor first, smallest compatible spot first.
    Override `find_spot` in a subclass to swap strategy without touching ParkingLot.
    """

    def find_spot(
        self, floors: list[ParkingFloor], vehicle: Vehicle
    ) -> Optional[ParkingSpot]:
        for floor in floors:                          # iterate floor 0 → N
            candidates = floor.available_spots_for(vehicle)
            if candidates:
                # Among candidates on this floor, prefer smallest fitting size
                candidates.sort(key=lambda s: s.size.value)
                return candidates[0]
        return None                                   # lot is full
