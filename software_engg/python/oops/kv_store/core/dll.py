"""
core/dll.py
-----------
Doubly Linked List with sentinel (dummy) head and tail nodes.

Layout:
    head <-> [MRU ... LRU] <-> tail
    head.next = Most Recently Used
    tail.prev = Least Recently Used

All operations are O(1):
  - add_to_front(node)    — makes node the MRU
  - remove(node)          — unlinks node
  - remove_last() -> Node — removes & returns the LRU node

Sentinel nodes eliminate all None checks — every real node always has
non-None prev and next pointers.
"""

from __future__ import annotations
from .node import Node


class DoublyLinkedList:

    def __init__(self) -> None:
        # Sentinel nodes — never hold real data
        self._head = Node()   # dummy MRU sentinel
        self._tail = Node()   # dummy LRU sentinel
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    # ── O(1) operations ──────────────────────────────────────────────────────

    def add_to_front(self, node: Node) -> None:
        """Insert node right after head (= mark as MRU)."""
        node.prev        = self._head
        node.next        = self._head.next
        self._head.next.prev = node
        self._head.next  = node
        self._size += 1

    def remove(self, node: Node) -> None:
        """Unlink node from its current position."""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None   # help GC
        self._size -= 1

    def remove_last(self) -> Node | None:
        """Remove and return the LRU node (tail.prev), or None if empty."""
        lru = self._tail.prev
        if lru is self._head:       # list is empty
            return None
        self.remove(lru)
        return lru

    def move_to_front(self, node: Node) -> None:
        """Re-mark an existing node as MRU — O(1)."""
        self.remove(node)
        self.add_to_front(node)

    # ── introspection ─────────────────────────────────────────────────────────

    @property
    def size(self) -> int:
        return self._size

    def to_list(self) -> list:
        """Return keys in MRU → LRU order (for debugging)."""
        result, cur = [], self._head.next
        while cur is not self._tail:
            result.append(cur.key)
            cur = cur.next
        return result

    def __repr__(self) -> str:
        return f"DLL({self.to_list()})"
