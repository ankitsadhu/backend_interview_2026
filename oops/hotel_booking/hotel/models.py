"""
models.py — Core domain models for the Hotel Booking System.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# Enumerations
# ============================================================

class RoomType(Enum):
    SINGLE     = "SINGLE"
    DOUBLE     = "DOUBLE"
    SUITE      = "SUITE"
    PENTHOUSE  = "PENTHOUSE"

    @property
    def capacity(self) -> int:
        return {
            RoomType.SINGLE    : 1,
            RoomType.DOUBLE    : 2,
            RoomType.SUITE     : 4,
            RoomType.PENTHOUSE : 6,
        }[self]


class RoomStatus(Enum):
    AVAILABLE   = "AVAILABLE"
    RESERVED    = "RESERVED"
    OCCUPIED    = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"


class ReservationStatus(Enum):
    PENDING     = "PENDING"
    CONFIRMED   = "CONFIRMED"
    CHECKED_IN  = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED   = "CANCELLED"


class LoyaltyTier(Enum):
    STANDARD  = "STANDARD"
    SILVER    = "SILVER"
    GOLD      = "GOLD"
    PLATINUM  = "PLATINUM"

    @property
    def discount_pct(self) -> float:
        return {
            LoyaltyTier.STANDARD : 0.00,
            LoyaltyTier.SILVER   : 0.05,
            LoyaltyTier.GOLD     : 0.10,
            LoyaltyTier.PLATINUM : 0.20,
        }[self]


class PaymentMethod(Enum):
    CREDIT_CARD  = "CREDIT_CARD"
    DEBIT_CARD   = "DEBIT_CARD"
    CASH         = "CASH"
    BANK_TRANSFER= "BANK_TRANSFER"


class PaymentStatus(Enum):
    PENDING   = "PENDING"
    COMPLETED = "COMPLETED"
    REFUNDED  = "REFUNDED"
    FAILED    = "FAILED"


# ============================================================
# Room
# ============================================================

@dataclass
class Room:
    number    : str
    room_type : RoomType
    floor     : int
    base_rate : float                      # per night, USD
    amenities : List[str]                  = field(default_factory=list)
    status    : RoomStatus                 = RoomStatus.AVAILABLE
    id        : str                        = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def capacity(self) -> int:
        return self.room_type.capacity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id"       : self.id,
            "number"   : self.number,
            "type"     : self.room_type.value,
            "floor"    : self.floor,
            "rate"     : self.base_rate,
            "capacity" : self.capacity,
            "amenities": self.amenities,
            "status"   : self.status.value,
        }


# ============================================================
# Guest
# ============================================================

@dataclass
class Guest:
    name         : str
    email        : str
    phone        : str                     = ""
    loyalty_tier : LoyaltyTier             = LoyaltyTier.STANDARD
    id           : str                     = field(default_factory=lambda: str(uuid.uuid4()))
    created_at   : datetime                = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id"          : self.id,
            "name"        : self.name,
            "email"       : self.email,
            "phone"       : self.phone,
            "loyalty_tier": self.loyalty_tier.value,
        }


# ============================================================
# Invoice
# ============================================================

@dataclass
class InvoiceLineItem:
    description : str
    quantity    : float
    unit_price  : float
    total       : float


@dataclass
class Invoice:
    reservation_id : str
    guest_name     : str
    room_number    : str
    check_in       : date
    check_out      : date
    line_items     : List[InvoiceLineItem] = field(default_factory=list)
    tax_rate       : float                 = 0.12          # 12%
    id             : str                   = field(default_factory=lambda: str(uuid.uuid4()))
    issued_at      : datetime              = field(default_factory=datetime.utcnow)

    @property
    def subtotal(self) -> float:
        return sum(item.total for item in self.line_items)

    @property
    def tax_amount(self) -> float:
        return round(self.subtotal * self.tax_rate, 2)

    @property
    def grand_total(self) -> float:
        return round(self.subtotal + self.tax_amount, 2)

    def add_item(self, description: str, quantity: float, unit_price: float) -> None:
        self.line_items.append(
            InvoiceLineItem(description, quantity, unit_price, round(quantity * unit_price, 2))
        )


# ============================================================
# Payment
# ============================================================

@dataclass
class Payment:
    reservation_id : str
    amount         : float
    method         : PaymentMethod
    status         : PaymentStatus = PaymentStatus.PENDING
    id             : str           = field(default_factory=lambda: str(uuid.uuid4()))
    created_at     : datetime      = field(default_factory=datetime.utcnow)
    notes          : str           = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id"             : self.id,
            "reservation_id" : self.reservation_id,
            "amount"         : self.amount,
            "method"         : self.method.value,
            "status"         : self.status.value,
            "created_at"     : self.created_at.isoformat(),
        }


# ============================================================
# Reservation
# ============================================================

@dataclass
class Reservation:
    room          : Room
    guest         : Guest
    check_in      : date
    check_out     : date
    status        : ReservationStatus      = ReservationStatus.PENDING
    total_price   : float                  = 0.0
    price_breakdown: Dict[str, float]      = field(default_factory=dict)
    notes         : str                    = ""
    cancellation_reason: str               = ""
    refund_amount : float                  = 0.0
    id            : str                    = field(default_factory=lambda: str(uuid.uuid4()))
    created_at    : datetime               = field(default_factory=datetime.utcnow)
    confirmed_at  : Optional[datetime]     = None
    checked_in_at : Optional[datetime]     = None
    checked_out_at: Optional[datetime]     = None
    payments      : List[Payment]          = field(default_factory=list)
    invoice       : Optional[Invoice]      = None

    @property
    def nights(self) -> int:
        return (self.check_out - self.check_in).days

    @property
    def is_active(self) -> bool:
        return self.status in (
            ReservationStatus.PENDING,
            ReservationStatus.CONFIRMED,
            ReservationStatus.CHECKED_IN,
        )

    @property
    def total_paid(self) -> float:
        return sum(
            p.amount for p in self.payments
            if p.status == PaymentStatus.COMPLETED
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id"          : self.id,
            "room"        : self.room.number,
            "guest"       : self.guest.name,
            "check_in"    : self.check_in.isoformat(),
            "check_out"   : self.check_out.isoformat(),
            "nights"      : self.nights,
            "status"      : self.status.value,
            "total_price" : self.total_price,
            "total_paid"  : self.total_paid,
            "created_at"  : self.created_at.isoformat(),
        }
