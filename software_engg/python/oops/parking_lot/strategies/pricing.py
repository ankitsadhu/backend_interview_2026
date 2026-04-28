"""
strategies/pricing.py
---------------------
Strategy pattern for fee calculation.
Add a new class + register in PricingFactory to extend without touching callers.

Rates are per-hour. Minimum 1 hour is charged.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from ..models.vehicle import VehicleType


class PricingStrategy(ABC):
    """Calculates parking fee given duration in hours."""

    @abstractmethod
    def calculate(self, vehicle_type: VehicleType, hours: float) -> float:
        ...


# ── Concrete Strategies ───────────────────────────────────────────────────────

class FlatRatePricing(PricingStrategy):
    """Same flat hourly rate for all vehicles."""

    _RATE = 50.0  # ₹ per hour

    def calculate(self, vehicle_type: VehicleType, hours: float) -> float:
        billable = max(1.0, hours)
        return round(billable * self._RATE, 2)


class TieredPricing(PricingStrategy):
    """
    Tiered hourly rates per vehicle type.
    Motorcycle < Car < Truck  (reflects real-world MAANG lot pricing).
    """

    _RATES: dict[VehicleType, float] = {
        VehicleType.MOTORCYCLE: 20.0,
        VehicleType.CAR:        50.0,
        VehicleType.TRUCK:      100.0,
    }

    def calculate(self, vehicle_type: VehicleType, hours: float) -> float:
        rate     = self._RATES[vehicle_type]
        billable = max(1.0, hours)
        return round(billable * rate, 2)


class DynamicPricing(PricingStrategy):
    """
    Peak / off-peak surge pricing (e.g., 1.5× during 8–10 AM and 5–8 PM).
    Extends TieredPricing with a surge multiplier.
    """

    _BASE = TieredPricing()
    _PEAK_HOURS = {8, 9, 17, 18, 19}
    _SURGE      = 1.5

    def calculate(self, vehicle_type: VehicleType, hours: float) -> float:
        base_fee   = self._BASE.calculate(vehicle_type, hours)
        current_hr = datetime.now().hour
        multiplier = self._SURGE if current_hr in self._PEAK_HOURS else 1.0
        return round(base_fee * multiplier, 2)


# ── Factory ───────────────────────────────────────────────────────────────────

class PricingFactory:
    _registry: dict[str, PricingStrategy] = {
        "flat":    FlatRatePricing(),
        "tiered":  TieredPricing(),
        "dynamic": DynamicPricing(),
    }

    @classmethod
    def get(cls, name: str = "tiered") -> PricingStrategy:
        strategy = cls._registry.get(name.lower())
        if strategy is None:
            raise ValueError(f"Unknown pricing strategy: '{name}'. "
                             f"Options: {list(cls._registry)}")
        return strategy

    @classmethod
    def register(cls, name: str, strategy: PricingStrategy) -> None:
        """Plug in a custom strategy at runtime."""
        cls._registry[name.lower()] = strategy
