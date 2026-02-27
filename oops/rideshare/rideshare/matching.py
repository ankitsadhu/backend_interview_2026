"""
matching.py — Strategy pattern for driver matching.

Strategies:
  - NearestDriverStrategy   : closest available driver
  - HighestRatedStrategy    : best-rated driver within radius
  - VehiclePreferenceStrategy : match vehicle type, then nearest
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .geo import GeoService
from .models import Driver, DriverStatus, Location, VehicleType


class MatchingStrategy(ABC):
    """Abstract base for driver matching algorithms."""

    @abstractmethod
    def find_drivers(
        self,
        available_drivers: List[Driver],
        pickup: Location,
        vehicle_pref: Optional[VehicleType] = None,
        max_radius_km: float = 10.0,
        max_results: int = 5,
    ) -> List[Driver]:
        """Return ranked list of suitable drivers."""
        ...


class NearestDriverStrategy(MatchingStrategy):
    """Select drivers by proximity (closest first)."""

    def find_drivers(
        self,
        available_drivers: List[Driver],
        pickup: Location,
        vehicle_pref: Optional[VehicleType] = None,
        max_radius_km: float = 10.0,
        max_results: int = 5,
    ) -> List[Driver]:
        candidates = []
        for driver in available_drivers:
            if driver.status != DriverStatus.AVAILABLE:
                continue
            if driver.location is None:
                continue
            dist = GeoService.haversine(driver.location, pickup)
            if dist <= max_radius_km:
                candidates.append((dist, driver))

        candidates.sort(key=lambda x: x[0])
        return [d for _, d in candidates[:max_results]]


class HighestRatedStrategy(MatchingStrategy):
    """Select drivers by rating (highest first), within radius."""

    def find_drivers(
        self,
        available_drivers: List[Driver],
        pickup: Location,
        vehicle_pref: Optional[VehicleType] = None,
        max_radius_km: float = 10.0,
        max_results: int = 5,
    ) -> List[Driver]:
        candidates = []
        for driver in available_drivers:
            if driver.status != DriverStatus.AVAILABLE:
                continue
            if driver.location is None:
                continue
            dist = GeoService.haversine(driver.location, pickup)
            if dist <= max_radius_km:
                candidates.append((driver.rating, dist, driver))

        # Sort by rating DESC, then distance ASC
        candidates.sort(key=lambda x: (-x[0], x[1]))
        return [d for _, _, d in candidates[:max_results]]


class VehiclePreferenceStrategy(MatchingStrategy):
    """Match by vehicle type first, then nearest within that set."""

    def find_drivers(
        self,
        available_drivers: List[Driver],
        pickup: Location,
        vehicle_pref: Optional[VehicleType] = None,
        max_radius_km: float = 10.0,
        max_results: int = 5,
    ) -> List[Driver]:
        candidates = []
        for driver in available_drivers:
            if driver.status != DriverStatus.AVAILABLE:
                continue
            if driver.location is None or driver.vehicle is None:
                continue
            dist = GeoService.haversine(driver.location, pickup)
            if dist > max_radius_km:
                continue
            # Prioritize matching vehicle type
            type_match = 0 if (vehicle_pref and driver.vehicle.vehicle_type == vehicle_pref) else 1
            candidates.append((type_match, dist, driver))

        candidates.sort(key=lambda x: (x[0], x[1]))
        return [d for _, _, d in candidates[:max_results]]


# ============================================================
# Matching Engine
# ============================================================

class MatchingEngine:
    """
    Composes a MatchingStrategy and provides the match_driver API.

    Default strategy: NearestDriverStrategy.
    """

    def __init__(self, strategy: Optional[MatchingStrategy] = None) -> None:
        self._strategy = strategy or NearestDriverStrategy()

    @property
    def strategy(self) -> MatchingStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, s: MatchingStrategy) -> None:
        self._strategy = s

    def find_best_driver(
        self,
        available_drivers: List[Driver],
        pickup: Location,
        vehicle_pref: Optional[VehicleType] = None,
        max_radius_km: float = 10.0,
    ) -> Optional[Driver]:
        """Return the single best driver, or None."""
        results = self._strategy.find_drivers(
            available_drivers, pickup, vehicle_pref, max_radius_km, max_results=1
        )
        return results[0] if results else None

    def find_drivers(
        self,
        available_drivers: List[Driver],
        pickup: Location,
        vehicle_pref: Optional[VehicleType] = None,
        max_radius_km: float = 10.0,
        max_results: int = 5,
    ) -> List[Driver]:
        """Return ranked list of suitable drivers."""
        return self._strategy.find_drivers(
            available_drivers, pickup, vehicle_pref, max_radius_km, max_results
        )
