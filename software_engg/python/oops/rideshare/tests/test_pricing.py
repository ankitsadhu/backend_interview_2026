"""
tests/test_pricing.py — Fare calculation tests.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from rideshare.models import Location, VehicleType
from rideshare.pricing import FareCalculator


PICKUP  = Location(40.7580, -73.9855)
DROPOFF = Location(40.7829, -73.9654)


# ============================================================
# Basic fare calculations
# ============================================================

def test_economy_fare_positive():
    bd = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.ECONOMY)
    assert bd.total > 0


def test_premium_more_expensive_than_economy():
    eco = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.ECONOMY)
    pre = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.PREMIUM)
    assert pre.total > eco.total


def test_suv_more_expensive_than_comfort():
    com = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.COMFORT)
    suv = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.SUV)
    assert suv.total > com.total


# ============================================================
# Surge pricing
# ============================================================

def test_surge_increases_fare():
    normal = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.ECONOMY, surge_multiplier=1.0)
    surged = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.ECONOMY, surge_multiplier=2.0)
    assert surged.total > normal.total


def test_surge_amount_recorded():
    bd = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.ECONOMY, surge_multiplier=1.5)
    assert bd.surge_amount > 0
    assert bd.surge_multiplier == 1.5


def test_no_surge_at_1x():
    bd = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.ECONOMY, surge_multiplier=1.0)
    assert bd.surge_amount == 0.0


# ============================================================
# Breakdown correctness
# ============================================================

def test_breakdown_components():
    bd = FareCalculator.calculate(
        PICKUP, DROPOFF, VehicleType.ECONOMY,
        distance_km=10.0, duration_min=20.0,
    )
    assert bd.base_fare == 2.50
    assert bd.distance_charge == 12.0   # 10 × 1.20
    assert bd.time_charge == 3.0        # 20 × 0.15
    assert bd.distance_km == 10.0
    assert bd.duration_min == 20.0


def test_minimum_fare():
    """Very short trip should still meet minimum fare."""
    bd = FareCalculator.calculate(
        PICKUP, DROPOFF, VehicleType.ECONOMY,
        distance_km=0.1, duration_min=1.0,
    )
    assert bd.total >= 5.00  # Economy minimum


def test_platform_fee_applied():
    bd = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.ECONOMY)
    assert bd.platform_fee > 0


# ============================================================
# Fare estimation range
# ============================================================

def test_fare_range():
    low, high = FareCalculator.estimate_fare_range(PICKUP, DROPOFF, VehicleType.ECONOMY)
    assert low < high
    bd = FareCalculator.calculate(PICKUP, DROPOFF, VehicleType.ECONOMY)
    assert low <= bd.total <= high


# ============================================================
# Cancellation fee
# ============================================================

def test_cancel_free_under_2min():
    assert FareCalculator.cancellation_fee(1.0) == 0.0


def test_cancel_3_bucks_2_to_5_min():
    assert FareCalculator.cancellation_fee(3.0) == 3.0


def test_cancel_5_bucks_over_5min():
    assert FareCalculator.cancellation_fee(6.0) == 5.0
