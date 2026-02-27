"""
reservation_service.py — Core booking business logic.

Responsibilities:
  - Availability search with price calculation
  - Reservation creation (double-booking prevention)
  - Confirmation, cancellation (with refund tiers), check-in, check-out
  - Invoice generation
  - Payment recording
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .models import (
    Guest, Invoice, Payment, PaymentMethod, PaymentStatus,
    Reservation, ReservationStatus,
    Room, RoomStatus, RoomType,
)
from .notifications import EventBus, EventType, HotelEvent, create_default_bus
from .pricing import PricingEngine
from .repository import GuestRepository, ReservationRepository, RoomRepository
from .state_machine import ReservationStateMachine

logger = logging.getLogger("hotel.service")


# ============================================================
# Refund Policy
# ============================================================

class RefundPolicy:
    """
    Cancellation refund tiers (based on hours before check-in):
      > 48 hours  → 100% refund
      24–48 hours → 50% refund
      < 24 hours  → 0% refund
    """
    TIERS: List[Tuple[int, float]] = [
        (48, 1.00),   # hours_ahead → refund_fraction
        (24, 0.50),
        (0,  0.00),
    ]

    @classmethod
    def refund_fraction(cls, check_in: date, now: datetime) -> Tuple[float, str]:
        check_in_dt = datetime.combine(check_in, datetime.min.time())
        hours_ahead = (check_in_dt - now).total_seconds() / 3600
        for threshold, fraction in cls.TIERS:
            if hours_ahead >= threshold:
                label = f"{int(fraction*100)}% refund ({hours_ahead:.0f}h before check-in)"
                return fraction, label
        return 0.0, "No refund (cancellation too close to check-in)"


# ============================================================
# Available Room Result
# ============================================================

class AvailableRoomResult:
    """Result of an availability search for a single room."""
    def __init__(self, room: Room, price: float, breakdown: Dict) -> None:
        self.room      = room
        self.price     = price
        self.breakdown = breakdown

    def __repr__(self) -> str:
        return (
            f"<AvailableRoom #{self.room.number} {self.room.room_type.value} "
            f"${self.price:.2f}>"
        )


# ============================================================
# Reservation Service
# ============================================================

class ReservationService:

    def __init__(
        self,
        room_repo        : RoomRepository,
        guest_repo       : GuestRepository,
        reservation_repo : ReservationRepository,
        pricing_engine   : Optional[PricingEngine] = None,
        event_bus        : Optional[EventBus]       = None,
    ) -> None:
        self._rooms        = room_repo
        self._guests       = guest_repo
        self._reservations = reservation_repo
        self._pricing      = pricing_engine or PricingEngine()
        self._bus          = event_bus or create_default_bus()
        self._sm           = ReservationStateMachine()

    # ----------------------------------------------------------
    # Search
    # ----------------------------------------------------------

    def search_available_rooms(
        self,
        check_in   : date,
        check_out  : date,
        room_type  : Optional[RoomType] = None,
        min_capacity: int               = 1,
        guest      : Optional[Guest]    = None,
    ) -> List[AvailableRoomResult]:
        """
        Return all rooms available for the requested dates,
        optionally filtered by type and capacity, with prices
        calculated for the given guest (or an anonymous standard guest).
        """
        if check_out <= check_in:
            raise ValueError("check_out must be after check_in")

        rooms = self._rooms.all()
        if room_type:
            rooms = [r for r in rooms if r.room_type == room_type]
        rooms = [r for r in rooms if r.capacity >= min_capacity]
        rooms = [r for r in rooms if r.status != RoomStatus.MAINTENANCE]

        # A guest placeholder for pricing when no guest supplied
        _dummy_guest = guest or Guest(name="Guest", email="anon@hotel.com")

        results = []
        for room in rooms:
            overlaps = self._reservations.overlapping(room.id, check_in, check_out)
            if overlaps:
                continue
            price, breakdown = self._pricing.calculate(
                room, _dummy_guest, check_in, check_out
            )
            results.append(AvailableRoomResult(room, price, breakdown))

        # Sort by price ascending
        results.sort(key=lambda x: x.price)
        return results

    # ----------------------------------------------------------
    # Create Reservation
    # ----------------------------------------------------------

    def create_reservation(
        self,
        room_id    : str,
        guest_id   : str,
        check_in   : date,
        check_out  : date,
        notes      : str = "",
    ) -> Reservation:
        room  = self._rooms.get(room_id)
        guest = self._guests.get(guest_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")
        if not guest:
            raise ValueError(f"Guest {guest_id} not found")
        if check_out <= check_in:
            raise ValueError("check_out must be after check_in")
        if room.status == RoomStatus.MAINTENANCE:
            raise ValueError(f"Room {room.number} is under maintenance")

        # Double-booking guard
        conflicts = self._reservations.overlapping(room_id, check_in, check_out)
        if conflicts:
            raise ValueError(
                f"Room {room.number} is already booked from "
                f"{conflicts[0].check_in} to {conflicts[0].check_out}"
            )

        price, breakdown = self._pricing.calculate(room, guest, check_in, check_out)

        reservation = Reservation(
            room            = room,
            guest           = guest,
            check_in        = check_in,
            check_out       = check_out,
            total_price     = price,
            price_breakdown = breakdown,
            notes           = notes,
        )
        self._reservations.add(reservation)
        self._rooms.update_status(room_id, RoomStatus.RESERVED)

        self._bus.publish(HotelEvent(
            EventType.BOOKING_CREATED,
            data={
                "id"          : reservation.id[:8],
                "reservation_id": reservation.id,
                "room"        : room.number,
                "guest"       : guest.name,
                "guest_email" : guest.email,
                "nights"      : reservation.nights,
                "total"       : price,
            },
        ))
        logger.info(
            "Reservation created: %s | %s | %s→%s | $%.2f",
            reservation.id[:8], guest.name, check_in, check_out, price,
        )
        return reservation

    # ----------------------------------------------------------
    # Confirm
    # ----------------------------------------------------------

    def confirm_reservation(self, reservation_id: str) -> Reservation:
        r = self._get_or_raise(reservation_id)
        r.status       = self._sm.transition(r.status, ReservationStatus.CONFIRMED)
        r.confirmed_at = datetime.utcnow()
        self._bus.publish(HotelEvent(
            EventType.BOOKING_CONFIRMED,
            data={"id": r.id[:8], "reservation_id": r.id, "guest": r.guest.name},
        ))
        return r

    # ----------------------------------------------------------
    # Cancel
    # ----------------------------------------------------------

    def cancel_reservation(
        self,
        reservation_id: str,
        reason        : str = "",
        now           : Optional[datetime] = None,
    ) -> Reservation:
        r   = self._get_or_raise(reservation_id)
        now = now or datetime.utcnow()
        r.status = self._sm.transition(r.status, ReservationStatus.CANCELLED)

        fraction, policy_label = RefundPolicy.refund_fraction(r.check_in, now)
        r.refund_amount         = round(r.total_price * fraction, 2)
        r.cancellation_reason   = reason

        # Mark room available again
        self._rooms.update_status(r.room.id, RoomStatus.AVAILABLE)

        self._bus.publish(HotelEvent(
            EventType.BOOKING_CANCELLED,
            data={
                "id"         : r.id[:8],
                "reservation_id": r.id,
                "guest"      : r.guest.name,
                "guest_email": r.guest.email,
                "refund"     : r.refund_amount,
                "policy"     : policy_label,
                "reason"     : reason,
            },
        ))
        logger.info(
            "Reservation %s cancelled. Refund: $%.2f (%s)",
            r.id[:8], r.refund_amount, policy_label,
        )
        return r

    # ----------------------------------------------------------
    # Check-in
    # ----------------------------------------------------------

    def check_in(self, reservation_id: str) -> Reservation:
        r = self._get_or_raise(reservation_id)
        r.status        = self._sm.transition(r.status, ReservationStatus.CHECKED_IN)
        r.checked_in_at = datetime.utcnow()
        self._rooms.update_status(r.room.id, RoomStatus.OCCUPIED)
        self._bus.publish(HotelEvent(
            EventType.CHECKED_IN,
            data={
                "room"        : r.room.number,
                "guest"       : r.guest.name,
                "guest_email" : r.guest.email,
                "guest_phone" : r.guest.phone,
                "reservation_id": r.id,
            },
        ))
        return r

    # ----------------------------------------------------------
    # Check-out
    # ----------------------------------------------------------

    def check_out(
        self,
        reservation_id: str,
        extras        : Optional[Dict[str, float]] = None,
    ) -> Tuple[Reservation, Invoice]:
        """
        Transitions to CHECKED_OUT, builds an itemised Invoice.
        *extras* is a dict of {description: amount} for add-on charges
        (room service, minibar, spa, etc.).
        """
        r = self._get_or_raise(reservation_id)
        r.status         = self._sm.transition(r.status, ReservationStatus.CHECKED_OUT)
        r.checked_out_at = datetime.utcnow()
        self._rooms.update_status(r.room.id, RoomStatus.AVAILABLE)

        invoice = Invoice(
            reservation_id = r.id,
            guest_name     = r.guest.name,
            room_number    = r.room.number,
            check_in       = r.check_in,
            check_out      = r.check_out,
        )
        # Room charges
        bd = r.price_breakdown
        invoice.add_item(
            f"Room {r.room.number} ({r.room.room_type.value}) × {r.nights} nights",
            r.nights,
            r.room.base_rate,
        )
        if bd.get("seasonal_surcharge", 0) != 0:
            invoice.add_item(
                f"Peak-season surcharge ({bd.get('peak_nights', 0)} nights)",
                1, bd["seasonal_surcharge"],
            )
        if bd.get("weekend_surcharge", 0) != 0:
            invoice.add_item(
                f"Weekend surcharge ({bd.get('weekend_nights', 0)} nights)",
                1, bd["weekend_surcharge"],
            )
        if bd.get("loyalty_discount", 0) != 0:
            invoice.add_item(
                f"Loyalty discount ({r.guest.loyalty_tier.value})",
                1, bd["loyalty_discount"],
            )
        if bd.get("corporate_discount", 0) != 0:
            invoice.add_item("Corporate rate discount", 1, bd["corporate_discount"])
        if bd.get("early_bird_discount", 0) != 0:
            invoice.add_item("Early bird discount", 1, bd["early_bird_discount"])

        # Extras
        for desc, amount in (extras or {}).items():
            invoice.add_item(desc, 1, amount)

        r.invoice = invoice

        self._bus.publish(HotelEvent(
            EventType.CHECKED_OUT,
            data={
                "room"        : r.room.number,
                "guest"       : r.guest.name,
                "guest_email" : r.guest.email,
                "guest_phone" : r.guest.phone,
                "total"       : invoice.grand_total,
                "reservation_id": r.id,
            },
        ))
        logger.info(
            "Check-out: %s | %s | Invoice total: $%.2f",
            r.id[:8], r.guest.name, invoice.grand_total,
        )
        return r, invoice

    # ----------------------------------------------------------
    # Payment
    # ----------------------------------------------------------

    def process_payment(
        self,
        reservation_id: str,
        method        : PaymentMethod,
        amount        : float,
        notes         : str = "",
    ) -> Payment:
        r = self._get_or_raise(reservation_id)
        payment = Payment(
            reservation_id = r.id,
            amount         = amount,
            method         = method,
            status         = PaymentStatus.COMPLETED,
            notes          = notes,
        )
        r.payments.append(payment)
        self._bus.publish(HotelEvent(
            EventType.PAYMENT_PROCESSED,
            data={
                "reservation_id": r.id,
                "guest"         : r.guest.name,
                "amount"        : amount,
                "method"        : method.value,
            },
        ))
        return payment

    # ----------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------

    def _get_or_raise(self, reservation_id: str) -> Reservation:
        r = self._reservations.get(reservation_id)
        if not r:
            raise ValueError(f"Reservation '{reservation_id}' not found")
        return r
