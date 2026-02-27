"""
facade.py — RideShareSystem: single entry point wiring all sub-systems.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .geo import GeoService
from .matching import (
    HighestRatedStrategy, MatchingEngine, NearestDriverStrategy,
    VehiclePreferenceStrategy,
)
from .models import (
    CancellationBy, Driver, DriverStatus, FareBreakdown,
    Location, Payment, PaymentMethod,
    Ride, RideStatus, Rider, Vehicle, VehicleType,
)
from .notifications import EventBus, create_default_bus
from .pricing import FareCalculator
from .repository import DriverRepository, RideRepository, RiderRepository
from .ride_service import RideService


class RideShareSystem:
    """
    Facade — high-level interface to the entire Ride-Sharing System.

    Example
    -------
    >>> app = RideShareSystem("QuickRide")
    >>> rider  = app.register_rider("Alice", "alice@ex.com", "+1-555-0101")
    >>> driver = app.register_driver("Bob", "+1-555-0202", vehicle)
    >>> app.go_online(driver.id, location)
    >>> ride   = app.request_ride(rider.id, pickup, dropoff)
    >>> ride   = app.match_driver(ride.id)
    >>> ride   = app.start_trip(ride.id)
    >>> ride   = app.complete_trip(ride.id)
    """

    def __init__(
        self,
        name      : str                     = "RideShare",
        matcher   : Optional[MatchingEngine] = None,
        event_bus : Optional[EventBus]       = None,
    ) -> None:
        self.name       = name
        self._drivers   = DriverRepository()
        self._riders    = RiderRepository()
        self._rides     = RideRepository()
        self._bus       = event_bus or create_default_bus()
        self._matcher   = matcher or MatchingEngine()
        self._service   = RideService(
            self._drivers, self._riders, self._rides,
            self._matcher, self._bus,
        )

    # ----------------------------------------------------------
    # Driver management
    # ----------------------------------------------------------

    def register_driver(
        self,
        name    : str,
        phone   : str,
        vehicle : Vehicle,
    ) -> Driver:
        driver = Driver(name=name, phone=phone, vehicle=vehicle)
        return self._drivers.add(driver)

    def go_online(self, driver_id: str, location: Location) -> None:
        self._drivers.update_location(driver_id, location)
        self._drivers.update_status(driver_id, DriverStatus.AVAILABLE)

    def go_offline(self, driver_id: str) -> None:
        self._drivers.update_status(driver_id, DriverStatus.OFFLINE)

    def update_driver_location(self, driver_id: str, loc: Location) -> None:
        self._drivers.update_location(driver_id, loc)

    def get_driver(self, driver_id: str) -> Optional[Driver]:
        return self._drivers.get(driver_id)

    def list_drivers(self, available_only: bool = False) -> List[Driver]:
        return self._drivers.available() if available_only else self._drivers.all()

    # ----------------------------------------------------------
    # Rider management
    # ----------------------------------------------------------

    def register_rider(
        self,
        name  : str,
        email : str,
        phone : str = "",
    ) -> Rider:
        rider = Rider(name=name, email=email, phone=phone)
        return self._riders.add(rider)

    def get_rider(self, rider_id: str) -> Optional[Rider]:
        return self._riders.get(rider_id)

    def list_riders(self) -> List[Rider]:
        return self._riders.all()

    # ----------------------------------------------------------
    # Fare Estimation
    # ----------------------------------------------------------

    def estimate_fare(
        self,
        pickup      : Location,
        dropoff     : Location,
        vehicle_type: VehicleType = VehicleType.ECONOMY,
        now         : Optional[datetime] = None,
    ) -> FareBreakdown:
        surge = GeoService.get_surge_multiplier(pickup, now)
        return FareCalculator.calculate(pickup, dropoff, vehicle_type, surge)

    def compare_fares(
        self,
        pickup  : Location,
        dropoff : Location,
        now     : Optional[datetime] = None,
    ) -> Dict[str, FareBreakdown]:
        """Compare fares across all vehicle types."""
        result = {}
        for vt in VehicleType:
            surge = GeoService.get_surge_multiplier(pickup, now)
            result[vt.value] = FareCalculator.calculate(pickup, dropoff, vt, surge)
        return result

    # ----------------------------------------------------------
    # Ride lifecycle
    # ----------------------------------------------------------

    def request_ride(
        self,
        rider_id    : str,
        pickup      : Location,
        dropoff     : Location,
        vehicle_pref: VehicleType = VehicleType.ECONOMY,
        now         : Optional[datetime] = None,
    ) -> Ride:
        return self._service.request_ride(rider_id, pickup, dropoff, vehicle_pref, now)

    def match_driver(self, ride_id: str,
                     max_radius_km: float = 10.0,
                     now: Optional[datetime] = None) -> Ride:
        return self._service.match_driver(ride_id, max_radius_km, now)

    def driver_arriving(self, ride_id: str,
                        now: Optional[datetime] = None) -> Ride:
        return self._service.driver_arriving(ride_id, now)

    def start_trip(self, ride_id: str,
                   now: Optional[datetime] = None) -> Ride:
        return self._service.start_trip(ride_id, now)

    def complete_trip(self, ride_id: str,
                      actual_km: Optional[float] = None,
                      actual_min: Optional[float] = None,
                      now: Optional[datetime] = None) -> Ride:
        return self._service.complete_trip(ride_id, actual_km, actual_min, now)

    def cancel_ride(self, ride_id: str,
                    by: CancellationBy = CancellationBy.RIDER,
                    reason: str = "",
                    now: Optional[datetime] = None) -> Ride:
        return self._service.cancel_ride(ride_id, by, reason, now)

    # ----------------------------------------------------------
    # Ratings & Payments
    # ----------------------------------------------------------

    def rate_driver(self, ride_id: str, score: float, comment: str = "") -> None:
        self._service.rate_driver(ride_id, score, comment)

    def rate_rider(self, ride_id: str, score: float, comment: str = "") -> None:
        self._service.rate_rider(ride_id, score, comment)

    def pay(self, ride_id: str,
            method: PaymentMethod = PaymentMethod.CREDIT_CARD,
            now: Optional[datetime] = None) -> Payment:
        return self._service.process_payment(ride_id, method, now)

    # ----------------------------------------------------------
    # Queries
    # ----------------------------------------------------------

    def get_ride(self, ride_id: str) -> Optional[Ride]:
        return self._rides.get(ride_id)

    def list_rides(self, rider_id: Optional[str] = None,
                   driver_id: Optional[str] = None) -> List[Ride]:
        if rider_id:
            return self._rides.by_rider(rider_id)
        if driver_id:
            return self._rides.by_driver(driver_id)
        return self._rides.all()

    def active_rides(self) -> List[Ride]:
        return self._rides.active()

    # ----------------------------------------------------------
    # Matching strategy switch
    # ----------------------------------------------------------

    def use_nearest_matching(self) -> None:
        self._matcher.strategy = NearestDriverStrategy()

    def use_rated_matching(self) -> None:
        self._matcher.strategy = HighestRatedStrategy()

    def use_vehicle_matching(self) -> None:
        self._matcher.strategy = VehiclePreferenceStrategy()

    # ----------------------------------------------------------
    # Event bus
    # ----------------------------------------------------------

    @property
    def event_bus(self) -> EventBus:
        return self._bus

    @property
    def event_history(self):
        return self._bus.history
