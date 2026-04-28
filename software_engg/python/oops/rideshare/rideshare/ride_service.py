"""
ride_service.py — Core ride lifecycle management.

State machine: REQUESTED → MATCHED → DRIVER_ARRIVING → IN_PROGRESS → COMPLETED
                  ↓          ↓            ↓                ↓
               CANCELLED  CANCELLED   CANCELLED        (no cancel)
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from .geo import GeoService
from .matching import MatchingEngine
from .models import (
    CancellationBy, Driver, DriverStatus, FareBreakdown,
    Location, Payment, PaymentMethod, PaymentStatus,
    Ride, RideStatus, Rider, VehicleType,
)
from .notifications import EventBus, EventType, RideEvent
from .pricing import FareCalculator
from .repository import DriverRepository, RideRepository, RiderRepository


# ============================================================
# State Machine
# ============================================================

_TRANSITIONS: Dict[RideStatus, set] = {
    RideStatus.REQUESTED      : {RideStatus.MATCHED, RideStatus.CANCELLED},
    RideStatus.MATCHED        : {RideStatus.DRIVER_ARRIVING, RideStatus.CANCELLED},
    RideStatus.DRIVER_ARRIVING: {RideStatus.IN_PROGRESS, RideStatus.CANCELLED},
    RideStatus.IN_PROGRESS    : {RideStatus.COMPLETED},
    RideStatus.COMPLETED      : set(),
    RideStatus.CANCELLED      : set(),
}


class InvalidRideTransition(Exception):
    def __init__(self, current: RideStatus, target: RideStatus):
        super().__init__(f"Cannot transition from {current.value} → {target.value}")


def _validate_transition(current: RideStatus, target: RideStatus) -> None:
    if target not in _TRANSITIONS.get(current, set()):
        raise InvalidRideTransition(current, target)


# ============================================================
# Ride Service
# ============================================================

class RideService:
    """Orchestrates the entire ride lifecycle."""

    def __init__(
        self,
        drivers  : DriverRepository,
        riders   : RiderRepository,
        rides    : RideRepository,
        matcher  : MatchingEngine,
        bus      : EventBus,
    ) -> None:
        self._drivers  = drivers
        self._riders   = riders
        self._rides    = rides
        self._matcher  = matcher
        self._bus      = bus

    # ----------------------------------------------------------
    # Request a ride
    # ----------------------------------------------------------

    def request_ride(
        self,
        rider_id    : str,
        pickup      : Location,
        dropoff     : Location,
        vehicle_pref: VehicleType = VehicleType.ECONOMY,
        now         : Optional[datetime] = None,
    ) -> Ride:
        now = now or datetime.now()
        rider = self._riders.get(rider_id)
        if not rider:
            raise ValueError(f"Rider {rider_id} not found")

        # Check rider doesn't have an active ride
        active = [r for r in self._rides.by_rider(rider_id)
                  if r.status not in (RideStatus.COMPLETED, RideStatus.CANCELLED)]
        if active:
            raise ValueError("Rider already has an active ride")

        # Get surge
        surge = GeoService.get_surge_multiplier(pickup, now)

        # Estimate fare
        breakdown = FareCalculator.calculate(
            pickup, dropoff, vehicle_pref, surge
        )

        ride = Ride(
            rider           = rider,
            pickup          = pickup,
            dropoff         = dropoff,
            vehicle_pref    = vehicle_pref,
            status          = RideStatus.REQUESTED,
            estimated_fare  = breakdown.total,
            fare_breakdown  = breakdown,
            distance_km     = breakdown.distance_km,
            duration_min    = breakdown.duration_min,
            surge_multiplier= surge,
            requested_at    = now,
        )
        self._rides.add(ride)

        self._bus.publish(RideEvent(
            EventType.RIDE_REQUESTED,
            data={"ride_id": ride.id, "rider_name": rider.name,
                  "pickup": str(pickup), "dropoff": str(dropoff),
                  "estimated_fare": breakdown.total,
                  "surge": surge},
        ))
        return ride

    # ----------------------------------------------------------
    # Match driver
    # ----------------------------------------------------------

    def match_driver(
        self,
        ride_id      : str,
        max_radius_km: float = 10.0,
        now          : Optional[datetime] = None,
    ) -> Ride:
        now  = now or datetime.now()
        ride = self._get_ride(ride_id)
        _validate_transition(ride.status, RideStatus.MATCHED)

        available = self._drivers.available()
        driver = self._matcher.find_best_driver(
            available, ride.pickup, ride.vehicle_pref, max_radius_km
        )
        if not driver:
            raise ValueError("No drivers available nearby")

        ride.driver     = driver
        ride.status     = RideStatus.MATCHED
        ride.matched_at = now
        driver.status   = DriverStatus.ON_TRIP

        eta = GeoService.estimate_eta(driver.location, ride.pickup)

        self._bus.publish(RideEvent(
            EventType.DRIVER_MATCHED,
            data={"ride_id": ride.id, "rider_name": ride.rider.name,
                  "driver_name": driver.name,
                  "driver_vehicle": str(driver.vehicle),
                  "eta_min": eta},
        ))
        return ride

    # ----------------------------------------------------------
    # Driver arriving
    # ----------------------------------------------------------

    def driver_arriving(
        self,
        ride_id: str,
        now    : Optional[datetime] = None,
    ) -> Ride:
        now  = now or datetime.now()
        ride = self._get_ride(ride_id)
        _validate_transition(ride.status, RideStatus.DRIVER_ARRIVING)

        ride.status    = RideStatus.DRIVER_ARRIVING
        ride.pickup_at = now

        self._bus.publish(RideEvent(
            EventType.DRIVER_ARRIVING,
            data={"ride_id": ride.id, "rider_name": ride.rider.name,
                  "driver_name": ride.driver.name},
        ))
        return ride

    # ----------------------------------------------------------
    # Start trip
    # ----------------------------------------------------------

    def start_trip(
        self,
        ride_id: str,
        now    : Optional[datetime] = None,
    ) -> Ride:
        now  = now or datetime.now()
        ride = self._get_ride(ride_id)
        _validate_transition(ride.status, RideStatus.IN_PROGRESS)

        ride.status     = RideStatus.IN_PROGRESS
        ride.started_at = now

        self._bus.publish(RideEvent(
            EventType.TRIP_STARTED,
            data={"ride_id": ride.id, "rider_name": ride.rider.name,
                  "driver_name": ride.driver.name},
        ))
        return ride

    # ----------------------------------------------------------
    # Complete trip
    # ----------------------------------------------------------

    def complete_trip(
        self,
        ride_id     : str,
        actual_km   : Optional[float] = None,
        actual_min  : Optional[float] = None,
        now         : Optional[datetime] = None,
    ) -> Ride:
        now  = now or datetime.now()
        ride = self._get_ride(ride_id)
        _validate_transition(ride.status, RideStatus.COMPLETED)

        # Use actual distance/time if provided, else keep estimates
        dist = actual_km  if actual_km  is not None else ride.distance_km
        dur  = actual_min if actual_min is not None else ride.duration_min

        # Recalculate fare with actual values
        breakdown = FareCalculator.calculate(
            ride.pickup, ride.dropoff, ride.vehicle_pref,
            ride.surge_multiplier, dist, dur,
        )

        ride.distance_km    = dist
        ride.duration_min   = dur
        ride.fare           = breakdown.total
        ride.fare_breakdown = breakdown
        ride.status         = RideStatus.COMPLETED
        ride.completed_at   = now

        # Update driver & rider stats
        ride.driver.status       = DriverStatus.AVAILABLE
        ride.driver.total_trips += 1
        ride.driver.earnings    += breakdown.total * (1 - 0.25)  # Driver gets 75%
        ride.rider.total_trips  += 1
        ride.rider.total_spent  += breakdown.total

        self._bus.publish(RideEvent(
            EventType.TRIP_COMPLETED,
            data={"ride_id": ride.id, "rider_name": ride.rider.name,
                  "driver_name": ride.driver.name,
                  "fare": breakdown.total,
                  "distance_km": dist, "duration_min": dur},
        ))
        return ride

    # ----------------------------------------------------------
    # Cancel ride
    # ----------------------------------------------------------

    def cancel_ride(
        self,
        ride_id : str,
        by      : CancellationBy = CancellationBy.RIDER,
        reason  : str = "",
        now     : Optional[datetime] = None,
    ) -> Ride:
        now  = now or datetime.now()
        ride = self._get_ride(ride_id)
        _validate_transition(ride.status, RideStatus.CANCELLED)

        # Calculate cancellation fee
        cancel_fee = 0.0
        if ride.matched_at:
            minutes_since_match = (now - ride.matched_at).total_seconds() / 60
            cancel_fee = FareCalculator.cancellation_fee(minutes_since_match)

        ride.status       = RideStatus.CANCELLED
        ride.cancelled_at = now
        ride.cancelled_by = by
        ride.cancel_reason= reason
        ride.cancel_fee   = cancel_fee

        # Release driver
        if ride.driver:
            ride.driver.status = DriverStatus.AVAILABLE

        self._bus.publish(RideEvent(
            EventType.RIDE_CANCELLED,
            data={"ride_id": ride.id, "rider_name": ride.rider.name,
                  "cancelled_by": by.value, "reason": reason,
                  "cancel_fee": cancel_fee},
        ))
        return ride

    # ----------------------------------------------------------
    # Rate ride
    # ----------------------------------------------------------

    def rate_driver(self, ride_id: str, score: float,
                    comment: str = "") -> None:
        if not 1 <= score <= 5:
            raise ValueError("Rating must be 1-5")
        ride = self._get_ride(ride_id)
        if ride.status != RideStatus.COMPLETED:
            raise ValueError("Can only rate completed rides")
        ride.driver_rating = score
        ride.driver.add_rating(score)

        self._bus.publish(RideEvent(
            EventType.RATING_SUBMITTED,
            data={"ride_id": ride.id, "from": "rider",
                  "to": ride.driver.name, "score": score},
        ))

    def rate_rider(self, ride_id: str, score: float,
                   comment: str = "") -> None:
        if not 1 <= score <= 5:
            raise ValueError("Rating must be 1-5")
        ride = self._get_ride(ride_id)
        if ride.status != RideStatus.COMPLETED:
            raise ValueError("Can only rate completed rides")
        ride.rider_rating = score
        ride.rider.add_rating(score)

        self._bus.publish(RideEvent(
            EventType.RATING_SUBMITTED,
            data={"ride_id": ride.id, "from": "driver",
                  "to": ride.rider.name, "score": score},
        ))

    # ----------------------------------------------------------
    # Payment
    # ----------------------------------------------------------

    def process_payment(
        self,
        ride_id: str,
        method : PaymentMethod = PaymentMethod.CREDIT_CARD,
        now    : Optional[datetime] = None,
    ) -> Payment:
        now  = now or datetime.now()
        ride = self._get_ride(ride_id)
        if ride.status != RideStatus.COMPLETED:
            raise ValueError("Can only pay for completed rides")

        payment = Payment(
            ride_id = ride.id,
            amount  = ride.fare,
            method  = method,
            status  = PaymentStatus.COMPLETED,
            paid_at = now,
        )

        self._bus.publish(RideEvent(
            EventType.PAYMENT_PROCESSED,
            data={"ride_id": ride.id, "amount": payment.amount,
                  "method": method.value},
        ))
        return payment

    # ----------------------------------------------------------
    # Internal
    # ----------------------------------------------------------

    def _get_ride(self, ride_id: str) -> Ride:
        ride = self._rides.get(ride_id)
        if not ride:
            raise ValueError(f"Ride {ride_id} not found")
        return ride
