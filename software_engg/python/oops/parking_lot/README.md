## Parking Lot System

This is a parking lot system that allows users to park and exit vehicles, and track the availability of parking spots.

## Features

- Parking and exiting vehicles
- Tracking the availability of parking spots
- Calculating parking fees based on the type of vehicle and the duration of parking
- Managing parking floors and spots
- Managing vehicle types
- Managing pricing strategies
- Managing availability tracking
- Managing ticket registry
- Managing spot allocator
- Managing parking lot

## Usage

```python
from parking_lot import ParkingLot

lot = ParkingLot("Lot")
lot.park(vehicle)
lot.exit(ticket_id)
lot.availability()
lot.subscribe(callback)
lot.print_availability()
```


```
parking_lot/
├── models/
│   ├── vehicle.py          # VehicleType enum, Vehicle ABC, VehicleFactory
│   ├── spot.py             # ParkingSpot, SpotSize, compatibility matrix
│   ├── floor.py            # ParkingFloor — manages spots, availability queries
│   └── ticket.py           # Immutable ParkingTicket value object (UUID + timestamps)
├── strategies/
│   └── pricing.py          # Strategy pattern: FlatRate, Tiered, DynamicPricing + factory
├── services/
│   ├── spot_allocator.py   # SpotAllocator — nearest-floor, smallest-spot strategy
│   └── availability_tracker.py  # Observer pattern — real-time free count + events
├── parking_lot.py          # Facade/Orchestrator — park(), exit(), availability()
├── builder.py              # Fluent LotBuilder API
└── main.py                 # Demo driver
```

## Design Patterns Applied

| Pattern      | Where Used |
|--------------|------------|
| Factory      | `VehicleFactory`, `PricingFactory` |
| Strategy     | `SpotAllocator`, `PricingStrategy` — swap without touching `ParkingLot` |
| Observer     | `AvailabilityTracker` → notifies `dashboard_logger` on every park/exit |
| Facade       | `ParkingLot` — single public API over multiple services |
| Builder      | `LotBuilder` — fluent API for constructing complex lot configurations |
| Value Object | `ParkingTicket` — `@dataclass(frozen=True)` |