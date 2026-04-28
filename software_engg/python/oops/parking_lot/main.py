# -*- coding: utf-8 -*-
"""
main.py  -  Demo driver for the Parking Lot system
---------------------------------------------------
Run:  python -m parking_lot.main
"""

import time
from datetime import datetime, timedelta

from parking_lot.builder import LotBuilder
from parking_lot.models.vehicle import VehicleFactory, VehicleType
from parking_lot.services.availability_tracker import SlotEvent


# ── 1. Observer / subscriber ─────────────────────────────────────────────────

def dashboard_logger(event: SlotEvent) -> None:
    icon = "[FREE]" if event.event_type == "VACATED" else "[OCC] "
    print(
        f"  {icon} [{event.event_type}]  "
        f"Floor {event.floor_id} / Spot {event.spot_id} | "
        f"Free slots remaining: {event.free_after}"
    )


# ── 2. Build the lot ─────────────────────────────────────────────────────────

lot = (
    LotBuilder("MAANG HQ Parking")
    .add_floor(floor_id=0, small=2, medium=3, large=1)   # Ground floor
    .add_floor(floor_id=1, small=1, medium=2, large=1)   # 1st floor
    .with_pricing("tiered")
    .build()
)

lot.subscribe(dashboard_logger)   # hook up the observer


# ── 3. Show initial availability ──────────────────────────────────────────────

lot.print_availability()


# ── 4. Park various vehicles ──────────────────────────────────────────────────

print("=" * 50)
print("  PARKING VEHICLES")
print("=" * 50)

v1 = VehicleFactory.create(VehicleType.MOTORCYCLE, "MH-01-AB-1234")
v2 = VehicleFactory.create(VehicleType.CAR,        "KA-05-CD-5678")
v3 = VehicleFactory.create(VehicleType.TRUCK,      "DL-08-EF-9999")
v4 = VehicleFactory.create(VehicleType.CAR,        "TN-09-GH-4321")
v5 = VehicleFactory.create(VehicleType.MOTORCYCLE, "MH-12-IJ-7777")

t1 = lot.park(v1)
t2 = lot.park(v2)
t3 = lot.park(v3)
t4 = lot.park(v4)
t5 = lot.park(v5)


# ── 5. Show live availability ─────────────────────────────────────────────────

lot.print_availability()


# ── 6. Exit vehicles (simulate 2-hour stay) ───────────────────────────────────

print("=" * 50)
print("  EXITS")
print("=" * 50)

fake_exit = datetime.now() + timedelta(hours=2)

lot.exit(t1.ticket_id, fake_exit)   # Motorcycle — 2 h
lot.exit(t3.ticket_id, fake_exit)   # Truck       — 2 h


# ── 7. Final availability ─────────────────────────────────────────────────────

lot.print_availability()


# ── 8. Full lot edge-case ─────────────────────────────────────────────────────

print("=" * 50)
print("  EDGE CASE — Fill lot completely")
print("=" * 50)

extra_vehicles = [
    VehicleFactory.create(VehicleType.CAR, f"XX-00-{i:02d}-0000")
    for i in range(20)
]

parked_count = 0
for v in extra_vehicles:
    try:
        lot.park(v)
        parked_count += 1
    except RuntimeError as e:
        print(f"  [FULL] {e}")
        break

print(f"\n  Total additionally parked: {parked_count}")
lot.print_availability()
