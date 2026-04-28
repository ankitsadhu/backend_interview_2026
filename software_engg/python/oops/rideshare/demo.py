"""
demo.py — End-to-end walkthrough of the Ride-Sharing System.

Demonstrates:
  1. Register riders & drivers with vehicles
  2. Drivers go online at different locations (NYC)
  3. Fare comparison across vehicle types
  4. Request ride → match → arriving → trip → complete
  5. Two-way ratings
  6. Surge pricing scenario
  7. Cancellation with fee
  8. Matching strategy switch (Nearest → Rated → Vehicle)
"""
from __future__ import annotations

from datetime import datetime

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from rideshare import (
    RideShareSystem, Location, VehicleType, Vehicle,
    PaymentMethod, DriverStatus, RideStatus,
)
from rideshare.models import CancellationBy

console = Console()


def section(title: str) -> None:
    console.print()
    console.print(Rule(f"[bold cyan]{title}[/]"))
    console.print()


# ============================================================
# NYC Locations
# ============================================================

TIMES_SQUARE   = Location(40.7580, -73.9855, "Times Square, NYC")
CENTRAL_PARK   = Location(40.7829, -73.9654, "Central Park, NYC")
WALL_STREET    = Location(40.7074, -74.0113, "Wall Street, NYC")
BROOKLYN       = Location(40.6782, -73.9442, "Brooklyn, NYC")
JFK_AIRPORT    = Location(40.6413, -73.7781, "JFK Airport, NYC")
SOHO           = Location(40.7233, -74.0030, "SoHo, NYC")
MIDTOWN        = Location(40.7549, -73.9840, "Midtown, NYC")
UPPER_EAST     = Location(40.7736, -73.9566, "Upper East Side, NYC")


