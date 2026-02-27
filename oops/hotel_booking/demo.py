"""
demo.py — End-to-end walkthrough of the Hotel Booking System.

Demonstrates:
  1. Seeding hotel with 12 rooms (4 types)
  2. Registering 4 guests (different loyalty tiers)
  3. Creating 6 reservations (summer peak, weekends, corporate)
  4. Pricing breakdown per reservation
  5. Confirming, checking-in & checking-out 2 reservations (with extras)
  6. Cancelling 1 reservation — showing refund tiers
  7. Occupancy + Revenue reports
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from hotel import HotelSystem
from hotel.models import (
    LoyaltyTier, PaymentMethod, RoomType,
    ReservationStatus,
)

console = Console()


# ============================================================
# Helpers
# ============================================================

def section(title: str) -> None:
    console.print()
    console.print(Rule(f"[bold cyan]{title}[/]"))
    console.print()


def print_pricing_table(reservations: list) -> None:
    table = Table(
        title="[bold]Reservation Pricing Breakdown[/]",
        box=box.ROUNDED, show_lines=True,
    )
    table.add_column("ID",           style="dim",   no_wrap=True)
    table.add_column("Guest",        style="bold")
    table.add_column("Room",         style="cyan",  no_wrap=True)
    table.add_column("Check-In",     no_wrap=True)
    table.add_column("Nights",       justify="right")
    table.add_column("Base Rate",    justify="right")
    table.add_column("Seasonal +",   justify="right", style="yellow")
    table.add_column("Weekend +",    justify="right", style="yellow")
    table.add_column("Discounts",    justify="right", style="green")
    table.add_column("Total",        justify="right", style="bold magenta")

    for r in reservations:
        bd       = r.price_breakdown
        seasonal = bd.get("seasonal_surcharge", 0)
        weekend  = bd.get("weekend_surcharge", 0)
        loyalty  = bd.get("loyalty_discount", 0)
        corp     = bd.get("corporate_discount", 0)
        early    = bd.get("early_bird_discount", 0)
        discounts = loyalty + corp + early

        table.add_row(
            r.id[:8],
            r.guest.name,
            f"{r.room.number} ({r.room.room_type.value})",
            str(r.check_in),
            str(r.nights),
            f"${r.room.base_rate:.2f}/n",
            f"+${seasonal:.2f}" if seasonal else "—",
            f"+${weekend:.2f}"  if weekend  else "—",
            f"-${abs(discounts):.2f}" if discounts else "—",
            f"[bold]${r.total_price:.2f}[/]",
        )
    console.print(table)


def print_invoice(invoice) -> None:
    table = Table(
        title=f"[bold]Invoice #{invoice.id[:8]}[/]",
        box=box.SIMPLE_HEAD, show_lines=True,
    )
    table.add_column("Description",  style="bold", min_width=40)
    table.add_column("Qty",          justify="right")
    table.add_column("Unit Price",   justify="right")
    table.add_column("Total",        justify="right")

    for item in invoice.line_items:
        table.add_row(
            item.description,
            f"{item.quantity}",
            f"${item.unit_price:.2f}",
            f"${item.total:.2f}",
        )

    table.add_section()
    table.add_row("[dim]Subtotal[/]", "", "", f"[dim]${invoice.subtotal:.2f}[/]")
    table.add_row("[dim]Tax (12%)[/]", "", "", f"[dim]${invoice.tax_amount:.2f}[/]")
    table.add_row("[bold]Grand Total[/]", "", "", f"[bold green]${invoice.grand_total:.2f}[/]")
    console.print(table)


def print_rooms_table(hotel: HotelSystem) -> None:
    table = Table(
        title="[bold]Hotel Rooms[/]",
        box=box.ROUNDED, show_lines=True,
    )
    table.add_column("No.",      style="bold cyan", no_wrap=True)
    table.add_column("Type",     no_wrap=True)
    table.add_column("Floor",    justify="right")
    table.add_column("Capacity", justify="right")
    table.add_column("Rate/Night", justify="right")
    table.add_column("Amenities")
    table.add_column("Status",   no_wrap=True)

    status_colour = {
        "AVAILABLE"  : "green",
        "RESERVED"   : "yellow",
        "OCCUPIED"   : "red",
        "MAINTENANCE": "dim",
    }
    for room in sorted(hotel.list_rooms(), key=lambda r: r.number):
        sc = status_colour.get(room.status.value, "white")
        table.add_row(
            room.number,
            room.room_type.value,
            str(room.floor),
            str(room.capacity),
            f"${room.base_rate:.2f}",
            ", ".join(room.amenities) or "—",
            f"[{sc}]{room.status.value}[/]",
        )
    console.print(table)


def print_guests_table(hotel: HotelSystem) -> None:
    table = Table(title="[bold]Registered Guests[/]", box=box.SIMPLE_HEAD)
    table.add_column("ID",      style="dim", no_wrap=True)
    table.add_column("Name",    style="bold")
    table.add_column("Email")
    table.add_column("Loyalty", no_wrap=True)

    lc = {"STANDARD": "white", "SILVER": "bright_white",
          "GOLD": "yellow", "PLATINUM": "bold magenta"}
    for g in hotel.list_guests():
        c = lc.get(g.loyalty_tier.value, "white")
        table.add_row(g.id[:8], g.name, g.email, f"[{c}]{g.loyalty_tier.value}[/]")
    console.print(table)


# ============================================================
# Main Demo
# ============================================================

def run():
    console.print(
        Panel.fit(
            "[bold cyan]🏨  Hotel Booking System — Live Demo[/]\n"
            "[dim]Rooms · Guests · Reservations · Pricing · Reporting[/]",
            border_style="cyan",
        )
    )

    hotel = HotelSystem("Grand Horizon Hotel")

    # ----------------------------------------------------------
    # 1. Seed rooms
    # ----------------------------------------------------------
    section("1 · Seeding Hotel Rooms")

    rooms_data = [
        ("101", RoomType.SINGLE,    1,  90, ["WiFi", "TV"]),
        ("102", RoomType.SINGLE,    1,  95, ["WiFi", "TV", "City View"]),
        ("201", RoomType.DOUBLE,    2, 140, ["WiFi", "TV", "Mini-bar"]),
        ("202", RoomType.DOUBLE,    2, 150, ["WiFi", "TV", "Balcony"]),
        ("203", RoomType.DOUBLE,    2, 145, ["WiFi", "TV", "Mini-bar", "City View"]),
        ("301", RoomType.SUITE,     3, 280, ["WiFi", "TV", "Jacuzzi", "Lounge"]),
        ("302", RoomType.SUITE,     3, 300, ["WiFi", "TV", "Jacuzzi", "Ocean View"]),
        ("303", RoomType.SUITE,     3, 260, ["WiFi", "TV", "Lounge", "City View"]),
        ("401", RoomType.PENTHOUSE, 4, 650, ["WiFi", "TV", "Pool", "Butler", "Ocean View"]),
        ("402", RoomType.PENTHOUSE, 4, 700, ["WiFi", "TV", "Pool", "Butler", "Chef"]),
        # Maintenance example
        ("115", RoomType.SINGLE,    1,  90, ["WiFi"]),
        ("116", RoomType.SINGLE,    1,  90, ["WiFi"]),
    ]

    room_objs = {}
    for num, rt, floor, rate, amenities in rooms_data:
        r = hotel.add_room(num, rt, floor, rate, amenities)
        room_objs[num] = r

    # Put one room in maintenance
    hotel.set_room_maintenance(room_objs["115"].id, True)

    print_rooms_table(hotel)

    # ----------------------------------------------------------
    # 2. Register guests
    # ----------------------------------------------------------
    section("2 · Registering Guests")

    alice  = hotel.register_guest("Alice Johnson",  "alice@example.com",  "+1-555-0101", LoyaltyTier.PLATINUM)
    bob    = hotel.register_guest("Bob Martinez",   "bob@example.com",    "+1-555-0202", LoyaltyTier.GOLD)
    carol  = hotel.register_guest("Carol White",    "carol@example.com",  "+1-555-0303", LoyaltyTier.SILVER)
    dave   = hotel.register_guest("Dave Kumar",     "dave@example.com",   "+1-555-0404", LoyaltyTier.STANDARD)

    print_guests_table(hotel)

    # ----------------------------------------------------------
    # 3. Search availability
    # ----------------------------------------------------------
    section("3 · Searching Available Rooms (Jul 1–5, 2026 — Peak Season)")

    results = hotel.search(
        check_in  = date(2026, 7, 1),
        check_out = date(2026, 7, 5),
        guest_id  = alice.id,
    )
    table = Table(title="Available Rooms (sorted by price)", box=box.SIMPLE_HEAD)
    table.add_column("Room",     style="bold cyan")
    table.add_column("Type")
    table.add_column("Capacity", justify="right")
    table.add_column("Base Rate", justify="right")
    table.add_column("Quoted Price (4n)", justify="right", style="bold magenta")
    for av in results:
        table.add_row(
            av.room.number, av.room.room_type.value, str(av.room.capacity),
            f"${av.room.base_rate:.2f}", f"${av.price:.2f}",
        )
    console.print(table)

    # ----------------------------------------------------------
    # 4. Create reservations
    # ----------------------------------------------------------
    section("4 · Creating Reservations")

    all_reservations = []

    # Peak summer stay — Platinum loyalty
    r1 = hotel.book(room_objs["301"].id, alice.id,
                    date(2026, 7, 1), date(2026, 7, 5))
    all_reservations.append(r1)

    # Weekend stay — Gold loyalty
    r2 = hotel.book(room_objs["202"].id, bob.id,
                    date(2026, 8, 7), date(2026, 8, 10))  # Fri–Mon
    all_reservations.append(r2)

    # Silver loyalty — standard midweek dates
    r3 = hotel.book(room_objs["201"].id, carol.id,
                    date(2026, 9, 15), date(2026, 9, 18))
    all_reservations.append(r3)

    # Standard guest — peak December
    r4 = hotel.book(room_objs["101"].id, dave.id,
                    date(2026, 12, 20), date(2026, 12, 25))
    all_reservations.append(r4)

    # Penthouse — Platinum
    r5 = hotel.book(room_objs["401"].id, alice.id,
                    date(2026, 8, 14), date(2026, 8, 18))
    all_reservations.append(r5)

    # Future stay > 30 days out — early bird
    r6 = hotel.book(room_objs["102"].id, dave.id,
                    date(2027, 1, 10), date(2027, 1, 13))
    all_reservations.append(r6)

    print_pricing_table(all_reservations)

    # ----------------------------------------------------------
    # 5. Confirm + check-in + check-out (r1 & r2)
    # ----------------------------------------------------------
    section("5 · Confirm → Check-In → Check-Out")

    # Confirm all
    for res in all_reservations:
        hotel.confirm(res.id)

    console.print("[green]✓ All reservations confirmed.[/]")

    # Check-in r1 (Alice – Suite)
    hotel.check_in(r1.id)
    console.print(f"[bold]✓ Checked in:[/] {r1.guest.name} → Room {r1.room.number}")

    # Check-out r1 with extras
    r1_checked_out, invoice1 = hotel.check_out(
        r1.id,
        extras={
            "Room Service (Dinner)" : 85.00,
            "Spa Treatment"         : 120.00,
            "Minibar"               : 42.50,
        }
    )
    console.print(f"[bold]✓ Checked out:[/] {r1_checked_out.guest.name}")
    print_invoice(invoice1)

    # Process payment
    payment = hotel.pay(r1.id, PaymentMethod.CREDIT_CARD, invoice1.grand_total)
    console.print(
        f"[green]✓ Payment processed:[/] ${payment.amount:.2f} via {payment.method.value}"
    )

    # Check-in / check-out r2 (Bob – Double)
    hotel.check_in(r2.id)
    r2_out, invoice2 = hotel.check_out(r2.id, extras={"Parking": 30.00})
    console.print(f"\n[bold]✓ Checked out:[/] {r2_out.guest.name}")
    print_invoice(invoice2)

    # ----------------------------------------------------------
    # 6. Cancel a reservation — show refund policy
    # ----------------------------------------------------------
    section("6 · Cancellation & Refund Policy")

    # Simulate cancelling r4 (Dave, Dec 20–25) with different notice periods
    scenarios = [
        ("72 hours before check-in (full refund)", timedelta(hours=72)),
        ("36 hours before check-in (50% refund)",  timedelta(hours=36)),
        ("12 hours before check-in (no refund)",   timedelta(hours=12)),
    ]

    for label, delta in scenarios:
        simulated_now = datetime.combine(r4.check_in, datetime.min.time()) - delta
        fraction_label = f"{'100' if delta.total_seconds() >= 48*3600 else '50' if delta.total_seconds() >= 24*3600 else '0'}%"
        console.print(
            f"  [cyan]{label}[/] → refund = [bold]{fraction_label} × ${r4.total_price:.2f}[/]"
        )

    # Actually cancel r4 with 72h notice
    simulated_72h = datetime.combine(r4.check_in, datetime.min.time()) - timedelta(hours=72)
    cancelled = hotel.cancel(r4.id, reason="Change of plans", now=simulated_72h)
    console.print(
        f"\n[red]✗ Cancelled:[/] Reservation {cancelled.id[:8]} | "
        f"Refund: [bold green]${cancelled.refund_amount:.2f}[/]"
    )

    # ----------------------------------------------------------
    # 7. Reports
    # ----------------------------------------------------------
    section("7 · Reports")

    # Room status
    status_rpt = hotel.room_status_report()
    st = status_rpt.summary
    status_table = Table(title="Room Status Snapshot", box=box.SIMPLE_HEAD)
    status_table.add_column("Status", style="bold")
    status_table.add_column("Count", justify="right")
    for s, cnt in sorted(st.items()):
        colour = {"AVAILABLE": "green", "OCCUPIED": "red",
                  "RESERVED": "yellow", "MAINTENANCE": "dim"}.get(s, "white")
        status_table.add_row(f"[{colour}]{s}[/]", str(cnt))
    console.print(status_table)

    # Occupancy
    occ_rpt = hotel.occupancy_report(date(2026, 7, 1), date(2026, 12, 31))
    occ_table = Table(title="Occupancy Report (Jul–Dec 2026)", box=box.SIMPLE_HEAD)
    occ_table.add_column("Metric", style="bold")
    occ_table.add_column("Value",  justify="right")
    all_rooms = hotel.list_rooms()
    occ_table.add_row("Total room-nights possible", str(occ_rpt.total_room_nights))
    occ_table.add_row("Occupied room-nights",       str(occ_rpt.occupied_room_nights))
    occ_table.add_row("Overall Occupancy %",        f"[bold]{occ_rpt.occupancy_pct}%[/]")
    console.print(occ_table)

    occ_by_type = occ_rpt.by_room_type(all_rooms)
    bt_table = Table(title="Occupancy by Room Type", box=box.SIMPLE_HEAD)
    bt_table.add_column("Room Type", style="bold")
    bt_table.add_column("Occupancy %", justify="right")
    for rt, pct in occ_by_type.items():
        bt_table.add_row(rt, f"{pct}%")
    console.print(bt_table)

    # Revenue
    rev_rpt = hotel.revenue_report(date(2026, 1, 1), date(2027, 12, 31))
    rev_table = Table(title="Revenue Report", box=box.SIMPLE_HEAD)
    rev_table.add_column("Metric", style="bold")
    rev_table.add_column("Value",  justify="right")
    rev_table.add_row("Total Bookings",     str(rev_rpt.total_bookings))
    rev_table.add_row("Cancelled Bookings", str(rev_rpt.cancelled_bookings))
    rev_table.add_row("Gross Revenue",      f"${rev_rpt.total_revenue:,.2f}")
    rev_table.add_row("Total Refunds",      f"[red]-${rev_rpt.total_refunds:,.2f}[/]")
    rev_table.add_row("Net Revenue",        f"[bold green]${rev_rpt.net_revenue:,.2f}[/]")
    rev_table.add_row("Avg Daily Rate",     f"${rev_rpt.avg_daily_rate:.2f}")
    console.print(rev_table)

    by_type_table = Table(title="Revenue by Room Type", box=box.SIMPLE_HEAD)
    by_type_table.add_column("Room Type", style="bold")
    by_type_table.add_column("Revenue",   justify="right")
    for rt_name, amount in rev_rpt.by_room_type.items():
        by_type_table.add_row(rt_name, f"${amount:,.2f}")
    console.print(by_type_table)

    # ----------------------------------------------------------
    # 8. Event log
    # ----------------------------------------------------------
    section("8 · Domain Event Log")

    events_table = Table(title="Events Published", box=box.SIMPLE_HEAD,
                         show_header=True, padding=(0, 1))
    events_table.add_column("Time",       style="dim",  no_wrap=True)
    events_table.add_column("Event",      style="bold", no_wrap=True)
    events_table.add_column("Details",    overflow="fold")

    for ev in hotel.event_history:
        events_table.add_row(
            ev.timestamp.strftime("%H:%M:%S"),
            ev.event_type.value,
            str({k: v for k, v in ev.data.items() if k not in ("reservation_id",)}),
        )
    console.print(events_table)

    console.print()
    console.print(
        Panel.fit(
            "[bold green]✓  Demo complete![/]\n"
            "[dim]All patterns demonstrated: Strategy (pricing), State Machine, "
            "Repository, Observer (events), Facade.[/]",
            border_style="green",
        )
    )


if __name__ == "__main__":
    run()
