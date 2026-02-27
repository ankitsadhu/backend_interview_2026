"""
core/ttl_manager.py
-------------------
Min-heap based TTL tracker with lazy deletion.

Design:
  - Each key with a TTL has an entry in `_expiry: dict[key, float]`
    mapping to its absolute expiry timestamp (time.monotonic()).
  - A min-heap `_heap` holds (expire_at, key) tuples for efficient
    "find the next key to expire" in O(log n).
  - Lazy deletion: stale heap entries (from updates/removes) are
    discarded when they surface during purge_expired().
  - Active cleanup: call purge_expired() periodically or before each
    get/put to reclaim memory.

Complexity:
  set_ttl(key, ttl)       -> O(log n)   heap push
  is_expired(key)         -> O(1)       dict lookup + time check
  remaining_ttl(key)      -> O(1)
  remove(key)             -> O(1)       dict delete (heap cleaned lazily)
  purge_expired()         -> O(k log n) where k = expired keys
"""

from __future__ import annotations
import heapq
import time
from typing import Any


class TTLManager:

    def __init__(self) -> None:
        # key -> absolute monotonic expiry time
        self._expiry: dict[Any, float] = {}
        # min-heap of (expire_at, key) — may contain stale entries
        self._heap: list[tuple[float, Any]] = []

    # ── set / update TTL ──────────────────────────────────────────────────────

    def set_ttl(self, key: Any, ttl_seconds: float) -> None:
        """Assign or reset TTL for key. O(log n)."""
        if ttl_seconds <= 0:
            raise ValueError(f"TTL must be positive, got {ttl_seconds}")
        expire_at = time.monotonic() + ttl_seconds
        self._expiry[key] = expire_at
        heapq.heappush(self._heap, (expire_at, key))

    def remove(self, key: Any) -> None:
        """
        Remove TTL for key (makes key permanent or was deleted).
        O(1) — stale heap entry cleaned up lazily in purge_expired().
        """
        self._expiry.pop(key, None)

    def persist(self, key: Any) -> bool:
        """Remove TTL to make key permanent. Returns True if TTL existed."""
        existed = key in self._expiry
        self._expiry.pop(key, None)
        return existed

    # ── query ──────────────────────────────────────────────────────────────────

    def has_ttl(self, key: Any) -> bool:
        return key in self._expiry

    def is_expired(self, key: Any) -> bool:
        """O(1). Returns True if key has a TTL that has passed."""
        expire_at = self._expiry.get(key)
        if expire_at is None:
            return False          # no TTL = immortal
        return time.monotonic() >= expire_at

    def remaining_ttl(self, key: Any) -> float | None:
        """
        Returns remaining TTL in seconds.
        Returns None if key has no TTL.
        Returns 0.0 if already expired (lazy — not yet purged).
        """
        expire_at = self._expiry.get(key)
        if expire_at is None:
            return None
        remaining = expire_at - time.monotonic()
        return max(0.0, round(remaining, 4))

    # ── cleanup ───────────────────────────────────────────────────────────────

    def purge_expired(self) -> list[Any]:
        """
        Drain the heap of all expired entries.
        Returns list of expired keys (ignoring stale/already-removed entries).
        O(k log n) where k = number of expired entries.
        """
        now = time.monotonic()
        expired: list[Any] = []

        while self._heap:
            expire_at, key = self._heap[0]

            if expire_at > now:
                break   # min-heap: nothing older left

            heapq.heappop(self._heap)

            # Check if this heap entry is stale (key was re-set or removed)
            current_expiry = self._expiry.get(key)
            if current_expiry is None:
                continue                        # key was removed — discard
            if current_expiry != expire_at:
                continue                        # key TTL was updated — discard

            # Genuinely expired
            del self._expiry[key]
            expired.append(key)

        return expired

    def __len__(self) -> int:
        return len(self._expiry)

    def __repr__(self) -> str:
        return f"TTLManager(tracked={len(self._expiry)}, heap_size={len(self._heap)})"