def run():
    console.print(Panel.fit(
        "[bold cyan]Ride-Sharing System — Live Demo[/]\n"
        "[dim]Drivers · Riders · Matching · Pricing · Ratings[/]",
        border_style="cyan",
    ))

    # Normal time (afternoon, no surge in these zones)
    normal_time = datetime(2026, 3, 10, 14, 30)  # Tuesday 2:30 PM

    app = RideShareSystem("QuickRide NYC")

    # ----------------------------------------------------------
    # 1. Register Drivers
    # ----------------------------------------------------------
    section("1 · Registering Drivers & Vehicles")

    drivers_data = [
        ("Marcus Johnson", "+1-555-1001",
         Vehicle(VehicleType.ECONOMY, "Toyota", "Camry", "NYC-1234", "Silver", 2023),
         MIDTOWN),
        ("Priya Patel", "+1-555-1002",
         Vehicle(VehicleType.COMFORT, "Honda", "Accord", "NYC-2345", "Black", 2024),
         SOHO),
        ("James Chen", "+1-555-1003",
         Vehicle(VehicleType.PREMIUM, "BMW", "5 Series", "NYC-3456", "White", 2025),
         UPPER_EAST),
        ("Sofia Rodriguez", "+1-555-1004",
         Vehicle(VehicleType.SUV, "Chevrolet", "Tahoe", "NYC-4567", "Black", 2024),
         BROOKLYN),
        ("Ahmed Hassan", "+1-555-1005",
         Vehicle(VehicleType.XL, "Ford", "Transit", "NYC-5678", "White", 2023),
         WALL_STREET),
    ]

    driver_objs = []
    for name, phone, vehicle, loc in drivers_data:
        d = app.register_driver(name, phone, vehicle)
        app.go_online(d.id, loc)
        driver_objs.append(d)

    # Give some drivers ratings
    driver_objs[0].rating_sum, driver_objs[0].rating_count = 22.5, 5   # 4.50
    driver_objs[1].rating_sum, driver_objs[1].rating_count = 24.0, 5   # 4.80
    driver_objs[2].rating_sum, driver_objs[2].rating_count = 24.5, 5   # 4.90
    driver_objs[3].rating_sum, driver_objs[3].rating_count = 21.0, 5   # 4.20
    driver_objs[4].rating_sum, driver_objs[4].rating_count = 23.0, 5   # 4.60

    table = Table(title="[bold]Registered Drivers[/]", box=box.ROUNDED, show_lines=True)
    table.add_column("Name",     style="bold")
    table.add_column("Vehicle",  style="cyan")
    table.add_column("Type",     no_wrap=True)
    table.add_column("Location")
    table.add_column("Rating",   justify="right")
    table.add_column("Status",   no_wrap=True)

    for d in driver_objs:
        sc = "green" if d.status == DriverStatus.AVAILABLE else "dim"
        table.add_row(
            d.name, str(d.vehicle), d.vehicle.vehicle_type.value,
            str(d.location), f"* {d.rating:.1f}",
            f"[{sc}]{d.status.value}[/]",
        )
    console.print(table)

    # ----------------------------------------------------------
    # 2. Register Riders
    # ----------------------------------------------------------
    section("2 · Registering Riders")

    alice = app.register_rider("Alice Wong",    "alice@example.com",  "+1-555-2001")
    bob   = app.register_rider("Bob Martinez",  "bob@example.com",    "+1-555-2002")
    carol = app.register_rider("Carol White",   "carol@example.com",  "+1-555-2003")

    rtable = Table(title="[bold]Registered Riders[/]", box=box.SIMPLE_HEAD)
    rtable.add_column("Name",  style="bold")
    rtable.add_column("Email")
    rtable.add_column("Phone")
    for r in [alice, bob, carol]:
        rtable.add_row(r.name, r.email, r.phone)
    console.print(rtable)

    # ----------------------------------------------------------
    # 3. Fare Comparison
    # ----------------------------------------------------------
    section("3 · Fare Comparison: Times Square -> JFK Airport")

    fares = app.compare_fares(TIMES_SQUARE, JFK_AIRPORT, now=normal_time)
    ftable = Table(title="[bold]Fare Comparison[/]", box=box.ROUNDED, show_lines=True)
    ftable.add_column("Vehicle Type", style="bold")
    ftable.add_column("Base",        justify="right")
    ftable.add_column("Distance",    justify="right")
    ftable.add_column("Time",        justify="right")
    ftable.add_column("Surge",       justify="right", style="yellow")
    ftable.add_column("Premium",     justify="right", style="cyan")
    ftable.add_column("Platform Fee",justify="right", style="dim")
    ftable.add_column("Total",       justify="right", style="bold magenta")

    for vt_name, bd in fares.items():
        ftable.add_row(
            vt_name, f"${bd.base_fare:.2f}", f"${bd.distance_charge:.2f}",
            f"${bd.time_charge:.2f}",
            f"+${bd.surge_amount:.2f}" if bd.surge_amount else "—",
            f"+${bd.vehicle_premium:.2f}" if bd.vehicle_premium else "—",
            f"${bd.platform_fee:.2f}",
            f"[bold]${bd.total:.2f}[/]",
        )
    console.print(ftable)
    console.print(f"  [dim]Distance: {list(fares.values())[0].distance_km} km | "
                  f"Duration: {list(fares.values())[0].duration_min} min[/]")

    # ----------------------------------------------------------
    # 4. Full Ride Lifecycle: Alice takes Economy
    # ----------------------------------------------------------
    section("4 · Full Ride: Alice — Times Square -> Central Park (Economy)")

    ride1 = app.request_ride(alice.id, TIMES_SQUARE, CENTRAL_PARK,
                             VehicleType.ECONOMY, now=normal_time)
    console.print(f"  [green]* Ride requested[/] | Est. fare: [bold]${ride1.estimated_fare:.2f}[/]")

    ride1 = app.match_driver(ride1.id, now=normal_time)
    console.print(f"  [green]* Driver matched[/] | {ride1.driver.name} — {ride1.driver.vehicle}")

    ride1 = app.driver_arriving(ride1.id, now=normal_time)
    console.print(f"  [green]* Driver arriving[/]")

    ride1 = app.start_trip(ride1.id, now=normal_time)
    console.print(f"  [green]* Trip started[/]")

    ride1 = app.complete_trip(ride1.id, actual_km=3.2, actual_min=12.0, now=normal_time)
    console.print(f"  [green]* Trip completed[/] | Fare: [bold]${ride1.fare:.2f}[/]")

    # Fare breakdown
    bd = ride1.fare_breakdown
    btable = Table(title="[bold]Fare Breakdown[/]", box=box.SIMPLE_HEAD)
    btable.add_column("Component",   style="bold", min_width=20)
    btable.add_column("Amount",      justify="right")
    btable.add_row("Base fare",      f"${bd.base_fare:.2f}")
    btable.add_row(f"Distance ({bd.distance_km} km)", f"${bd.distance_charge:.2f}")
    btable.add_row(f"Time ({bd.duration_min} min)",    f"${bd.time_charge:.2f}")
    if bd.surge_amount:
        btable.add_row(f"Surge ({bd.surge_multiplier}×)", f"[yellow]+${bd.surge_amount:.2f}[/]")
    btable.add_row("Platform fee",   f"${bd.platform_fee:.2f}")
    btable.add_row("[bold]Total[/]",  f"[bold green]${bd.total:.2f}[/]")
    console.print(btable)

    # Payment
    payment = app.pay(ride1.id, PaymentMethod.CREDIT_CARD)
    console.print(f"  [green]* Payment: ${payment.amount:.2f} via {payment.method.value}[/]")

    # Ratings
    app.rate_driver(ride1.id, 5.0, "Great driver!")
    app.rate_rider(ride1.id, 4.5, "Friendly rider")
    console.print(f"  [green]* Ratings submitted[/] | Driver: *5.0 | Rider: *4.5")

    # ----------------------------------------------------------
    # 5. Premium ride: Bob → JFK
    # ----------------------------------------------------------
    section("5 · Premium Ride: Bob — SoHo -> JFK Airport")

    ride2 = app.request_ride(bob.id, SOHO, JFK_AIRPORT,
                             VehicleType.PREMIUM, now=normal_time)
    console.print(f"  [green]* Ride requested[/] | Est. fare: [bold]${ride2.estimated_fare:.2f}[/]")

    app.use_rated_matching()  # Switch to highest-rated strategy
    console.print(f"  [cyan]> Matching strategy -> Highest Rated[/]")

    ride2 = app.match_driver(ride2.id, now=normal_time)
    console.print(f"  [green]* Matched[/] | {ride2.driver.name} (*{ride2.driver.rating:.1f}) — {ride2.driver.vehicle}")

    ride2 = app.driver_arriving(ride2.id, now=normal_time)
    ride2 = app.start_trip(ride2.id, now=normal_time)
    ride2 = app.complete_trip(ride2.id, actual_km=22.5, actual_min=42.0, now=normal_time)
    console.print(f"  [green]* Completed[/] | Fare: [bold]${ride2.fare:.2f}[/] | {ride2.distance_km} km, {ride2.duration_min} min")

    app.rate_driver(ride2.id, 4.8)
    app.pay(ride2.id, PaymentMethod.UPI)

    # ----------------------------------------------------------
    # 6. Surge Pricing Scenario
    # ----------------------------------------------------------
    section("6 · Surge Pricing — Rush Hour (5:30 PM)")

    rush_time = datetime(2026, 3, 10, 17, 30)  # 5:30 PM rush hour
    surge_fare = app.estimate_fare(TIMES_SQUARE, BROOKLYN, VehicleType.ECONOMY, now=rush_time)
    normal_fare = app.estimate_fare(TIMES_SQUARE, BROOKLYN, VehicleType.ECONOMY, now=normal_time)

    stable = Table(title="[bold]Surge vs Normal Pricing[/]", box=box.SIMPLE_HEAD)
    stable.add_column("Metric",  style="bold", min_width=20)
    stable.add_column("Normal (2:30 PM)", justify="right")
    stable.add_column("Rush Hour (5:30 PM)", justify="right", style="yellow")

    stable.add_row("Surge multiplier", f"{normal_fare.surge_multiplier}×",
                   f"[bold]{surge_fare.surge_multiplier}×[/]")
    stable.add_row("Surge amount",     f"${normal_fare.surge_amount:.2f}",
                   f"[yellow]+${surge_fare.surge_amount:.2f}[/]")
    stable.add_row("Total fare",       f"${normal_fare.total:.2f}",
                   f"[bold red]${surge_fare.total:.2f}[/]")
    stable.add_row("Difference",       "—",
                   f"[red]+${surge_fare.total - normal_fare.total:.2f}[/]")
    console.print(stable)

    # ----------------------------------------------------------
    # 7. Cancellation
    # ----------------------------------------------------------
    section("7 · Ride Cancellation & Fee")

    ride3 = app.request_ride(carol.id, CENTRAL_PARK, WALL_STREET,
                             VehicleType.COMFORT, now=normal_time)
    app.use_nearest_matching()
    ride3 = app.match_driver(ride3.id, now=normal_time)
    console.print(f"  Ride matched: {ride3.driver.name}")

    # Cancel after 3 minutes (within 2-5 min window → $3 fee)
    cancel_time = datetime(2026, 3, 10, 14, 33)
    ride3 = app.cancel_ride(ride3.id, CancellationBy.RIDER,
                            "Changed my mind", now=cancel_time)
    console.print(
        f"  [red]x Cancelled[/] | By: {ride3.cancelled_by.value} | "
        f"Fee: [bold]${ride3.cancel_fee:.2f}[/] | Reason: {ride3.cancel_reason}"
    )

    # ----------------------------------------------------------
    # 8. Driver & Rider Stats
    # ----------------------------------------------------------
    section("8 · Driver Leaderboard")

    dtable = Table(title="[bold]Driver Stats[/]", box=box.ROUNDED, show_lines=True)
    dtable.add_column("Driver",   style="bold")
    dtable.add_column("Vehicle",  style="cyan")
    dtable.add_column("Trips",    justify="right")
    dtable.add_column("Earnings", justify="right")
    dtable.add_column("Rating",   justify="right")
    dtable.add_column("Status",   no_wrap=True)

    for d in sorted(app.list_drivers(), key=lambda x: x.earnings, reverse=True):
        sc = {"AVAILABLE": "green", "ON_TRIP": "yellow", "OFFLINE": "dim"}.get(d.status.value, "white")
        dtable.add_row(
            d.name,
            d.vehicle.vehicle_type.value if d.vehicle else "—",
            str(d.total_trips),
            f"[green]${d.earnings:.2f}[/]",
            f"* {d.rating:.2f}",
            f"[{sc}]{d.status.value}[/]",
        )
    console.print(dtable)

    # ----------------------------------------------------------
    # 9. Event Log
    # ----------------------------------------------------------
    section("9 · Event Log")

    etable = Table(title="[bold]Events Published[/]", box=box.SIMPLE_HEAD)
    etable.add_column("Time",    style="dim", no_wrap=True)
    etable.add_column("Event",   style="bold", no_wrap=True)
    etable.add_column("Details", overflow="fold")

    for ev in app.event_history[:20]:
        details = {k: v for k, v in ev.data.items() if k not in ("ride_id",)}
        etable.add_row(
            ev.timestamp.strftime("%H:%M:%S"),
            ev.event_type.value,
            str(details),
        )
    console.print(etable)

    if len(app.event_history) > 20:
        console.print(f"  [dim]... and {len(app.event_history) - 20} more events[/]")

    console.print()
    console.print(Panel.fit(
        "[bold green]*  Demo complete![/]\n"
        "[dim]Patterns: Strategy (matching), State Machine (ride lifecycle), "
        "Observer (events), Repository (data), Facade (entry point)[/]",
        border_style="green",
    ))


if __name__ == "__main__":
    run()
