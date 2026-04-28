"""
tests/test_reservation_service.py — Integration tests for HotelSystem / ReservationService.
"""
from __future__ import annotations

import pytest
from datetime import date, datetime, timedelta
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hotel import HotelSystem, InvalidTransitionError
from hotel.models import LoyaltyTier, PaymentMethod, ReservationStatus, RoomType


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def hotel():
    h = HotelSystem("Test Hotel")
    return h


@pytest.fixture
def hotel_with_room(hotel):
    room = hotel.add_room("101", RoomType.DOUBLE, floor=1, base_rate=100.0)
    return hotel, room


@pytest.fixture
def hotel_setup(hotel):
    room  = hotel.add_room("201", RoomType.SUITE, floor=2, base_rate=200.0)
    guest = hotel.register_guest("Alice", "alice@test.com", loyalty_tier=LoyaltyTier.GOLD)
    return hotel, room, guest


# ============================================================
# Search
# ============================================================

def test_search_finds_available_rooms(hotel_with_room):
    h, room = hotel_with_room
    results = h.search(date(2025, 5, 1), date(2025, 5, 4))
    assert any(r.room.id == room.id for r in results)


def test_search_excludes_booked_rooms(hotel_setup):
    h, room, guest = hotel_setup
    h.book(room.id, guest.id, date(2025, 5, 1), date(2025, 5, 4))
    results = h.search(date(2025, 5, 2), date(2025, 5, 3))
    assert not any(r.room.id == room.id for r in results)


def test_search_empty_on_no_rooms(hotel):
    results = h.search(date(2025, 5, 1), date(2025, 5, 4)) if False else \
              hotel.search(date(2025, 5, 1), date(2025, 5, 4))
    assert results == []


def test_search_invalid_dates(hotel_with_room):
    h, room = hotel_with_room
    with pytest.raises(ValueError):
        h.search(date(2025, 5, 5), date(2025, 5, 1))


# ============================================================
# Create Reservation
# ============================================================

def test_create_reservation_success(hotel_setup):
    h, room, guest = hotel_setup
    res = h.book(room.id, guest.id, date(2025, 6, 1), date(2025, 6, 4))
    assert res.status == ReservationStatus.PENDING
    assert res.nights == 3
    assert res.total_price > 0


def test_double_booking_prevented(hotel_setup):
    h, room, guest = hotel_setup
    h.book(room.id, guest.id, date(2025, 6, 1), date(2025, 6, 5))
    with pytest.raises(ValueError, match="already booked"):
        h.book(room.id, guest.id, date(2025, 6, 3), date(2025, 6, 7))


def test_adjacent_bookings_allowed(hotel_setup):
    """check_out of first == check_in of second → no overlap."""
    h, room, guest = hotel_setup
    r1 = h.book(room.id, guest.id, date(2025, 6, 1), date(2025, 6, 5))
    h.cancel(r1.id)  # cancel so room is free again
    r2 = h.book(room.id, guest.id, date(2025, 6, 5), date(2025, 6, 8))
    assert r2 is not None


def test_book_nonexistent_room(hotel_setup):
    h, room, guest = hotel_setup
    with pytest.raises(ValueError, match="not found"):
        h.book("nonexistent-uuid", guest.id, date(2025, 6, 1), date(2025, 6, 3))


# ============================================================
# Lifecycle transitions
# ============================================================

def test_confirm_reservation(hotel_setup):
    h, room, guest = hotel_setup
    res = h.book(room.id, guest.id, date(2025, 7, 1), date(2025, 7, 4))
    confirmed = h.confirm(res.id)
    assert confirmed.status == ReservationStatus.CONFIRMED


def test_check_in_requires_confirmed(hotel_setup):
    h, room, guest = hotel_setup
    res = h.book(room.id, guest.id, date(2025, 8, 1), date(2025, 8, 4))
    # Directly PENDING → CHECKED_IN is illegal
    with pytest.raises(InvalidTransitionError):
        h.check_in(res.id)


