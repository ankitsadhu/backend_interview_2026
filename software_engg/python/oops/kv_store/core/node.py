"""
core/node.py
------------
Doubly Linked List Node.

Each node holds one key-value pair.
The LRU list positions nodes from MRU (head-side) to LRU (tail-side).
"""

from __future__ import annotations
from typing import Any


class Node:
    """
    A node in the doubly linked list used by the LRU engine.

    Attributes:
        key   : Cache key (used to locate node in the hashmap on eviction)
        value : Cached value
        prev  : Pointer to previous (more recently used) node
        next  : Pointer to next (less recently used) node
    """

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: Any = None, value: Any = None) -> None:
        self.key:   Any           = key
        self.value: Any           = value
        self.prev:  Node | None   = None
        self.next:  Node | None   = None

    def __repr__(self) -> str:
        return f"Node({self.key!r}: {self.value!r})"
