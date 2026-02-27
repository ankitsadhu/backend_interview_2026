"""
pricing.py — Fare calculation engine with surge pricing.

Fare formula:
  subtotal   = base_fare + (per_km × distance) + (per_min × duration)
  with_surge = subtotal × surge_multiplier
  vehicle    = with_surge × vehicle_multiplier
  total      = max(vehicle + platform_fee, minimum_fare)
"""
from __future__ import annotations

from typing import Optional

from .models import FareBreakdown, Location, VehicleType
from .geo import GeoService


# ============================================================
# Rate cards per vehicle type
# ============================================================

_RATE_CARDS = {
    VehicleType.ECONOMY : {"base": 2.50, "per_km": 1.20, "per_min": 0.15, "multiplier": 1.0,  "min_fare": 5.00},
    VehicleType.COMFORT : {"base": 3.50, "per_km": 1.60, "per_min": 0.25, "multiplier": 1.25, "min_fare": 7.00},
    VehicleType.PREMIUM : {"base": 5.00, "per_km": 2.50, "per_min": 0.40, "multiplier": 1.75, "min_fare": 12.00},
    VehicleType.SUV     : {"base": 4.00, "per_km": 2.00, "per_min": 0.30, "multiplier": 1.50, "min_fare": 10.00},
    VehicleType.XL      : {"base": 4.50, "per_km": 2.20, "per_min": 0.35, "multiplier": 1.60, "min_fare": 11.00},
}

PLATFORM_FEE_RATE = 0.15   # 15% platform fee
CANCELLATION_FEE  = 5.00


class FareCalculator:
    """Calculate ride fare with full breakdown."""

    @staticmethod
    def calculate(
        pickup          : Location,
        dropoff         : Location,
        vehicle_type    : VehicleType = VehicleType.ECONOMY,
        surge_multiplier: float       = 1.0,
        distance_km     : Optional[float] = None,
        duration_min    : Optional[float] = None,
    ) -> FareBreakdown:
        """
        Compute the fare for a ride.

        If distance_km / duration_min are not provided, they are
        calculated from the pickup/dropoff locations.
        """
        if distance_km is None:
            distance_km = GeoService.haversine(pickup, dropoff)
        if duration_min is None:
            duration_min = GeoService.estimate_duration(distance_km)

        card = _RATE_CARDS[vehicle_type]

        base_fare       = card["base"]
        distance_charge = round(card["per_km"] * distance_km, 2)
        time_charge     = round(card["per_min"] * duration_min, 2)

        subtotal = base_fare + distance_charge + time_charge

        # Surge
        surge_amount = round(subtotal * (surge_multiplier - 1.0), 2) if surge_multiplier > 1.0 else 0.0
        with_surge   = subtotal + surge_amount

        # Vehicle premium
        vehicle_premium = round(with_surge * (card["multiplier"] - 1.0), 2) if card["multiplier"] > 1.0 else 0.0
        pre_fee = with_surge + vehicle_premium

        # Platform fee
        platform_fee = round(pre_fee * PLATFORM_FEE_RATE, 2)
        total = pre_fee + platform_fee

        # Minimum fare
        total = max(total, card["min_fare"])

        return FareBreakdown(
            base_fare        = base_fare,
            distance_charge  = distance_charge,
            time_charge      = time_charge,
            surge_amount     = surge_amount,
            vehicle_premium  = vehicle_premium,
            subtotal         = round(subtotal, 2),
            platform_fee     = platform_fee,
            total            = round(total, 2),
            surge_multiplier = surge_multiplier,
            distance_km      = distance_km,
            duration_min     = duration_min,
        )

    @staticmethod
    def estimate_fare_range(
        pickup      : Location,
        dropoff     : Location,
        vehicle_type: VehicleType = VehicleType.ECONOMY,
        surge       : float       = 1.0,
    ) -> tuple[float, float]:
        """Return (low, high) fare estimate — ±15% of calculated fare."""
        breakdown = FareCalculator.calculate(pickup, dropoff, vehicle_type, surge)
        low  = round(breakdown.total * 0.85, 2)
        high = round(breakdown.total * 1.15, 2)
        return low, high

    @staticmethod
    def cancellation_fee(minutes_after_match: float) -> float:
        """
        Cancellation fee based on time after matching:
          < 2 min : free
          2-5 min : $3
          > 5 min : $5
        """
        if minutes_after_match < 2:
            return 0.0
        elif minutes_after_match < 5:
            return 3.0
        else:
            return CANCELLATION_FEE