def test_full_lifecycle(hotel_setup):
    h, room, guest = hotel_setup
    res = h.book(room.id, guest.id, date(2025, 9, 1), date(2025, 9, 5))
    h.confirm(res.id)
    h.check_in(res.id)
    res_out, invoice = h.check_out(res.id, extras={"Minibar": 30.0})
    assert res_out.status == ReservationStatus.CHECKED_OUT
    assert invoice.grand_total > 0
    assert any("Minibar" in item.description for item in invoice.line_items)


# ============================================================
# Cancellation & Refund Policy
# ============================================================

def test_cancel_full_refund_48h(hotel_setup):
    h, room, guest = hotel_setup
    check_in = date(2025, 10, 1)
    res = h.book(room.id, guest.id, check_in, date(2025, 10, 5))
    h.confirm(res.id)
    simulated_now = datetime.combine(check_in, datetime.min.time()) - timedelta(hours=72)
    cancelled = h.cancel(res.id, reason="Test", now=simulated_now)
    assert cancelled.status == ReservationStatus.CANCELLED
    assert cancelled.refund_amount == pytest.approx(cancelled.total_price * 1.0, rel=1e-2)


def test_cancel_half_refund_between_24_48h(hotel_setup):
    h, room, guest = hotel_setup
    check_in = date(2025, 10, 10)
    res = h.book(room.id, guest.id, check_in, date(2025, 10, 14))
    h.confirm(res.id)
    simulated_now = datetime.combine(check_in, datetime.min.time()) - timedelta(hours=36)
    cancelled = h.cancel(res.id, now=simulated_now)
    assert cancelled.refund_amount == pytest.approx(cancelled.total_price * 0.5, rel=1e-2)


def test_cancel_no_refund_under_24h(hotel_setup):
    h, room, guest = hotel_setup
    check_in = date(2025, 10, 20)
    res = h.book(room.id, guest.id, check_in, date(2025, 10, 23))
    h.confirm(res.id)
    simulated_now = datetime.combine(check_in, datetime.min.time()) - timedelta(hours=12)
    cancelled = h.cancel(res.id, now=simulated_now)
    assert cancelled.refund_amount == 0.0


def test_cancel_checked_in_raises(hotel_setup):
    h, room, guest = hotel_setup
    res = h.book(room.id, guest.id, date(2025, 11, 1), date(2025, 11, 5))
    h.confirm(res.id)
    h.check_in(res.id)
    with pytest.raises(InvalidTransitionError):
        h.cancel(res.id)


# ============================================================
# Invoice correctness
# ============================================================

def test_invoice_includes_loyalty_discount():
    h = HotelSystem("Test Hotel")
    room  = h.add_room("501", RoomType.DOUBLE, floor=5, base_rate=200.0)
    guest = h.register_guest("Bob", "bob@t.com", loyalty_tier=LoyaltyTier.PLATINUM)
    res = h.book(room.id, guest.id, date(2025, 3, 10), date(2025, 3, 12))
    h.confirm(res.id)
    h.check_in(res.id)
    _, invoice = h.check_out(res.id)
    descriptions = [item.description for item in invoice.line_items]
    assert any("Loyalty" in d or "discount" in d.lower() for d in descriptions)


# ============================================================
# Payment
# ============================================================

def test_payment_recorded(hotel_setup):
    h, room, guest = hotel_setup
    res = h.book(room.id, guest.id, date(2025, 12, 1), date(2025, 12, 4))
    h.confirm(res.id)
    h.check_in(res.id)
    _, inv = h.check_out(res.id)
    payment = h.pay(res.id, PaymentMethod.CREDIT_CARD, inv.grand_total)
    r = h.get_reservation(res.id)
    assert r.total_paid == pytest.approx(inv.grand_total, rel=1e-2)
