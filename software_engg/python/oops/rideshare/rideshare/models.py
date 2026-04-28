"""
models.py — Core domain models for the Ride-Sharing system.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# ============================================================
# Enumerations
# ============================================================

class VehicleType(Enum):
    ECONOMY  = "ECONOMY"
    COMFORT  = "COMFORT"
    PREMIUM  = "PREMIUM"
    SUV      = "SUV"
    XL       = "XL"

    @property
    def capacity(self) -> int:
        return {
            "ECONOMY": 4, "COMFORT": 4, "PREMIUM": 4,
            "SUV": 6, "XL": 6,
        }[self.value]


class DriverStatus(Enum):
    OFFLINE   = "OFFLINE"
    AVAILABLE = "AVAILABLE"
    ON_TRIP   = "ON_TRIP"
    BUSY      = "BUSY"


class RideStatus(Enum):
    REQUESTED       = "REQUESTED"
    MATCHED         = "MATCHED"
    DRIVER_ARRIVING = "DRIVER_ARRIVING"
    IN_PROGRESS     = "IN_PROGRESS"
    COMPLETED       = "COMPLETED"
    CANCELLED       = "CANCELLED"


class PaymentMethod(Enum):
    CREDIT_CARD  = "CREDIT_CARD"
    DEBIT_CARD   = "DEBIT_CARD"
    WALLET       = "WALLET"
    CASH         = "CASH"
    UPI          = "UPI"


class PaymentStatus(Enum):
    PENDING   = "PENDING"
    COMPLETED = "COMPLETED"
    REFUNDED  = "REFUNDED"
    FAILED    = "FAILED"


class CancellationBy(Enum):
    RIDER  = "RIDER"
    DRIVER = "DRIVER"
    SYSTEM = "SYSTEM"


# ============================================================
# Value Objects
# ============================================================

@dataclass(frozen=True)
class Location:
    """GPS coordinate + optional address label."""
    lat     : float
    lng     : float
    address : str = ""

    def __str__(self) -> str:
        return self.address if self.address else f"({self.lat:.4f}, {self.lng:.4f})"


# ============================================================
# Entities
# ============================================================

@dataclass
class Vehicle:
    vehicle_type : VehicleType
    make         : str
    model        : str
    plate        : str
    color        : str = ""
    year         : int = 2024

    def __str__(self) -> str:
        return f"{self.color} {self.year} {self.make} {self.model} ({self.plate})"


@dataclass
class Driver:
    id           : str           = field(default_factory=lambda: str(uuid.uuid4())[:12])
    name         : str           = ""
    phone        : str           = ""
    vehicle      : Optional[Vehicle] = None
    location     : Optional[Location] = None
    status       : DriverStatus  = DriverStatus.OFFLINE
    rating_sum   : float         = 0.0
    rating_count : int           = 0
    total_trips  : int           = 0
    earnings     : float         = 0.0

    @property
    def rating(self) -> float:
        return round(self.rating_sum / self.rating_count, 2) if self.rating_count else 5.0

    def add_rating(self, score: float) -> None:
        self.rating_sum += score
        self.rating_count += 1


@dataclass
class Rider:
    id           : str           = field(default_factory=lambda: str(uuid.uuid4())[:12])
    name         : str           = ""
    phone        : str           = ""
    email        : str           = ""
    location     : Optional[Location] = None
    rating_sum   : float         = 0.0
    rating_count : int           = 0
    total_trips  : int           = 0
    total_spent  : float         = 0.0

    @property
    def rating(self) -> float:
        return round(self.rating_sum / self.rating_count, 2) if self.rating_count else 5.0

    def add_rating(self, score: float) -> None:
        self.rating_sum += score
        self.rating_count += 1


# ============================================================
# Fare Breakdown
# ============================================================

@dataclass
class FareBreakdown:
    base_fare         : float = 0.0
    distance_charge   : float = 0.0
    time_charge       : float = 0.0
    surge_amount      : float = 0.0
    vehicle_premium   : float = 0.0
    subtotal          : float = 0.0
    platform_fee      : float = 0.0
    total             : float = 0.0
    surge_multiplier  : float = 1.0
    distance_km       : float = 0.0
    duration_min      : float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "base_fare": self.base_fare,
            "distance_charge": self.distance_charge,
            "time_charge": self.time_charge,
            "surge_amount": self.surge_amount,
            "vehicle_premium": self.vehicle_premium,
            "subtotal": self.subtotal,
            "platform_fee": self.platform_fee,
            "total": self.total,
            "surge_multiplier": self.surge_multiplier,
            "distance_km": self.distance_km,
            "duration_min": self.duration_min,
        }


# ============================================================
# Ride
# ============================================================

@dataclass
class Ride:
    id              : str                = field(default_factory=lambda: str(uuid.uuid4())[:12])
    rider           : Optional[Rider]    = None
    driver          : Optional[Driver]   = None
    pickup          : Optional[Location] = None
    dropoff         : Optional[Location] = None
    vehicle_pref    : VehicleType        = VehicleType.ECONOMY
    status          : RideStatus         = RideStatus.REQUESTED
    fare            : float              = 0.0
    fare_breakdown  : Optional[FareBreakdown] = None
    estimated_fare  : float              = 0.0
    distance_km     : float              = 0.0
    duration_min    : float              = 0.0
    surge_multiplier: float              = 1.0
    # Timestamps
    requested_at    : Optional[datetime] = None
    matched_at      : Optional[datetime] = None
    pickup_at       : Optional[datetime] = None
    started_at      : Optional[datetime] = None
    completed_at    : Optional[datetime] = None
    cancelled_at    : Optional[datetime] = None
    # Cancellation
    cancelled_by    : Optional[CancellationBy] = None
    cancel_reason   : str                = ""
    cancel_fee      : float              = 0.0
    # Ratings
    rider_rating    : Optional[float]    = None
    driver_rating   : Optional[float]    = None


# ============================================================
# Payment
# ============================================================

@dataclass
class Payment:
    id       : str           = field(default_factory=lambda: str(uuid.uuid4())[:12])
    ride_id  : str           = ""
    amount   : float         = 0.0
    method   : PaymentMethod = PaymentMethod.CREDIT_CARD
    status   : PaymentStatus = PaymentStatus.PENDING
    paid_at  : Optional[datetime] = None


# ============================================================
# Rating
# ============================================================

@dataclass
class RatingRecord:
    id        : str   = field(default_factory=lambda: str(uuid.uuid4())[:12])
    ride_id   : str   = ""
    from_id   : str   = ""
    to_id     : str   = ""
    score     : float = 5.0
    comment   : str   = ""
    created_at: Optional[datetime] = None
