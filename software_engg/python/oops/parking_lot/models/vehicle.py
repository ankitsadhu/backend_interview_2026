"""
models/vehicle.py
-----------------
Defines vehicle types using Enum and a Vehicle ABC.
Factory method `VehicleFactory.create()` acts as the entry point.
"""

from abc import ABC, abstractmethod
from enum import Enum


class VehicleType(Enum):
    MOTORCYCLE = "Motorcycle"
    CAR        = "Car"
    TRUCK      = "Truck"


class Vehicle(ABC):
    """Abstract base for all vehicles."""

    def __init__(self, license_plate: str):
        self.license_plate = license_plate

    @property
    @abstractmethod
    def vehicle_type(self) -> VehicleType:
        ...

    def __repr__(self) -> str:
        return f"{self.vehicle_type.value}({self.license_plate})"


class Motorcycle(Vehicle):
    @property
    def vehicle_type(self) -> VehicleType:
        return VehicleType.MOTORCYCLE


class Car(Vehicle):
    @property
    def vehicle_type(self) -> VehicleType:
        return VehicleType.CAR


class Truck(Vehicle):
    @property
    def vehicle_type(self) -> VehicleType:
        return VehicleType.TRUCK


# ── Factory ──────────────────────────────────────────────────────────────────

_VEHICLE_MAP: dict[VehicleType, type[Vehicle]] = {
    VehicleType.MOTORCYCLE: Motorcycle,
    VehicleType.CAR:        Car,
    VehicleType.TRUCK:      Truck,
}


class VehicleFactory:
    """Creates Vehicle instances without exposing concrete classes."""

    @staticmethod
    def create(vehicle_type: VehicleType, license_plate: str) -> Vehicle:
        cls = _VEHICLE_MAP.get(vehicle_type)
        if cls is None:
            raise ValueError(f"Unsupported vehicle type: {vehicle_type}")
        return cls(license_plate)
