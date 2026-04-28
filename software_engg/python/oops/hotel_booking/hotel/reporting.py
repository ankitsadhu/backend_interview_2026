"""
reporting.py — Hotel analytics and reporting.

Reports:
  - OccupancyReport   : occupancy % by date range / room type
  - RevenueReport     : revenue totals, per room type breakdown
  - RoomStatusReport  : current snapshot of all room statuses
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List

from .models import Reservation, ReservationStatus, Room, RoomStatus, RoomType


# ============================================================
# Helpers
# ============================================================

def _date_range(start: date, end: date) -> List[date]:
    days = []
    d = start
    while d < end:
        days.append(d)
        d += timedelta(days=1)
    return days


# ============================================================
# Room Status Snapshot
# ============================================================

@dataclass
class RoomStatusReport:
    snapshot_at   : date
    rooms         : List[Room]

    @property
    def by_status(self) -> Dict[str, List[Room]]:
        result: Dict[str, List[Room]] = defaultdict(list)
        for room in self.rooms:
            result[room.status.value].append(room)
        return dict(result)

    @property
    def summary(self) -> Dict[str, int]:
        return {status: len(rooms) for status, rooms in self.by_status.items()}


# ============================================================
# Occupancy Report
# ============================================================

@dataclass
class OccupancyReport:
    start_date       : date
    end_date         : date
    total_rooms      : int
    reservations     : List[Reservation]

    @property
    def total_room_nights(self) -> int:
        return self.total_rooms * (self.end_date - self.start_date).days

    @property
    def occupied_room_nights(self) -> int:
        """Count how many room-nights overlap the report window."""
        count = 0
        dates = _date_range(self.start_date, self.end_date)
        for r in self.reservations:
            if r.status == ReservationStatus.CANCELLED:
                continue
            for d in dates:
                if r.check_in <= d < r.check_out:
                    count += 1
        return count

    @property
    def occupancy_pct(self) -> float:
        if self.total_room_nights == 0:
            return 0.0
        return round(100 * self.occupied_room_nights / self.total_room_nights, 2)

    def by_room_type(self, rooms: List[Room]) -> Dict[str, float]:
        """Occupancy % broken down by RoomType."""
        result: Dict[str, float] = {}
        dates  = _date_range(self.start_date, self.end_date)
        n_days = len(dates)
        by_type: Dict[RoomType, List[Room]] = defaultdict(list)
        for room in rooms:
            by_type[room.room_type].append(room)

        for rt, rt_rooms in by_type.items():
            rt_ids     = {r.id for r in rt_rooms}
            total_rn   = len(rt_rooms) * n_days
            occupied   = 0
            for res in self.reservations:
                if res.status == ReservationStatus.CANCELLED:
                    continue
                if res.room.id not in rt_ids:
                    continue
                for d in dates:
                    if res.check_in <= d < res.check_out:
                        occupied += 1
            result[rt.value] = round(100 * occupied / total_rn, 2) if total_rn else 0.0
        return result


# ============================================================
# Revenue Report
# ============================================================

@dataclass
class RevenueReport:
    start_date   : date
    end_date     : date
    reservations : List[Reservation]

    @property
    def _completed(self) -> List[Reservation]:
        """Only count checked-out or confirmed reservations (not cancelled)."""
        return [
            r for r in self.reservations
            if r.status in (ReservationStatus.CHECKED_OUT, ReservationStatus.CONFIRMED,
                            ReservationStatus.CHECKED_IN)
            and r.check_out >= self.start_date
            and r.check_in  <= self.end_date
        ]

    @property
    def total_revenue(self) -> float:
        return round(sum(r.total_price for r in self._completed), 2)

    @property
    def total_refunds(self) -> float:
        return round(
            sum(r.refund_amount for r in self.reservations
                if r.status == ReservationStatus.CANCELLED), 2
        )

    @property
    def net_revenue(self) -> float:
        return round(self.total_revenue - self.total_refunds, 2)

    @property
    def by_room_type(self) -> Dict[str, float]:
        result: Dict[str, float] = defaultdict(float)
        for r in self._completed:
            result[r.room.room_type.value] += r.total_price
        return {k: round(v, 2) for k, v in result.items()}

    @property
    def avg_daily_rate(self) -> float:
        completed = self._completed
        if not completed:
            return 0.0
        adr = sum(r.total_price / r.nights for r in completed) / len(completed)
        return round(adr, 2)

    @property
    def total_bookings(self) -> int:
        return len(self._completed)

    @property
    def cancelled_bookings(self) -> int:
        return sum(1 for r in self.reservations if r.status == ReservationStatus.CANCELLED)
