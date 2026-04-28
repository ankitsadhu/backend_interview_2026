"""
tests/test_ride_service.py — Integration tests for the ride lifecycle.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime, timedelta

from rideshare import RideShareSystem, Location, VehicleType, Vehicle, RideStatus, PaymentMethod
from rideshare.models import CancellationBy, DriverStatus
from rideshare.ride_service import InvalidRideTransition


# ============================================================
# Fixtures
# ============================================================

PICKUP  = Location(40.7580, -73.9855, "Times Square")
DROPOFF = Location(40.7829, -73.9654, "Central Park")
NOW     = datetime(2026, 3, 10, 14, 0)


def _make_app():
    app = RideShareSystem("Test")
    rider = app.register_rider("Alice", "alice@t.com", "+1-555")
    driver = app.register_driver("Bob", "+1-666",
                                 Vehicle(VehicleType.ECONOMY, "Toyota", "Camry", "T123"))
    app.go_online(driver.id, Location(40.7585, -73.9860))
    return app, rider, driver


# ============================================================
# Full lifecycle
# ============================================================

def test_full_ride_lifecycle():
    app, rider, driver = _make_app()

    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    assert ride.status == RideStatus.REQUESTED
    assert ride.estimated_fare > 0

    ride = app.match_driver(ride.id, now=NOW)
    assert ride.status == RideStatus.MATCHED
    assert ride.driver.id == driver.id

    ride = app.driver_arriving(ride.id, now=NOW)
    assert ride.status == RideStatus.DRIVER_ARRIVING

    ride = app.start_trip(ride.id, now=NOW)
    assert ride.status == RideStatus.IN_PROGRESS

    ride = app.complete_trip(ride.id, actual_km=3.0, actual_min=10.0, now=NOW)
    assert ride.status == RideStatus.COMPLETED
    assert ride.fare > 0
    assert ride.fare_breakdown is not None


def test_driver_becomes_available_after_trip():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    ride = app.match_driver(ride.id, now=NOW)
    assert driver.status == DriverStatus.ON_TRIP

    app.driver_arriving(ride.id, now=NOW)
    app.start_trip(ride.id, now=NOW)
    app.complete_trip(ride.id, now=NOW)
    assert driver.status == DriverStatus.AVAILABLE


# ============================================================
# State machine
# ============================================================

def test_cannot_start_trip_before_match():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    with pytest.raises(InvalidRideTransition):
        app.start_trip(ride.id)


def test_cannot_complete_requested_ride():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    with pytest.raises(InvalidRideTransition):
        app.complete_trip(ride.id)


def test_cannot_cancel_in_progress():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    app.match_driver(ride.id, now=NOW)
    app.driver_arriving(ride.id, now=NOW)
    app.start_trip(ride.id, now=NOW)
    with pytest.raises(InvalidRideTransition):
        app.cancel_ride(ride.id)


# ============================================================
# Cancellation
# ============================================================

def test_cancel_free_before_2min():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    ride = app.match_driver(ride.id, now=NOW)
    cancel_time = NOW + timedelta(seconds=60)  # 1 min after match
    ride = app.cancel_ride(ride.id, CancellationBy.RIDER, now=cancel_time)
    assert ride.status == RideStatus.CANCELLED
    assert ride.cancel_fee == 0.0


def test_cancel_fee_after_3min():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    ride = app.match_driver(ride.id, now=NOW)
    cancel_time = NOW + timedelta(minutes=3)
    ride = app.cancel_ride(ride.id, CancellationBy.RIDER, now=cancel_time)
    assert ride.cancel_fee == 3.0


def test_cancel_fee_after_6min():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    ride = app.match_driver(ride.id, now=NOW)
    cancel_time = NOW + timedelta(minutes=6)
    ride = app.cancel_ride(ride.id, CancellationBy.RIDER, now=cancel_time)
    assert ride.cancel_fee == 5.0


def test_driver_released_on_cancel():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    ride = app.match_driver(ride.id, now=NOW)
    assert driver.status == DriverStatus.ON_TRIP
    app.cancel_ride(ride.id, now=NOW)
    assert driver.status == DriverStatus.AVAILABLE


# ============================================================
# Ratings
# ============================================================

def test_rate_driver():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    app.match_driver(ride.id, now=NOW)
    app.driver_arriving(ride.id, now=NOW)
    app.start_trip(ride.id, now=NOW)
    app.complete_trip(ride.id, now=NOW)

    app.rate_driver(ride.id, 4.5)
    assert driver.rating_count == 1
    assert driver.rating == 4.5


def test_rate_must_be_1_to_5():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    app.match_driver(ride.id, now=NOW)
    app.driver_arriving(ride.id, now=NOW)
    app.start_trip(ride.id, now=NOW)
    app.complete_trip(ride.id, now=NOW)

    with pytest.raises(ValueError, match="1-5"):
        app.rate_driver(ride.id, 6.0)


def test_cannot_rate_uncompleted_ride():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    with pytest.raises(ValueError, match="completed"):
        app.rate_driver(ride.id, 5.0)


# ============================================================
# Payment
# ============================================================

def test_payment():
    app, rider, driver = _make_app()
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    app.match_driver(ride.id, now=NOW)
    app.driver_arriving(ride.id, now=NOW)
    app.start_trip(ride.id, now=NOW)
    app.complete_trip(ride.id, actual_km=3.0, actual_min=10.0, now=NOW)

    payment = app.pay(ride.id, PaymentMethod.CREDIT_CARD)
    assert payment.amount == ride.fare
    assert payment.status.value == "COMPLETED"


# ============================================================
# No driver available
# ============================================================

def test_no_drivers_raises():
    app = RideShareSystem("Test")
    rider = app.register_rider("Solo", "solo@t.com")
    ride = app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    with pytest.raises(ValueError, match="No drivers"):
        app.match_driver(ride.id)


# ============================================================
# Duplicate active ride
# ============================================================

def test_cannot_have_two_active_rides():
    app, rider, driver = _make_app()
    # Add a second driver
    d2 = app.register_driver("Carol", "+1-777",
                             Vehicle(VehicleType.COMFORT, "Honda", "Civic", "H456"))
    app.go_online(d2.id, Location(40.7600, -73.9840))

    app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
    with pytest.raises(ValueError, match="active ride"):
        app.request_ride(rider.id, PICKUP, DROPOFF, now=NOW)
