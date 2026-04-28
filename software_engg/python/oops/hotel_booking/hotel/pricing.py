"""
pricing.py — Strategy pattern for dynamic hotel room pricing.

Strategies are applied in a chain by PricingEngine.
Each strategy receives the current total and may modify it.

Chain order:
  1. BasePricingStrategy   → nights × base_rate
  2. SeasonalPricing       → +30% in peak months (Jun–Aug, Dec)
  3. WeekendPricing        → +20% for each Fri/Sat night in stay
  4. CorporatePricing      → −15% flat (if guest has corporate tag)
  5. LoyaltyPricing        → discount from guest.loyalty_tier
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Room, Guest, Reservation

PEAK_MONTHS = {6, 7, 8, 12}       # Jun, Jul, Aug, Dec
WEEKEND_DAYS = {4, 5}             # Friday=4, Saturday=5  (Python weekday())


# ============================================================
# Abstract base
# ============================================================

class PricingStrategy(ABC):
    @abstractmethod
    def apply(
        self,
        base_total: float,
        room: "Room",
        guest: "Guest",
        check_in: date,
        check_out: date,
        breakdown: Dict[str, float],
    ) -> float:
        """Return adjusted total price."""
        ...

    @property
    @abstractmethod
    def name(self) -> str: ...


# ============================================================
# Concrete strategies
# ============================================================

class BasePricingStrategy(PricingStrategy):
    """Flat rate: room.base_rate × number of nights."""

    name = "base"

    def apply(self, base_total, room, guest, check_in, check_out, breakdown):
        nights = (check_out - check_in).days
        total  = round(room.base_rate * nights, 2)
        breakdown["base_rate"]  = room.base_rate
        breakdown["nights"]     = nights
        breakdown["base_total"] = total
        return total


class SeasonalPricingStrategy(PricingStrategy):
    """Peak-season surcharge: +30% per peak-month night."""

    name     = "seasonal"
    SURCHARGE = 0.30

    def apply(self, base_total, room, guest, check_in, check_out, breakdown):
        peak_nights = 0
        current = check_in
        while current < check_out:
            if current.month in PEAK_MONTHS:
                peak_nights += 1
            current += timedelta(days=1)

        if peak_nights == 0:
            breakdown["seasonal_surcharge"] = 0.0
            return base_total

        extra = round(room.base_rate * self.SURCHARGE * peak_nights, 2)
        breakdown["peak_nights"]        = peak_nights
        breakdown["seasonal_surcharge"] = extra
        return round(base_total + extra, 2)


class WeekendPricingStrategy(PricingStrategy):
    """Weekend surcharge: +20% per Friday/Saturday night."""

    name     = "weekend"
    SURCHARGE = 0.20

    def apply(self, base_total, room, guest, check_in, check_out, breakdown):
        weekend_nights = 0
        current = check_in
        while current < check_out:
            if current.weekday() in WEEKEND_DAYS:
                weekend_nights += 1
            current += timedelta(days=1)

        if weekend_nights == 0:
            breakdown["weekend_surcharge"] = 0.0
            return base_total

        extra = round(room.base_rate * self.SURCHARGE * weekend_nights, 2)
        breakdown["weekend_nights"]    = weekend_nights
        breakdown["weekend_surcharge"] = extra
        return round(base_total + extra, 2)


class CorporatePricingStrategy(PricingStrategy):
    """Corporate discount: −15% applied if guest has 'corporate' tag."""

    name     = "corporate"
    DISCOUNT  = 0.15

    def apply(self, base_total, room, guest, check_in, check_out, breakdown):
        if not getattr(guest, "is_corporate", False):
            breakdown["corporate_discount"] = 0.0
            return base_total
        saving = round(base_total * self.DISCOUNT, 2)
        breakdown["corporate_discount"] = -saving
        return round(base_total - saving, 2)


class LoyaltyPricingStrategy(PricingStrategy):
    """Loyalty tier discount: SILVER 5%, GOLD 10%, PLATINUM 20%."""

    name = "loyalty"

    def apply(self, base_total, room, guest, check_in, check_out, breakdown):
        pct = guest.loyalty_tier.discount_pct
        if pct == 0.0:
            breakdown["loyalty_discount"] = 0.0
            return base_total
        saving = round(base_total * pct, 2)
        breakdown["loyalty_discount"] = -saving
        breakdown["loyalty_tier"]      = guest.loyalty_tier.value
        return round(base_total - saving, 2)


class EarlyBirdPricingStrategy(PricingStrategy):
    """Early bird discount: −10% if booked more than 30 days in advance."""

    name     = "early_bird"
    DISCOUNT  = 0.10
    DAYS_AHEAD = 30

    def apply(self, base_total, room, guest, check_in, check_out, breakdown):
        days_until = (check_in - date.today()).days
        if days_until < self.DAYS_AHEAD:
            breakdown["early_bird_discount"] = 0.0
            return base_total
        saving = round(base_total * self.DISCOUNT, 2)
        breakdown["early_bird_discount"] = -saving
        return round(base_total - saving, 2)


# ============================================================
# Pricing Engine — composes all strategies
# ============================================================

class PricingEngine:
    """
    Chain of responsibility: applies each strategy in order,
    feeding the running total into the next strategy.
    """

    DEFAULT_STRATEGIES: List[PricingStrategy] = [
        BasePricingStrategy(),
        SeasonalPricingStrategy(),
        WeekendPricingStrategy(),
        LoyaltyPricingStrategy(),
        CorporatePricingStrategy(),
        EarlyBirdPricingStrategy(),
    ]

    def __init__(self, strategies: List[PricingStrategy] | None = None) -> None:
        self._strategies = strategies if strategies is not None else self.DEFAULT_STRATEGIES

    def calculate(
        self,
        room: "Room",
        guest: "Guest",
        check_in: date,
        check_out: date,
    ) -> tuple[float, Dict[str, float]]:
        """
        Returns (final_price, breakdown_dict).
        breakdown_dict maps strategy labels → contribution amount.
        """
        if check_out <= check_in:
            raise ValueError("check_out must be after check_in")

        breakdown: Dict[str, float] = {}
        total = 0.0
        for strategy in self._strategies:
            total = strategy.apply(total, room, guest, check_in, check_out, breakdown)

        breakdown["final_total"] = round(total, 2)
        return round(total, 2), breakdown

    def add_strategy(self, strategy: PricingStrategy, position: int = -1) -> None:
        if position == -1:
            self._strategies.append(strategy)
        else:
            self._strategies.insert(position, strategy)
