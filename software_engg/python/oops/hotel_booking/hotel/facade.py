"""
facade.py — HotelSystem: single entry point wiring all sub-systems.

Provides a simplified API over:
  - ReservationService (booking, cancel, check-in/out)
  - RoomRepository     (room management)
  - GuestRepository    (guest management)
  - ReportingEngine    (occupancy, revenue)
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from .models import (
    Guest, Invoice, LoyaltyTier,
    Payment, PaymentMethod,
    Reservation, ReservationStatus,
    Room, RoomStatus, RoomType,
)
from .notifications import EventBus, create_default_bus
from .pricing import PricingEngine
from .repository import GuestRepository, ReservationRepository, RoomRepository
from .reporting import OccupancyReport, RevenueReport, RoomStatusReport
from .reservation_service import AvailableRoomResult, ReservationService
from .state_machine import InvalidTransitionError


class HotelSystem:
    """
    Facade — high-level interface to the entire Hotel Booking System.

    Example
    -------
    >>> hotel = HotelSystem("Grand Plaza")
    >>> room  = hotel.add_room("101", RoomType.DOUBLE, floor=1, base_rate=120)
    >>> guest = hotel.register_guest("Alice", "alice@example.com", LoyaltyTier.GOLD)
    >>> res   = hotel.book(room.id, guest.id, date(2026, 7, 1), date(2026, 7, 5))
    >>> hotel.confirm(res.id)
    >>> hotel.check_in(res.id)
    >>> res, inv = hotel.check_out(res.id, extras={"Minibar": 45.00})
    """

    def __init__(
        self,
        name          : str = "Hotel",
        pricing_engine: Optional[PricingEngine] = None,
        event_bus     : Optional[EventBus]      = None,
    ) -> None:
        self.name = name
        self._rooms        = RoomRepository()
        self._guests       = GuestRepository()
        self._reservations = ReservationRepository()
        self._bus          = event_bus or create_default_bus()
        self._pricing      = pricing_engine or PricingEngine()
        self._service      = ReservationService(
            self._rooms, self._guests, self._reservations,
            self._pricing, self._bus,
        )

    # ----------------------------------------------------------
    # Room management
    # ----------------------------------------------------------

    def add_room(
        self,
        number    : str,
        room_type : RoomType,
        floor     : int,
        base_rate : float,
        amenities : Optional[List[str]] = None,
    ) -> Room:
        room = Room(number=number, room_type=room_type, floor=floor,
                    base_rate=base_rate, amenities=amenities or [])
        return self._rooms.add(room)

    def get_room(self, room_id: str) -> Optional[Room]:
        return self._rooms.get(room_id)

    def get_room_by_number(self, number: str) -> Optional[Room]:
        return self._rooms.get_by_number(number)

    def list_rooms(self, room_type: Optional[RoomType] = None) -> List[Room]:
        rooms = self._rooms.all()
        if room_type:
            rooms = [r for r in rooms if r.room_type == room_type]
        return rooms

    def set_room_maintenance(self, room_id: str, in_maintenance: bool) -> None:
        status = RoomStatus.MAINTENANCE if in_maintenance else RoomStatus.AVAILABLE
        self._rooms.update_status(room_id, status)

    # ----------------------------------------------------------
    # Guest management
    # ----------------------------------------------------------

    def register_guest(
        self,
        name         : str,
        email        : str,
        phone        : str           = "",
        loyalty_tier : LoyaltyTier   = LoyaltyTier.STANDARD,
    ) -> Guest:
        guest = Guest(name=name, email=email, phone=phone, loyalty_tier=loyalty_tier)
        return self._guests.add(guest)

    def get_guest(self, guest_id: str) -> Optional[Guest]:
        return self._guests.get(guest_id)

    def find_guest_by_email(self, email: str) -> Optional[Guest]:
        return self._guests.find_by_email(email)

    def upgrade_loyalty(self, guest_id: str, tier: LoyaltyTier) -> bool:
        return self._guests.update_loyalty(guest_id, tier)

    def list_guests(self) -> List[Guest]:
        return self._guests.all()

    # ----------------------------------------------------------
    # Booking workflow
    # ----------------------------------------------------------

    def search(
        self,
        check_in     : date,
        check_out    : date,
        room_type    : Optional[RoomType] = None,
        min_capacity : int                = 1,
        guest_id     : Optional[str]      = None,
    ) -> List[AvailableRoomResult]:
        guest = self._guests.get(guest_id) if guest_id else None
        return self._service.search_available_rooms(
            check_in, check_out, room_type, min_capacity, guest
        )

    def book(
        self,
        room_id  : str,
        guest_id : str,
        check_in : date,
        check_out: date,
        notes    : str = "",
    ) -> Reservation:
        return self._service.create_reservation(room_id, guest_id, check_in, check_out, notes)

    def confirm(self, reservation_id: str) -> Reservation:
        return self._service.confirm_reservation(reservation_id)

    def cancel(
        self,
        reservation_id: str,
        reason        : str = "",
        now           : Optional[datetime] = None,
    ) -> Reservation:
        return self._service.cancel_reservation(reservation_id, reason, now)

    def check_in(self, reservation_id: str) -> Reservation:
        return self._service.check_in(reservation_id)

    def check_out(
        self,
        reservation_id: str,
        extras        : Optional[Dict[str, float]] = None,
    ) -> Tuple[Reservation, Invoice]:
        return self._service.check_out(reservation_id, extras)

    def pay(
        self,
        reservation_id: str,
        method        : PaymentMethod,
        amount        : float,
        notes         : str = "",
    ) -> Payment:
        return self._service.process_payment(reservation_id, method, amount, notes)

    # ----------------------------------------------------------
    # Reservation queries
    # ----------------------------------------------------------

    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        return self._reservations.get(reservation_id)

    def list_reservations(
        self,
        status   : Optional[ReservationStatus] = None,
        guest_id : Optional[str]               = None,
    ) -> List[Reservation]:
        if guest_id:
            return self._reservations.by_guest(guest_id)
        if status:
            return self._reservations.by_status(status)
        return self._reservations.all()

    # ----------------------------------------------------------
    # Reports
    # ----------------------------------------------------------

    def room_status_report(self) -> RoomStatusReport:
        from datetime import date
        return RoomStatusReport(
            snapshot_at = date.today(),
            rooms       = self._rooms.all(),
        )

    def occupancy_report(self, start: date, end: date) -> OccupancyReport:
        return OccupancyReport(
            start_date   = start,
            end_date     = end,
            total_rooms  = len(self._rooms.all()),
            reservations = self._reservations.all(),
        )

    def revenue_report(self, start: date, end: date) -> RevenueReport:
        return RevenueReport(
            start_date   = start,
            end_date     = end,
            reservations = self._reservations.all(),
        )

    # ----------------------------------------------------------
    # Event Bus access
    # ----------------------------------------------------------

    @property
    def event_bus(self) -> EventBus:
        return self._bus

    @property
    def event_history(self):
        return self._bus.history
