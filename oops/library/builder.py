"""
library/builder.py
------------------
LibraryBuilder -- fluent API over Library + helper for bulk-seeding a catalog.
"""

from __future__ import annotations
from .library          import Library
from .models.book      import Book, Genre
from .models.member    import Member, MemberFactory, MemberType
from .strategies.fine  import FineFactory, FineStrategy


class LibraryBuilder:
    """
    Usage:
        lib = (
            LibraryBuilder("City Public Library")
            .with_fine_strategy("tiered")
            .add_book("978-0-06-112008-4", "To Kill a Mockingbird", "Harper Lee",
                      Genre.FICTION, copies=3)
            .add_member("Alice",   "alice@ex.com", MemberType.STUDENT)
            .build()
        )
    """

    def __init__(self, name: str) -> None:
        self._name:    str           = name
        self._fine:    FineStrategy  = FineFactory.get("tiered")
        self._books:   list[tuple]   = []   # (isbn, title, author, genre, copies)
        self._members: list[Member]  = []

    def with_fine_strategy(self, name: str) -> "LibraryBuilder":
        self._fine = FineFactory.get(name)
        return self

    def add_book(
        self,
        isbn:   str,
        title:  str,
        author: str,
        genre:  Genre,
        copies: int = 1,
    ) -> "LibraryBuilder":
        self._books.append((isbn, title, author, genre, copies))
        return self

    def add_member(
        self,
        name:        str,
        email:       str,
        member_type: MemberType = MemberType.STUDENT,
    ) -> "LibraryBuilder":
        self._members.append(MemberFactory.create(name, email, member_type))
        return self

    def build(self) -> Library:
        lib = Library(self._name, self._fine)
        for (isbn, title, author, genre, copies) in self._books:
            lib.add_book(Book(isbn, title, author, genre), copies)
        for member in self._members:
            lib.register_member(member)
        return lib
