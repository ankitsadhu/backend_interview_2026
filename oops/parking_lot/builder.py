"""
parking_lot/builder.py
----------------------
LotBuilder assembles a ParkingLot with a fluent API.
Hides spot-ID generation and floor wiring from callers.
"""

from .models.spot   import ParkingSpot, SpotSize
from .models.floor  import ParkingFloor
from .parking_lot   import ParkingLot
from .strategies.pricing import PricingFactory, PricingStrategy


class LotBuilder:
    """
    Fluent builder for ParkingLot.

    Usage:
        lot = (
            LotBuilder("Mall Parking")
            .add_floor(floor_id=0, small=10, medium=20, large=5)
            .add_floor(floor_id=1, small=5,  medium=15, large=3)
            .with_pricing("dynamic")
            .build()
        )
    """

    def __init__(self, name: str):
        self._name    = name
        self._floors: list[ParkingFloor] = []
        self._pricing: PricingStrategy   = PricingFactory.get("tiered")

    def add_floor(
        self,
        floor_id: int,
        small:    int = 0,
        medium:   int = 0,
        large:    int = 0,
    ) -> "LotBuilder":
        spots: list[ParkingSpot] = []
        for i in range(small):
            spots.append(ParkingSpot(f"F{floor_id}-S{i+1:02d}",  floor_id, SpotSize.SMALL))
        for i in range(medium):
            spots.append(ParkingSpot(f"F{floor_id}-M{i+1:02d}",  floor_id, SpotSize.MEDIUM))
        for i in range(large):
            spots.append(ParkingSpot(f"F{floor_id}-L{i+1:02d}",  floor_id, SpotSize.LARGE))
        self._floors.append(ParkingFloor(floor_id, spots))
        return self

    def with_pricing(self, strategy_name: str) -> "LotBuilder":
        self._pricing = PricingFactory.get(strategy_name)
        return self

    def build(self) -> ParkingLot:
        if not self._floors:
            raise ValueError("A parking lot must have at least one floor.")
        return ParkingLot(self._name, self._floors, self._pricing)
