"""
stats.py
--------
StoreStats — tracks operational metrics of the KVStore.
Separated so instrumentation doesn't clutter core logic.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class StoreStats:
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    hits:         int = 0
    misses:       int = 0
    evictions:    int = 0   # LRU evictions
    expirations:  int = 0   # TTL expirations
    total_sets:   int = 0
    total_deletes: int = 0

    # ── atomic increments ─────────────────────────────────────────────────────

    def record_hit(self)        -> None:
        with self._lock: self.hits += 1

    def record_miss(self)       -> None:
        with self._lock: self.misses += 1

    def record_eviction(self)   -> None:
        with self._lock: self.evictions += 1

    def record_expiration(self) -> None:
        with self._lock: self.expirations += 1

    def record_set(self)        -> None:
        with self._lock: self.total_sets += 1

    def record_delete(self)     -> None:
        with self._lock: self.total_deletes += 1

    # ── derived metrics ───────────────────────────────────────────────────────

    @property
    def total_requests(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        total = self.total_requests
        return round(self.hits / total, 4) if total > 0 else 0.0

    @property
    def miss_rate(self) -> float:
        return round(1.0 - self.hit_rate, 4)

    def report(self) -> dict:
        return {
            "hits":          self.hits,
            "misses":        self.misses,
            "hit_rate":      f"{self.hit_rate:.1%}",
            "evictions":     self.evictions,
            "expirations":   self.expirations,
            "total_sets":    self.total_sets,
            "total_deletes": self.total_deletes,
        }

    def reset(self) -> None:
        with self._lock:
            self.hits = self.misses = self.evictions = 0
            self.expirations = self.total_sets = self.total_deletes = 0
