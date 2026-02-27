"""
tests/test_pricing.py — Unit tests for the PricingEngine and strategies.
"""
from __future__ import annotations

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date
from hotel.models import Guest, LoyaltyTier, Room, RoomType, RoomStatus
from hotel.pricing import (
    BasePricingStrategy,
    CorporatePricingStrategy,
    EarlyBirdPricingStrategy,
    LoyaltyPricingStrategy,
    PricingEngine,
    SeasonalPricingStrategy,
    WeekendPricingStrategy,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def standard_room():
    return Room(
        number="101", room_type=RoomType.DOUBLE, floor=1, base_rate=100.0
    )


@pytest.fixture
def standard_guest():
    return Guest(name="Test", email="t@t.com", loyalty_tier=LoyaltyTier.STANDARD)


@pytest.fixture
def gold_guest():
    return Guest(name="Gold", email="g@g.com", loyalty_tier=LoyaltyTier.GOLD)


@pytest.fixture
def platinum_guest():
    return Guest(name="Plat", email="p@p.com", loyalty_tier=LoyaltyTier.PLATINUM)


# ============================================================
# BasePricingStrategy
# ============================================================

def test_base_pricing_correct(standard_room, standard_guest):
    bd: dict = {}
    total = BasePricingStrategy().apply(0, standard_room, standard_guest,
                                       date(2025, 3, 10), date(2025, 3, 13), bd)
    assert total == 300.0      # 100 × 3 nights
    assert bd["nights"] == 3
    assert bd["base_rate"] == 100.0


def test_base_pricing_one_night(standard_room, standard_guest):
    bd: dict = {}
    total = BasePricingStrategy().apply(0, standard_room, standard_guest,
                                       date(2025, 4, 1), date(2025, 4, 2), bd)
    assert total == 100.0


# ============================================================
# SeasonalPricingStrategy
# ============================================================

def test_seasonal_surcharge_applied_in_june(standard_room, standard_guest):
    """Jul 1–5 is peak: all 4 nights attract 30% surcharge."""
    bd    = {}
    base  = BasePricingStrategy().apply(0, standard_room, standard_guest,
                                       date(2025, 7, 1), date(2025, 7, 5), bd)
    total = SeasonalPricingStrategy().apply(base, standard_room, standard_guest,
                                           date(2025, 7, 1), date(2025, 7, 5), bd)
    # 4 peak nights × 100 × 0.30 = 120 surcharge
    assert total == 400.0 + 120.0


def test_seasonal_no_surcharge_in_march(standard_room, standard_guest):
    bd   = {}
    base = BasePricingStrategy().apply(0, standard_room, standard_guest,
                                      date(2025, 3, 1), date(2025, 3, 5), bd)
    total = SeasonalPricingStrategy().apply(base, standard_room, standard_guest,
                                            date(2025, 3, 1), date(2025, 3, 5), bd)
    assert total == base
    assert bd.get("seasonal_surcharge", 0) == 0.0


# ============================================================
# WeekendPricingStrategy
# ============================================================

def test_weekend_surcharge(standard_room, standard_guest):
    """2025-08-08 is a Friday; 2025-08-09 is Saturday — 2 weekend nights."""
    ci, co = date(2025, 8, 8), date(2025, 8, 11)  # Fri–Mon (3 nights)
    bd   = {}
    base = BasePricingStrategy().apply(0, standard_room, standard_guest, ci, co, bd)
    total = WeekendPricingStrategy().apply(base, standard_room, standard_guest, ci, co, bd)
    # 2 weekend nights × 100 × 0.20 = 40 extra
    assert total == 300.0 + 40.0


def test_no_weekend_surcharge_midweek(standard_room, standard_guest):
    ci, co = date(2025, 8, 11), date(2025, 8, 14)  # Mon–Thu (3 nights)
    bd   = {}
    base = BasePricingStrategy().apply(0, standard_room, standard_guest, ci, co, bd)
    total = WeekendPricingStrategy().apply(base, standard_room, standard_guest, ci, co, bd)
    assert total == base


# ============================================================
# LoyaltyPricingStrategy
# ============================================================

def test_loyalty_standard_no_discount(standard_room, standard_guest):
    bd   = {}
    base = 300.0
    total = LoyaltyPricingStrategy().apply(base, standard_room, standard_guest,
                                           date(2025, 5, 1), date(2025, 5, 4), bd)
    assert total == 300.0
    assert bd["loyalty_discount"] == 0.0


def test_loyalty_gold_10_percent(standard_room, gold_guest):
    bd   = {}
    base = 300.0
    total = LoyaltyPricingStrategy().apply(base, standard_room, gold_guest,
                                           date(2025, 5, 1), date(2025, 5, 4), bd)
    assert total == 270.0   # 300 - 10%
    assert bd["loyalty_discount"] == -30.0


def test_loyalty_platinum_20_percent(standard_room, platinum_guest):
    bd   = {}
    base = 300.0
    total = LoyaltyPricingStrategy().apply(base, standard_room, platinum_guest,
                                           date(2025, 5, 1), date(2025, 5, 4), bd)
    assert total == 240.0   # 300 - 20%


# ============================================================
# CorporatePricingStrategy
# ============================================================

def test_corporate_discount_not_applied_without_flag(standard_room, standard_guest):
    bd   = {}
    base = 300.0
    total = CorporatePricingStrategy().apply(base, standard_room, standard_guest,
                                             date(2025, 5, 1), date(2025, 5, 4), bd)
    assert total == 300.0


def test_corporate_discount_applied_with_flag(standard_room, standard_guest):
    standard_guest.is_corporate = True  # type: ignore[attr-defined]
    bd   = {}
    base = 300.0
    total = CorporatePricingStrategy().apply(base, standard_room, standard_guest,
                                             date(2025, 5, 1), date(2025, 5, 4), bd)
    assert total == pytest.approx(255.0)   # 300 - 15%


# ============================================================
# PricingEngine (composition)
# ============================================================

def test_engine_returns_positive_total(standard_room, standard_guest):
    engine = PricingEngine()
    total, bd = engine.calculate(standard_room, standard_guest,
                                 date(2025, 3, 10), date(2025, 3, 13))
    assert total > 0
    assert "final_total" in bd


def test_engine_check_out_not_after_check_in_raises(standard_room, standard_guest):
    engine = PricingEngine()
    with pytest.raises(ValueError):
        engine.calculate(standard_room, standard_guest,
                         date(2025, 3, 13), date(2025, 3, 10))


def test_engine_same_day_raises(standard_room, standard_guest):
    engine = PricingEngine()
    with pytest.raises(ValueError):
        engine.calculate(standard_room, standard_guest,
                         date(2025, 3, 10), date(2025, 3, 10))


def test_engine_peak_season_higher_than_offseason(standard_room, standard_guest):
    engine = PricingEngine()
    # Same 5-night stay, July vs March
    peak_total, _ = engine.calculate(standard_room, standard_guest,
                                     date(2025, 7, 1), date(2025, 7, 6))
    off_total, _  = engine.calculate(standard_room, standard_guest,
                                     date(2025, 3, 1), date(2025, 3, 6))
    assert peak_total > off_total
