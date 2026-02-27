"""
repository.py — In-memory repositories for Drivers, Riders, Rides.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .geo import GeoService
from .models import (
    Driver, DriverStatus, Location, Ride, RideStatus, Rider, VehicleType,
)


class DriverRepository:
    """In-memory driver store with spatial queries."""

    def __init__(self) -> None:
        self._store: Dict[str, Driver] = {}

    def add(self, driver: Driver) -> Driver:
        self._store[driver.id] = driver
        return driver

    def get(self, driver_id: str) -> Optional[Driver]:
        return self._store.get(driver_id)

    def all(self) -> List[Driver]:
        return list(self._store.values())

    def available(self) -> List[Driver]:
        return [d for d in self._store.values() if d.status == DriverStatus.AVAILABLE]

    def available_nearby(self, location: Location,
                         radius_km: float = 10.0) -> List[Driver]:
        return [
            d for d in self.available()
            if d.location and GeoService.is_within_radius(d.location, location, radius_km)
        ]

    def by_vehicle_type(self, vt: VehicleType) -> List[Driver]:
        return [
            d for d in self._store.values()
            if d.vehicle and d.vehicle.vehicle_type == vt
        ]

    def update_status(self, driver_id: str, status: DriverStatus) -> None:
        d = self._store.get(driver_id)
        if d:
            d.status = status

    def update_location(self, driver_id: str, loc: Location) -> None:
        d = self._store.get(driver_id)
        if d:
            d.location = loc


class RiderRepository:
    """In-memory rider store."""

    def __init__(self) -> None:
        self._store: Dict[str, Rider] = {}

    def add(self, rider: Rider) -> Rider:
        self._store[rider.id] = rider
        return rider

    def get(self, rider_id: str) -> Optional[Rider]:
        return self._store.get(rider_id)

    def all(self) -> List[Rider]:
        return list(self._store.values())

    def find_by_email(self, email: str) -> Optional[Rider]:
        for r in self._store.values():
            if r.email == email:
                return r
        return None


class RideRepository:
    """In-memory ride store with query helpers."""

    def __init__(self) -> None:
        self._store: Dict[str, Ride] = {}

    def add(self, ride: Ride) -> Ride:
        self._store[ride.id] = ride
        return ride

    def get(self, ride_id: str) -> Optional[Ride]:
        return self._store.get(ride_id)

    def all(self) -> List[Ride]:
        return list(self._store.values())

    def active(self) -> List[Ride]:
        active_statuses = {
            RideStatus.REQUESTED, RideStatus.MATCHED,
            RideStatus.DRIVER_ARRIVING, RideStatus.IN_PROGRESS,
        }
        return [r for r in self._store.values() if r.status in active_statuses]

    def by_rider(self, rider_id: str) -> List[Ride]:
        return [r for r in self._store.values() if r.rider and r.rider.id == rider_id]

    def by_driver(self, driver_id: str) -> List[Ride]:
        return [r for r in self._store.values() if r.driver and r.driver.id == driver_id]

    def completed(self) -> List[Ride]:
        return [r for r in self._store.values() if r.status == RideStatus.COMPLETED]

    def cancelled(self) -> List[Ride]:
        return [r for r in self._store.values() if r.status == RideStatus.CANCELLED]
