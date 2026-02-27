"""
tests/test_geo.py — Geographic utility tests.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime
from rideshare.geo import GeoService
from rideshare.models import Location


# Well-known NYC locations
TIMES_SQUARE = Location(40.7580, -73.9855, "Times Square")
CENTRAL_PARK = Location(40.7829, -73.9654, "Central Park")
JFK_AIRPORT  = Location(40.6413, -73.7781, "JFK Airport")
STATUE_LIB   = Location(40.6892, -74.0445, "Statue of Liberty")


# ============================================================
# Haversine
# ============================================================

def test_haversine_same_point():
    dist = GeoService.haversine(TIMES_SQUARE, TIMES_SQUARE)
    assert dist == 0.0


def test_haversine_ts_to_cp():
    """Times Square → Central Park is ~3 km."""
    dist = GeoService.haversine(TIMES_SQUARE, CENTRAL_PARK)
    assert 2.5 < dist < 4.0


def test_haversine_ts_to_jfk():
    """Times Square → JFK is ~20 km."""
    dist = GeoService.haversine(TIMES_SQUARE, JFK_AIRPORT)
    assert 18.0 < dist < 25.0


def test_haversine_symmetry():
    d1 = GeoService.haversine(TIMES_SQUARE, JFK_AIRPORT)
    d2 = GeoService.haversine(JFK_AIRPORT, TIMES_SQUARE)
    assert d1 == d2


# ============================================================
# Duration estimation
# ============================================================

def test_duration_basic():
    dur = GeoService.estimate_duration(30.0, 30.0)  # 30km at 30km/h
    assert dur == 60.0


def test_duration_zero_speed():
    assert GeoService.estimate_duration(10.0, 0) == 0.0


# ============================================================
# ETA
# ============================================================

def test_eta_nearby():
    """Nearby driver should have short ETA."""
    driver_loc = Location(40.7590, -73.9850, "Near TS")
    eta = GeoService.estimate_eta(driver_loc, TIMES_SQUARE)
    assert eta < 5.0  # Less than 5 minutes


# ============================================================
# Surge multiplier
# ============================================================

def test_surge_normal_afternoon():
    normal = datetime(2026, 3, 10, 14, 0)  # Tuesday 2 PM
    surge = GeoService.get_surge_multiplier(TIMES_SQUARE, normal)
    assert surge == 1.0  # No surge


def test_surge_rush_hour():
    rush = datetime(2026, 3, 10, 17, 30)  # Tuesday 5:30 PM
    surge = GeoService.get_surge_multiplier(TIMES_SQUARE, rush)
    assert surge >= 1.5


def test_surge_late_night():
    late = datetime(2026, 3, 10, 23, 30)  # 11:30 PM
    surge = GeoService.get_surge_multiplier(TIMES_SQUARE, late)
    assert surge >= 1.8


def test_surge_capped_at_3():
    """Surge should never exceed 3.0."""
    late_fri = datetime(2026, 3, 13, 23, 30)  # Friday 11:30 PM
    downtown = Location(40.75, -73.98)
    surge = GeoService.get_surge_multiplier(downtown, late_fri)
    assert surge <= 3.0


# ============================================================
# Radius check
# ============================================================

def test_within_radius():
    assert GeoService.is_within_radius(TIMES_SQUARE, CENTRAL_PARK, 5.0)


def test_outside_radius():
    assert not GeoService.is_within_radius(TIMES_SQUARE, JFK_AIRPORT, 5.0)
