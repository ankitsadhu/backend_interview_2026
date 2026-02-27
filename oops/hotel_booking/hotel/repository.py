"""
repository.py — Repository pattern for in-memory storage of hotel entities.

Provides clean data-access interfaces for:
  - RoomRepository
  - GuestRepository
  - ReservationRepository
"""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from .models import (
    Guest, LoyaltyTier,
    Reservation, ReservationStatus,
    Room, RoomStatus, RoomType,
)


# ============================================================
# Room Repository
# ============================================================

class RoomRepository:
    """CRUD + availability queries for Room objects."""

    def __init__(self) -> None:
        self._rooms: Dict[str, Room] = {}

    def add(self, room: Room) -> Room:
        if room.number in {r.number for r in self._rooms.values()}:
            raise ValueError(f"Room number '{room.number}' already exists")
        self._rooms[room.id] = room
        return room

    def get(self, room_id: str) -> Optional[Room]:
        return self._rooms.get(room_id)

    def get_by_number(self, number: str) -> Optional[Room]:
        return next((r for r in self._rooms.values() if r.number == number), None)

    def all(self) -> List[Room]:
        return list(self._rooms.values())

    def by_type(self, room_type: RoomType) -> List[Room]:
        return [r for r in self._rooms.values() if r.room_type == room_type]

    def available(self) -> List[Room]:
        return [r for r in self._rooms.values() if r.status == RoomStatus.AVAILABLE]

    def update_status(self, room_id: str, status: RoomStatus) -> None:
        room = self.get(room_id)
        if room:
            room.status = status

    def remove(self, room_id: str) -> bool:
        if room_id in self._rooms:
            del self._rooms[room_id]
            return True
        return False


# ============================================================
# Guest Repository
# ============================================================

class GuestRepository:
    """CRUD + lookup for Guest objects."""

    def __init__(self) -> None:
        self._guests: Dict[str, Guest] = {}

    def add(self, guest: Guest) -> Guest:
        if any(g.email == guest.email for g in self._guests.values()):
            raise ValueError(f"Guest with email '{guest.email}' already exists")
        self._guests[guest.id] = guest
        return guest

    def get(self, guest_id: str) -> Optional[Guest]:
        return self._guests.get(guest_id)

    def find_by_email(self, email: str) -> Optional[Guest]:
        return next((g for g in self._guests.values() if g.email == email), None)

    def all(self) -> List[Guest]:
        return list(self._guests.values())

    def by_loyalty_tier(self, tier: LoyaltyTier) -> List[Guest]:
        return [g for g in self._guests.values() if g.loyalty_tier == tier]

    def update_loyalty(self, guest_id: str, tier: LoyaltyTier) -> bool:
        g = self.get(guest_id)
        if g:
            g.loyalty_tier = tier
            return True
        return False


# ============================================================
# Reservation Repository
# ============================================================

class ReservationRepository:
    """CRUD + queries for Reservation objects."""

    def __init__(self) -> None:
        self._reservations: Dict[str, Reservation] = {}

    def add(self, reservation: Reservation) -> Reservation:
        self._reservations[reservation.id] = reservation
        return reservation

    def get(self, reservation_id: str) -> Optional[Reservation]:
        return self._reservations.get(reservation_id)

    def all(self) -> List[Reservation]:
        return list(self._reservations.values())

    def by_guest(self, guest_id: str) -> List[Reservation]:
        return [r for r in self._reservations.values() if r.guest.id == guest_id]

    def by_room(self, room_id: str) -> List[Reservation]:
        return [r for r in self._reservations.values() if r.room.id == room_id]

    def by_status(self, status: ReservationStatus) -> List[Reservation]:
        return [r for r in self._reservations.values() if r.status == status]

    def active(self) -> List[Reservation]:
        """Returns reservations that are not cancelled or checked-out."""
        return [r for r in self._reservations.values() if r.is_active]

    def overlapping(self, room_id: str, check_in: date, check_out: date) -> List[Reservation]:
        """Return active reservations for *room_id* that overlap the requested window."""
        result = []
        for r in self._reservations.values():
            if r.room.id != room_id:
                continue
            if not r.is_active:
                continue
            # Overlap: r.check_in < check_out AND r.check_out > check_in
            if r.check_in < check_out and r.check_out > check_in:
                result.append(r)
        return result

    def remove(self, reservation_id: str) -> bool:
        if reservation_id in self._reservations:
            del self._reservations[reservation_id]
            return True
        return False
