"""
models/book.py
--------------
Book      - logical title (ISBN, metadata)
BookCopy  - physical copy of a Book with a state machine
BookStatus - AVAILABLE | BORROWED | RESERVED | LOST

One Book ---> many BookCopy instances
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Genre(Enum):
    FICTION     = "Fiction"
    NON_FICTION = "Non-Fiction"
    SCIENCE     = "Science"
    TECHNOLOGY  = "Technology"
    HISTORY     = "History"
    BIOGRAPHY   = "Biography"
    SELF_HELP   = "Self-Help"
    OTHER       = "Other"


class BookCopyStatus(Enum):
    AVAILABLE = "Available"
    BORROWED  = "Borrowed"
    RESERVED  = "Reserved"
    LOST      = "Lost"


# ── BookCopy — physical instance ──────────────────────────────────────────────

class BookCopy:
    """
    Represents one physical copy of a Book.
    Owns a simple state machine:
        AVAILABLE --> BORROWED --> AVAILABLE
        AVAILABLE --> RESERVED --> AVAILABLE | BORROWED
        BORROWED  --> LOST
    """

    # Valid transitions: source_status -> set of allowed target statuses
    _TRANSITIONS: dict[BookCopyStatus, set[BookCopyStatus]] = {
        BookCopyStatus.AVAILABLE: {BookCopyStatus.BORROWED, BookCopyStatus.RESERVED},
        BookCopyStatus.BORROWED:  {BookCopyStatus.AVAILABLE, BookCopyStatus.LOST},
        BookCopyStatus.RESERVED:  {BookCopyStatus.AVAILABLE, BookCopyStatus.BORROWED},
        BookCopyStatus.LOST:      set(),  # terminal state
    }

    def __init__(self, isbn: str):
        self.copy_id: str             = str(uuid.uuid4())[:8].upper()
        self.isbn:    str             = isbn
        self._status: BookCopyStatus  = BookCopyStatus.AVAILABLE

    @property
    def status(self) -> BookCopyStatus:
        return self._status

    @property
    def is_available(self) -> bool:
        return self._status == BookCopyStatus.AVAILABLE

    def transition(self, new_status: BookCopyStatus) -> None:
        allowed = self._TRANSITIONS[self._status]
        if new_status not in allowed:
            raise ValueError(
                f"Copy {self.copy_id}: invalid transition "
                f"{self._status.value} -> {new_status.value}"
            )
        self._status = new_status

    def __repr__(self) -> str:
        return f"BookCopy[{self.copy_id} | {self._status.value}]"


# ── Book — logical title ──────────────────────────────────────────────────────

@dataclass
class Book:
    isbn:   str
    title:  str
    author: str
    genre:  Genre
    _copies: list[BookCopy] = field(default_factory=list, init=False, repr=False)

    # ── copy management ───────────────────────────────────────────────────────

    def add_copy(self) -> BookCopy:
        copy = BookCopy(self.isbn)
        self._copies.append(copy)
        return copy

    def available_copies(self) -> list[BookCopy]:
        return [c for c in self._copies if c.is_available]

    def total_copies(self) -> int:
        return len(self._copies)

    def get_copy(self, copy_id: str) -> Optional[BookCopy]:
        return next((c for c in self._copies if c.copy_id == copy_id), None)

    def copy_summary(self) -> dict[str, int]:
        summary: dict[str, int] = {s.value: 0 for s in BookCopyStatus}
        for c in self._copies:
            summary[c.status.value] += 1
        return summary

    def __repr__(self) -> str:
        avail = len(self.available_copies())
        total = self.total_copies()
        return f'Book["{self.title}" by {self.author} | {avail}/{total} avail]'
