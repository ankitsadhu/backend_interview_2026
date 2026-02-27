"""
parking_lot/parking_lot.py
--------------------------
Facade / Orchestrator.
ParkingLot coordinates floors, ticket registry, spot allocator, pricing,
and availability tracker without any one module knowing about others.
"""

from datetime import datetime
from typing import Optional

from .models.floor  import ParkingFloor
from .models.ticket import ParkingTicket
from .models.vehicle import Vehicle
from .services.spot_allocator       import SpotAllocator
from .services.availability_tracker import AvailabilityTracker, Subscriber
from .strategies.pricing import PricingStrategy, PricingFactory


class ParkingLot:
    """
    Entry point for all parking operations.

    Responsibilities:
      - park(vehicle)  → issues ParkingTicket
      - exit(ticket)   → vacates spot, returns fee
      - availability() → real-time snapshot per floor
    """

    def __init__(
        self,
        name:             str,
        floors:           list[ParkingFloor],
        pricing_strategy: PricingStrategy | None = None,
        allocator:        SpotAllocator | None   = None,
    ):
        self.name   = name
        self._floors = floors

        # services
        total_spots       = sum(len(f.available_spots()) for f in floors)
        self._tracker     = AvailabilityTracker(total_spots)
        self._allocator   = allocator or SpotAllocator()
        self._pricing     = pricing_strategy or PricingFactory.get("tiered")

        # active tickets: ticket_id → ParkingTicket
        self._tickets:    dict[str, ParkingTicket] = {}

    # ── public API ───────────────────────────────────────────────────────────

    def park(self, vehicle: Vehicle) -> ParkingTicket:
        """
        Find a spot, assign vehicle, issue ticket.
        Raises RuntimeError if lot is full.
        """
        if self._tracker.is_full:
            raise RuntimeError(f"[FULL] Parking lot '{self.name}' is full!")

        spot = self._allocator.find_spot(self._floors, vehicle)
        if spot is None:
            raise RuntimeError(
                f"No compatible spot found for {vehicle} in '{self.name}'."
            )

        spot.park(vehicle)
        ticket = ParkingTicket.issue(vehicle, spot)
        self._tickets[ticket.ticket_id] = ticket
        self._tracker.on_parked(spot, vehicle)

        print(f"[PARKED]  | {vehicle} -> Floor {spot.floor_id}, Spot {spot.spot_id} | {ticket}")
        return ticket

    def exit(self, ticket_id: str, exit_time: datetime | None = None) -> float:
        """
        Vacate spot, calculate and return fee.
        Removes ticket from active registry.
        """
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            raise ValueError(f"Ticket '{ticket_id}' not found or already settled.")

        # find the spot and vacate
        floor = self._get_floor(ticket.floor_id)
        spot  = floor.get_spot(ticket.spot.spot_id)
        if spot is None:
            raise RuntimeError("Data inconsistency: spot not found on floor.")

        spot.vacate()
        del self._tickets[ticket_id]
        self._tracker.on_vacated(spot)

        hours = ticket.duration_hours(exit_time)
        fee   = self._pricing.calculate(ticket.vehicle.vehicle_type, hours)

        print(
            f"[EXIT]    | {ticket.vehicle} | "
            f"{hours:.2f}h | Fee: Rs.{fee:.2f}"
        )
        return fee

    # ── availability snapshot ─────────────────────────────────────────────────

    def availability(self) -> dict:
        """Returns a nested dict: floor → size → free count."""
        snapshot = {}
        for floor in self._floors:
            snapshot[f"Floor {floor.floor_id}"] = floor.availability_summary()
        snapshot["total_free"] = self._tracker.free_spots
        return snapshot

    def print_availability(self) -> None:
        print(f"\n{'-'*50}")
        print(f"  [LOT] {self.name}  - Availability Snapshot")
        print(f"{'-'*50}")
        for floor in self._floors:
            summary = floor.availability_summary()
            parts   = " | ".join(f"{k}: {v}" for k, v in summary.items())
            print(f"  {floor}  ->  {parts}")
        print(f"  Total Free: {self._tracker.free_spots}")
        print(f"{'-'*50}\n")

    # ── observer hook (pass-through) ──────────────────────────────────────────

    def subscribe(self, callback: Subscriber) -> None:
        """Subscribe to real-time slot change events."""
        self._tracker.subscribe(callback)

    # ── internal helpers ──────────────────────────────────────────────────────

    def _get_floor(self, floor_id: int) -> ParkingFloor:
        for f in self._floors:
            if f.floor_id == floor_id:
                return f
        raise RuntimeError(f"Floor {floor_id} does not exist.")
