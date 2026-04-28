"""
store.py
--------
KVStore — Main in-memory key-value store.

Combines:
  - LRUEngine    (O(1) get/put/evict via DLL + HashMap)
  - TTLManager   (min-heap expiry tracking with lazy cleanup)
  - StoreStats   (hit/miss/eviction counters)
  - threading.RLock (full thread-safety for concurrent access)

Public API:
  set(key, value, ttl=None)     -> None
  get(key, default=None)        -> Any
  delete(key)                   -> bool
  exists(key)                   -> bool
  persist(key)                  -> bool     (remove TTL, make permanent)
  ttl(key)                      -> float|None
  get_with_ttl(key)             -> (value, remaining_ttl) | (None, None)
  keys()                        -> list
  size()                        -> int
  clear()                       -> None
  stats()                       -> dict

Thread-safety: All public methods acquire a single RLock (reentrant).
               RLock allows the same thread to re-acquire without deadlock.
"""

from __future__ import annotations
import threading
from typing import Any

from .core.lru         import LRUEngine, MISSING
from .core.ttl_manager import TTLManager
from .stats            import StoreStats


class KVStore:
    """
    Thread-safe in-memory KV store with LRU eviction and per-key TTL.

    Parameters
    ----------
    capacity    : Maximum number of keys in the store at once.
                  When full, the LRU (least recently used) key is evicted.
    default_ttl : Optional default TTL (seconds) applied to every set()
                  that doesn't supply its own ttl argument.
    """

    def __init__(self, capacity: int = 128, default_ttl: float | None = None) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be >= 1")

        self._capacity    = capacity
        self._default_ttl = default_ttl
        self._lru         = LRUEngine(capacity)
        self._ttl         = TTLManager()
        self._stats       = StoreStats()
        self._lock        = threading.RLock()   # reentrant — same thread can re-enter

    # ── WRITE ─────────────────────────────────────────────────────────────────

    def set(self, key: Any, value: Any, ttl: float | None = None) -> None:
        """
        Insert or overwrite key with value.

        TTL priority: explicit ttl arg > default_ttl > None (immortal).

        If adding the key causes capacity overflow, the LRU key is
        evicted (and its TTL entry cleaned up) automatically.
        """
        effective_ttl = ttl if ttl is not None else self._default_ttl

        with self._lock:
            # Purge expired keys before writing (keeps memory tight)
            self._purge()

            evicted_key = self._lru.put(key, value)
            if evicted_key is not None:
                self._ttl.remove(evicted_key)
                self._stats.record_eviction()

            # Register / update TTL
            if effective_ttl is not None:
                self._ttl.set_ttl(key, effective_ttl)
            else:
                # key might have had a TTL before — remove it (now immortal)
                self._ttl.remove(key)

            self._stats.record_set()

    # ── READ ──────────────────────────────────────────────────────────────────

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Retrieve value for key, promoting it to MRU.

        Returns `default` if key is absent or expired.
        Expired keys are lazily removed on access.
        """
        with self._lock:
            # Lazy expiry check — O(1)
            if self._ttl.is_expired(key):
                self._expire_key(key)
                self._stats.record_miss()
                return default

            result = self._lru.get(key)
            if result is MISSING:
                self._stats.record_miss()
                return default

            self._stats.record_hit()
            return result

    def get_with_ttl(self, key: Any) -> tuple[Any, float | None]:
        """
        Returns (value, remaining_ttl_seconds).
        Returns (None, None) if key is absent or expired.
        remaining_ttl = None means key is immortal (no TTL set).
        """
        with self._lock:
            if self._ttl.is_expired(key):
                self._expire_key(key)
                return None, None

            result = self._lru.get(key)
            if result is MISSING:
                return None, None

            self._stats.record_hit()
            return result, self._ttl.remaining_ttl(key)

    # ── DELETE ────────────────────────────────────────────────────────────────

    def delete(self, key: Any) -> bool:
        """
        Explicitly delete a key.
        Returns True if the key existed, False otherwise.
        """
        with self._lock:
            removed = self._lru.remove(key)
            self._ttl.remove(key)
            if removed:
                self._stats.record_delete()
            return removed

    # ── UTILITIES ─────────────────────────────────────────────────────────────

    def exists(self, key: Any) -> bool:
        """True if key exists AND is not expired."""
        with self._lock:
            if self._ttl.is_expired(key):
                self._expire_key(key)
                return False
            return self._lru.contains(key)

    def persist(self, key: Any) -> bool:
        """
        Remove TTL from key, making it permanent (immortal).
        Returns True if the key had a TTL that was removed.
        """
        with self._lock:
            if not self._lru.contains(key):
                return False
            return self._ttl.persist(key)

    def ttl(self, key: Any) -> float | None:
        """
        Returns remaining TTL in seconds.
        Returns None  if key has no TTL (immortal).
        Returns -1.0  if key does not exist.
        Returns 0.0   if key is expired but not yet purged.
        """
        with self._lock:
            if not self._lru.contains(key):
                return -1.0
            return self._ttl.remaining_ttl(key)

    def update_ttl(self, key: Any, new_ttl: float) -> bool:
        """Reset TTL for an existing key. Returns False if key not found."""
        with self._lock:
            if not self._lru.contains(key):
                return False
            self._ttl.set_ttl(key, new_ttl)
            return True

    # ── INTROSPECTION ─────────────────────────────────────────────────────────

    def size(self) -> int:
        """Current number of live (non-expired) keys."""
        with self._lock:
            self._purge()
            return self._lru.size()

    def capacity(self) -> int:
        return self._capacity

    def keys(self) -> list:
        """All live keys in MRU → LRU order."""
        with self._lock:
            self._purge()
            return self._lru.lru_order()

    def clear(self) -> None:
        """Wipe all keys, TTLs, and stats."""
        with self._lock:
            self._lru  = LRUEngine(self._capacity)
            self._ttl  = TTLManager()
            self._stats.reset()

    def stats(self) -> dict:
        """Return operational metrics snapshot."""
        with self._lock:
            report = self._stats.report()
            report["size"]     = self._lru.size()
            report["capacity"] = self._capacity
            report["lru_order"] = self._lru.lru_order()
            return report

    # ── INTERNAL ──────────────────────────────────────────────────────────────

    def _purge(self) -> None:
        """Drain TTL heap and evict all expired keys from LRU. Caller holds lock."""
        for expired_key in self._ttl.purge_expired():
            self._lru.remove(expired_key)
            self._stats.record_expiration()

    def _expire_key(self, key: Any) -> None:
        """Lazily remove a single key known to be expired. Caller holds lock."""
        self._ttl.remove(key)
        self._lru.remove(key)
        self._stats.record_expiration()

    # ── DUNDER ────────────────────────────────────────────────────────────────

    def __setitem__(self, key: Any, value: Any) -> None:
        """kv[key] = value  (uses default_ttl)"""
        self.set(key, value)

    def __getitem__(self, key: Any) -> Any:
        """kv[key]  — raises KeyError on miss"""
        result = self.get(key, default=MISSING)
        if result is MISSING:
            raise KeyError(key)
        return result

    def __delitem__(self, key: Any) -> None:
        if not self.delete(key):
            raise KeyError(key)

    def __contains__(self, key: Any) -> bool:
        return self.exists(key)

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return (
            f"KVStore(capacity={self._capacity}, "
            f"size={self._lru.size()}, "
            f"default_ttl={self._default_ttl})"
        )
