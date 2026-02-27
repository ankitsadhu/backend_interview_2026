"""
geo.py — Geographic utilities: distance, ETA, surge zones.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

from .models import Location


EARTH_RADIUS_KM = 6371.0


class GeoService:
    """Geographic calculations for the ride-sharing system."""

    @staticmethod
    def haversine(loc1: Location, loc2: Location) -> float:
        """
        Calculate great-circle distance between two points in km.
        Uses the Haversine formula.
        """
        lat1, lon1 = math.radians(loc1.lat), math.radians(loc1.lng)
        lat2, lon2 = math.radians(loc2.lat), math.radians(loc2.lng)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (math.sin(dlat / 2) ** 2
             + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))

        return round(EARTH_RADIUS_KM * c, 2)

    @staticmethod
    def estimate_duration(distance_km: float, avg_speed_kmh: float = 30.0) -> float:
        """Estimate trip duration in minutes given distance and average speed."""
        if avg_speed_kmh <= 0:
            return 0.0
        return round((distance_km / avg_speed_kmh) * 60, 1)

    @staticmethod
    def estimate_eta(driver_loc: Location, pickup_loc: Location,
                     avg_speed_kmh: float = 25.0) -> float:
        """Estimate driver ETA to pickup in minutes."""
        dist = GeoService.haversine(driver_loc, pickup_loc)
        return GeoService.estimate_duration(dist, avg_speed_kmh)

    @staticmethod
    def get_surge_multiplier(location: Location,
                             now: Optional[datetime] = None) -> float:
        """
        Calculate surge pricing multiplier based on time of day
        and simulated demand zones.

        Surge tiers:
          - Rush hour (7-9 AM, 5-8 PM):  1.5×
          - Late night (11 PM - 5 AM):   1.8×
          - Weekend evenings (Fri/Sat 9 PM-2 AM): 2.0×
          - High-demand zones (simulated): +0.5×
          - Normal: 1.0×
        """
        now = now or datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday

        multiplier = 1.0

        # Rush hour
        if 7 <= hour <= 9 or 17 <= hour <= 20:
            multiplier = 1.5

        # Late night
        if hour >= 23 or hour < 5:
            multiplier = max(multiplier, 1.8)

        # Weekend evenings (Friday=4, Saturday=5)
        if weekday in (4, 5) and (hour >= 21 or hour < 2):
            multiplier = max(multiplier, 2.0)

        # Simulated high-demand zone (downtown: lat 40.7-40.8, lng -74.0 to -73.9)
        if (40.70 <= location.lat <= 40.80
                and -74.02 <= location.lng <= -73.90):
            multiplier += 0.3

        return round(min(multiplier, 3.0), 1)  # Cap at 3.0

    @staticmethod
    def is_within_radius(loc1: Location, loc2: Location,
                         radius_km: float) -> bool:
        """Check if two locations are within a given radius."""
        return GeoService.haversine(loc1, loc2) <= radius_km
