"""
core/lru.py
-----------
Pure LRU engine — no TTL, no threading, no stats.
Combines a DoublyLinkedList with a HashMap for O(1) get / put / remove.

Complexity:
  get(key)         -> O(1)
  put(key, value)  -> O(1)  [amortised, includes eviction]
  remove(key)      -> O(1)
  evict_lru()      -> O(1)

HashMap:  key -> Node   (find node in O(1))
DLL:      Node ordering MRU...LRU  (evict LRU in O(1), promote in O(1))

                 ┌─────────────────────────────────────┐
    HashMap      │  key1─►Node1   key2─►Node2  ...     │
                 └─────────────────────────────────────┘
                           │              │
    DLL    head <-> [Node1 <-> Node2 <-> ...] <-> tail
                    (MRU)                    (LRU)
"""

from __future__ import annotations
from typing import Any
from .dll  import DoublyLinkedList
from .node import Node

_SENTINEL = object()   # distinct from None so None can be a valid value


class LRUEngine:
    """
    Thread-UNsafe LRU engine.
    KVStore wraps this with a lock.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("LRU capacity must be >= 1")
        self._capacity = capacity
        self._map:  dict[Any, Node] = {}
        self._dll   = DoublyLinkedList()

    # ── public interface ──────────────────────────────────────────────────────

    def get(self, key: Any) -> Any:
        """
        Return value for key, promoting it to MRU.
        Returns _SENTINEL if key not found (so None can be a stored value).
        """
        node = self._map.get(key)
        if node is None:
            return _SENTINEL
        self._dll.move_to_front(node)
        return node.value

    def put(self, key: Any, value: Any) -> Any | None:
        """
        Insert or update key.
        Returns the evicted key if capacity was exceeded, else None.
        """
        if key in self._map:
            node = self._map[key]
            node.value = value
            self._dll.move_to_front(node)
            return None                      # update — no eviction

        # new key
        node = Node(key, value)
        self._map[key] = node
        self._dll.add_to_front(node)

        if self._dll.size > self._capacity:
            return self._evict_lru()
        return None

    def remove(self, key: Any) -> bool:
        """Remove key explicitly. Returns True if key existed."""
        node = self._map.pop(key, None)
        if node is None:
            return False
        self._dll.remove(node)
        return True

    def update_value(self, key: Any, value: Any) -> bool:
        """Update value of an existing key WITHOUT changing LRU order."""
        node = self._map.get(key)
        if node is None:
            return False
        node.value = value
        return True

    # ── introspection ─────────────────────────────────────────────────────────

    def contains(self, key: Any) -> bool:
        return key in self._map

    def size(self) -> int:
        return self._dll.size

    def capacity(self) -> int:
        return self._capacity

    def lru_order(self) -> list:
        """Keys from MRU → LRU (for debugging/testing)."""
        return self._dll.to_list()

    # ── internal ──────────────────────────────────────────────────────────────

    def _evict_lru(self) -> Any:
        lru_node = self._dll.remove_last()
        if lru_node:
            del self._map[lru_node.key]
            return lru_node.key
        return None


MISSING = _SENTINEL    # export for callers that need to check for absence
