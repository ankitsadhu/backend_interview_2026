"""
tests/test_matching.py — Driver matching strategy tests.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rideshare.matching import (
    HighestRatedStrategy, MatchingEngine, NearestDriverStrategy,
    VehiclePreferenceStrategy,
)
from rideshare.models import Driver, DriverStatus, Location, Vehicle, VehicleType


# ============================================================
# Helpers
# ============================================================

def _make_driver(name, lat, lng, rating_sum=20, rating_count=4,
                 vtype=VehicleType.ECONOMY, status=DriverStatus.AVAILABLE):
    d = Driver(name=name, phone="", status=status,
               location=Location(lat, lng),
               vehicle=Vehicle(vtype, "Test", "Car", "X123"),
               rating_sum=rating_sum, rating_count=rating_count)
    return d

PICKUP = Location(40.7580, -73.9855)  # Times Square


# ============================================================
# Nearest strategy
# ============================================================

def test_nearest_returns_closest():
    close  = _make_driver("Close",  40.7585, -73.9860)   # ~50m
    medium = _make_driver("Medium", 40.7650, -73.9800)   # ~1km
    far    = _make_driver("Far",    40.8000, -73.9500)   # ~5km

    result = NearestDriverStrategy().find_drivers(
        [far, close, medium], PICKUP
    )
    assert result[0].name == "Close"


def test_nearest_excludes_offline():
    online  = _make_driver("Online", 40.7585, -73.9860)
    offline = _make_driver("Offline", 40.7583, -73.9858,
                           status=DriverStatus.OFFLINE)

    result = NearestDriverStrategy().find_drivers(
        [online, offline], PICKUP
    )
    assert len(result) == 1
    assert result[0].name == "Online"


def test_nearest_respects_radius():
    close = _make_driver("Close", 40.7585, -73.9860)  # ~50m
    far   = _make_driver("Far",   41.0000, -74.2000)  # ~30km

    result = NearestDriverStrategy().find_drivers(
        [close, far], PICKUP, max_radius_km=5.0
    )
    assert len(result) == 1


# ============================================================
# Highest rated strategy
# ============================================================

def test_rated_returns_highest():
    low  = _make_driver("Low",  40.7585, -73.9860, rating_sum=15, rating_count=5)   # 3.0
    mid  = _make_driver("Mid",  40.7590, -73.9850, rating_sum=22, rating_count=5)   # 4.4
    high = _make_driver("High", 40.7600, -73.9840, rating_sum=24, rating_count=5)   # 4.8

    result = HighestRatedStrategy().find_drivers(
        [low, mid, high], PICKUP
    )
    assert result[0].name == "High"
    assert result[-1].name == "Low"


# ============================================================
# Vehicle preference strategy
# ============================================================

def test_vehicle_pref_matches_type():
    eco = _make_driver("Eco", 40.7590, -73.9850, vtype=VehicleType.ECONOMY)
    pre = _make_driver("Pre", 40.7585, -73.9860, vtype=VehicleType.PREMIUM)

    result = VehiclePreferenceStrategy().find_drivers(
        [eco, pre], PICKUP, vehicle_pref=VehicleType.PREMIUM
    )
    assert result[0].name == "Pre"


def test_vehicle_pref_falls_back_to_nearest():
    """If no matching vehicle type, fall back to nearest of any type."""
    eco1 = _make_driver("Eco1", 40.7585, -73.9860, vtype=VehicleType.ECONOMY)
    eco2 = _make_driver("Eco2", 40.7700, -73.9800, vtype=VehicleType.ECONOMY)

    result = VehiclePreferenceStrategy().find_drivers(
        [eco2, eco1], PICKUP, vehicle_pref=VehicleType.PREMIUM
    )
    assert result[0].name == "Eco1"  # Closest, even though wrong type


# ============================================================
# Matching Engine
# ============================================================

def test_engine_find_best_driver():
    close = _make_driver("Close", 40.7585, -73.9860)
    far   = _make_driver("Far",   40.7700, -73.9800)

    engine = MatchingEngine()
    best = engine.find_best_driver([far, close], PICKUP)
    assert best.name == "Close"


def test_engine_no_drivers_returns_none():
    engine = MatchingEngine()
    assert engine.find_best_driver([], PICKUP) is None


def test_engine_strategy_swap():
    engine = MatchingEngine(NearestDriverStrategy())
    assert isinstance(engine.strategy, NearestDriverStrategy)

    engine.strategy = HighestRatedStrategy()
    assert isinstance(engine.strategy, HighestRatedStrategy)
